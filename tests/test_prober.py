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


def zero_price_entry() -> Entry:
    e = api_entry()
    e.probe.require_zero_price = True
    return e


@respx.mock
async def test_zero_priced_model_passes():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0", "completion": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_free_id_that_acquired_a_price_is_fail():
    """The hole this closes: an aggregator keeps the id — suffix and all — and
    starts charging for it. Substring matching alone would pass forever."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0.0000002", "completion": "0.0000008"}},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail and "2e-07/8e-07" in result.detail


@respx.mock
async def test_zero_price_accepts_vercel_style_input_output_rows():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "pricing": {"input": "0", "output": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_zero_price_reads_a_row_quoted_with_its_unit():
    """Routeway publishes the price inside the unit it is quoted in. Read as a
    bare number the row came back unparseable, and every free id on that gateway
    answered "publishes no price" — unverifiable, so unlistable."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "pricing": {
            "input": {"unit": "1M tokens", "price_per_million_t": 0},
            "output": {"unit": "1M tokens", "price_per_million_t": 0.0}}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_unit_quoted_row_that_acquired_a_price_is_fail():
    """Same shape, billing now. The unit wrapper must not become a place a price
    can hide."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "pricing": {
            "input": {"unit": "1M tokens", "price_per_million_t": 0.2},
            "output": {"unit": "1M tokens", "price_per_million_t": 0.8}}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail and "0.2/0.8" in result.detail


@respx.mock
async def test_a_unit_wrapper_without_a_number_is_not_a_zero():
    """An empty wrapper is silence, not a published zero."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "pricing": {
            "input": {"unit": "1M tokens"}, "output": {"unit": "1M tokens"}}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "publishes no price" in result.detail


@respx.mock
async def test_zero_price_reads_a_price_published_one_tier_per_row():
    """Requesty ships `pricing` as a list of usage tiers instead of one object.
    Read as a pricing object the list is not one, so every zero-priced id on that
    gateway answered "publishes no price" — unverifiable, so unlistable."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free",
                             "input_price": 0, "output_price": 0, "pricing": [
                                 {"prompt_tokens_threshold": 0,
                                  "input_price": 0, "cached_price": 0, "output_price": 0}]}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_tier_that_starts_billing_above_a_threshold_is_not_free():
    """Free up to a token threshold and metered above it is a discount, not a
    free model. The cheap first row must not stand in for the whole list."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "pricing": [
            {"prompt_tokens_threshold": 0, "input_price": 0, "output_price": 0},
            {"prompt_tokens_threshold": 200000, "input_price": 0.3, "output_price": 0.9}]}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail and "0.3/0.9" in result.detail


@respx.mock
async def test_an_empty_tier_list_is_not_a_zero():
    """A catalog that stopped publishing its tiers is silent, not free."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "pricing": []}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "publishes no price" in result.detail


@respx.mock
async def test_zero_price_ignores_cache_and_image_rows():
    """A free lane is priced by ordinary tokens; vendors publish cache and image
    rows next to them, and a nonzero one there does not make the model paid."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", "pricing": {
            "prompt": "0", "completion": "0", "input_cache_read": "0.0000001", "image": "0.001"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_zero_price_needs_a_published_price():
    """Silence is not a zero: an entry that qualifies only because two models are
    priced 0 cannot be verified against a catalog that stopped saying so."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "publishes no price" in result.detail


@respx.mock
async def test_one_free_variant_is_enough():
    """The paid twin sits in the same catalog under the same family name."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"id": "vendor/qwen3-coder:free-preview", "pricing": {"prompt": "0.001", "completion": "0.002"}},
            {"id": "vendor/qwen3-coder:free", "pricing": {"prompt": "0", "completion": "0"}},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


def new_api_entry() -> Entry:
    """A catalog shaped the way the new-api family of gateways ships it:
    `model_name` for the id, and multipliers instead of a pricing object."""
    e = Entry.model_validate({
        **BASE,
        "models": [{"family": "kimi-k3", "tier": "frontier"}],
        "probe": {
            "type": "api-models",
            "endpoint": "https://api.x.ai/v1/models",
            "free_marker": "free",
            "require_zero_price": True,
        },
    })
    return e


@respx.mock
async def test_new_api_names_the_id_field_model_name():
    """Reading only `id` left this whole catalog shape unverifiable: every row
    answered "no model ids in response" and the entry could never be probed."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_name": "moonshotai/kimi-k3-free", "quota_type": 0,
             "model_ratio": 0, "model_price": 0, "completion_ratio": 1},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, new_api_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_new_api_free_lane_that_acquired_a_ratio_is_fail():
    """The multiplier is the price here: the id keeps its `-free` suffix and the
    row starts billing the moment `model_ratio` stops being zero."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_name": "moonshotai/kimi-k3-free", "quota_type": 0,
             "model_ratio": 1.5, "completion_ratio": 5},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, new_api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail and "1.5/7.5" in result.detail


