import json
import uuid
from datetime import date

import httpx
import respx

from freetier_radar.history import load_history
from freetier_radar.models import ApiInfo, DataUse, Entry, ModelFamily, save_registry
from freetier_radar.prober import (
    ProbeResult, ProbeStatus, _amain, apply_results, family_named, for_a_human, is_model_stale,
    probe_entry,
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


@respx.mock
async def test_a_free_id_the_catalog_marks_unavailable_is_fail():
    """The price is not the whole offer. Routeway carries `laguna-m.1:free` at a
    published 0 and marks it `available: false` in the same row — a lane nobody
    can call, which a price-only check would keep vouching for forever."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "available": False, "pricing": {
            "input": {"unit": "1M tokens", "price_per_million_t": 0},
            "output": {"unit": "1M tokens", "price_per_million_t": 0}}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "marked unavailable" in result.detail and "qwen3-coder:free" in result.detail


@respx.mock
async def test_a_withdrawn_row_does_not_vouch_for_a_family_that_now_bills():
    """The withdrawn row is the free one, the callable row is priced. Counting
    both as matches would read the family as still having a free lane."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"id": "vendor/qwen3-coder:free", "available": False,
             "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "vendor/qwen3-coder:free-v2", "available": True,
             "pricing": {"prompt": "0.001", "completion": "0.002"}},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail and "0.001/0.002" in result.detail
    # The withdrawn row is not the reason and must not be quoted as the price.
    assert "qwen3-coder:free priced 0/0" not in result.detail


@respx.mock
async def test_availability_is_read_when_a_vendor_stringifies_the_flag():
    """A check that only ever fires on a JSON boolean is a check one `"false"`
    away from never firing at all — the same trap `quota_type` already sprang."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "available": "false",
                             "pricing": {"prompt": "0", "completion": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "marked unavailable" in result.detail


@respx.mock
async def test_an_outdated_marker_is_not_an_availability_verdict():
    """Routeway flags eight superseded models `outdated: true` while leaving them
    `available: true` and callable. Staleness is is_model_stale's question, and
    reading it here would fail live entries over a model's age."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "available": True,
                             "outdated": True, "pricing": {"prompt": "0", "completion": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_availability_is_checked_without_a_price_requirement():
    """Presence, not price: an entry that does not demand a published zero still
    claims the family is callable, and the vendor here says it is not."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", "available": False}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "marked unavailable" in result.detail


LANES_URL = "https://api.x.ai/api/v1/ai/recommended-models"


def keyed_lanes(free: list[str], cline_pass: list[str] = (), recommended: list[str] = ()) -> dict:
    """The shape Cline serves at api.cline.bot/api/v1/ai/cline/recommended-models
    (read 2026-09-14): lanes side by side under keys of their own, one object per
    model, and no price or free flag anywhere — the lane a model sits in is the
    vendor's whole account of what it costs."""
    def rows(ids):
        return [{"id": i, "name": i.split("/")[-1], "description": "", "tags": []} for i in ids]
    return {"recommended": rows(recommended), "free": rows(free),
            "clinePass": rows(cline_pass), "clineCloud": rows(["cline-cloud/glm-5.2"])}


def lane_entry() -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "laney",
        "category": "agent-cli",
        "models": [{"family": "deepseek-v4-flash", "tier": "strong"}],
        "probe": {"type": "api-models", "endpoint": LANES_URL, "lane": "free"},
    })


@respx.mock
async def test_a_family_is_read_from_the_lane_its_vendor_names():
    """Read as an OpenAI catalog this document holds no model rows at all: there
    is no `data`, only lanes, and the `free` one is the offer."""
    respx.get(LANES_URL).mock(return_value=httpx.Response(200, json=keyed_lanes(
        free=["deepseek/deepseek-v4-flash", "poolside/laguna-s-2.1:free"],
        cline_pass=["cline-pass/glm-5.2"])))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, lane_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_family_only_a_paid_lane_names_is_not_free():
    """Why the lane is named instead of every array being read: DeepSeek V4 Flash
    is in ClinePass, the $9.99 plan, whether or not it is also in the free lane,
    so a family matched anywhere in the document would outlive its promotion in
    the Models column."""
    respx.get(LANES_URL).mock(return_value=httpx.Response(200, json=keyed_lanes(
        free=["poolside/laguna-s-2.1:free"],
        cline_pass=["cline-pass/deepseek-v4-flash"],
        recommended=["deepseek/deepseek-v4-flash"])))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, lane_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "deepseek-v4-flash" in result.detail


@respx.mock
async def test_an_empty_or_missing_lane_fails_and_says_which_lane():
    """An empty `free` array is the vendor saying no promotion is running, so it
    fails like a catalog without rows. Both failures name the lane — "no model
    ids in response" reads as a broken endpoint, and this endpoint answered —
    and they say different things, because a promotion that ended and a key
    the vendor renamed want opposite repairs."""
    details = []
    for body in (keyed_lanes(free=[], cline_pass=["cline-pass/deepseek-v4-flash"]),
                 {"recommended": [], "clinePass": []}):
        respx.get(LANES_URL).mock(return_value=httpx.Response(200, json=body))
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, lane_entry(), backoff=0)
        assert result.status is ProbeStatus.FAIL
        assert "lane" in result.detail and "free" in result.detail
        details.append(result.detail)
    assert details[0] != details[1]


@respx.mock
async def test_config_ids_are_read_from_the_lane_too():
    """`api.model_ids` makes the Models column's claim in config form, so it is
    checked against the same lane: an id the document still names elsewhere, but
    no longer lists as free, is a dead config line."""
    entry = lane_entry()
    entry.api = ApiInfo(base_url="https://api.x.ai/v1",
                        model_ids=["deepseek/deepseek-v4-flash", "z-ai/glm-5.3-flash"])
    respx.get(LANES_URL).mock(return_value=httpx.Response(200, json=keyed_lanes(
        free=["deepseek/deepseek-v4-flash"], recommended=["z-ai/glm-5.3-flash"])))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "z-ai/glm-5.3-flash" in result.detail
    assert "deepseek/deepseek-v4-flash" not in result.detail


def _read(url: str, **body) -> httpx.Response:
    return httpx.Response(200, request=httpx.Request("GET", url), **body)


def test_a_newer_family_is_named_only_where_the_rows_own_page_names_it():
    """The question a generation bump has to clear before a human reads it. On
    2026-09-14 the scout pointed Groq, Hetzner, OVH and three more rows at
    qwen3.7-flash, a model none of their pages names."""
    page = _read("https://x.ai/pricing", text="qwen/qwen3.8-27b at 30 RPM. Gemini 3.6 Flash is free.")
    assert family_named(page, page_entry(), "gemini-3.6-flash") is True
    assert family_named(page, page_entry(), "qwen3.7-flash") is False


def test_a_family_served_in_another_lane_or_at_a_price_is_not_named_free():
    """Routeway carried Llama 4 at a price beside a free lane whose only Llama
    was 3.3, and the bump was dismissed on exactly that: a catalog a row can
    reach is not the lane the row is listed for."""
    lanes = _read(LANES_URL, json=keyed_lanes(free=["cline-free/deepseek-v4.1-flash"],
                                             cline_pass=["cline-pass/glm-5.2"]))
    assert family_named(lanes, lane_entry(), "deepseek-v4.1-flash") is True
    assert family_named(lanes, lane_entry(), "glm-5.2") is False

    priced = Entry.model_validate({**BASE, "probe": {
        "type": "api-models", "endpoint": "https://api.x.ai/v1/models", "require_zero_price": True}})
    catalog = _read("https://api.x.ai/v1/models", json={"data": [
        {"id": "vendor/llama-3.3-70b:free", "pricing": {"prompt": "0", "completion": "0"}},
        {"id": "vendor/llama-4-maverick", "pricing": {"prompt": "0.00000011", "completion": "0.00000044"}},
    ]})
    assert family_named(catalog, priced, "llama-3.3") is True
    assert family_named(catalog, priced, "llama-4") is False


