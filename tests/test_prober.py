from datetime import date

import httpx
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeResult, ProbeStatus, apply_results, probe_entry

BASE = {
    "id": "x",
    "name": "X",
    "category": "api-free-tier",
    "url": "https://x.ai",
    "offering": "stuff",
    "first_seen": date(2026, 1, 1),
    "last_verified": date(2026, 1, 1),
}


def api_entry() -> Entry:
    return Entry.model_validate({
        **BASE,
        "models": [{"family": "qwen3-coder", "tier": "strong"}],
        "probe": {
            "type": "api-models",
            "endpoint": "https://api.x.ai/v1/models",
            "free_marker": ":free",
        },
    })


def page_entry() -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "pagey",
        "probe": {
            "type": "page-keywords",
            "endpoint": "https://x.ai/pricing",
            "keywords": ["free tier", "no credit card"],
        },
    })


@respx.mock
async def test_api_models_ok():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}, {"id": "other/paid"}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_api_models_missing_family_is_fail():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}]}  # listed, but without the :free marker
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "qwen3-coder" in result.detail


@respx.mock
async def test_page_keywords_missing_is_fail():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="Free tier for everyone"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "no credit card" in result.detail


@respx.mock
async def test_blocked_is_inconclusive_without_retry():
    route = respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(403))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE and "403" in result.detail
    assert route.call_count == 1


@respx.mock
async def test_page_gone_is_fail():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "404" in result.detail


@respx.mock
async def test_transient_5xx_retries_then_passes():
    route = respx.get("https://x.ai/pricing")
    route.side_effect = [
        httpx.Response(503),
        httpx.Response(200, text="free tier, no credit card"),
    ]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert route.call_count == 2


@respx.mock
async def test_unreachable_after_retries_is_inconclusive():
    route = respx.get("https://x.ai/pricing")
    route.side_effect = httpx.ConnectError("boom")
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), attempts=2, backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE and "unreachable" in result.detail
    assert route.call_count == 2


def test_apply_results():
    ok, failing, blocked = api_entry(), page_entry(), page_entry()
    blocked.id = "blocked"
    entries = [ok, failing, blocked]
    today = date(2026, 7, 19)
    flagged = apply_results(entries, {
        "x": ProbeResult(ProbeStatus.PASS),
        "pagey": ProbeResult(ProbeStatus.FAIL, "missing keywords"),
        "blocked": ProbeResult(ProbeStatus.INCONCLUSIVE, "blocked: HTTP 403"),
    }, today)
    assert ok.last_verified == today and ok.probe_failures == 0
    assert failing.probe_failures == 1 and failing.last_verified == date(2026, 1, 1)
    assert blocked.probe_failures == 0 and blocked.last_verified == date(2026, 1, 1)
    assert [e.id for e in flagged] == ["pagey", "blocked"]
