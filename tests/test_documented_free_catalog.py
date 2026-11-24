"""Documented free access is checked at the HTTP boundary.

FreeInference: https://doc.freeinference.org/models, checked 2026-10-27. The explicit Free table provides
the public entitlement; authenticated catalogs determine each key's access.
"""
import httpx
import pytest

from freetier_radar.prober import ProbeStatus, probe_entry


@pytest.mark.parametrize('input_floor,expected', [(5000, ProbeStatus.PASS), (4000, ProbeStatus.STALE_IDS)])
async def test_cheapllm_current_beta_and_after_beta_floor_remain_distinct(registry_entry, input_floor, expected):
    # https://cheapllm.shop/docs and /terms, checked 2026-11-24.
    entry = registry_entry('cheapllm-shop')
    docs = '''Free during the beta. After it, every account keeps a <b>permanent free tier</b>,
    no card: <b>at least 5,000 input and 1,000 output tokens per hour</b>, per account over a rolling hour.
    GET /v1/models lists one model: deepseek-v4.1-flash-1017.'''
    terms = f'''During the beta it is free and has no rate limit.
    When the beta ends, every account keeps a free tier of at least {input_floor:,} input tokens and
    1,000 output tokens per hour, without a card; usage beyond it is billed at the prices shown on the site at that time.'''
    def respond(request):
        if request.url.path == '/docs':
            return httpx.Response(200, text=docs)
        if request.url.path == '/terms':
            return httpx.Response(200, text=terms)
        if request.url.path == '/v1/models':
            return httpx.Response(200, json={'data': [{'id': 'deepseek-v4.1-flash-1017'}]})
        return httpx.Response(401)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert result.status is expected, result.detail


@pytest.mark.parametrize('minimax_access,expected', [('Free',ProbeStatus.PASS),('Pro',ProbeStatus.STALE_MODELS)])
async def test_documented_free_table_controls_models_when_catalog_is_access_filtered(registry_entry, minimax_access, expected):
    entry=registry_entry('freeinference')
    entry=entry.model_copy(update={'quotas':[],'border':None,'data_use':None,
                                  'api':entry.api.model_copy(update={'anthropic_base_url':None,'codex':None})})
    items=[('glm-5.3-flash','Free'),('deepseek-v4-flash','Free'),('minimax-m3',minimax_access),('qwen3.6-35b','Free'),('glm-5.2','Pro'),('kimi-k2.7-code','Pro')]
    table='<table><tr>'+''.join('<th>'+h+'</th>' for h in ['Model ID','Access','Context','Max Output','Input','Highlights'])+'</tr>'
    table+=''.join('<tr><td>'+mid+'</td><td>'+access+'</td><td>1M</td><td>8K</td><td>Text</td><td>Tools</td></tr>' for mid,access in items)+'</table>'
    # Missing here means this public/access-filtered view lacks the ID. The
    # primary docs explicitly require the reader's authenticated catalog.
    calls=[]
    def respond(request):
        calls.append(str(request.url))
        if str(request.url)==entry.probe.endpoint:
            return httpx.Response(200,text='Free accounts can use models marked Free. '+table)
        assert str(request.url)=='https://freeinference.org/v1/models'
        return httpx.Response(200,json={'data':[{'id':mid} for mid,_ in items if mid!='minimax-m3']})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await probe_entry(client,entry,attempts=1,backoff=0)
    assert result.status is expected,result.detail
    assert calls==[entry.probe.endpoint]