def test_a_catalog_that_cannot_be_read_names_no_family_either_way():
    maintenance = _read("https://api.x.ai/v1/models", text="<html>back soon</html>")
    assert family_named(maintenance, api_entry(), "qwen3.8") is None
    empty_lane = _read(LANES_URL, json=keyed_lanes(free=[]))
    assert family_named(empty_lane, lane_entry(), "deepseek-v4.1-flash") is None


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
async def test_a_non_breaking_space_does_not_hide_the_keyword():
    """Inception Labs writes its grant as "100 million&nbsp;free tokens", so the
    quoted sentence a reader copies off the page never occurs in the bytes. A
    typographic space is not a withdrawn offer, and it must not read as one."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free\u00a0tier no\u202fcredit\u2009card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_keyword_the_page_source_wraps_across_lines_still_matches():
    """HTML renders any run of whitespace as one space, so a sentence a template
    wraps at eighty columns reads whole in a browser. LLM Tech's quickstart
    serves "2 concurrent requests and 2M tokens\\n    per day per address", and the
    sentence a reader copies off the page failed a live offer on 2026-09-18.
    freetier-quotes already read whitespace that way; the probe reads it the same,
    for the offer's keywords and for the sentence announcing its end."""
    wrapped = ("<p>Shared and rate-limited: 2 concurrent requests and 2M tokens\n"
               "    per day per address. qwen3-coder free tier, no credit card</p>")
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=wrapped))
    entry = page_entry()
    entry.probe.keywords = ["2 concurrent requests and 2M tokens per day per address"]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS

    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text=wrapped + "<p>The free tier has been\n  discontinued.</p>"))
    entry.probe.dead_markers = ["free tier has been discontinued"]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL and "offer withdrawn" in result.detail


def titled_entry() -> Entry:
    """A catalog that publishes both field names with opposite meanings:
    `model_id` is what goes in the request body, `model_name` is the human
    title beside it."""
    return Entry.model_validate({
        **BASE,
        "models": [{"family": "coding-glm-5.1", "tier": "frontier"}],
        "probe": {
            "type": "api-models",
            "endpoint": "https://api.x.ai/v1/models",
            "free_marker": "free",
            "require_zero_price": True,
        },
    })


@respx.mock
async def test_the_callable_id_wins_over_the_title_beside_it():
    """AIHubMix keeps the id in `model_id` and a spaced-out title in
    `model_name` — the same field the new-api gateways use for the id. Reading
    the pair in that order turned every family into a miss, because a
    hyphenated id never occurs inside a title that spells it with spaces."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_id": "coding-glm-5.1-free", "model_name": "Coding GLM 5.1 (free)",
             "pricing": {"input": 0, "output": 0}},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, titled_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_titled_row_that_started_billing_is_reported_by_its_id():
    """The price is still the offer here, and the failure has to name the string
    a reader can look up — the id, not the title."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"model_id": "coding-glm-5.1-free", "model_name": "Coding GLM 5.1 (free)",
             "pricing": {"input": 0.6, "output": 2.2}},
        ]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, titled_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail
    assert "coding-glm-5.1-free priced 0.6/2.2" in result.detail


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


def listing_entry() -> Entry:
    """A page-keywords entry that publishes a Models column, which page_entry()
    deliberately does not: the families are the thing under test here."""
    e = page_entry()
    e.models = [m.model_copy() for m in api_entry().models]  # qwen3-coder
    return e


@respx.mock
async def test_a_family_the_page_does_not_name_flags_without_failing():
    """The offer is evidenced — the keywords all match — but the README lists a
    model the page says nothing about. novita's lesson generalised: a probe that
    only watches the offer lets the Models column drift on its own. It must not
    FAIL, or three runs of a restyled marketing page archive a live service."""
    entry = listing_entry()
    entry.models.append(entry.models[0].model_copy(update={"family": "llama-4"}))
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS
    assert "llama-4" in result.detail and "qwen3-coder" not in result.detail


@respx.mock
async def test_a_family_the_page_spells_with_spaces_is_evidenced():
    """Vendors write "Qwen3 Coder", the registry writes qwen3-coder. Comparing
    with separators and case removed is what keeps this check from flagging
    every entry on its first run."""
    entry = listing_entry()
    entry.models.append(entry.models[0].model_copy(update={"family": "llama-4"}))
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder and Llama 4 on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_family_folded_into_a_shared_suffix_is_evidenced():
    """Antigravity's pricing page enumerates its free agent models as "Claude
    Sonnet & Opus 4.6" — two models, one version number. A substring test calls
    a true row a lie, and a warning that fires on correct entries is a warning
    nobody reads. The parts have to arrive close together, though: "claude" and
    "4.6" at opposite ends of a price list vouch for nothing."""
    entry = listing_entry()
    entry.models = [entry.models[0].model_copy(update={"family": "claude-opus-4.6"})]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder, free tier, no credit card. "
                  "Agent model: Claude Sonnet &amp; Opus 4.6, gpt-oss-120b"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_family_parts_scattered_over_the_page_are_not_evidence():
    entry = listing_entry()
    entry.models = [entry.models[0].model_copy(update={"family": "claude-opus-4.6"})]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder, free tier, no credit card. Claude models are on the Pro plan."
                  + " filler" * 40 + " Opus is a trademark." + " filler" * 40 + " version 4.6"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS and "claude-opus-4.6" in result.detail


@respx.mock
async def test_an_older_version_on_the_page_does_not_name_a_newer_family():
    """The version half of a family name must not match inside a different
    version. Kiro's pricing page is the live case: it puts Sonnet 4.5 on the
    free tier and sells 4.6 and Opus, and its "Opus 4.5" used to be evidence for
    a family called opus-5 — the exact drift this check exists to catch, waved
    through by the check itself."""
    entry = listing_entry()
    entry.models = [entry.models[0].model_copy(update={"family": "opus-5"})]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder, free tier, no credit card. "
                  "Paid plans add Opus 4.5 and Opus 4.6."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS and "opus-5" in result.detail


@respx.mock
async def test_a_version_ending_a_sentence_still_names_its_family():
    """The other side of the same anchor: "MiniMax 2.1." ends a sentence on the
    page Kiro's row is probed against, so a family may be followed by a period
    and still be named. Only the left edge of each part is anchored."""
    entry = listing_entry()
    entry.models = [entry.models[0].model_copy(update={"family": "minimax-2.1"})]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder, free tier, no credit card. "
                  "Open weight models such as DeepSeek v3.2 and MiniMax 2.1."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_version_the_vendor_prefixes_with_a_letter_still_names_its_family():
    """The live regression this rule was written for. On 2026-08-14 Kiro's
    pricing page listed its free-tier models as "DeepSeek v3.2 and MiniMax 2.1.";
    on 2026-08-20 the same sentence about the same free tier read "DeepSeek 3.2,
    and MiniMax M2.1". Nothing was withdrawn — a caption was retyped — but both
    families went unnamed, and the scout turned that into a PR deleting them."""
    entry = listing_entry()
    entry.models = [entry.models[0].model_copy(update={"family": f})
                    for f in ("deepseek-v3.2", "minimax-2.1")]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder, free tier, no credit card. Users on the Free Tier "
                  "have access to open weight models such as DeepSeek 3.2, and MiniMax M2.1."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_letter_never_carries_a_bare_version_number():
    """The relaxation stops at the dot. A generation written "2.1" is specific
    enough to survive a vendor gluing an M to it; a bare "5" is not, and letting
    a letter carry it would hand glm-5 every hashed h5 in the markup after a
    GLM — undoing the left anchor two tests above."""
    entry = listing_entry()
    entry.models = [entry.models[0].model_copy(update={"family": "glm-5"})]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder, free tier, no credit card. "
                  "GLM models are sold by the token.<span class=h5></span>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS and "glm-5" in result.detail


