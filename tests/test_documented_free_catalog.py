"""FreeInference's documented per-key catalog scope, checked 2026-10-27.

Source: https://doc.freeinference.org/models. The explicit Free table provides
the public entitlement; authenticated catalogs determine each key's access.
"""
from pathlib import Path

import httpx
import pytest

from freetier_radar.models import load_registry
from freetier_radar.prober import ProbeStatus, probe_entry


@pytest.mark.parametrize('minimax_access,expected', [('Free',ProbeStatus.PASS),('Pro',ProbeStatus.STALE_MODELS)])
async def test_documented_free_table_controls_models_when_catalog_is_access_filtered(minimax_access, expected):
    entry=next(e for e in load_registry(Path('registry.yaml')) if e.id=='freeinference')
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
