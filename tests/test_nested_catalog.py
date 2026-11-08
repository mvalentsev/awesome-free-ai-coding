from datetime import date

import httpx
import pytest

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry


def entry(lane=None):
    return Entry.model_validate({
        'id': 'fixture', 'name': 'Fixture', 'url': 'https://vendor.example',
        'category': 'aggregator', 'offering': 'A free model gateway', 'free_part': 'models',
        'models': [{'family': 'fixture'}],
        'api': {'base_url': 'https://vendor.example/v1', 'auth': 'api-key', 'model_ids': ['fixture-free']},
        'probe': {'type': 'api-models', 'endpoint': 'https://vendor.example/v1/models',
                  'require_zero_price': True, **({'lane': lane} if lane else {})},
        'first_seen': date(2026, 11, 8), 'last_verified': date(2026, 11, 8),
    })


@pytest.mark.asyncio
async def test_nested_openai_catalog_is_read_at_the_http_boundary():
    body = {'data': {'object': 'list', 'data': [
        {'id': 'fixture-free', 'pricing': {'prompt': '0', 'completion': '0'}}]}}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))) as client:
        result = await probe_entry(client, entry(), attempts=1, today=date(2026, 11, 8))
    assert result.status is ProbeStatus.PASS


@pytest.mark.asyncio
async def test_explicit_empty_lane_does_not_fall_back_to_a_nested_catalog():
    body = {'free': [], 'data': {'data': [
        {'id': 'fixture-free', 'pricing': {'prompt': '0', 'completion': '0'}}]}}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))) as client:
        result = await probe_entry(client, entry('free'), attempts=1, today=date(2026, 11, 8))
    assert result.status is ProbeStatus.FAIL


@pytest.mark.asyncio
@pytest.mark.parametrize('fields, expected', [
    ({'pricing': {'request': '0.000000'}}, ProbeStatus.PASS),
    ({'pricing': {'request': '0.001'}}, ProbeStatus.FAIL),
    ({'pricing': {'request': 'unknown'}}, ProbeStatus.FAIL),
    ({'pricing': {'request': '0'}, 'min_request_price': 0.01}, ProbeStatus.FAIL),
    ({'pricing': {'request': '0'}, 'model_ratio': 2}, ProbeStatus.FAIL),
    ({'pricing': {'request': '0', 'prompt': '0', 'completion': '1'}}, ProbeStatus.FAIL),
])
async def test_complete_request_prices_are_checked_at_the_http_boundary(fields, expected):
    # The complete request price is the Free catalog's billing format:
    # https://docs.orcarouter.ai/routing/free-models.md, checked 2026-11-08.
    body = {'data': [{'id': 'fixture-free', **fields}]}
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))) as client:
        result = await probe_entry(client, entry(), attempts=1, today=date(2026, 11, 8))
    assert result.status is expected


@pytest.mark.asyncio
@pytest.mark.parametrize('endpoints, expected_gap', [
    (['openai'], False),
    (['OpenAI'], False),
    (['openai', '/v1/responses'], True),
    (['/v1/responses'], True),
    (['/v1/chat/completions'], False),
])
async def test_protocol_labels_do_not_withdraw_a_documented_chat_id(endpoints, expected_gap):
    # BeatAPI labels the protocol, not an operation, in its text catalog:
    # https://api.beatapi.io/v1/text/models, checked 2026-11-08.
    body = {'data': [{'id': 'fixture-free', 'endpoints': endpoints,
                     'pricing': {'prompt': '0', 'completion': '0'}}]}
    configured = entry()
    configured.api.openai_compatible = True
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))) as client:
        result = await probe_entry(client, configured, attempts=1, today=date(2026, 11, 8))
    assert result.status is (ProbeStatus.STALE_IDS if expected_gap else ProbeStatus.PASS)


@pytest.mark.asyncio
@pytest.mark.parametrize('published_maximum, expected', [(2000, ProbeStatus.PASS), (1000, ProbeStatus.STALE_IDS)])
async def test_documented_request_budgets_are_rechecked_at_the_http_boundary(published_maximum, expected):
    from types import SimpleNamespace

    configured = entry()
    configured.api = configured.api.model_copy(update={
        'opencode_output_tokens': {'fixture-free': 2000},
        'opencode_output_sources': {'fixture-free': SimpleNamespace(
            source='https://vendor.example/parameters', quote='max_tokens integer Optional 50-2000')},
    })
    catalog = {'data': [{'id': 'fixture-free', 'pricing': {'prompt': '0', 'completion': '0'},
                         'supported_parameters': ['max_tokens', 'max_completion_tokens'],
                         'max_output_tokens': 2000}]}
    def answer(request):
        return (httpx.Response(200, json=catalog) if request.url.path.endswith('/models') else
                httpx.Response(200, text=f'<p>max_tokens integer Optional 50-{published_maximum}</p>'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(answer)) as client:
        result = await probe_entry(client, configured, attempts=1, today=date(2026, 11, 8))
    assert result.status is expected


@pytest.mark.parametrize('overrides', [
    {'source': 'http://vendor.example/parameters'},
    {'source': 'https://user:password@vendor.example/parameters'},
    {'quote': 'max_tokens integer Optional 50-1000'},
    {'quote': 'context window 2000'},
])
def test_documented_request_budget_requires_an_https_parameter_source(overrides):
    from pydantic import ValidationError
    from freetier_radar.models import ApiInfo

    source = {'source': 'https://vendor.example/parameters',
              'quote': 'max_tokens integer Optional 50-2000', **overrides}
    with pytest.raises(ValidationError):
        ApiInfo(base_url='https://vendor.example/v1', model_ids=['fixture-free'],
                opencode_output_tokens={'fixture-free': 2000},
                opencode_output_sources={'fixture-free': source})