@respx.mock
async def test_a_family_named_only_in_the_page_data_is_evidenced():
    """A name the vendor serves inside its page data is served, so the Models
    column is not flagged over it. Whether it is named AS FREE is the stronger
    question, and the one an anchor keyword exists to answer — which is why the
    keywords here are read against the rendered page while this check is not:
    an unevidenced family is a note on a live row, and a missing keyword ends
    it."""
    entry = listing_entry()
    entry.models = [ModelFamily(family="mercury-2")]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text='qwen3-coder on the free tier, no credit card'
                  '<script>{"id":"vendor/mercury-2"}</script>'))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_dead_offer_outranks_an_unevidenced_family():
    """Both are true at once when a vendor pulls a tier and its models with it.
    The withdrawal is the bigger news and must not be downgraded to a flag."""
    entry = listing_entry()
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="free tier, no credit card, qwen3-coder — "
                  "update: the free API service has ended"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL and "offer withdrawn" in result.detail


@respx.mock
async def test_an_api_models_entry_is_not_family_checked_against_prose():
    """_check_api_models already demands every family back from the catalog. A
    second pass over the same bytes would only invent a second vocabulary for
    the same finding."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


def config_entry(*ids: str, zero_price: bool = True) -> Entry:
    """An api-models entry that also publishes connection ids. `models[]` and
    `api.model_ids` are separate claims about the same catalog, and only the
    first of them was ever checked."""
    e = api_entry()
    e.api = ApiInfo(base_url="https://api.x.ai/v1", model_ids=list(ids))
    e.probe.require_zero_price = zero_price
    return e


LANE = {"data": [{"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0", "completion": "0"}}]}


def _lane(*extra: dict) -> dict:
    return {"data": LANE["data"] + list(extra)}


@respx.mock
async def test_a_config_id_the_catalog_dropped_flags_without_failing():
    """The defect this check was written for: a family leaves `models[]`, its id
    stays in `api.model_ids`, and the three generated configs go on handing out
    an id that 404s. The offer is intact, so it must not FAIL — three failures
    archive a live row over a stale config line."""
    entry = config_entry("qwen/qwen3-coder:free", "openai/gpt-oss-20b:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(200, json=_lane()))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "openai/gpt-oss-20b:free" in result.detail
    assert "qwen/qwen3-coder:free" not in result.detail


@respx.mock
async def test_a_reversioned_config_id_is_reported_with_its_successor():
    """NVIDIA kept the model and re-dated its id — deepseek-v4-flash became
    deepseek-v4-flash-0731 — so the repair is a rename. Without the hint a
    reviewer cannot tell that case from a withdrawal, and the two want opposite
    edits."""
    entry = config_entry("deepseek-ai/deepseek-v4-flash")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "deepseek-ai/deepseek-v4-flash-0731",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "carries deepseek-ai/deepseek-v4-flash-0731" in result.detail


@respx.mock
async def test_a_renamed_config_id_is_reported_though_no_prefix_matches():
    """NVIDIA moved the version into the middle of the name: on 2026-09-02
    nvidia/nemotron-3-nano-30b-a3b had left that catalog while
    nvidia/nemotron-nano-3-30b-a3b sat in it. Same model, same words, no shared
    prefix — and the repair is still a rename."""
    entry = config_entry("nvidia/nemotron-3-nano-30b-a3b")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "nvidia/nemotron-nano-3-30b-a3b",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "carries nvidia/nemotron-nano-3-30b-a3b" in result.detail


@respx.mock
async def test_a_free_id_that_left_the_lane_does_not_name_its_metered_twin():
    """Routeway's llama-3.1-8b-instruct:free left the free lane while
    llama-3.1-8b-instruct went on being metered beside it. A successor has to
    extend the missing id or be built from the same words, and the metered twin
    is neither — it is the missing id with the word `free` taken off."""
    entry = config_entry("llama-3.1-8b-instruct:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "llama-3.1-8b-instruct",
                         "pricing": {"prompt": "0.0000002", "completion": "0.0000006"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "carries" not in result.detail


@respx.mock
async def test_a_config_id_the_vendor_marks_unavailable_is_dead():
    """The same `available` flag `_check_api_models` reads for a family: a row
    the vendor says cannot be called is not a config line, whatever it costs."""
    entry = config_entry("qwen/qwen3-coder:free", "vendor/paused:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/paused:free", "available": False,
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS and "marked unavailable" in result.detail


@respx.mock
async def test_a_config_id_that_started_billing_is_dead_where_prices_are_read():
    """An aggregator can leave an id exactly where it was and start charging for
    it. On a row that sets require_zero_price the zero is the offer, and the
    config should stop advertising the id the moment it stops being one."""
    entry = config_entry("qwen/qwen3-coder:free", "vendor/nowpaid:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/nowpaid:free",
                         "pricing": {"prompt": "0.000001", "completion": "0.000003"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS and "priced" in result.detail


@respx.mock
async def test_a_priced_config_id_is_kept_where_the_lane_is_a_quota():
    """NVIDIA NIM and OVHcloud publish list prices for every row and hand out
    the free tier as a quota instead, which is what require_zero_price: false
    means. Reading the price there would empty two healthy configs."""
    entry = config_entry("vendor/metered", zero_price=False)
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/metered",
                         "pricing": {"prompt": "0.000001", "completion": "0.000003"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_config_ids_are_never_read_off_a_page():
    """A page-keywords probe reads prose, where a missing id means nothing —
    that is why unevidenced_families only ever flags, and here the consequence
    would be a deletion from a config rather than a note on a column."""
    entry = page_entry()
    entry.api = ApiInfo(base_url="https://api.x.ai/v1", model_ids=["some/id-the-page-never-names"])
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_family_matches_an_id_that_writes_its_dots_as_hyphens():
    """Kenari lists glm-4.7-flash as glm-4-7-flash:free and step-3.7-flash as
    step-3-7-flash:free. The registry spells a family one way for every row,
    so the catalog id is squashed the same way a page is — plus the dot,
    which an id has no other reason to lose."""
    entry = api_entry()
    entry.models = [ModelFamily(family="glm-4.7-flash"), ModelFamily(family="step-3.7-flash")]
    entry.probe.require_zero_price = True
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"id": "glm-4-7-flash:free", "pricing": {"free": True, "input": 1100000000}},
            {"id": "step-3-7-flash:free", "pricing": {"free": True, "input": 900000000}},
            {"id": "glm-5-3", "pricing": {"free": False, "input": 10000000000}}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_zero_token_price_beside_a_per_request_charge_is_not_free():
    """Vercel prices spacexai/grok-stt at 0 per token and 0.000028 per second of
    audio in the same row; EmpirioLabs prices gemma-3-27b at 0 per token and
    $0.004 per message. Reading only the token rows called both free. A row is
    free when every price the vendor publishes for it is zero — measured
    2026-09-02, no listed id on the eight rows whose prices are read carries a
    non-zero price outside the token rows, so nothing live changes."""
    entry = config_entry("qwen/qwen3-coder:free", "vendor/stt:free", "vendor/per-message:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane(
            {"id": "vendor/stt:free",
             "pricing": {"input": "0", "transcription_duration_cost_per_second": "0.000028"}},
            {"id": "vendor/per-message:free",
             "pricing": {"prompt": "0", "completion": "0", "request": "0.004"}},
            {"id": "vendor/annotated:free",
             "pricing": {"prompt": "0", "completion": "0", "varies_by_provider": True}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "vendor/stt:free priced" in result.detail
    assert "vendor/per-message:free priced" in result.detail
    # the boolean is an annotation, not a price: the row stays free, and unlisted
    assert "vendor/annotated:free" in result.detail.split("does not list")[1]


@respx.mock
async def test_the_vendors_own_free_flag_outranks_its_price_rows():
    """Kilo marks Google's Lyria previews isFree: false and prices them at 0;
    Kenari marks twelve :free ids free: true and prints the metered rate beside
    each one, since a :free call "does not deduct balance". Where a catalog says
    in so many words whether a row is free, that is the answer, and the price
    rows are read only where it does not."""
    entry = config_entry("qwen/qwen3-coder:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane(
            {"id": "google/lyria-3-pro-preview:free", "isFree": False,
             "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "step-3-7-flash:free",
             "pricing": {"free": True, "input": 1100000000, "output": 7700000000,
                         "currency": "IDR"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "step-3-7-flash:free" in result.detail
    assert "lyria" not in result.detail


@respx.mock
async def test_a_free_id_the_catalog_carries_and_the_config_does_not_is_reported():
    """The other half of the same defect. STALE_IDS read only the ids the
    registry already had, so a lane that grew was invisible: measured
    2026-09-02, eleven zero-priced ids sat unlisted across four rows whose
    probes were passing — Vercel 5, Routeway 3, Requesty 2, TokenRouter 1 —
    and Kilo's six new free models had been found by hand that morning."""
    entry = config_entry("qwen/qwen3-coder:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "google/gemma-4:free",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "api.model_ids does not list" in result.detail
    assert "google/gemma-4:free" in result.detail
    assert "qwen/qwen3-coder:free" not in result.detail


@respx.mock
async def test_growth_is_read_with_the_row_s_own_lane_definition():
    """A zero price alone is not the lane. OpenRouter and Kilo both price
    Google's Lyria music previews at 0 with no :free suffix (Kilo marks them
    isFree: false), and TokenRouter carries a zero-priced stealth preview
    outside its free lane. The marker the offer check matches families with
    draws the same line here; a metered :free id and a withdrawn one stay out
    for the reasons dead_model_ids would report them."""
    entry = config_entry("qwen/qwen3-coder:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane(
            {"id": "google/lyria-3-pro-preview", "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "vendor/metered:free",
             "pricing": {"prompt": "0.000001", "completion": "0.000003"}},
            {"id": "vendor/paused:free", "available": False,
             "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_where_no_marker_names_the_lane_every_zero_is_in_it():
    """Vercel and Requesty suffix nothing: on those rows the price is the only
    thing separating a free id from the metered rows beside it, and the
    registry says so with an empty free_marker."""
    entry = config_entry("qwen/qwen3-coder:free")
    entry.probe.free_marker = ""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane(
            {"id": "minimax/minimax-m3-free", "pricing": {"input": "0", "output": "0"}},
            {"id": "vendor/metered", "pricing": {"input": "0.000015", "output": "0.000075"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "minimax/minimax-m3-free" in result.detail
    assert "vendor/metered" not in result.detail


@respx.mock
async def test_an_ignored_id_is_seen_and_not_reported():
    """AIHubMix prices two image generators at 0 beside its text lane, and one
    row whose own description says it was removed from the platform. A zero
    the registry has looked at and left out is recorded in api.ignored_ids,
    with the reason beside it in api.note, so the report only ever shows ids
    nobody has judged yet."""
    entry = config_entry("qwen/qwen3-coder:free")
    entry.api.ignored_ids = ["spacexai/grok-stt:free"]
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "spacexai/grok-stt:free",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_rename_that_changed_words_shows_both_halves_in_one_verdict():
    """_successor_hint sees an id that extends the missing one or reorders its
    words, and nothing else. A vendor that bumps the version inside the name —
    llama-4-maverick to llama-4.1-maverick — leaves a dead id on one side and
    an unlisted one on the other, and only a verdict that carries both puts
    them on the same line of the pull request."""
    entry = config_entry("qwen/qwen3-coder:free", "meta/llama-4-maverick:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "meta/llama-4.1-maverick:free",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "no longer answers for: meta/llama-4-maverick:free" in result.detail
    assert "carries" not in result.detail
    assert "api.model_ids does not list" in result.detail
    assert "meta/llama-4.1-maverick:free" in result.detail


@respx.mock
async def test_growth_is_not_read_where_prices_are_not():
    """NVIDIA NIM lists every model it hosts with no price field and hands out
    the free tier as a quota. On a row that does not read prices a zero is not
    an offer, and a report built on one would be the whole catalog."""
    entry = config_entry("qwen/qwen3-coder:free", zero_price=False)
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/another:free",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


def catalog_entry(*ids: str) -> Entry:
    """A page-keywords entry whose offer lives on a pricing page and whose ids
    live in a keyless catalog at another url — Ollama, opencode Zen,
    SambaNova, Inception and Regolo on 2026-09-02, 20 of the 37 ids that
    nothing had read back."""
    e = page_entry()
    e.probe.catalog = "https://api.x.ai/v1/models"
    e.api = ApiInfo(base_url="https://api.x.ai/v1", model_ids=list(ids))
    return e


PAGE_OK = "qwen3-coder on the free tier, no credit card"


@respx.mock
async def test_a_page_row_checks_its_ids_against_the_catalog_it_names():
    entry = catalog_entry("qwen/qwen3-coder", "qwen/qwen3-coder-legacy")
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=PAGE_OK))
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "qwen/qwen3-coder-legacy is not in the catalog" in result.detail
    assert "qwen/qwen3-coder " not in result.detail


@respx.mock
async def test_a_page_row_whose_catalog_answers_for_every_id_passes():
    entry = catalog_entry("qwen/qwen3-coder")
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=PAGE_OK))
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}, {"id": "other/paid"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_catalog_that_wraps_its_rows_in_models_is_read():
    """Opper's keyless catalog answers `{"models": [...]}` rather than an
    OpenAI `data` array (api.opper.ai/v3/models, 2026-09-17). Read as `data`
    alone it would be an empty catalog, and the run would report a catalog
    that answered no model ids for a row whose ids are all there."""
    entry = catalog_entry("gemini/gemma-4-31b", "gemini/gemma-3-27b")
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=PAGE_OK))
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"models": [{"id": "gemini/gemma-4-31b"}, {"id": "other/paid"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "gemini/gemma-3-27b is not in the catalog" in result.detail
    assert "gemini/gemma-4-31b " not in result.detail


@respx.mock
async def test_a_catalog_that_stops_answering_is_said_out_loud():
    """The offer is still on the page, so the row is verified; but a check that
    silently did not run is the INCONCLUSIVE silence again, one field down.
    A line in the pull request costs nothing and a dead id in the configs
    costs a reader."""
    entry = catalog_entry("qwen/qwen3-coder")
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=PAGE_OK))
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        401, json={"error": "unauthorized"}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "could not be checked" in result.detail and "401" in result.detail


@respx.mock
async def test_a_dead_offer_outranks_a_catalog_check():
    """The catalog is a second question about the ids; the first question is
    the page, and a page that no longer carries the offer fails the row before
    the catalog is fetched at all."""
    entry = catalog_entry("qwen/qwen3-coder")
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="pricing: pay as you go"))
    route = respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(200, json={"data": []}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert not route.called


@respx.mock
async def test_a_flagged_column_still_carries_what_the_catalog_says_about_the_ids():
    """A page that stops naming a family flags the Models column, and until
    2026-09-21 that verdict returned before the row's catalog was asked. Regolo
    dropped Llama 3.3 from its price table and its catalog at once; the run
    said stale-models, the scout dropped the family, and Llama-3.3-70B-Instruct
    stayed in the configs with nothing in the pull request to say so."""
    entry = catalog_entry("qwen/qwen3-coder", "vendor/llama-4-70b")
    entry.models = [ModelFamily(family="qwen3-coder"), ModelFamily(family="llama-4")]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=PAGE_OK))
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS
    assert result.detail == ("listed families the page does not name: llama-4 | "
                             "api.model_ids the catalog no longer answers for: "
                             "vendor/llama-4-70b is not in the catalog")


