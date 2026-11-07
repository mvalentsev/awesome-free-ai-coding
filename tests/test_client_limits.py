import html
import json
from datetime import date

import httpx
import pytest
import respx
from pydantic import ValidationError

from freetier_radar.client_limits import opencode_limits
from freetier_radar.models import Entry, load_registry, save_registry
from freetier_radar.prober import ProbeStatus, for_a_human, probe_entry


def config(context=131072, output=4096, provider='vendor', model='alpha'):
    return {'provider': {provider: {'models': {model: {
        'name': 'Alpha', 'limit': {'context': context, 'output': output}}}}}}


def code(value):
    # Syntax highlighting must not split a JSON token or introduce whitespace.
    return '<pre><code><span>' + html.escape(json.dumps(value)) + '</span></code></pre>'


def entry():
    return Entry.model_validate(dict(
        id='x', name='X', category='trial', url='https://x.ai', offering='A starting credit',
        first_seen=date(2026, 1, 1), last_verified=date(2026, 1, 1),
        free_part='sum', models=[],
        api=dict(base_url='https://api.x.ai/v1', model_ids=['alpha'], no_family_ids=['alpha'],
                 model_limits={'alpha': dict(context_tokens=131072, output_tokens=4096,
                     source='https://x.ai/client-guide', read='opencode-config', source_provider='vendor')}),
        probe=dict(type='page-keywords', endpoint='https://x.ai/pricing', keywords=['A free starting credit']),
    ))


@pytest.mark.parametrize('body', [
    code(config()), json.dumps(config()), '```json\n' + json.dumps(config()) + '\n```',
    code(config()) + code(config()),
])
def test_structured_client_limits_bind_exact_provider_and_model(body):
    assert opencode_limits(body, 'vendor', 'alpha') == (
        {'context_tokens': 131072, 'output_tokens': 4096}, '')
    assert opencode_limits(body, 'another', 'alpha')[0] is None
    assert opencode_limits(body, 'vendor', 'another')[0] is None


@pytest.mark.parametrize('body, reason', [
    (code(config(65536)) + code(config()), 'ambiguous'),
    (code(config(output=True)), 'invalid'),
    (code(config(output='4096')), 'invalid'),
    (code(config(output=0)), 'invalid'),
    (code(config(context=2048)), 'invalid'),
    ('<script type="application/json">' + json.dumps(config()) + '</script>', 'unavailable'),
    ('<p>alpha context 131072 output 4096</p>', 'unavailable'),
    ('{"provider":{"vendor":{"models":{"alpha":{"limit":{"context":131072,"output":8192,"output":4096}}}}}}', 'invalid'),
    (code(config()) + '<pre>' + '{"provider":{"vendor":{"models":{"alpha":{"limit":{"context":131072,"output":8192,"output":4096}}}}}}' + '</pre>', 'invalid'),
])
def test_malformed_ambiguous_or_unbound_examples_do_not_authorize_limits(body, reason):
    values, detail = opencode_limits(body, 'vendor', 'alpha')
    assert values is None and reason in detail


def test_page_limits_require_explicit_reader_and_round_trip(tmp_path):
    row = entry()
    path = tmp_path / 'registry.yaml'
    save_registry(path, [row])
    assert load_registry(path)[0].api.model_limits == row.api.model_limits
    data = row.model_dump()
    for update in [{'source_provider': None}, {'source_provider': ' '},
                   {'read': 'catalog'}, {'read': 'unknown'}]:
        data['api']['model_limits']['alpha'] = row.api.model_limits['alpha'].model_dump() | update
        with pytest.raises(ValidationError):
            Entry.model_validate(data)


def test_changed_client_limits_remain_a_human_review_finding():
    detail = 'api.model_limits alpha: output_tokens=2048 (recorded 4096)'
    assert for_a_human('unrelated family | ' + detail) == detail


@pytest.mark.parametrize('body, status, detail', [
    (code(config()), 200, ''),
    (code(config(output=2048)), 200, 'output_tokens=2048 (recorded 4096)'),
    (code(config(context=65536)), 200, 'context_tokens=65536 (recorded 131072)'),
    (code(config(provider='other')), 200, 'documented limits unavailable'),
    (code(config(model='other')), 200, 'documented limits unavailable'),
    (code(config()) + code(config(output=8192)), 200, 'documented limits ambiguous'),
    ('Unavailable', 503, 'source could not be checked'),
])
@respx.mock
async def test_probe_rechecks_page_limits_at_http_boundary(body, status, detail):
    row = entry()
    respx.get(row.probe.endpoint).respond(200, text='<h1>A free starting credit</h1>')
    source = respx.get('https://x.ai/client-guide').respond(status, text=body)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, row, attempts=1, backoff=0)
    assert result.status is (ProbeStatus.STALE_IDS if detail else ProbeStatus.PASS), result.detail
    assert source.call_count == 1
    if detail:
        assert 'api.model_limits alpha: ' + detail in result.detail


@respx.mock
async def test_models_share_one_parsed_source_without_sharing_their_limits(monkeypatch):
    import freetier_radar.client_limits as limits
    row = entry()
    row.api.model_ids.append('beta')
    row.api.no_family_ids.append('beta')
    row.api.model_limits['beta'] = row.api.model_limits['alpha'].model_copy()
    source_config = config()
    source_config['provider']['vendor']['models']['beta'] = {
        'limit': {'context': 131072, 'output': 2048}}
    respx.get(row.probe.endpoint).respond(200, text='A free starting credit')
    source = respx.get('https://x.ai/client-guide').respond(200, text=code(source_config))
    parsed = []
    original_feed = limits._CodeBlocks.feed

    def record_feed(parser, body):
        parsed.append(body)
        return original_feed(parser, body)

    monkeypatch.setattr(limits._CodeBlocks, 'feed', record_feed)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, row, attempts=1, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert 'api.model_limits beta: output_tokens=2048 (recorded 4096)' in result.detail
    assert 'api.model_limits alpha:' not in result.detail
    assert source.call_count == 1
    assert len(parsed) == 1
