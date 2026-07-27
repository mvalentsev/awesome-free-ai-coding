from datetime import date

import httpx
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import (
    ProbeResult, ProbeStatus, apply_results, is_model_stale, probe_entry,
)

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
            "keywords": ["qwen3-coder", "free tier", "no credit card"],
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
async def test_api_models_accepts_a_bare_list():
    """GitHub's catalog answers with a bare array instead of {"data": [...]}."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=[{"id": "vendor/qwen3-coder:free"}]
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
async def test_withdrawal_wording_fails_even_when_keywords_match():
    """mimo-code's case: the page still advertises the free channel and says,
    further down, that it is over."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card. "
                  "Update: the free API service has ended on 2026-07-26."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "offer withdrawn" in result.detail and "free api service has ended" in result.detail


@respx.mock
async def test_entry_specific_dead_marker():
    entry = page_entry()
    entry.probe.dead_markers = ["mimo auto is gone"]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card. MiMo Auto is gone."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL and "mimo auto is gone" in result.detail


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
        httpx.Response(200, text="qwen3-coder on the free tier, no credit card"),
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
    assert [e.id for e, _ in flagged] == ["pagey", "blocked"]
    assert [r.status for _, r in flagged] == [ProbeStatus.FAIL, ProbeStatus.INCONCLUSIVE]


def test_fully_superseded_entry_passes_but_needs_attention():
    """A supersede mark never archives — but it must not sit there either, or the
    README keeps rendering "—" where the free models belong."""
    e = api_entry()
    e.models[0].superseded_by = "qwen4-coder"
    assert is_model_stale(e)
    flagged = apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 7, 19))
    assert e.last_verified == date(2026, 7, 19) and e.probe_failures == 0  # still live
    assert [(x.id, r.status) for x, r in flagged] == [("x", ProbeStatus.STALE_MODELS)]


def test_partly_superseded_entry_is_left_alone():
    e = api_entry()
    e.models.append(e.models[0].model_copy(update={"family": "qwen4-coder"}))
    e.models[0].superseded_by = "qwen4-coder"
    assert not is_model_stale(e)
    assert apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 7, 19)) == []


def test_pass_promotes_provisional_after_settling():
    e = api_entry()  # first_seen 2026-01-01
    e.provisional = True
    apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 1, 10))
    assert e.provisional is True  # too young to promote
    apply_results([e], {"x": ProbeResult(ProbeStatus.FAIL, "gone")}, date(2026, 2, 1))
    assert e.provisional is True  # only PASS promotes
    apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 1, 15))
    assert e.provisional is False