@respx.mock
async def test_a_flagged_column_with_sound_ids_reads_as_it_did():
    entry = catalog_entry("qwen/qwen3-coder")
    entry.models = [ModelFamily(family="qwen3-coder"), ModelFamily(family="llama-4")]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=PAGE_OK))
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result == ProbeResult(ProbeStatus.STALE_MODELS,
                                 "listed families the page does not name: llama-4")


def test_the_half_of_a_line_for_a_human_is_what_follows_the_models_half():
    """The fix prompt tells the model to leave everything after the family
    verdict alone; this is that part, so a row the model repaired can still
    carry it to the pull request."""
    ids = ("api.model_ids the catalog no longer answers for: a is not in the catalog | "
           "zero-priced ids in the catalog that api.model_ids does not list "
           "(add them, or record them in api.ignored_ids): b")
    assert for_a_human(f"missing families: x | no longer free: y | {ids}") == ids
    assert for_a_human("listed families the page does not name: x | keyless lane "
                       "rate-limited: m answered HTTP 429") == ("keyless lane rate-limited: "
                                                                "m answered HTTP 429")
    assert for_a_human("missing families: x | no longer free: y") == ""
    assert for_a_human("") == ""
    # the row's word on training is restated by a person reading the data page
    moved = "data_use quote is no longer on https://x.ai/privacy — read what the vendor says now"
    assert for_a_human(f"listed families the page does not name: x | {moved}") == moved


