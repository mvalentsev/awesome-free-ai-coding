"""Expiring one access mode must preserve separately documented free eligibility."""
from datetime import date, datetime, timezone

import httpx
import pytest
import respx

from freetier_radar.models import Entry, expire_entries, load_registry, save_registry, requires_payment
from freetier_radar.prober import ProbeStatus, probe_entry
from freetier_radar.quotes import row_urls, row_quotes, row_quote_source

SOURCE = 'https://vendor.example/free-terms'
QUOTE = 'Recharged users retain their monthly free allowance after model replacement.'


def entry():
    return Entry.model_validate({
        'id': 'vendor', 'name': 'Vendor', 'category': 'api-free-tier',
        'url': 'https://vendor.example', 'offering': 'Free allowance',
        'free_part': 'models', 'models': [{'family': 'science-flash'}],
        'first_seen': '2026-10-01', 'last_verified': '2026-10-01',
        'probe': {'type': 'api-models', 'endpoint': 'https://vendor.example/v1/models',
                  'require_zero_price': True},
        'api': {'base_url': 'https://vendor.example/v1', 'model_ids': ['science-flash'],
                'model_access': {'science-flash': {'source': SOURCE, 'until': '2026-11-24T00:00:00-08:00'}}},
        'remaining_free': {'source': SOURCE, 'quote': QUOTE, 'free_part': 'unnamed',
                           'access': {'source': SOURCE, 'initial_payment_usd': 10}},
    })


@pytest.mark.parametrize('state', ['current', 'changed', 'unreadable'])
@respx.mock
async def test_continuing_eligibility_quote_is_checked_at_http_boundary(state):
    row = entry()
    respx.get(row.probe.endpoint).respond(200, json={'data': [
        {'id': 'science-flash', 'pricing': {'input': 0, 'output': 0}}]})
    respx.get(SOURCE).respond(503 if state == 'unreadable' else 200,
                             text=QUOTE if state == 'current' else 'The benefit has ended.')
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, row, attempts=1, backoff=0)
    assert result.status is (ProbeStatus.PASS if state == 'current' else ProbeStatus.STALE_IDS)
    if state != 'current':
        assert 'remaining free offer' in result.detail


def test_last_model_expiry_preserves_the_other_mode_payment_and_sources(tmp_path):
    row = entry()
    ended = expire_entries([row], datetime(2026, 11, 24, 8, tzinfo=timezone.utc))[0]
    path = tmp_path / 'registry.yaml'
    save_registry(path, [ended])
    current = load_registry(path)[0]
    assert current.models == [] and current.api.model_ids == []
    assert current.api.ignored_ids == ['science-flash']
    assert current.retired_on is None and current.free_part.value == 'unnamed'
    assert requires_payment(current) and current.access.initial_payment_usd == 10
    assert current.probe.endpoint == SOURCE and current.probe.keywords == [QUOTE]
    assert current.probe.catalog == row.probe.endpoint
    assert QUOTE in current.limits and current.offering != row.offering
    assert 'check the continuing offer' in current.api.note
    assert current.first_seen == row.first_seen and current.last_verified == row.last_verified
    assert row_quote_source(current, 'remaining_free.quote') == SOURCE
    assert ('remaining_free.quote', QUOTE) in row_quotes(current)
    assert SOURCE in row_urls(current)
    assert expire_entries([current], datetime(2026, 11, 25, tzinfo=timezone.utc))[0] == current


def test_continuing_mode_drops_unrecheckable_undated_catalog_exclusions(tmp_path):
    from freetier_radar.models import ModelBinding, ModelLimits
    from freetier_radar.quotas import UsageQuota
    row = entry()
    row.api.ignored_ids = ['decision-only']
    row.api.model_bindings['decision-only'] = ModelBinding(
        family='decision-only', source=SOURCE, quote='A specialist decision model')
    row.api.model_limits['decision-only'] = ModelLimits(
        context_tokens=4096, output_tokens=1024, source=row.probe.endpoint)
    row.api.opencode_output_tokens['decision-only'] = 512
    row.quotas = [UsageQuota(unit='requests', scope='account-model', model_ids=['decision-only'],
                            source=SOURCE, quote='A separate specialist allowance', reviewed_on=date(2026, 10, 28))]
    row = Entry.model_validate(row.model_dump(mode='json', exclude_none=True))
    ended = expire_entries([row], datetime(2026, 11, 24, 8, tzinfo=timezone.utc))[0]
    path = tmp_path / 'registry.yaml'
    save_registry(path, [ended])
    current = load_registry(path)[0]
    assert current.api.ignored_ids == ['science-flash']
    assert 'science-flash' in current.api.model_access
    assert not current.api.model_bindings and not current.api.model_limits
    assert not current.api.opencode_output_tokens
    assert not current.quotas
    assert row.api.ignored_ids == ['decision-only']
