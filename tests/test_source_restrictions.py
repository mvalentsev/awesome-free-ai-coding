"""A restricted source cannot establish that the vendor ended its offer."""
from datetime import date
import httpx
import respx
from freetier_radar.prober import probe_entry,ProbeStatus,apply_results
from test_page_recovery import entry,URL

@respx.mock
async def test_451_never_counts_toward_archive_or_verification():
    respx.get(URL).respond(451,text='This content has been blocked for legal reasons\nDEPLOYMENT_DISABLED')
    row=entry();before=(row.last_verified,row.probe_failures,row.provisional)
    async with httpx.AsyncClient() as client:
        for _ in range(3):
            result=await probe_entry(client,row,backoff=0)
            assert result.status is ProbeStatus.INCONCLUSIVE
            apply_results([row],{row.id:result},date(2026,10,12))
    assert (row.last_verified,row.probe_failures,row.provisional)==before

@respx.mock
async def test_404_is_still_an_established_gone_page():
    respx.get(URL).respond(404,text='Gone')
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client,entry(),backoff=0)).status is ProbeStatus.FAIL