@respx.mock
async def test_a_failed_family_still_reports_the_ids_beside_it():
    """The blind spot the 2026-09-07 run walked into. LLMTR failed on
    minimax-m3 — the free id had left the catalog and the metered twin stayed —
    and the same read had taken two more ids out of `api.model_ids`, which
    nothing said: this function returned on the offer check, above the id
    check. The scout dropped the family, the pull request read as a whole
    repair, and the dead ids stayed in configs/claude-code.sh, opencode.json,
    litellm.yaml and free-llm.env.example, which is what a reader pastes.

    Only on an api-models row, where the catalog that failed the family is the
    object already in hand — a page row keeps the behaviour above it, because
    there the failure IS the offer and the row is repaired or archived whole.
    """
    entry = config_entry("qwen/qwen3-coder:free", "vendor/gone")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(200, json={"data": [
        {"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0.0000003", "completion": "0.0000012"}},
        {"id": "vendor/arrived:free", "pricing": {"prompt": "0", "completion": "0"}},
    ]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail
    assert "vendor/gone is not in the catalog" in result.detail
    # Both directions, as on a passing row: a lane that swapped one id for
    # another is a dead id and an unlisted one, and the repair needs both.
    assert "vendor/arrived:free" in result.detail


@respx.mock
async def test_a_failed_row_whose_ids_are_intact_says_only_what_failed():
    """The other half of the same rule: the offer check's own words are the
    report, and nothing is appended where there is nothing to append."""
    entry = config_entry("vendor/still-free:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(200, json={"data": [
        {"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0.0000003", "completion": "0.0000012"}},
        {"id": "vendor/still-free:free", "pricing": {"prompt": "0", "completion": "0"}},
    ]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "api.model_ids" not in result.detail


@respx.mock
async def test_a_dry_run_counts_its_failures_so_a_shell_chain_can_stop(tmp_path):
    """The dry run printed "1 need attention" and exited 0, and the `&&` after
    it committed a row whose keyword its page did not carry. A count of FAILs
    is what main() turns into the exit code; a stale-ids flag is a verified
    row with a note and is not counted."""
    good = api_entry()
    bad = page_entry()
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}]}))
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="pay as you go"))
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [good, bad])
    failed = await _amain(reg, tmp_path / "failures", dry_run=True)
    assert failed == 1


def test_stale_ids_verifies_the_entry_like_a_pass():
    """Same reasoning as stale-models one test below: the offer was confirmed,
    only a field beside it is in doubt, and freezing last_verified would archive
    a live row in sixty days over a config line."""
    e = config_entry("vendor/gone")
    e.provisional = True
    flagged = apply_results([e], {"x": ProbeResult(
        ProbeStatus.STALE_IDS, "api.model_ids the catalog no longer answers for: vendor/gone")},
        date(2026, 7, 19))
    assert e.last_verified == date(2026, 7, 19) and e.probe_failures == 0
    assert e.provisional is False
    assert [(x.id, r.status) for x, r in flagged] == [("x", ProbeStatus.STALE_IDS)]


def test_stale_models_verifies_the_entry_like_a_pass():
    """The offer was confirmed; only the Models column is in doubt. Freezing
    last_verified instead would archive the row by staleness in sixty days."""
    e = listing_entry()
    e.provisional = True
    flagged = apply_results([e], {"pagey": ProbeResult(
        ProbeStatus.STALE_MODELS, "listed families the page does not name: llama-4")},
        date(2026, 7, 19))
    assert e.last_verified == date(2026, 7, 19) and e.probe_failures == 0
    assert e.provisional is False
    assert [(x.id, r.status) for x, r in flagged] == [("pagey", ProbeStatus.STALE_MODELS)]


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


def test_a_delisted_entry_is_left_alone():
    e = Entry.model_validate({**api_entry().model_dump(),
                              "delisted": {"on": date(2026, 7, 30), "reason": "taken off"}})
    assert apply_results([e], {"x": ProbeResult(ProbeStatus.PASS)}, date(2026, 8, 3)) == []
    assert e.probe_failures == 0 and e.last_verified == date(2026, 1, 1)


@respx.mock
async def test_a_row_archived_for_good_is_not_probed_at_all(tmp_path, capsys):
    """A delisted row keeps the probe it was published with, and some of those
    point at services the blocklist says never to fetch; a retired one points at
    an endpoint that is meant to be dead, and GitHub Models' 410 once crashed a
    run. Neither answer could change anything, so neither request is made —
    respx fails the run on any route it was not told about."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free tier no credit card"))
    retired = api_entry().model_copy(update={"id": "retired", "retired_on": date(2026, 1, 2)})
    delisted = Entry.model_validate({**api_entry().model_dump(), "id": "delisted",
                                     "delisted": {"on": date(2026, 1, 2), "reason": "taken off"}})
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [page_entry(), retired, delisted])

    assert await _amain(registry, tmp_path / "failures", dry_run=True) == 0
    assert "probed 1 entries, 0 need attention" in capsys.readouterr().out


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


@respx.mock
async def test_a_probe_run_records_what_changed_beside_the_registry(tmp_path):
    """The prober is the first of the two commands that write registry.yaml, so
    it is the first that owes the change log an entry."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free tier no credit card"))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [page_entry()])

    await _amain(registry, tmp_path / "failures", dry_run=False)

    events = load_history(tmp_path / "history.jsonl")
    assert [(e.event.value, e.id) for e in events] == [("added", "pagey")]


@respx.mock
async def test_the_summary_line_names_what_needs_attention(tmp_path, capsys):
    """failures.json stays on the runner, so "1 need attention" in the log was
    the whole account of a probe that passes from a laptop and fails from CI —
    the one discrepancy nobody can reproduce locally by definition. The id and
    its reason belong in the line everyone reads."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="nothing the entry claims is on this page"))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [page_entry()])

    await _amain(registry, tmp_path / "failures", dry_run=True)

    out = capsys.readouterr().out
    assert "probed 1 entries, 1 need attention" in out
    assert "pagey" in out and "qwen3-coder" in out


@respx.mock
async def test_a_clean_run_says_so_without_a_trailing_list(tmp_path, capsys):
    """Nothing flagged has to read as nothing flagged — an empty bracket after
    the count is the shape that makes a green run look broken."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free tier no credit card"))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [page_entry()])

    await _amain(registry, tmp_path / "failures", dry_run=True)

    assert "probed 1 entries, 0 need attention\n" in capsys.readouterr().out


