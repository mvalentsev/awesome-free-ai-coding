from datetime import date, datetime, timezone
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError

from freetier_radar.models import Entry, expire_entries, load_registry, save_registry
from freetier_radar.prober import ProbeStatus, probe_entry
from freetier_radar.render import build_index, build_model_page, build_provider_page, model_pages, render_repository

DAY = date(2026, 11, 9)
SOURCE = 'https://vendor.example/models'
QUOTE = 'Preview Medium is included in the Free plan. High and Max need a paid plan.'
DEADLINE = 'Preview Medium is free until December 4, 2026 at 18:00 UTC.'
REMAINING = 'The Free plan includes 50 tasks every month.'


def entry(*, steady=False, remaining=True):
    return Entry.model_validate({
        'id': 'tool', 'name': 'Tool', 'url': 'https://vendor.example', 'category': 'agent-cli',
        'offering': 'A coding agent with a Free plan', 'free_part': 'models',
        'models': [{'family': 'preview-medium'}, *([{'family': 'steady'}] if steady else [])],
        'model_access': {'preview-medium': {'source': SOURCE, 'quote': QUOTE,
                                          'deadline_quote': DEADLINE, 'until': '2026-12-04T18:00:00Z'}},
        'remaining_free': {'source': 'https://vendor.example/pricing', 'quote': REMAINING,
                           'free_part': 'unnamed'} if remaining else None,
        'limits': 'Shared account limits apply to the Free plan.',
        'probe': {'type': 'page-keywords', 'endpoint': SOURCE, 'keywords': [REMAINING]},
        'first_seen': DAY, 'last_verified': DAY,
    })


def test_prose_promotion_uses_the_shared_labels_and_its_own_model_page():
    row = entry(steady=True)
    page = build_provider_page(row, [], DAY)
    assert row.api is None and row.client_lane is None
    assert '2026-12-04' in page and '18:00' in page
    assert 'preview-medium' in model_pages([row], [], DAY)
    data = build_index([row], DAY)
    assert '2026-12-04' in data['entries'][0]['access_labels']['models']['preview-medium']
    assert not data['entries'][0]['access_labels']['models']['steady']


def test_prose_promotion_expires_at_the_writer_clock_and_preserves_the_free_plan(tmp_path):
    path = tmp_path / 'registry.yaml'
    save_registry(path, [entry()])
    before = datetime(2026, 12, 4, 17, 59, 59, tzinfo=timezone.utc)
    after = datetime(2026, 12, 4, 18, tzinfo=timezone.utc)
    render_repository(path, Path('templates'), tmp_path, today=before.date(), now=before)
    assert [m.family for m in load_registry(path)[0].models] == ['preview-medium']
    render_repository(path, Path('templates'), tmp_path, today=after.date(), now=after)
    row = load_registry(path)[0]
    assert row.models == [] and row.free_part.value == 'unnamed'
    assert row.expired_models == ['preview-medium']
    assert row.model_access['preview-medium'].until == after
    assert row.probe.endpoint == row.remaining_free.source
    assert row.retired_on is None
    assert row.api is None and row.client_lane is None
    assert (tmp_path / 'models/preview-medium.md').is_file()
    assert 'preview-medium' not in {m['family'] for m in build_index([row], after.date())['models']}


def test_one_ended_prose_promotion_preserves_another_free_family():
    row = expire_entries([entry(steady=True)], datetime(2026, 12, 4, 18, tzinfo=timezone.utc))[0]
    assert [m.family for m in row.models] == ['steady']
    assert row.free_part.value == 'models' and row.retired_on is None


def test_model_specific_deadline_does_not_leak_onto_an_unaffected_peer_page():
    row = entry(steady=True)
    peer = build_model_page('steady', [row], [], DAY)
    assert '2026-12-04' not in peer
    assert '18:00' not in peer
    assert 'Shared account limits apply to the Free plan.' in peer
    promoted = build_model_page('preview-medium', [row], [], DAY)
    assert '2026-12-04' in promoted and '18:00' in promoted


def test_pending_page_model_keeps_its_numeric_quota_canonical_before_promotion():
    data = entry(steady=True).model_dump(mode='json')
    data['newcomers'] = [{'family': 'next-model', 'on': DAY.isoformat(), 'source': SOURCE}]
    data['quotas'] = [{'amount': 100, 'unit': 'requests', 'period': 'day', 'scope': 'unspecified',
                       'source': SOURCE, 'quote': 'Next Model has 100 requests per day.',
                       'families': ['next-model'], 'label': 'Next Model', 'reviewed_on': DAY.isoformat()}]
    row = Entry.model_validate(data)
    assert 'next-model' not in {model.family for model in row.models}
    page = build_provider_page(row, [], DAY)
    assert page.count('100 requests/day') == 1
    assert '100 requests' not in page.split('## Free models', 1)[1].split('## Limits', 1)[0]
    assert build_index([row], DAY)['entries'][0]['quotas'][0]['families'] == ['next-model']
    data['quotas'][0]['families'] = ['unrecorded-model']
    with pytest.raises(ValidationError):
        Entry.model_validate(data)


@pytest.mark.parametrize('shared', [False, True])
def test_expired_family_quota_stays_out_of_current_limits_and_machine_data(shared):
    data = entry(steady=shared).model_dump(mode='json')
    data['quotas'] = [{'amount': 20, 'unit': 'requests', 'period': 'day', 'scope': 'account-model',
                       'source': SOURCE, 'quote': 'Preview Medium allows 20 requests per day.',
                       'families': ['preview-medium'], 'label': 'Preview Medium quota'}]
    if shared:
        data['quotas'].append({'amount': 50, 'unit': 'tasks', 'period': 'month', 'scope': 'account',
                               'source': 'https://vendor.example/pricing', 'quote': REMAINING})
    row = Entry.model_validate(data)
    if shared:
        assert '20 requests' not in build_model_page('steady', [row], [], DAY)
    now = datetime(2026, 12, 4, 18, tzinfo=timezone.utc)
    ended = expire_entries([row], now)[0]
    published = build_index([ended], now.date())['entries'][0]
    assert [q['amount'] for q in published['quotas']] == ([50] if shared else [])
    assert '20 requests' not in build_provider_page(ended, [], now.date())
    assert ended.quotas[0].amount == 20


@pytest.mark.parametrize('free,changed_deadline', [(True, False), (False, False), (True, True)])
async def test_prose_free_plan_and_deadline_quotes_are_rechecked_at_http_boundary(free, changed_deadline):
    row = entry()
    quote = QUOTE if free else 'Preview Medium needs a paid plan. High and Max need a paid plan.'
    deadline = DEADLINE.replace('December 4', 'November 30') if changed_deadline else DEADLINE
    body = REMAINING + ' ' + quote + ' ' + deadline
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_entry(client, row, attempts=1, backoff=0, today=DAY)
    assert result.status is (ProbeStatus.PASS if free and not changed_deadline else ProbeStatus.STALE_IDS)
    if not free or changed_deadline:
        assert 'model_access' in result.detail


def test_prose_access_cannot_duplicate_an_api_lane_or_name_an_unrecorded_family():
    data = entry().model_dump(mode='json')
    with pytest.raises(ValidationError):
        Entry.model_validate({**data, 'api': {'model_ids': ['preview-medium']}})
    with pytest.raises(ValidationError):
        Entry.model_validate({**data, 'models': []})
