"""A client-only promotion needs current per-model offer evidence and real expiry."""
from datetime import date, datetime, timezone

import httpx
import pytest
import respx
from pydantic import ValidationError

from freetier_radar.models import Entry, expire_entries, family_access, load_registry, save_registry
from freetier_radar.prober import ProbeStatus, probe_entry

SOURCE = 'https://vendor.example/promotion'
IDENTITY = 'Choose Science Flash in the model selector.'
OFFER = 'Free accounts can use Science Flash with a zero credit balance.'


def data():
    return {
        'id': 'client', 'name': 'Client', 'category': 'agent-cli',
        'url': 'https://vendor.example', 'offering': 'Free basic models and a model promotion',
        'free_part': 'models', 'models': [{'family': 'science-flash'}],
        'first_seen': '2026-10-01', 'last_verified': '2026-10-01',
        'remaining_free': {'source': 'https://vendor.example/pricing',
                           'quote': 'Free basic models for limited messages', 'free_part': 'unnamed'},
        'probe': {'type': 'page-keywords', 'endpoint': 'https://vendor.example/pricing',
                  'keywords': ['Free basic models for limited messages']},
        'client_lane': {
            'model_ids': ['Flash'],
            'model_bindings': {'Flash': {'family': 'science-flash', 'source': SOURCE, 'quote': IDENTITY}},
            'model_access': {'Flash': {'source': SOURCE, 'until': '2026-11-01T00:00:00+08:00'}},
        },
        'quotas': [{'unit': 'requests', 'scope': 'account-model', 'model_ids': ['Flash'],
                    'source': SOURCE, 'quote': OFFER, 'reviewed_on': '2026-10-28'}],
    }


@pytest.mark.parametrize('change', ['none', 'identity', 'offer', 'unreadable'])
@respx.mock
async def test_page_lane_checks_each_identity_and_allowance_at_http_boundary(change):
    row = Entry.model_validate(data())
    respx.get(row.probe.endpoint).respond(200, text='Free basic models for limited messages')
    body = IDENTITY + ' ' + OFFER
    if change == 'identity':
        body = body.replace(IDENTITY, 'Choose a different model.')
    if change == 'offer':
        body = body.replace(OFFER, 'A paid subscription is required.')
    respx.get(SOURCE).respond(503 if change == 'unreadable' else 200, text=body)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, row, attempts=1, backoff=0, today=date(2026, 10, 28))
    assert result.status is (ProbeStatus.PASS if change == 'none' else ProbeStatus.STALE_IDS)
    if change != 'none':
        assert 'model binding' in result.detail or 'quota' in result.detail


@pytest.mark.parametrize('missing', ['model_bindings', 'quotas', 'source', 'shared'])
def test_page_lane_cannot_borrow_a_general_wallet_or_unbound_identity(missing):
    value = data()
    if missing == 'model_bindings':
        value['client_lane']['model_bindings'] = {}
    elif missing == 'quotas':
        value['quotas'][0]['model_ids'] = []
    elif missing == 'source':
        value['quotas'][0]['source'] = 'https://vendor.example/general-wallet'
    else:
        value['quotas'][0]['scope'] = 'account'
    with pytest.raises(ValidationError, match='per-model identity and allowance'):
        Entry.model_validate(value)


def test_page_lane_deadline_uses_shared_expiry_and_retains_its_evidence(tmp_path):
    row = Entry.model_validate(data())
    before = datetime(2026, 10, 31, 15, 59, 59, tzinfo=timezone.utc)
    assert expire_entries([row], before)[0].client_lane.model_ids == ['Flash']
    assert family_access(row, 'science-flash').until.isoformat() == '2026-11-01T00:00:00+08:00'
    ended = expire_entries([row], datetime(2026, 10, 31, 16, tzinfo=timezone.utc))[0]
    path = tmp_path / 'registry.yaml'
    save_registry(path, [ended])
    restored = load_registry(path)[0]
    assert restored.client_lane.model_ids == []
    assert restored.client_lane.ignored_ids == ['Flash']
    assert restored.models == []
    assert restored.retired_on is None
    assert restored.free_part.value == 'unnamed'
    assert restored.client_lane.model_access['Flash'].until == family_access(row, 'science-flash').until
    assert restored.first_seen == row.first_seen and restored.last_verified == row.last_verified


def test_ending_a_model_only_offer_still_archives_the_provider():
    value = data()
    value.pop('remaining_free')
    ended = expire_entries([Entry.model_validate(value)], datetime(2026, 10, 31, 16, tzinfo=timezone.utc))[0]
    assert ended.retired_on == date(2026, 10, 31)