@respx.mock
async def test_a_dry_run_records_no_history(tmp_path):
    """A local read must leave no trace, exactly as it leaves no verification
    date — the history is a log of what was published, not of who looked."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free tier no credit card"))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [page_entry()])

    await _amain(registry, tmp_path / "failures", dry_run=True)

    assert not (tmp_path / "history.jsonl").exists()


def anthropic_entry() -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "anth",
        "api": {"base_url": "https://x.ai/v1", "anthropic_base_url": "https://x.ai/anthropic"},
        "probe": {
            "type": "page-keywords",
            "endpoint": "https://x.ai/pricing",
            "keywords": ["qwen3-coder"],
        },
    })


@respx.mock
async def test_an_anthropic_route_is_called_with_a_model_the_row_publishes():
    """Fireworks checks the model before the key: its Anthropic route answered a
    made-up model with 404 "Model not found" and a model it serves with 401 on
    2026-09-17. A 404 is how this check tells a route that is gone, so the call
    names the row's own first id, the way the keyless check does — and only a
    row with no ids falls back to a placeholder."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))

    def answer(request: httpx.Request) -> httpx.Response:
        if json.loads(request.content)["model"] == "qwen3-coder-30b":
            return httpx.Response(401, json={"error": {"message": "You must provide an API key."}})
        return httpx.Response(404, json={"error": {"message": "Model not found", "param": "model"}})
    route = respx.post("https://x.ai/anthropic/v1/messages").mock(side_effect=answer)
    data = anthropic_entry().model_dump()
    data["api"]["model_ids"] = ["qwen3-coder-30b"]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, Entry.model_validate(data), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert json.loads(route.calls.last.request.content)["model"] == "qwen3-coder-30b"


@respx.mock
async def test_a_published_anthropic_route_that_answers_is_a_pass():
    """A keyless POST cannot complete a message, and does not try to: a 401 is
    the route saying it exists, which is the whole question."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    route = respx.post("https://x.ai/anthropic/v1/messages").mock(
        return_value=httpx.Response(401, json={"type": "error", "error": {"type": "authentication_error"}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert route.called


@respx.mock
async def test_an_anthropic_route_that_is_gone_is_a_note_not_a_failure():
    """The offer is still evidenced by its page; what died is a connection
    detail this list publishes. Same shape as a dead id in api.model_ids: the
    row stays verified and the run says what to fix."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://x.ai/anthropic/v1/messages").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "anthropic route gone" in result.detail and "HTTP 404" in result.detail


@respx.mock
async def test_an_anthropic_route_that_cannot_be_checked_is_said_so():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://x.ai/anthropic/v1/messages").mock(side_effect=httpx.ConnectError("boom"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0, attempts=2)
    assert result.status is ProbeStatus.STALE_IDS
    assert "could not be checked" in result.detail


def keyless_entry() -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "keyless",
        "models": [{"family": "gpt-oss", "tier": "strong"}],
        "api": {"base_url": "https://open.x.ai/v1", "auth": "none",
                "model_ids": ["gpt-oss-120b", "qwen3-coder-30b"]},
        "probe": {"type": "api-models", "endpoint": "https://open.x.ai/v1/models"},
    })


KEYLESS_CATALOG = {"data": [{"id": "gpt-oss-120b"}, {"id": "qwen3-coder-30b"}]}


@respx.mock
async def test_a_keyless_lane_that_answers_is_a_pass():
    """The catalog saying a model exists is not the lane letting anyone call it,
    so a row published as keyless is called, keylessly, on its first id."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    # The README's call first, bare; then the same id with the bearer token a
    # proxy sends (see the refuses_bearer tests below).
    assert call.call_count == 2
    sent = call.calls[0].request
    assert "authorization" not in sent.headers
    assert json.loads(sent.content)["model"] == "gpt-oss-120b"
    assert call.calls[1].request.headers["authorization"] == "Bearer none"


def _refuses_a_bearer(status_with_bearer: int):
    def answer(request: httpx.Request) -> httpx.Response:
        if "authorization" in request.headers:
            return httpx.Response(status_with_bearer, json={"error": "invalid token"})
        return httpx.Response(200, json={})
    return answer


@respx.mock
async def test_a_keyless_lane_that_refuses_a_bearer_token_is_a_note_for_the_proxy_config():
    """LiteLLM sends a bearer token on every call — `api_key: none` goes out as
    "Bearer none" — and OVHcloud's anonymous lane, VLM Run's and Kilo's refuse
    one while answering a bare call (2026-09-21). The README's curl works and
    the LiteLLM config does not, so the lane stays verified and the run says
    which field keeps it out of that config; the field is then measured every
    run, both ways."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    route = respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=_refuses_a_bearer(403))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == ("keyless call to gpt-oss-120b with a bearer token answered HTTP 403 — "
                             "LiteLLM sends one on every call, so set api.refuses_bearer: true to "
                             "leave the lane out of its config")

    marked = keyless_entry()
    marked.api.refuses_bearer = True
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client, marked, backoff=0)).status is ProbeStatus.PASS

    route.mock(return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, marked, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == ("keyless call to gpt-oss-120b with a bearer token answered HTTP 200 — "
                             "drop api.refuses_bearer, and the LiteLLM config takes the lane back")

    # A rate limit on the second call says nothing about the header either way.
    route.mock(side_effect=_refuses_a_bearer(429))
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client, keyless_entry(), backoff=0)).status is ProbeStatus.PASS


def _answer_by_model(statuses: dict[str, int]):
    def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(statuses[json.loads(request.content)["model"]], json={})
    return answer


@respx.mock
async def test_a_first_id_that_is_rate_limited_while_another_answers_is_a_note_naming_it():
    """opencode's big-pickle answered 429 FreeUsageLimitError to every keyless
    call on 2026-09-16 while ling-3.0-flash-fin-free answered 200 three times out
    of three, and the README's first command was the one that never worked. A
    rate limit does not end the offer, so the row stays verified; it does end the
    command, so the run says which id to put first."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=_answer_by_model({"gpt-oss-120b": 429, "qwen3-coder-30b": 200}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "gpt-oss-120b answered HTTP 429" in result.detail
    assert "put qwen3-coder-30b first" in result.detail
    assert call.call_count == 3 + 1  # the first id asked three times, then the next once


@respx.mock
async def test_the_next_id_is_asked_only_after_the_pause_the_probe_takes_between_tries(monkeypatch):
    """LLM7 serves an anonymous caller one request a second, so an id asked the
    instant the one before it answered is refused for the rate and not for
    itself. On 2026-09-18 its first id answered 404 upstream_not_found, the next
    two answered 429 within the same second, and the run named no id to put
    first while minimax-m2.7 answered 200 two seconds later. The ids after the
    first are spaced by the pause the probe already takes between tries."""
    import freetier_radar.prober as prober
    pauses: list[float] = []

    async def pause(seconds: float) -> None:
        pauses.append(seconds)
    monkeypatch.setattr(prober.asyncio, "sleep", pause)
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=_answer_by_model({"gpt-oss-120b": 404, "qwen3-coder-30b": 200}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=1.5)
    assert result.status is ProbeStatus.STALE_IDS and "put qwen3-coder-30b first" in result.detail
    assert pauses == [1.5]


@respx.mock
async def test_a_first_id_rate_limited_for_a_moment_is_asked_again_before_another_is_named():
    """A 429 is often the moment and not the lane. On 2026-09-17 kilo-auto/free
    answered 429 from its upstream to the runner and 200 from elsewhere within
    the hour, LLM7's GLM-5.3-Flash did the reverse, and each run told a reader to
    reorder the row the other run had just passed. The README's id gets the
    patience a 5xx gets before the check walks on to name another."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=[httpx.Response(429, json={}), httpx.Response(200, json={}),
                     httpx.Response(200, json={})])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    # asked twice bare, then once with the bearer token a proxy sends
    assert [(json.loads(c.request.content)["model"], "authorization" in c.request.headers)
            for c in call.calls] == [("gpt-oss-120b", False)] * 2 + [("gpt-oss-120b", True)]


