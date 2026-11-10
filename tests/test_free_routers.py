from datetime import date, datetime, timezone

import httpx
import pytest
import respx
from pydantic import ValidationError

from freetier_radar.models import Entry, Tier, expire_entries
from freetier_radar.prober import ProbeStatus, probe_entry
from freetier_radar.render import build_index, build_litellm_config, build_model_page, build_provider_page

DAY = date(2026, 11, 10)
CATALOG = 'https://vendor.example/v1/models'
UPSTREAM = 'https://upstream.example/v1/models'
QUOTE = 'This router chooses from the available free models on Upstream.'


def entry():
    return Entry.model_validate({
        'id': 'vendor', 'name': 'Vendor', 'category': 'api-free-tier', 'url': 'https://vendor.example',
        'offering': 'Named and automatically selected free models', 'free_part': 'models',
        'first_seen': DAY, 'last_verified': DAY,
        'models': [{'family': 'science-flash', 'router': {'id': 'free-router', 'model_id': 'lab/science-flash:free'}},
                   {'family': 'steady'}],
        'api': {'base_url': 'https://vendor.example/v1', 'model_ids': ['free-router', 'steady'],
                'free_routers': {'free-router': {'source': UPSTREAM, 'quote': QUOTE}},
                'no_family_ids': ['free-router']},
        'probe': {'type': 'api-models', 'endpoint': CATALOG, 'require_zero_price': True},
    })


@respx.mock
async def test_priced_local_twin_can_coexist_with_a_verified_free_router_member():
    respx.get(CATALOG).respond(200, json={'data': [
        {'id': 'lab/science-flash', 'pricing': {'input': 1, 'output': 2}},
        {'id': 'free-router', 'description': QUOTE, 'pricing': {'input': 0, 'output': 0}},
        {'id': 'steady', 'pricing': {'input': 0, 'output': 0}},
    ]})
    member = respx.get(UPSTREAM).respond(200, json={'data': [
        {'id': 'lab/science-flash:free', 'pricing': {'input': 0, 'output': 0}},
    ]})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0, today=DAY)
    assert result.status is ProbeStatus.PASS
    assert member.call_count == 1


@pytest.mark.parametrize('member', [None,
    {'id': 'lab/science-flash:free', 'pricing': {'input': 1, 'output': 0}},
    {'id': 'lab/science-flash:free', 'pricing': {'input': 0, 'output': 0}, 'available': False},
])
@respx.mock
async def test_router_membership_cannot_survive_missing_paid_or_unavailable_upstream(member):
    respx.get(CATALOG).respond(200, json={'data': [
        {'id': 'free-router', 'description': QUOTE, 'pricing': {'input': 0, 'output': 0}},
        {'id': 'steady', 'pricing': {'input': 0, 'output': 0}},
    ]})
    respx.get(UPSTREAM).respond(200, json={'data': [member] if member else []})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0, today=DAY)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'routed model science-flash' in result.detail


@pytest.mark.parametrize('router', [None,
    {'id': 'free-router', 'description': QUOTE, 'pricing': {'input': 1, 'output': 0}},
    {'id': 'free-router', 'description': 'A paid routing service.', 'pricing': {'input': 0, 'output': 0}},
])
@respx.mock
async def test_an_upstream_free_model_cannot_establish_the_owning_router_offer(router):
    respx.get(CATALOG).respond(200, json={'data': [
        {'id': 'steady', 'pricing': {'input': 0, 'output': 0}},
        *([router] if router else []),
    ]})
    if router and router['description'] != QUOTE:
        respx.get(UPSTREAM).respond(200, json={'data': [
            {'id': 'lab/science-flash:free', 'pricing': {'input': 0, 'output': 0}},
        ]})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry(), attempts=1, backoff=0, today=DAY)
    assert result.status is ProbeStatus.STALE_MODELS
    assert 'free router or forwarding quote unavailable' in result.detail


def test_router_access_uses_shared_labels_and_connections_without_a_fixed_family_alias():
    row = entry()
    provider = build_provider_page(row, [], DAY)
    model = build_model_page('science-flash', [row], [], DAY)
    assert 'via free-router; the router chooses the model' in provider
    assert '`free-router`' in model and 'the router chooses the model' in model
    assert 'the row lists none for this model' not in model
    labels = build_index([row], DAY)['entries'][0]['access_labels']['models']
    assert 'the router chooses the model' in labels['science-flash']
    assert labels['steady'] == ''
    data = row.model_dump(mode='json')
    router_id = 'lab/science-flash/free-router'
    data['api']['model_ids'][0] = router_id
    data['api']['free_routers'][router_id] = data['api']['free_routers'].pop('free-router')
    data['api']['no_family_ids'] = []
    data['models'][0]['router']['id'] = router_id
    data['models'][0]['tier'] = Tier.STRONG.value
    measured_member = Entry.model_validate(data)
    config = build_litellm_config([measured_member], DAY)
    assert 'free/strong' not in {item['model_name'] for item in config['model_list']}
    from freetier_radar.conformance import routed_pool_violations
    assert routed_pool_violations([measured_member], config) == []
    wrong = {'model_list': [{'model_name': 'free/strong', 'litellm_params': {
        'api_base': measured_member.api.base_url + '/', 'model': 'openai/' + router_id}}]}
    assert routed_pool_violations([measured_member], wrong)


def test_router_deadline_expires_dependent_family_and_keeps_the_other_free_model():
    data = entry().model_dump(mode='json')
    data['api']['model_access'] = {'free-router': {'source': 'https://vendor.example/offer',
                                                  'until': '2026-11-11T00:00:00Z'}}
    row = Entry.model_validate(data)
    ended = expire_entries([row], datetime(2026, 11, 11, tzinfo=timezone.utc))[0]
    assert [model.family for model in ended.models] == ['steady']
    assert ended.api.model_ids == ['steady']
    assert ended.api.model_access['free-router'].until is not None
    Entry.model_validate(ended.model_dump())


def test_router_references_require_a_declared_route_and_exact_family_member():
    data = entry().model_dump(mode='json')
    data['models'][0]['router']['id'] = 'undeclared'
    with pytest.raises(ValidationError):
        Entry.model_validate(data)
    data['models'][0]['router'] = {'id': 'free-router', 'model_id': 'lab/another-family:free'}
    with pytest.raises(ValidationError):
        Entry.model_validate(data)