@respx.mock
async def test_new_api_paid_twin_does_not_vouch_for_the_free_lane():
    """`kimi-k3` and `kimi-k3-free` share a family name; only the second one is
    the offer, which is what free_marker keeps the check pointed at."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_name": "moonshotai/kimi-k3", "quota_type": 0, "model_ratio": 1.5},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, new_api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "kimi-k3" in result.detail


@respx.mock
async def test_new_api_per_request_billing_is_read_from_model_price():
    """`quota_type` 1 bills per call, and then `model_ratio` is meaningless —
    reading it anyway would call a per-request-priced model free."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_name": "moonshotai/kimi-k3-free", "quota_type": 1,
             "model_ratio": 0, "model_price": 0.01},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, new_api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "0.01" in result.detail


@respx.mock
async def test_new_api_per_request_billing_sent_as_a_string():
    """Same row, `quota_type` quoted. Compared strictly it would miss the
    per-request branch and read the zero `model_ratio` as a free lane."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_name": "moonshotai/kimi-k3-free", "quota_type": "1",
             "model_ratio": 0, "model_price": 0.01},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, new_api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "0.01" in result.detail


@respx.mock
async def test_new_api_row_without_any_price_field_is_not_free():
    """Same rule as the OpenAI-shaped catalogs: silence is not a zero."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"model_name": "moonshotai/kimi-k3-free"}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, new_api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "publishes no price" in result.detail


@respx.mock
async def test_a_price_row_that_is_not_a_number_is_not_a_zero():
    """A vendor that replaces its price with null or "on request" has stopped
    publishing one; an empty price list would otherwise read as all-zeros."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"id": "qwen/qwen3-coder:free", "pricing": {"prompt": None, "completion": "0"}},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "publishes no price" in result.detail


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
async def test_bot_challenge_is_inconclusive_not_a_dead_offer():
    """cto.new answered a Vercel checkpoint to everything that was not a browser.
    A wall served with HTTP 200 carries none of the keywords, and counting that
    as a failure archives a live service after three runs."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="<html><title>Just a moment...</title>"
                  "<body>Enable JavaScript and cookies to continue</body></html>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE and "bot challenge" in result.detail


@respx.mock
async def test_a_noscript_notice_does_not_shield_a_dead_offer():
    """The marker is only consulted once the keywords have already failed — but a
    page that serves its offer above a <noscript> must still pass, and one that
    has genuinely dropped the offer must still fail on the keywords."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="<noscript>Please enable JavaScript to view this site</noscript>"
                  "qwen3-coder on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_challenge_wording_in_a_models_response_is_inconclusive():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, text="<html>Checking your browser before accessing api.x.ai</html>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE and "checking your browser" in result.detail


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


def test_a_retired_entry_is_left_alone():
    """GitHub Models started answering HTTP 410 the day after its shutdown. The
    entry is already archived by retired_on, so flagging it only sent the scout
    to repair a probe for a product that no longer exists."""
    e = api_entry()
    e.retired_on = date(2026, 7, 30)
    assert apply_results([e], {"x": ProbeResult(ProbeStatus.FAIL, "page gone: HTTP 410")},
                         date(2026, 8, 3)) == []
    assert e.probe_failures == 0 and e.last_verified == date(2026, 1, 1)


def test_an_announced_retirement_still_in_the_future_is_probed_normally():
    e = api_entry()
    e.retired_on = date(2026, 8, 30)
    flagged = apply_results([e], {"x": ProbeResult(ProbeStatus.FAIL, "missing families")},
                            date(2026, 8, 3))
    assert [x.id for x, _ in flagged] == ["x"] and e.probe_failures == 1


def test_pass_promotes_provisional_after_settling():
    e = api_entry()  # first_seen 2026-01-01
    e.provisional = True
    apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 1, 10))
    assert e.provisional is True  # too young to promote
    apply_results([e], {"x": ProbeResult(ProbeStatus.FAIL, "gone")}, date(2026, 2, 1))
    assert e.provisional is True  # only PASS promotes
    apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 1, 15))
    assert e.provisional is False