@respx.mock
async def test_a_rate_limit_that_names_a_long_wait_is_not_asked_again():
    """Asking again inside a window the vendor has named only spends an anonymous
    lane's allowance — OVHcloud gives two requests a minute per IP. A Retry-After
    longer than the pause the check would take is a wait the run does not make."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=[
        httpx.Response(429, headers={"Retry-After": "60"}, json={}), httpx.Response(200, json={})])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS and "put qwen3-coder-30b first" in result.detail
    assert [json.loads(c.request.content)["model"] for c in call.calls] == ["gpt-oss-120b", "qwen3-coder-30b"]


@respx.mock
async def test_a_lane_rate_limited_on_every_id_is_a_note_and_not_a_failure():
    """Every id answering 429 is a lane rate-limited from where the run stands —
    OVHcloud documents two anonymous requests a minute per IP — so it is said
    beside a row that stays verified, never counted towards archiving it."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "rate-limited" in result.detail
    assert "gpt-oss-120b, qwen3-coder-30b" in result.detail
    assert call.call_count == 3 + 1


@respx.mock
async def test_a_refused_first_id_beside_one_that_answers_is_a_note_not_a_failure():
    """A key asked for on one id while another answers keyless is a row that
    lists a metered id first, not a lane that closed."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=_answer_by_model({"gpt-oss-120b": 401, "qwen3-coder-30b": 200}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "put qwen3-coder-30b first" in result.detail


@respx.mock
async def test_a_keyless_lane_that_wants_a_session_header_is_called_with_one():
    """opencode Zen's free ids answer a keyless call only when it carries
    x-opencode-session: 400 MissingSessionID without it, 200 with a UUID of the
    caller's own (measured 2026-09-16). A row that names the header is called
    with a fresh id under this project's own user agent, the way the vendor asks
    any client to call it; without one every run would report a live lane as a
    note."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={}))
    entry = keyless_entry()
    entry.api.session_header = "x-open-session"
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS
    sent = call.calls[0].request
    assert "authorization" not in sent.headers
    uuid.UUID(sent.headers["x-open-session"])


@respx.mock
async def test_a_keyless_lane_that_asks_for_a_key_fails():
    """For a row published as keyless the missing key is the offer — the
    README's zero-signup curl and its "No account at all" answer are built from
    that one field — so a vendor asking for a key is the offer ending, and
    three runs of it archive the row and take the command off the page."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    for status, body in ((401, {"error": "missing api key"}),
                         (403, {"message": "Forbidden: Authentication Failed"})):
        respx.post("https://open.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(status, json=body))
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, keyless_entry(), backoff=0)
        assert result.status is ProbeStatus.FAIL
        assert f"HTTP {status}" in result.detail


def noticed_keyless_entry(since: date) -> Entry:
    data = keyless_entry().model_dump()
    data["api"]["notice"] = {"since": since, "text": "Every client but the vendor's own is refused.",
                             "url": "https://github.com/x/x/issues/1"}
    return Entry.model_validate(data)


@respx.mock
async def test_a_refusal_the_list_has_put_a_notice_on_is_a_note_while_the_notice_holds():
    """opencode Zen began refusing every client but OpenCode on 2026-09-17, and
    OpenCode said nothing. The maintainer chose to wait for its word with a
    notice on the page, and three runs of FAIL would have archived the row on
    the Thursday after — overruling that choice by calendar. So a refusal on a
    lane whose notice still holds is reported beside a row that stays verified
    by its own page, saying which notice holds it and until when."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(
        403, json={"type": "error", "error": {"type": "FreeTierError"}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, noticed_keyless_entry(date(2026, 9, 17)), backoff=0,
                                   today=date(2026, 9, 21))
    assert result.status is ProbeStatus.STALE_IDS
    assert "keyless lane refused" in result.detail and "HTTP 403" in result.detail
    assert "api.notice of 2026-09-17 holds the row until 2026-10-17" in result.detail
    entry = noticed_keyless_entry(date(2026, 9, 17))
    flagged = apply_results([entry], {"keyless": result}, date(2026, 9, 21))
    assert entry.probe_failures == 0 and entry.last_verified == date(2026, 9, 21)
    assert [(x.id, r.status) for x, r in flagged] == [("keyless", ProbeStatus.STALE_IDS)]


@respx.mock
async def test_a_notice_past_its_hold_lets_the_refusal_count_again():
    """A month of silence from a vendor that broke every other client is its
    answer. Past NOTICE_HOLD_DAYS the refusal fails the row as it would have
    without the notice, and the failure says the notice has stopped holding."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(403, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, noticed_keyless_entry(date(2026, 9, 17)), backoff=0,
                                   today=date(2026, 10, 18))
    assert result.status is ProbeStatus.FAIL
    assert "api.notice of 2026-09-17 stopped holding on 2026-10-17" in result.detail


@respx.mock
async def test_a_lane_that_answers_again_under_a_notice_asks_for_the_notice_to_come_down():
    """The notice tells readers the command does not work. The day the lane
    answers again that sentence is the stale thing on the page, so the run says
    so instead of passing quietly beside it."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, noticed_keyless_entry(date(2026, 9, 17)), backoff=0,
                                   today=date(2026, 9, 21))
    assert result.status is ProbeStatus.STALE_IDS
    assert "gpt-oss-120b answered HTTP 200" in result.detail
    assert "take down api.notice of 2026-09-17" in result.detail


