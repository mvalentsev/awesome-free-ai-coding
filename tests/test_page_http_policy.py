"""Page evidence policy exercised through synchronous and asynchronous HTTP reads."""
from datetime import date

import httpx
import pytest

from freetier_radar.discovery import Evidence, fetch_page_texts, format_evidence
from freetier_radar.models import Entry
from freetier_radar.prober import (
    ProbeStatus, _fetch_page, probe_entry, probe_page_url, probe_page_url_sync,
)
from freetier_radar.quotes import check_entries
from freetier_radar.scout import named_by_row, probe_check_sync

URL = "https://vendor.example/pricing"
QUOTE = "Our free tier stays available"


def entry() -> Entry:
    return Entry.model_validate({
        "id": "vendor", "name": "Vendor", "category": "api-free-tier",
        "url": URL, "source_urls": [URL], "offering": "A free tier",
        "limits": f'The page says "{QUOTE}".',
        "first_seen": date.today(), "last_verified": date.today(),
        "probe": {"type": "page-keywords", "endpoint": URL, "keywords": [QUOTE]},
    })


@pytest.mark.parametrize("status", [200, 202, 302, 304, 401, 403, 404, 410, 429, 503])
async def test_all_page_readers_agree_on_which_bodies_can_supply_evidence(status):
    calls = []

    def answer(request):
        calls.append(request)
        return httpx.Response(status, text=QUOTE)

    transport = httpx.MockTransport(answer)
    unread = []
    accepted = status in (200, 202)
    with httpx.Client(transport=transport) as client:
        pages = fetch_page_texts([URL], client, on_unread=unread.append)
        assert pages == {URL: QUOTE if accepted else ""}
        assert unread == ([] if accepted else [f"{URL}: HTTP {status}"])
        assert probe_check_sync(entry(), client) == (None if accepted else f"HTTP {status}")
        assert named_by_row(client)(entry(), "absent-model") is (False if accepted else None)

    async with httpx.AsyncClient(transport=transport) as client:
        missing, unread = await check_entries([entry()], client)
        assert unread == ({} if accepted else {"vendor": [f"{URL}: HTTP {status}"]})
        assert [(m.quote, m.unverified) for m in missing] == ([] if accepted else [(QUOTE, True)])
        result = await probe_entry(client, entry(), attempts=2, backoff=0)
        expected = (ProbeStatus.PASS if accepted else ProbeStatus.FAIL if status in (404, 410)
                    else ProbeStatus.INCONCLUSIVE)
        assert result.status is expected
        if not accepted:
            assert f"HTTP {status}" in result.detail
        response, failure = await _fetch_page(client, URL, attempts=2, backoff=0)
        assert (response is not None) is accepted
        assert bool(failure) is not accepted
    # Only the two probe reads retry 5xx; quote and scout reads remain single-shot.
    assert len(calls) == (8 if status == 503 else 6)


@pytest.mark.parametrize("final_status", [200, 403])
async def test_redirect_evidence_comes_from_the_final_response(final_status):
    final_url = "https://vendor.example/current"

    def answer(request):
        if str(request.url) == URL:
            return httpx.Response(302, headers={"Location": final_url}, text="untrusted redirect body")
        return httpx.Response(final_status, text=QUOTE)

    transport = httpx.MockTransport(answer)
    unread = []
    with httpx.Client(transport=transport) as client:
        pages = fetch_page_texts([URL], client, on_unread=unread.append)
    assert pages == {URL: QUOTE if final_status == 200 else ""}
    assert unread == ([] if final_status == 200 else [f"{URL}: HTTP 403"])
    async with httpx.AsyncClient(transport=transport) as client:
        missing, unread = await check_entries([entry()], client)
        result = await probe_entry(client, entry(), backoff=0)
    assert len(missing) == (0 if final_status == 200 else 1)
    assert bool(unread) is (final_status != 200)
    assert result.status is (ProbeStatus.PASS if final_status == 200 else ProbeStatus.INCONCLUSIVE)


@pytest.mark.parametrize("status", [200, 302, 403, 503])
async def test_an_unread_index_cannot_choose_the_evidence_url(status):
    data = entry().model_dump()
    data["probe"]["follow"] = {"field": "docs"}
    e = Entry.model_validate(data)
    selected = "https://vendor.example/current"
    transport = httpx.MockTransport(lambda request: httpx.Response(status, json={"docs": selected}))
    with httpx.Client(transport=transport) as client:
        assert probe_page_url_sync(client, e.probe) == (selected if status == 200 else URL)
    async with httpx.AsyncClient(transport=transport) as client:
        assert await probe_page_url(client, e.probe) == (selected if status == 200 else URL)


async def test_network_failure_keeps_diagnostics_without_inventing_page_evidence():
    def answer(request):
        raise httpx.ReadTimeout("private transport detail", request=request)

    transport = httpx.MockTransport(answer)
    unread = []
    with httpx.Client(transport=transport) as client:
        pages = fetch_page_texts([URL], client, on_unread=unread.append)
    assert pages == {URL: ""} and unread == [f"{URL}: ReadTimeout"]
    ev = Evidence(pages=pages, page_warnings=unread)
    assert URL not in format_evidence(ev)
    assert "private transport detail" not in format_evidence(ev)
    async with httpx.AsyncClient(transport=transport) as client:
        missing, unread = await check_entries([entry()], client)
        result = await probe_entry(client, entry(), attempts=2, backoff=0)
    assert len(missing) == 1 and missing[0].unverified
    assert unread == {"vendor": [f"{URL}: ReadTimeout"]}
    assert result.status is ProbeStatus.INCONCLUSIVE


async def test_a_redirect_loop_is_unread_instead_of_page_evidence():
    transport = httpx.MockTransport(lambda request: httpx.Response(
        302, headers={"Location": URL}, text=QUOTE))
    unread = []
    with httpx.Client(transport=transport, max_redirects=2) as client:
        assert fetch_page_texts([URL], client, on_unread=unread.append) == {URL: ""}
    assert unread == [f"{URL}: TooManyRedirects"]
    async with httpx.AsyncClient(transport=transport, max_redirects=2) as client:
        missing, unread = await check_entries([entry()], client)
        result = await probe_entry(client, entry(), attempts=2, backoff=0)
    assert len(missing) == 1 and missing[0].unverified
    assert unread == {"vendor": [f"{URL}: TooManyRedirects"]}
    assert result.status is ProbeStatus.INCONCLUSIVE