@respx.mock
async def test_a_bot_wall_on_the_keyless_call_is_not_a_refusal():
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(
        403, text="<html><title>Just a moment...</title>Enable JavaScript and cookies to continue</html>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE


@respx.mock
async def test_a_keyless_call_refused_for_its_model_id_is_a_note():
    """Any other 4xx is about the request rather than the lane: vLLM answers
    404 for a model id that has rotated out, and uncloseai serves one id at a
    time. The row stays verified and the run says which id to look at."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(
        404, json={"error": {"message": "The model `gpt-oss-120b` does not exist."}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "gpt-oss-120b" in result.detail and "HTTP 404" in result.detail


@respx.mock
async def test_a_keyless_lane_that_cannot_be_checked_is_said_so():
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=httpx.ConnectError("boom"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0, attempts=2)
    assert result.status is ProbeStatus.STALE_IDS
    assert "could not be checked" in result.detail


def follow_entry() -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "indexed",
        "models": [{"family": "qwen3.8-27b"}],
        "probe": {"type": "page-keywords", "endpoint": "https://x.ai/api/doc-index",
                  "keywords": ["200 credits a day"],
                  "follow": {"field": "Data.TargetPrefix", "suffix": "/dist/limits.md"}},
    })


DOC_INDEX = {"Code": 200, "Data": {"TargetPrefix": "https://docs.x.ai/docdata/2026-9-10"}}


@respx.mock
async def test_a_probe_that_follows_an_index_reads_the_page_the_index_names():
    """ModelScope's docs live under a dated release path, and the path of the
    last release keeps answering after the next one ships — a probe pinned to
    it would read an old page for as long as the old page is kept. The index
    names today's path, so the probe reads the page it names and nothing
    else."""
    respx.get("https://x.ai/api/doc-index").mock(return_value=httpx.Response(200, json=DOC_INDEX))
    page = respx.get("https://docs.x.ai/docdata/2026-9-10/dist/limits.md").mock(
        return_value=httpx.Response(200, text="Sign in for 200 credits a day on Qwen3.8-27B."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, follow_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert page.called


@respx.mock
async def test_an_index_that_names_no_page_is_inconclusive():
    """An index that stopped naming the page says where the docs are no more
    than a timeout does: the offer may be exactly where it was."""
    respx.get("https://x.ai/api/doc-index").mock(return_value=httpx.Response(
        200, json={"Code": 200, "Data": {}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, follow_entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE
    assert "Data.TargetPrefix" in result.detail


@respx.mock
async def test_a_page_the_index_names_that_is_gone_fails_as_a_page_would():
    respx.get("https://x.ai/api/doc-index").mock(return_value=httpx.Response(200, json=DOC_INDEX))
    respx.get("https://docs.x.ai/docdata/2026-9-10/dist/limits.md").mock(
        return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, follow_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "page gone" in result.detail and "/dist/limits.md" in result.detail


def public_key_entry(key_url: str = "https://trial.x.ai/docs") -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "trial",
        "models": [{"family": "qwen3.8-27b", "tier": "strong"}],
        "api": {"base_url": "https://api.trial.x.ai/v1", "key_url": key_url,
                "model_ids": ["qwen-27b"], "public_key": "lt-trial-abc"},
        "probe": {"type": "page-keywords", "endpoint": "https://trial.x.ai/docs",
                  "keywords": ["2M tokens per day per address"]},
    })


TRIAL_DOCS = ("<p>Shared trial key <code>lt-trial-abc</code>: 2M tokens per day per address "
              "on Qwen3.8-27B.</p>")


@respx.mock
async def test_a_lane_the_vendor_prints_a_key_for_is_called_with_that_key():
    """LLM Tech prints a shared trial key on its quickstart so that anyone can
    call its lane without an account. A catalog or a page saying so is not the
    lane letting anyone in, so the run calls it the way a reader is told to —
    with that key, one token, on the first id."""
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    call = respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    sent = call.calls.last.request
    assert sent.headers["authorization"] == "Bearer lt-trial-abc"
    assert json.loads(sent.content)["model"] == "qwen-27b"


@respx.mock
async def test_a_public_key_the_lane_refuses_fails_the_row():
    """The key is what makes the row need no account, the way the missing key
    does on a keyless row, so a lane that stops taking it is that offer ending —
    or a key the vendor has replaced, which only a person reading the page can
    copy. Either way the row fails until someone does."""
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(return_value=httpx.Response(
        401, json={"error": {"message": "Invalid API key"}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "public-key lane refused" in result.detail and "HTTP 401" in result.detail


@respx.mock
async def test_a_public_key_the_vendor_no_longer_prints_is_a_note():
    """A key is the vendor's to hand out only while the vendor's page prints it.
    One that still works after the page stopped printing it is a key the vendor
    may revoke any day, or one it has replaced, so the run says so beside a row
    its page keeps verified."""
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(
        200, text="<p>Shared trial key <code>lt-trial-new</code>: 2M tokens per day per address "
                  "on Qwen3.8-27B.</p>"))
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "api.public_key is no longer printed on https://trial.x.ai/docs" in result.detail


@respx.mock
async def test_a_public_key_is_read_back_off_its_own_page_when_the_probe_reads_another():
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    keys = respx.get("https://trial.x.ai/keys").mock(return_value=httpx.Response(
        200, text="<pre>Authorization: Bearer lt-trial-abc</pre>"))
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry("https://trial.x.ai/keys"), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert keys.called


@respx.mock
async def test_a_public_key_whose_page_cannot_be_read_is_said_so():
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    respx.get("https://trial.x.ai/keys").mock(return_value=httpx.Response(503))
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry("https://trial.x.ai/keys"),
                                   backoff=0, attempts=2)
    assert result.status is ProbeStatus.STALE_IDS
    assert "api.public_key could not be checked against https://trial.x.ai/keys" in result.detail


@respx.mock
async def test_a_row_that_needs_a_key_is_never_called_without_one():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0", "completion": "0"}}]}))
    call = respx.post(url__regex=r".*").mock(return_value=httpx.Response(401))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, config_entry("qwen/qwen3-coder:free"), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert not call.called


@respx.mock
async def test_a_row_without_an_anthropic_route_never_posts_anywhere():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder free tier no credit card"))
    route = respx.post(url__regex=r".*").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert not route.called


@respx.mock
async def test_a_keyword_that_lives_only_in_the_page_machinery_no_longer_passes():
    """Groq, 2026-09-08. Its Free Plan Limits table had thirteen rows and no
    Llama in any of them, but llama-3.3-70b-versatile — the id this row anchored
    on — still occurred ten times in the bytes: an OpenAPI enum and a set of
    response samples, every hit inside a <script>. The probe passed, and the
    list went on publishing a model the vendor had stopped giving away.

    An anchor has to die with the offer. A script tag is where an id outlives
    it, so keywords are read against what the page renders."""
    entry = page_entry()
    entry.probe.keywords = ["free plan limits", "llama-3.3-70b-versatile"]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=(
        '<h1>Free Plan Limits</h1><table><tr><td>qwen/qwen3.8-27b</td></tr></table>'
        '<script>{"enum":["llama-3.3-70b-versatile","qwen/qwen3.8-27b"]}</script>'
    )))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "llama-3.3-70b-versatile" in result.detail


@respx.mock
async def test_a_keyword_the_vendor_only_serves_as_page_data_is_declared():
    """Four of the live page rows match only in bytes a reader never sees, and
    each is deliberate — trae's `"name":"free"`, cursor's
    `"name":"hobby","price":"0"`, z.ai's ids glued to their price cells, and
    Upstage's own heading inside a client-rendered payload. Those are still
    evidence; they are just evidence about the page's data rather than its
    prose, and saying so in the registry is the difference between a considered
    anchor and the Groq accident above."""
    entry = page_entry()
    entry.probe.keywords = ["free tier"]
    entry.probe.machinery_keywords = ['"name":"hobby","price":"0"']
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=(
        '<p>Free tier</p><script>{"name":"hobby","price":"0"}</script>'
    )))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_json_ld_is_the_page_speaking_and_stays_readable():
    """Freebuff's offer is in a JSON-LD FAQ block and nowhere else — structured
    data is the vendor answering a question, not the framework's state. It sits
    in a script tag like everything else, so stripping script tags by their name
    would take a real page's only evidence with it."""
    entry = page_entry()
    entry.probe.keywords = ["25 free requests per day"]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=(
        '<p>Pricing</p><script type="application/ld+json">'
        '{"@type":"Question","acceptedAnswer":{"text":"25 free requests per day"}}</script>'
    )))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_missing_keyword_says_whether_the_bytes_had_it_at_all():
    """trae, 2026-09-10: the row failed from CI on `5000 / month` and passed from
    a laptop minutes later, and the failure line said only which keyword was
    missing. Whether the string was absent from the response or merely absent
    from the rendered half is the difference between "the origin served us
    something else" and "our own stripping ate it", and it is the one question
    that cannot be answered afterwards — the runner keeps no copy of the page.

    The byte count rides along for the same reason: a page that answers 200 with
    a shell is a different size, and the size is the only trace left of it."""
    entry = page_entry()
    entry.probe.keywords = ["free tier", "qwen3-coder"]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text=(
        '<p>nothing on offer</p><script>{"model":"qwen3-coder"}</script>'
    )))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert result.detail == ("missing keywords: free tier, "
                             "qwen3-coder (in the page's machinery only) — 63 bytes read")


@respx.mock
async def test_a_row_s_word_on_training_is_read_back_off_its_page():
    """The glyph beside a name says the vendor may train on what a reader
    sends, and it is only as true as the sentence it rests on. So the run reads
    `data_use.url` back for `data_use.quote`, typography flattened the way
    freetier-quotes does, and a sentence that is gone — or a page that cannot be
    read — is a note beside a row that stays verified."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card"))
    privacy = respx.get("https://x.ai/privacy").mock(return_value=httpx.Response(
        200, text="<p>We <b>never</b> train on your prompts’ content.</p>"))
    entry = page_entry()
    entry.data_use = DataUse(trains="no", quote="We never train on your prompts' content",
                             url="https://x.ai/privacy")
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client, entry, backoff=0)).status is ProbeStatus.PASS

    privacy.mock(return_value=httpx.Response(200, text="<p>We may use your content.</p>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == ("data_use quote is no longer on https://x.ai/privacy — read what "
                             "the vendor says now about training on what users send")

    privacy.mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0, attempts=1)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == "data_use could not be checked against https://x.ai/privacy: answered HTTP 404"
