import json
import uuid
from datetime import date

import httpx
import pytest
import respx

from freetier_radar.models import ApiInfo, DataUse, Entry, ModelFamily, save_registry
from freetier_radar.prober import (
    ProbeResult, ProbeStatus, _amain, apply_results, check_content, family_named, for_a_human,
    free_list_dates, is_model_stale, probe_entry,
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
    """A bare array instead of {"data": [...]} is read as the model list."""
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


FREE_QWEN = {"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0", "completion": "0"}}


@pytest.mark.parametrize("id_field", ["id", "model_id"])
@pytest.mark.parametrize("catalog_limits, detail", [
    ({"context_length": 131042, "top_provider": {"max_completion_tokens": 16384}}, ""),
    ({"context_length": 65536, "top_provider": {"max_completion_tokens": 8192}},
     "context_tokens=65536 (recorded 131042), output_tokens=8192 (recorded 16384)"),
    ({"context_length": 131042}, "output_tokens unavailable"),
    ({"context_length": True, "top_provider": {"max_completion_tokens": "16384"}},
     "context_tokens unavailable, output_tokens unavailable"),
])
@respx.mock
async def test_catalog_rechecks_limits_used_by_generated_clients(catalog_limits, detail, id_field):
    row = zero_price_entry().model_dump()
    row["api"] = {
        "base_url": "https://api.x.ai/v1", "model_ids": [FREE_QWEN["id"]],
        "model_limits": {FREE_QWEN["id"]: {
            "context_tokens": 131042, "output_tokens": 16384,
            "source": row["probe"]["endpoint"],
        }},
    }
    model = {**FREE_QWEN, **catalog_limits}
    model[id_field] = model.pop("id")
    respx.get(row["probe"]["endpoint"]).mock(return_value=httpx.Response(
        200, json={"data": [{"id": []}, model]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, Entry.model_validate(row), backoff=0)
    assert result.status is (ProbeStatus.STALE_IDS if detail else ProbeStatus.PASS)
    if detail:
        assert f"api.model_limits {FREE_QWEN['id']}: {detail}" in result.detail


def two_family_entry() -> Entry:
    e = zero_price_entry()
    e.models = [ModelFamily(family="qwen3-coder"), ModelFamily(family="llama-4")]
    return e


@respx.mock
async def test_a_family_that_left_beside_one_that_stands_flags_the_column_not_the_offer():
    """A lane that still serves one listed family free is alive: the family that
    left is a Models-column flag, not a failure, so one rotating model cannot
    archive the row."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [FREE_QWEN, {"id": "meta/llama-4-70b"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, two_family_entry(), backoff=0)
    assert result == ProbeResult(ProbeStatus.STALE_MODELS, "missing families: llama-4")


@respx.mock
async def test_a_family_that_started_billing_beside_a_free_one_flags_the_column():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [FREE_QWEN, {"id": "meta/llama-4-70b:free",
                                         "pricing": {"prompt": "0.0000001", "completion": "0.0000003"}}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, two_family_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS
    assert result.detail.startswith("no longer free: ") and "llama-4-70b:free" in result.detail


@respx.mock
async def test_a_lane_that_serves_none_of_its_families_still_fails_the_row():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}, {"id": "meta/llama-4-70b"}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, two_family_entry(), backoff=0)
    assert result == ProbeResult(ProbeStatus.FAIL, "missing families: qwen3-coder, llama-4")


@respx.mock
async def test_a_column_flagged_on_a_catalog_still_carries_what_it_says_about_the_ids():
    """The column flag leads and the id check still runs, as on a page row: the
    run that loses a family is the one most likely to have lost its id."""
    entry = two_family_entry()
    entry.api = ApiInfo(base_url="https://api.x.ai/v1",
                        model_ids=["qwen/qwen3-coder:free", "meta/llama-4-70b:free"])
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [FREE_QWEN]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result == ProbeResult(ProbeStatus.STALE_MODELS,
                                 "missing families: llama-4 | api.model_ids the catalog no longer "
                                 "answers for: meta/llama-4-70b:free is not in the catalog")


@respx.mock
async def test_a_family_is_not_kept_alive_by_a_more_specific_familys_id():
    """An id vouches only for the most specific of the row's families that names
    it: coding-glm-5.2-free contains glm-5 too, and must not keep glm-5 alive
    once glm-5's own ids have left."""
    entry = Entry.model_validate({**BASE, "models": [{"family": "glm-5"}, {"family": "glm-5.2"}],
                                  "probe": {"type": "api-models", "require_zero_price": True,
                                            "endpoint": "https://api.x.ai/v1/models"}})
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "coding-glm-5.2-free",
                             "pricing": {"prompt": "0", "completion": "0"}}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result == ProbeResult(ProbeStatus.STALE_MODELS, "missing families: glm-5")


def test_a_repair_is_still_held_to_every_family_it_lists():
    """check_content still fails a listed family the lane no longer serves: the
    scout vets its repair with it, and a reply that keeps the flagged family must
    be refused."""
    catalog = httpx.Response(200, json={"data": [FREE_QWEN]})
    assert check_content(catalog, two_family_entry()) == "missing families: llama-4"


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
    """An aggregator can keep a `:free` id and start charging for it, so a
    published nonzero price fails the id whatever its name says."""
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
    """Routeway wraps each price in the unit it is quoted in; the zero inside the
    wrapper is a published zero, not "publishes no price"."""
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
    """A nonzero price inside a unit wrapper fails the id like a bare one."""
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
    """Requesty ships `pricing` as a list of usage tiers instead of one object; a
    list of zero tiers is a published zero, not "publishes no price"."""
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
    """Every tier is read: free up to a token threshold and metered above it is a
    discount, not a free model."""
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
    """Silence is not a zero: a row listed for its zero price fails when the
    catalog stops publishing one."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "publishes no price" in result.detail


@respx.mock
async def test_one_free_variant_is_enough():
    """One zero-priced id carries the family, though its paid twin sits in the
    same catalog under the same family name."""
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
    """A zero-priced id marked `available: false` (Routeway's field) fails: the
    price stays 0 while nobody can call the lane."""
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
async def test_a_free_id_past_the_retirement_its_own_catalog_dates_is_withdrawn():
    """A retirement date the row publishes, once it has come, withdraws the id even
    at a price of 0: Requesty's `retires` (Unix time, 1789948800 is 2026-09-21)
    and OpenRouter's and Kilo's `expiration_date` day alike."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [
            {"id": "qwen/qwen3-coder:free", "retires": 1789948800,
             "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "qwen/qwen3-coder-next:free", "expiration_date": "2026-09-01",
             "pricing": {"prompt": "0", "completion": "0"}},
        ]}
    ))
    entry = zero_price_entry()
    entry.api = ApiInfo(base_url="https://api.x.ai/v1",
                        model_ids=["qwen/qwen3-coder:free", "qwen/qwen3-coder-next:free"])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "qwen/qwen3-coder:free retired on 2026-09-21" in result.detail
    assert "qwen/qwen3-coder-next:free retired on 2026-09-01" in result.detail


@respx.mock
async def test_a_retirement_date_still_to_come_leaves_the_id_callable():
    """A retirement date still ahead is notice, not a withdrawal: the id answers
    until then (see _retired_on)."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", "retires": 4102444800,
                             "expiration_date": "2099-12-31",
                             "pricing": {"prompt": "0", "completion": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@pytest.mark.parametrize("field,value", [
    ("expiration_date", "2026-10-05"),
    ("retires", 1791216000),  # 2026-10-05 16:00 UTC
    ("expiration_date", "2026-10-05T19:00:00+03:00"),
])
@respx.mock
async def test_retirement_does_not_invent_an_earlier_instant(monkeypatch, field, value):
    from datetime import datetime, timezone
    import freetier_radar.prober as prober

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 5, 15, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(prober, "datetime", Clock)
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", field: value,
                             "pricing": {"prompt": "0", "completion": "0"}}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@pytest.mark.parametrize("field,value", [
    ("expiration_date", "2026-10-04"),
    ("retires", 1791212400),  # 2026-10-05 15:00 UTC
    ("expiration_date", "2026-10-05T18:00:00+03:00"),
])
@respx.mock
async def test_retirement_is_withdrawn_after_the_published_boundary(monkeypatch, field, value):
    from datetime import datetime, timezone
    import freetier_radar.prober as prober

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 5, 15, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(prober, "datetime", Clock)
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", field: value,
                             "pricing": {"prompt": "0", "completion": "0"}}]}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "retired on" in result.detail

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
    """`available: "false"` as a string is a withdrawal too, or a gateway that
    stringifies the flag would never trip the check."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "available": "false",
                             "pricing": {"prompt": "0", "completion": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "marked unavailable" in result.detail


@respx.mock
async def test_an_outdated_marker_is_not_an_availability_verdict():
    """`outdated: true` (Routeway's mark on superseded but callable models) does not
    withdraw an id: a model's age is is_model_stale's question."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/qwen3-coder:free", "available": True,
                             "outdated": True, "pricing": {"prompt": "0", "completion": "0"}}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, zero_price_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_availability_is_checked_without_a_price_requirement():
    """Availability is read without require_zero_price too: every api-models row
    claims its family is callable."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free", "available": False}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "marked unavailable" in result.detail


LANES_URL = "https://api.x.ai/api/v1/ai/recommended-models"


def keyed_lanes(free: list[str], cline_pass: list[str] = (), recommended: list[str] = ()) -> dict:
    """The shape Cline serves at api.cline.bot/api/v1/ai/cline/recommended-models:
    lanes side by side under keys of their own, one object per model, and no price
    or free flag — the lane a model sits in is all it says about cost."""
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
    """Only the named lane counts: a paid lane (ClinePass) lists the same models,
    so a family matched anywhere in the document would outlive its free promotion."""
    respx.get(LANES_URL).mock(return_value=httpx.Response(200, json=keyed_lanes(
        free=["poolside/laguna-s-2.1:free"],
        cline_pass=["cline-pass/deepseek-v4-flash"],
        recommended=["deepseek/deepseek-v4-flash"])))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, lane_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "deepseek-v4-flash" in result.detail


@respx.mock
async def test_an_empty_or_missing_lane_fails_and_says_which_lane():
    """An empty lane (no promotion running) and a missing lane key both fail and
    name the lane, in different words: an ended promotion and a renamed key want
    different repairs."""
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


def client_lane_entry(*model_ids: str) -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "laney",
        "category": "agent-cli",
        "models": [{"family": "deepseek-v4.1-flash", "tier": "strong"}],
        "probe": {"type": "api-models", "endpoint": LANES_URL, "lane": "free"},
        "client_lane": {"model_ids": list(model_ids)},
    })


@respx.mock
async def test_a_client_lane_is_held_to_its_lane_in_both_directions():
    """client_lane.model_ids is checked against the lane as api.model_ids is
    against a catalog: an id that left and one that arrived are notes for a
    human, and ids in the paid lanes beside it are ignored."""
    respx.get(LANES_URL).mock(return_value=httpx.Response(200, json=keyed_lanes(
        free=["cline-free/deepseek-v4.1-flash", "cline-free/gemini-3.8-flash"],
        cline_pass=["cline-pass/glm-5.3"], recommended=["anthropic/claude-opus-5"])))
    entry = client_lane_entry("cline-free/deepseek-v4.1-flash", "cline-free/solar-pro4")
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "cline-free/solar-pro4" in result.detail
    assert "cline-free/gemini-3.8-flash" in result.detail
    assert "glm-5.3" not in result.detail and "claude-opus-5" not in result.detail
    assert result.detail.startswith("client_lane.model_ids ")
    # Addressed to a human, like every note about the ids: the fix prompt leaves it alone.
    assert for_a_human(f"missing families: x | {result.detail}") == result.detail

    entry = client_lane_entry("cline-free/deepseek-v4.1-flash", "cline-free/gemini-3.8-flash")
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


NIM_CATALOG = "https://integrate.api.nvidia.com/v1/models"
NGC_SEARCH = "https://api.ngc.nvidia.com/v2/search/catalog/resources/ENDPOINT?q=free"


def nim_catalog(*ids: str) -> dict:
    """NVIDIA's catalog shape: ids and their owners, with no price and no free flag."""
    return {"object": "list", "data": [
        {"id": i, "object": "model", "created": 735790403, "owned_by": i.split("/")[0]}
        for i in ids]}


def ngc_endpoint(publisher: str, name: str, deprecation: str | None = None,
                 free: bool = True, created: str | None = "2026-08-27T20:40:37.796Z") -> dict:
    """One endpoint as NGC's catalog search answers it: named without its
    publisher, the publisher in a label of its own, the free mark as the label
    value NVIDIA displays as "Free Endpoint", a retirement as a DEPRECATION
    attribute in MM/DD/YYYY, and the moment NVIDIA created it as `dateCreated`."""
    general = ["playgroundtype_chat", "nim_type_run_anywhere"] + (["nim_type_preview"] if free else [])
    attributes = [{"key": "AVAILABLE", "value": "false"}, {"key": "PREVIEW", "value": "true"}]
    if deprecation:
        attributes.append({"key": "DEPRECATION", "value": deprecation})
    endpoint = {"resourceType": "ENDPOINT", "resourceId": f"qc69jvmznzxy/{name}", "name": name,
                "labels": [{"key": "general", "values": ["chat"], "unresolvedValues": general},
                           {"key": "publisher", "values": [publisher],
                            "unresolvedValues": [publisher]}],
                "attributes": attributes}
    if created is not None:
        endpoint.update(dateCreated=created, dateModified=created)
    return endpoint


def ngc_search(*endpoints: dict, pages: int = 1) -> dict:
    return {"resultTotal": len(endpoints), "resultPageTotal": pages,
            "results": [{"groupValue": "_scored", "resources": list(endpoints[:1])},
                        {"groupValue": "ENDPOINT", "resources": list(endpoints[1:])}]}


def nim_entry(**api) -> Entry:
    return Entry.model_validate({
        **BASE,
        "id": "nimmy",
        "models": [{"family": "kimi-k3", "tier": "strong"}],
        "api": {"base_url": "https://integrate.api.nvidia.com/v1",
                "model_ids": ["moonshotai/kimi-k3", "z-ai/glm-5.3"], **api},
        "probe": {"type": "api-models", "endpoint": NIM_CATALOG,
                  "require_zero_price": True, "free_list": NGC_SEARCH},
    })


def mock_nim(catalog: dict, search: dict | httpx.Response) -> None:
    respx.get(NIM_CATALOG).mock(return_value=httpx.Response(200, json=catalog))
    respx.get(NGC_SEARCH).mock(return_value=search if isinstance(search, httpx.Response)
                               else httpx.Response(200, json=search))


@respx.mock
async def test_a_catalog_that_prices_nothing_reads_free_off_the_vendor_s_free_list():
    """A catalog id is free only where the vendor's free list marks it, since
    NVIDIA's catalog also hosts unmarked ids; the list names an endpoint as its
    page URL does, glm-5-3 for z-ai/glm-5.3."""
    mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3", "nvidia/nemotron-nano-3-30b-a3b"),
             ngc_search(ngc_endpoint("moonshotai", "kimi-k3"), ngc_endpoint("z-ai", "glm-5-3")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_family_the_free_list_no_longer_marks_is_no_longer_free():
    """A catalog id the free list no longer marks free fails: the catalog keeps
    the id either way, so the mark is the offer."""
    mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3"),
             ngc_search(ngc_endpoint("moonshotai", "kimi-k3", free=False),
                        ngc_endpoint("z-ai", "glm-5-3")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "no longer free" in result.detail and "moonshotai/kimi-k3" in result.detail


@respx.mock
async def test_the_free_mark_is_read_per_endpoint_and_per_publisher():
    """The free mark belongs to one publisher's endpoint: another lab's model under
    the same name does not carry it to this one."""
    mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3"),
             ngc_search(ngc_endpoint("somelab", "kimi-k3"), ngc_endpoint("z-ai", "glm-5-3")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "moonshotai/kimi-k3" in result.detail


@respx.mock
async def test_a_deprecation_date_takes_an_id_out_before_it_stops_answering():
    """A DEPRECATION date on the free list withdraws the endpoint on the first run
    that sees it, while it still answers: a config id becomes a note, and a Models
    family resting on it fails."""
    mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3"),
             ngc_search(ngc_endpoint("moonshotai", "kimi-k3"),
                        ngc_endpoint("z-ai", "glm-5-3", deprecation="10/06/2026")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "z-ai/glm-5.3 is marked unavailable" in result.detail

    mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3"),
             ngc_search(ngc_endpoint("moonshotai", "kimi-k3", deprecation="10/06/2026"),
                        ngc_endpoint("z-ai", "glm-5-3")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "marked unavailable" in result.detail and "moonshotai/kimi-k3" in result.detail


@respx.mock
async def test_a_free_model_the_row_does_not_list_is_reported_until_it_is_read():
    """An endpoint the free list marks free, the catalog serves and api.model_ids
    lacks is reported on every run until it is added or put in api.ignored_ids;
    one the catalog does not serve (a speech or vision service) is not the row's."""
    catalog = nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3", "deepseek-ai/deepseek-v4.1-flash",
                          "nvidia/nemotron-3-embed-1b")
    search = ngc_search(ngc_endpoint("moonshotai", "kimi-k3"), ngc_endpoint("z-ai", "glm-5-3"),
                        ngc_endpoint("deepseek-ai", "deepseek-v4.1-flash"),
                        ngc_endpoint("nvidia", "nemotron-3-embed-1b"),
                        ngc_endpoint("nvidia", "magpie-tts-zeroshot"))
    mock_nim(catalog, search)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail.startswith("ids the free list marks free that api.model_ids does not list")
    assert "deepseek-ai/deepseek-v4.1-flash" in result.detail
    assert "nvidia/nemotron-3-embed-1b" in result.detail
    assert "magpie" not in result.detail
    # Addressed to a human, like every note about the ids: the fix prompt leaves it alone.
    assert for_a_human(f"no longer free: x | {result.detail}") == result.detail

    read = nim_entry(ignored_ids=["nvidia/nemotron-3-embed-1b"])
    read.api.model_ids.append("deepseek-ai/deepseek-v4.1-flash")
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, read, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_free_list_that_cannot_be_read_leaves_the_offer_unchecked():
    """A free list that is walled, in another shape or runs past the one page read
    is inconclusive and named: read as marking nothing free, it would fail every
    family of a live row."""
    unreadable = [
        httpx.Response(403, text="<html>Access denied</html>"),
        httpx.Response(200, text="<html>maintenance</html>"),
        httpx.Response(200, json={"data": [{"id": "moonshotai/kimi-k3"}]}),
        httpx.Response(200, json=ngc_search(ngc_endpoint("moonshotai", "kimi-k3"),
                                            ngc_endpoint("z-ai", "glm-5-3"), pages=2)),
    ]
    for answer in unreadable:
        mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3"), answer)
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, nim_entry(), backoff=0)
        assert result.status is ProbeStatus.INCONCLUSIVE, answer
        assert "free list" in result.detail and NGC_SEARCH in result.detail


@respx.mock
async def test_a_free_list_that_marks_nothing_free_fails_the_row():
    """A free list in its own shape that marks nothing free is the vendor's word
    that the offer is over, like an empty free lane."""
    mock_nim(nim_catalog("moonshotai/kimi-k3", "z-ai/glm-5.3"),
             {"resultTotal": 0, "resultPageTotal": 0, "results": []})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, nim_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL and "no longer free" in result.detail


def _read(url: str, **body) -> httpx.Response:
    return httpx.Response(200, request=httpx.Request("GET", url), **body)


def test_a_free_list_dates_each_free_id_the_day_the_vendor_created_its_endpoint():
    """A free id's date is the UTC day NVIDIA created its endpoint, which can start
    the two-week bar before the row's first read; an endpoint not marked free, or
    named without a date, gives no date rather than a guess."""
    search = _read(NGC_SEARCH, json=ngc_search(
        ngc_endpoint("z-ai", "glm-5-3", created="2026-09-15T19:47:58.961Z"),
        ngc_endpoint("moonshotai", "kimi-k3", created="2026-08-27T23:40:37.796Z"),
        ngc_endpoint("nvidia", "nemotron-3-embed-1b", created="2026-09-01T08:00:00Z", free=False),
        ngc_endpoint("z-ai", "glm-5-3-flash", created=None)))
    ids = ["z-ai/glm-5.3", "moonshotai/kimi-k3", "nvidia/nemotron-3-embed-1b",
           "z-ai/glm-5.3-flash", "somelab/unlisted"]
    assert free_list_dates(search, ids) == {"z-ai/glm-5.3": date(2026, 9, 15),
                                            "moonshotai/kimi-k3": date(2026, 8, 27)}


def test_a_free_list_that_cannot_be_read_dates_nothing_and_says_why():
    """An empty answer would read as a vendor that dates none of its free ids,
    and the bars would quietly fall back to the row's own dates; a reason lets
    the report say which list it could not read."""
    for answer in (_read(NGC_SEARCH, text="<html>maintenance</html>"),
                   _read(NGC_SEARCH, json={"data": [{"id": "z-ai/glm-5.3"}]}),
                   _read(NGC_SEARCH, json=ngc_search(ngc_endpoint("z-ai", "glm-5-3"), pages=2))):
        said = free_list_dates(answer, ["z-ai/glm-5.3"])
        assert isinstance(said, str) and said, answer


def test_a_newer_family_is_named_only_where_the_rows_own_page_names_it():
    """A generation bump must clear family_named before a human reads it: the
    scout can propose a newer family the row's own page never names."""
    page = _read("https://x.ai/pricing", text="qwen/qwen3.8-27b at 30 RPM. Gemini 3.6 Flash is free.")
    assert family_named(page, page_entry(), "gemini-3.6-flash") is True
    assert family_named(page, page_entry(), "qwen3.7-flash") is False


def test_a_family_served_in_another_lane_or_at_a_price_is_not_named_free():
    """family_named reads only the row's free lane and zero prices: a family the
    catalog serves in a paid lane or at a price is not named free."""
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
    """new-api gateways put the id in `model_name`; read as `id` alone, the whole
    catalog answers "no model ids in response"."""
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
    """A non-breaking or thin space character matches a keyword's plain space."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free\u00a0tier no\u202fcredit\u2009card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_an_entity_in_the_page_source_reads_as_its_character():
    """A page source that writes a space, an apostrophe or an ampersand as an
    entity shows the reader the character, and the keyword quoted from what the
    reader sees still matches — a framework that starts escaping apostrophes does
    not end the offer."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="<p>qwen3-coder free&nbsp;tier, no credit card &amp; it&#39;s free "
                  "for R&amp;D &#x2014; 100&#160;million tokens</p>"))
    entry = page_entry()
    entry.probe.keywords = ["qwen3-coder free tier", "it's free for R&D",
                            "\u2014 100 million tokens"]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS, result.detail


@respx.mock
async def test_a_comment_in_the_page_source_splits_no_sentence():
    """React writes an empty comment on each side of a value it prints into a
    sentence; a reader sees one sentence and so does the keyword quoted from it
    (Experiential Labs' pricing, 2026-09-29). What a comment holds is no more on
    the page than a script is."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="<p>The hosted gateway with <!-- -->500<!-- --> credits a month once you verify "
                  "a card, on qwen3-coder with no credit card</p><!-- free tier ended -->"))
    entry = page_entry()
    entry.probe.keywords = ["500 credits a month once you verify a card"]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS, result.detail

    entry.probe.keywords = ["free tier ended"]
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert result.detail.startswith("missing keywords: free tier ended (in the page's machinery only)")


@respx.mock
async def test_a_keyword_the_page_source_wraps_across_lines_still_matches():
    """Any run of whitespace in the source reads as one space, as a browser renders
    it, for keywords and dead markers alike — the way freetier-quotes reads it."""
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
    """`model_id` is read before `model_name`: AIHubMix puts a spaced-out title in
    `model_name`, where a hyphenated family never matches."""
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
    """A price row that is null or not a number means the vendor stopped
    publishing a price; the other row's zero must not make the id free."""
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
    """Withdrawal wording fails the row even while the page still advertises the
    offer above it."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card. "
                  "Update: the free API service has ended on 2026-07-26."))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "offer withdrawn" in result.detail and "free api service has ended" in result.detail


@respx.mock
async def test_bot_challenge_is_inconclusive_not_a_dead_offer():
    """A bot wall served with HTTP 200 carries none of the keywords; counting it
    as a failure would archive a live service."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="<html><title>Just a moment...</title>"
                  "<body>Enable JavaScript and cookies to continue</body></html>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.INCONCLUSIVE and "bot challenge" in result.detail


@respx.mock
async def test_a_noscript_notice_beside_a_live_offer_still_passes():
    """A page that serves its offer beside a <noscript> JavaScript notice passes:
    the challenge markers are read only once the keywords have failed. (A page
    whose offer is gone and which carries such a notice reads as a wall, and so
    INCONCLUSIVE, until the staleness rule archives it.)"""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="<noscript>Please enable JavaScript to view this site</noscript>"
                  "qwen3-coder on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


def listing_entry() -> Entry:
    """page_entry() with a Models column, for the tests of the family check."""
    e = page_entry()
    e.models = [m.model_copy() for m in api_entry().models]  # qwen3-coder
    return e


@respx.mock
async def test_a_family_the_page_does_not_name_flags_without_failing():
    """A listed family the page does not name flags the Models column while the
    keywords still pass: a note, not a FAIL, so a restyled page cannot archive a
    live service."""
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
    """A family is compared with separators and case removed: vendors write
    "Llama 4" where the registry writes llama-4."""
    entry = listing_entry()
    entry.models.append(entry.models[0].model_copy(update={"family": "llama-4"}))
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder and Llama 4 on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS



@respx.mock
async def test_a_mixture_of_experts_named_without_its_active_parameters_is_evidenced():
    """A page that drops a mixture-of-experts family's active-parameter suffix
    (qwen3.5-122b for qwen3.5-122b-a10b) still names it; a different active count
    (-a6b) is a different model."""
    entry = listing_entry()
    entry.probe.keywords = ["free tier", "no credit card"]
    entry.models = [entry.models[0].model_copy(update={"family": "qwen3.5-122b-a10b"})]
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3.5-122b €1.00 €4.20 Included, no credit card, free tier"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3.5-122b-a6b €1.00 €4.20 Included, no credit card, free tier"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_MODELS

@respx.mock
async def test_a_family_folded_into_a_shared_suffix_is_evidenced():
    """A family's parts may be split by a shared phrase ("Claude Sonnet & Opus 4.6"
    names claude-opus-4.6) as long as they sit close together — see
    test_family_parts_scattered_over_the_page_are_not_evidence."""
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
    """A family's version must not match inside a different version: "Opus 4.5"
    does not name opus-5, or the check would wave through the drift it exists to
    catch."""
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
    """Only the left edge of each part is anchored, so a family followed by a
    period ("MiniMax 2.1.") is still named."""
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
    """A dotted version may carry a letter prefix or drop one: "DeepSeek 3.2" names
    deepseek-v3.2 and "MiniMax M2.1" names minimax-2.1, so a retyped caption does
    not unname live families."""
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
    """The letter prefix is allowed only on a dotted version: on a bare "5" it
    would let markup like `h5` after a "GLM" name glm-5."""
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
    """The family check reads the raw page, script data included, while keywords
    read the rendered text: a family named only in page data is served, and
    whether it is free is the keywords' question."""
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
    """unevidenced_families skips api-models rows: _check_api_models already
    demands every family back from the catalog."""
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}]}
    ))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, api_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


def config_entry(*ids: str, zero_price: bool = True) -> Entry:
    """An api-models entry that also publishes connection ids: `models[]` and
    `api.model_ids` are separate claims about the same catalog."""
    e = api_entry()
    e.api = ApiInfo(base_url="https://api.x.ai/v1", model_ids=list(ids))
    e.probe.require_zero_price = zero_price
    return e


LANE = {"data": [{"id": "qwen/qwen3-coder:free", "pricing": {"prompt": "0", "completion": "0"}}]}


def _lane(*extra: dict) -> dict:
    return {"data": LANE["data"] + list(extra)}


@respx.mock
async def test_a_config_id_the_catalog_dropped_flags_without_failing():
    """An `api.model_ids` id the catalog no longer serves is a STALE_IDS note, not
    a FAIL: the configs would hand out a dead id, but the offer is intact, and
    failures archive the row."""
    entry = config_entry("qwen/qwen3-coder:free", "openai/gpt-oss-20b:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(200, json=_lane()))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "openai/gpt-oss-20b:free" in result.detail
    assert "qwen/qwen3-coder:free" not in result.detail


@respx.mock
async def test_a_reversioned_config_id_is_reported_with_its_successor():
    """A missing id is reported with the catalog id that extends it (a re-dated
    -0731): a rename and a withdrawal want opposite edits."""
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
    """A catalog id built from the same words in another order is named as the
    successor too: a vendor can move the version inside the name."""
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
    """The metered twin of a `:free` id that left is not its successor: it neither
    extends the missing id nor carries the same words."""
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
    """On a require_zero_price row a config id that starts billing is dead: the
    zero is the offer."""
    entry = config_entry("qwen/qwen3-coder:free", "vendor/nowpaid:free")
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/nowpaid:free",
                         "pricing": {"prompt": "0.000001", "completion": "0.000003"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS and "priced" in result.detail


@respx.mock
async def test_a_priced_config_id_is_kept_where_the_lane_is_a_quota():
    """Without require_zero_price (a free tier handed out as a quota over listed
    prices) a priced config id stays: reading the price would empty a healthy
    config."""
    entry = config_entry("vendor/metered", zero_price=False)
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/metered",
                         "pricing": {"prompt": "0.000001", "completion": "0.000003"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_config_ids_are_never_read_off_a_page():
    """A page row's api.model_ids are never checked against its prose, where a
    missing id means nothing."""
    entry = page_entry()
    entry.api = ApiInfo(base_url="https://api.x.ai/v1", model_ids=["some/id-the-page-never-names"])
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder on the free tier, no credit card"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_family_matches_an_id_that_writes_its_dots_as_hyphens():
    """A catalog id is squashed like a page, dots included, so Kenari's
    glm-4-7-flash:free matches the family glm-4.7-flash."""
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
    """A zero token price beside a nonzero per-request or per-second charge is not
    free: Vercel prices speech-to-text by the second of audio, EmpirioLabs some
    models by the message."""
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
    """A catalog's own free flag outranks its prices: Kilo's isFree: false on a
    zero-priced row, Kenari's free: true beside a metered rate."""
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
    """A zero-priced id the catalog carries and api.model_ids lacks is reported,
    so a lane that grows is seen as well as one that shrinks."""
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
    """An unlisted id counts as growth only inside the row's lane: it carries
    free_marker (a zero-priced preview without `:free` is outside), is priced 0
    and is callable."""
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
    """With an empty free_marker (Vercel, Requesty) every zero-priced id is in the
    lane, and the price alone separates it from the metered rows."""
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
    """An id in api.ignored_ids (a zero someone judged and left out, the reason in
    api.note) is not reported, so the report shows only ids nobody has judged."""
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
    """A rename _successor_hint cannot see (a version bumped inside the name) shows
    as a dead id and an unlisted one in the same verdict, so a reviewer reads them
    together."""
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
    """Growth is not read on a row that neither reads prices nor names a lane:
    there a zero is not an offer, and the report would be the whole catalog."""
    entry = config_entry("qwen/qwen3-coder:free", zero_price=False)
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json=_lane({"id": "vendor/another:free",
                         "pricing": {"prompt": "0", "completion": "0"}})))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.PASS


def catalog_entry(*ids: str) -> Entry:
    """A page-keywords entry whose offer lives on a pricing page and whose ids
    live in a keyless catalog at another url (probe.catalog)."""
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
    """A catalog without `data` is read from `models` (Opper answers
    `{"models": [...]}`); read as `data` alone it would look empty."""
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
    """A catalog that does not answer is a STALE_IDS note naming the failure: the
    page still verifies the row, and an id check that silently did not run would
    read as one that passed."""
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
    """A flagged Models column does not end the read: the catalog's note on the ids
    follows it after " | ", since a vendor often drops a family from its page and
    its catalog at once."""
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
    # and so are the Codex route and the border, which only a person can re-read
    for note in ("codex route gone: POST https://x.ai/v1/responses answered HTTP 404",
                 "codex route could not be checked: POST https://x.ai/v1/responses timed out",
                 "border: https://x.ai/terms no longer names Chad — re-read the terms",
                 "border could not be checked against https://x.ai/terms: HTTP 503"):
        assert for_a_human(f"listed families the page does not name: x | {note}") == note, note


@respx.mock
async def test_a_failed_family_still_reports_the_ids_beside_it():
    """A failing api-models row still reports what its catalog says about the ids:
    the catalog is already in hand, and a human is about to edit the row. A page
    row does not — see test_a_dead_offer_outranks_a_catalog_check."""
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
    """_amain returns the number of FAILs, which main() turns into a dry run's exit
    code, so a shell `&&` chain stops on a failing row."""
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
    """STALE_IDS verifies and promotes the row like a PASS and is still flagged:
    the offer was confirmed, and freezing last_verified would archive a live row
    by staleness."""
    e = config_entry("vendor/gone")
    e.provisional = True
    flagged = apply_results([e], {"x": ProbeResult(
        ProbeStatus.STALE_IDS, "api.model_ids the catalog no longer answers for: vendor/gone")},
        date(2026, 7, 19))
    assert e.last_verified == date(2026, 7, 19) and e.probe_failures == 0
    assert e.provisional is False
    assert [(x.id, r.status) for x, r in flagged] == [("x", ProbeStatus.STALE_IDS)]


def test_stale_models_verifies_the_entry_like_a_pass():
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


@respx.mock
async def test_the_pause_before_a_try_grows_with_the_tries_made(monkeypatch):
    """Every call the probe makes waits the same way: nothing before the first
    try, then the backoff times the tries already made — and a 5xx that never
    clears is named in the verdict."""
    import freetier_radar.prober as prober
    pauses: list[float] = []

    async def pause(seconds: float) -> None:
        pauses.append(seconds)
    monkeypatch.setattr(prober.asyncio, "sleep", pause)
    route = respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(503))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, page_entry(), attempts=3, backoff=2)
    assert result.status is ProbeStatus.INCONCLUSIVE
    assert result.detail == "unreachable after 3 attempts: HTTP 503"
    assert route.call_count == 3 and pauses == [2, 4]


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
    """A row past retired_on is already archived: a failing probe is neither
    counted nor flagged, or the scout would repair a probe for a product that is
    gone."""
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
    """A retired or delisted row is not requested at all: no answer could change
    it, and a delisted row's probe may point at a blocklisted service. respx fails
    the test on any route it was not told about."""
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
async def test_the_summary_line_names_what_needs_attention(tmp_path, capsys):
    """The run's log names each flagged row and its reason: failures.json stays on
    the runner, and a probe that fails only from CI cannot be reproduced locally."""
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
    """A run with nothing flagged ends at the count, with no empty list after it."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(
        200, text="qwen3-coder free tier no credit card"))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [page_entry()])

    await _amain(registry, tmp_path / "failures", dry_run=True)

    assert "probed 1 entries, 0 need attention\n" in capsys.readouterr().out


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
    """The Anthropic route is called with the row's first id, and only a row with
    no ids uses a placeholder: a vendor that checks the model before the key
    (Fireworks) answers an unknown model 404, which reads as a route that is gone."""
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
    """A 401 to the keyless POST passes: it shows the route exists, which is all
    this check asks."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    route = respx.post("https://x.ai/anthropic/v1/messages").mock(
        return_value=httpx.Response(401, json={"type": "error", "error": {"type": "authentication_error"}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert route.called


@respx.mock
async def test_an_anthropic_route_that_is_gone_is_a_note_not_a_failure():
    """A gone Anthropic route is a STALE_IDS note, like a dead id: the page still
    evidences the offer, so the row stays verified."""
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://x.ai/anthropic/v1/messages").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "anthropic route gone" in result.detail and "HTTP 404" in result.detail


@respx.mock
async def test_an_anthropic_route_is_asked_again_after_a_5xx():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    route = respx.post("https://x.ai/anthropic/v1/messages").mock(
        side_effect=[httpx.Response(503), httpx.Response(404)])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0)
    assert "anthropic route gone" in result.detail and route.call_count == 2


@respx.mock
async def test_an_anthropic_route_whose_5xx_never_clears_says_which():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    route = respx.post("https://x.ai/anthropic/v1/messages").mock(return_value=httpx.Response(503))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, anthropic_entry(), backoff=0, attempts=2)
    assert result.status is ProbeStatus.STALE_IDS and route.call_count == 2
    assert result.detail == ("anthropic route could not be checked: "
                             "POST https://x.ai/anthropic/v1/messages HTTP 503")


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


def completion(model: str) -> dict:
    """A working lane's whole answer to the one-token call, as vLLM returns it: one
    choice cut at the token limit, reasoning begun and no content yet."""
    return {"id": "chatcmpl-1", "object": "chat.completion", "created": 1790000000,
            "model": model,
            "choices": [{"index": 0, "finish_reason": "length",
                         "message": {"role": "assistant", "content": None, "reasoning": "The"}}],
            "usage": {"prompt_tokens": 53, "completion_tokens": 1, "total_tokens": 54}}


def no_codex_route(base: str = "https://open.x.ai/v1") -> respx.Route:
    """A lane with no Responses route, the usual case: a lane without an account
    that answers a chat call is then asked the request Codex CLI sends (see
    test_codex.py)."""
    return respx.post(f"{base}/responses").mock(return_value=httpx.Response(404))


@respx.mock
async def test_a_keyless_lane_that_answers_is_a_pass():
    """The catalog saying a model exists is not the lane letting anyone call it,
    so a row published as keyless is called, keylessly, on its first id."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("gpt-oss-120b")))
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



@respx.mock
async def test_every_keyless_call_asks_something_no_cache_has_answered_before():
    """Every keyless call sends a new prompt: a caching host (Pollinations' old
    one) would answer a repeated prompt from its cache after its backend died."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("gpt-oss-120b")))
    async with httpx.AsyncClient() as client:
        await probe_entry(client, keyless_entry(), backoff=0)
        await probe_entry(client, keyless_entry(), backoff=0)
    prompts = [json.loads(c.request.content)["messages"][0]["content"] for c in call.calls]
    assert len(prompts) == 4
    assert len(set(prompts)) == len(prompts)
    assert all(json.loads(c.request.content)["max_tokens"] == 1 for c in call.calls)

def _refuses_a_bearer(status_with_bearer: int):
    def answer(request: httpx.Request) -> httpx.Response:
        if "authorization" in request.headers:
            return httpx.Response(status_with_bearer, json={"error": "invalid token"})
        return httpx.Response(200, json=completion(json.loads(request.content)["model"]))
    return answer


@respx.mock
async def test_a_keyless_lane_that_refuses_a_bearer_token_is_a_note_for_the_proxy_config():
    """A keyless lane that answers bare but refuses LiteLLM's "Bearer none" stays
    verified, with a note to set api.refuses_bearer; the field is then re-measured
    every run, both ways."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
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

    route.mock(return_value=httpx.Response(200, json=completion("gpt-oss-120b")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, marked, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail == ("keyless call to gpt-oss-120b with a bearer token answered HTTP 200 — "
                             "drop api.refuses_bearer, and the LiteLLM config takes the lane back")

    # A rate limit on the second call says nothing about the header either way.
    route.mock(side_effect=_refuses_a_bearer(429))
    async with httpx.AsyncClient() as client:
        assert (await probe_entry(client, keyless_entry(), backoff=0)).status is ProbeStatus.PASS


@respx.mock
@pytest.mark.parametrize("control_status,control_body,expected", [
    (200, completion("gpt-oss-120b"), ProbeStatus.STALE_IDS),
    (429, {"error": "rate limited"}, ProbeStatus.PASS),
    (200, {"error": "payment required"}, ProbeStatus.PASS),
    (502, {"error": "upstream unavailable"}, ProbeStatus.PASS),
])
async def test_a_bearer_payment_refusal_needs_a_fresh_bare_completion(
        control_status, control_body, expected):
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    calls = []

    def answer(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if "authorization" in request.headers:
            return httpx.Response(402, json={})
        if len(calls) == 1:
            return httpx.Response(200, json=completion("gpt-oss-120b"))
        return httpx.Response(control_status, json=control_body)

    respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=answer)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is expected
    assert len(calls) == 3
    prompts = [json.loads(call.content)["messages"][0]["content"] for call in calls]
    assert len(set(prompts)) == 3
    if expected is ProbeStatus.STALE_IDS:
        assert "HTTP 402" in result.detail
        assert "api.refuses_bearer: true" in result.detail
    else:
        assert "refuses_bearer" not in result.detail


@respx.mock
async def test_a_2xx_without_a_completion_is_not_the_lane_answering():
    """A gateway can refuse with a 200, so only a completion is an answer: a 200
    without one sends the check on to the next id like any other non-answer."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))

    def first_id_errs(request: httpx.Request) -> httpx.Response:
        model = json.loads(request.content)["model"]
        if model == "gpt-oss-120b":
            return httpx.Response(200, json={"error": {"message": "Free models need a signed-in account"}})
        return httpx.Response(200, json=completion(model))
    route = respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=first_id_errs)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "gpt-oss-120b answered HTTP 200 without a completion" in result.detail
    assert "Free models need a signed-in account" in result.detail
    assert "put qwen3-coder-30b first" in result.detail

    # No id answering with one is a lane that did not answer: said, never passed,
    # and never failed either — a 200 is no key being asked for.
    route.mock(return_value=httpx.Response(200, text="<html><title>Sign in</title></html>"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert result.detail.startswith("keyless call to gpt-oss-120b answered HTTP 200 without a completion")


# HTTP 200 bodies that are not an answer; the lane serves each one on every call.
NOT_A_COMPLETION = [
    # OpenRouter (and Kilo, in its format) sends the 200 before the first token,
    # so a provider error arrives in the body.
    {"error": {"code": 502, "message": "Provider returned error",
               "metadata": {"error_type": "provider_unavailable"}}},
    # An error after the call began sits on the choice, beside any message so far.
    {"choices": [{"message": {"role": "assistant", "content": ""}, "finish_reason": "error",
                  "error": {"code": 502, "message": "Provider disconnected mid-stream",
                            "metadata": {"error_type": "provider_unavailable"}}}]},
    # An error field fails the body however complete the rest of it looks.
    {"id": "gen-1", "object": "chat.completion", "model": "gpt-oss-120b",
     "error": {"code": 429, "message": "Rate limit exceeded",
               "metadata": {"error_type": "rate_limit_exceeded"}},
     "choices": [{"index": 0, "message": {"role": "assistant", "content": ""}, "finish_reason": None}]},
    ["pong"],  # JSON, and not an object at all
    {"object": "chat.completion", "choices": []},  # nothing chosen
    {"object": "chat.completion", "choices": [None]},  # a choice that is not one
    {"object": "chat.completion", "choices": [{"index": 0, "finish_reason": "stop"}]},  # no message
]


@respx.mock
async def test_a_200_is_an_answer_only_as_a_choice_holding_a_message_and_no_error():
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    for body in NOT_A_COMPLETION:
        respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(200, json=body))
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, keyless_entry(), backoff=0)
        assert result.status is ProbeStatus.STALE_IDS, body
        assert "gpt-oss-120b answered HTTP 200 without a completion" in result.detail, body


def keyless_lane(first_id: str) -> tuple[Entry, dict]:
    """keyless_entry with `first_id` first, and the catalog that lists it
    beside the ids that keep the row's gpt-oss family evidenced."""
    entry = keyless_entry()
    entry.api.model_ids = [first_id, "qwen3-coder-30b"]
    return entry, {"data": [{"id": first_id}, *KEYLESS_CATALOG["data"]]}


# (id asked, model the completion names) — every pair a note, and why.
ANSWERED_AS_ANOTHER = [
    ("open/deepseek-v4-flash-0731", "synth-2.5-preview"),  # Lucidity's open/* routes
    ("glm-4.5-air-free", "minimax-m2.5-free"),  # Septor's -free aliases
    ("zai-org/GLM-5.2-FP8", "zai-org/GLM-5.3"),  # Sail's legacy GLM-5.2 id
    ("openai/gpt-oss-120b", "openai/gpt-oss-20b"),  # the smaller sibling under the bigger name
]


@respx.mock
async def test_an_id_answered_as_another_model_is_a_note():
    """An id answered by a model it does not name is a note naming both: the
    README's curl still gets an answer, but from a model the Models column and
    the configs do not list."""
    for asked, served in ANSWERED_AS_ANOTHER:
        entry, catalog = keyless_lane(asked)
        respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=catalog))
        no_codex_route()
        respx.post("https://open.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=completion(served)))
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, entry, backoff=0)
        assert result.status is ProbeStatus.STALE_IDS, (asked, served)
        assert f"keyless call to {asked} answered as {served}" in result.detail

    # The id that answered after the README's did not is read the same way.
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))

    def second_id_swapped(request: httpx.Request) -> httpx.Response:
        if json.loads(request.content)["model"] == "gpt-oss-120b":
            return httpx.Response(404, json={"error": {"message": "model not found"}})
        return httpx.Response(200, json=completion("minimax-m2.5-free"))
    respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=second_id_swapped)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "put qwen3-coder-30b first" in result.detail
    assert "keyless call to qwen3-coder-30b answered as minimax-m2.5-free" in result.detail


# (id asked, model the completion names) — every pair the model asked, and why.
ANSWERED_AS_ITSELF = [
    ("nvidia/Qwen3.8-27B-NVFP4", "qwen38"),  # LLM Tech's served name
    ("qwen/qwen3.8-27b", "Qwen/Qwen3.8-27B"),  # an upper-case spelling
    ("nvidia/nemotron-3-super-120b-a12b:free", "nvidia/nemotron-3-super-120b-a12b"),  # the :free variant tag
    ("deepseek/deepseek-v4-flash", "deepseek/deepseek-v4-flash-0731"),  # a dated revision
    ("codestral-latest", "codestral-2508"),  # an alias for the newest revision, answered under its date
    ("qwen/qwen3.8-flash-free", "qwen3.8-flash-0701"),  # a -free alias names a price, not a model
    ("kilo-auto/free", "inclusionai/ling-3.0-flash-vl:free"),  # Kilo's router
    ("openrouter/free", "nvidia/nemotron-3-super-120b-a12b:free"),  # the router OpenRouter and Kilo list
    ("auto:free", "qwen/qwen3.7-flash:free"),  # BazaarLink's router
]


@respx.mock
async def test_a_model_answering_under_its_own_spelling_or_a_router_s_pick_is_the_model_asked():
    """A vendor's own spelling of the model asked, and a router's pick, are the
    model asked, not another one (each case is named in ANSWERED_AS_ITSELF)."""
    for asked, served in ANSWERED_AS_ITSELF:
        entry, catalog = keyless_lane(asked)
        respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=catalog))
        no_codex_route()
        respx.post("https://open.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=completion(served)))
        async with httpx.AsyncClient() as client:
            result = await probe_entry(client, entry, backoff=0)
        assert result.status is ProbeStatus.PASS, (asked, served, result.detail)


@respx.mock
async def test_a_completion_that_names_no_model_is_taken_at_its_word():
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    unnamed = {k: v for k, v in completion("gpt-oss-120b").items() if k != "model"}
    no_codex_route()
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(200, json=unnamed))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS


@respx.mock
async def test_a_bearer_call_answered_without_a_completion_says_nothing_about_the_header():
    """Taking the bearer token back into the LiteLLM config needs a lane that
    answers with it, and a 200 carrying an error is not that."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))

    def answer(request: httpx.Request) -> httpx.Response:
        if "authorization" in request.headers:
            return httpx.Response(200, json={"error": {"message": "Your authentication token is invalid"}})
        return httpx.Response(200, json=completion(json.loads(request.content)["model"]))
    no_codex_route()
    respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=answer)
    marked = keyless_entry()
    marked.api.refuses_bearer = True
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, marked, backoff=0)
    assert result.status is ProbeStatus.PASS


def _answer_by_model(statuses: dict[str, int]):
    def answer(request: httpx.Request) -> httpx.Response:
        model = json.loads(request.content)["model"]
        status = statuses[model]
        return httpx.Response(status, json=completion(model) if status < 300 else {})
    return answer


@respx.mock
async def test_a_first_id_that_is_rate_limited_while_another_answers_is_a_note_naming_it():
    """A first id rate-limited while a later one answers is a note naming the id
    to put first: a rate limit does not end the offer, but it breaks the README's
    command."""
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
    """The ids after the first wait the probe's pause between tries: a lane that
    serves one anonymous request a second (LLM7) would refuse the next id for the
    rate, not for itself."""
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
async def test_a_keyless_call_is_asked_again_after_a_5xx():
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json=completion("gpt-oss-120b")),
                     httpx.Response(200, json=completion("gpt-oss-120b"))])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert [(json.loads(c.request.content)["model"], "authorization" in c.request.headers)
            for c in call.calls] == [("gpt-oss-120b", False)] * 2 + [("gpt-oss-120b", True)]


OVERLOADED = {"id": "gen-1", "error": {"code": 503, "message": "Upstream error from Nvidia: Service "
                                                               "temporarily overloaded"}}


@respx.mock
async def test_a_5xx_a_200_carries_in_its_body_is_asked_again_like_any_5xx():
    """OpenRouter's format, which Kilo answers in, sends the status line before
    the first token, so an upstream's 503 arrives inside a 200 (Kilo's
    kilo-auto/free, 2026-09-29): asked again as a 503 would be, and named in
    full if it never clears."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=[httpx.Response(200, json=OVERLOADED), httpx.Response(200, json=completion("gpt-oss-120b")),
                     httpx.Response(200, json=completion("gpt-oss-120b"))])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS, result.detail
    assert [json.loads(c.request.content)["model"] for c in call.calls] == ["gpt-oss-120b"] * 3


@respx.mock
async def test_a_4xx_a_200_carries_in_its_body_is_an_answer():
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=[
        httpx.Response(200, json={"error": {"code": 400, "message": "No such model"}}),
        httpx.Response(200, json=completion("qwen3-coder-30b"))])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert "put qwen3-coder-30b first" in result.detail
    assert [json.loads(c.request.content)["model"] for c in call.calls] == ["gpt-oss-120b", "qwen3-coder-30b"]


@respx.mock
async def test_a_network_error_with_no_message_is_named_by_its_kind():
    """httpx raises a read timeout with an empty message; the note names the
    timeout rather than ending on a colon (VLM Run's 27B, cold for 109 s,
    2026-09-29)."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()

    def answer(request: httpx.Request) -> httpx.Response:
        model = json.loads(request.content)["model"]
        if model == "gpt-oss-120b":
            raise httpx.ReadTimeout("")
        return httpx.Response(200, json=completion(model))
    respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=answer)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0, attempts=2)
    assert "keyless call to gpt-oss-120b answered network error: ReadTimeout while" in result.detail


@respx.mock
async def test_a_first_id_rate_limited_for_a_moment_is_asked_again_before_another_is_named():
    """The README's id is asked again after a 429, as after a 5xx, before another
    id is named: a momentary rate limit would otherwise reorder the row from run
    to run."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        side_effect=[httpx.Response(429, json={}), httpx.Response(200, json=completion("gpt-oss-120b")),
                     httpx.Response(200, json=completion("gpt-oss-120b"))])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    # asked twice bare, then once with the bearer token a proxy sends
    assert [(json.loads(c.request.content)["model"], "authorization" in c.request.headers)
            for c in call.calls] == [("gpt-oss-120b", False)] * 2 + [("gpt-oss-120b", True)]


@respx.mock
async def test_a_rate_limit_that_names_a_long_wait_is_not_asked_again():
    """A Retry-After longer than the probe's pause is not waited out: asking again
    inside it only spends an anonymous lane's allowance (two a minute per IP on
    OVHcloud)."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(side_effect=[
        httpx.Response(429, headers={"Retry-After": "60"}, json={}),
        httpx.Response(200, json=completion("qwen3-coder-30b"))])
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, keyless_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS and "put qwen3-coder-30b first" in result.detail
    assert [json.loads(c.request.content)["model"] for c in call.calls] == ["gpt-oss-120b", "qwen3-coder-30b"]


@respx.mock
async def test_a_lane_rate_limited_on_every_id_is_a_note_and_not_a_failure():
    """Every id answering 429 is a lane rate-limited from where the run stands: a
    note on a row that stays verified, never a failure towards archiving it."""
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
async def test_a_keyless_note_rides_with_every_other_note_the_read_finds():
    """A keyless lane's note is not dropped when another part of the read has a
    note of its own — here a gone Anthropic route: the verdict carries both."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(429, json={}))
    respx.post("https://open.x.ai/anthropic/v1/messages").mock(return_value=httpx.Response(404))
    entry = keyless_entry()
    entry.api.anthropic_base_url = "https://open.x.ai/anthropic"
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "anthropic route gone" in result.detail and "rate-limited" in result.detail


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
    """A row that names api.session_header is called with a fresh UUID in it."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    call = respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("gpt-oss-120b")))
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
    """A 401 or 403 with no id answering fails a keyless row: for such a row the
    missing key is the offer, and the README's zero-signup curl is built on it."""
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
    """While api.notice holds, a refusal is a note naming the notice and its end,
    and the row stays verified: the maintainer chose to wait for the vendor's
    word, and three FAILs would overrule that by calendar."""
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
    """Past NOTICE_HOLD_DAYS the refusal fails the row as it would without the
    notice, and says the notice has stopped holding."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(return_value=httpx.Response(403, json={}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, noticed_keyless_entry(date(2026, 9, 17)), backoff=0,
                                   today=date(2026, 10, 18))
    assert result.status is ProbeStatus.FAIL
    assert "api.notice of 2026-09-17 stopped holding on 2026-10-17" in result.detail


@respx.mock
async def test_a_lane_that_answers_again_under_a_notice_asks_for_the_notice_to_come_down():
    """A lane that answers again while its notice stands is a note to take the
    notice down: the notice tells readers the command does not work."""
    respx.get("https://open.x.ai/v1/models").mock(return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    no_codex_route()
    respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("gpt-oss-120b")))
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
    """A 4xx that is neither a refusal nor a rate limit is about the request, not
    the lane (vLLM answers 404 for an id that rotated out): a note naming the id."""
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
    """A probe with `follow` reads the page its index names: ModelScope's docs live
    under a dated release path, and an old release's path keeps answering."""
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
    """A lane the vendor prints a shared key for is called the way a reader is
    told to: with that key as a bearer token, one token, on the first id. The
    key's page is the page the probe reads, so it is read once."""
    docs = respx.get("https://trial.x.ai/docs").mock(
        return_value=httpx.Response(200, text=TRIAL_DOCS))
    no_codex_route("https://api.trial.x.ai/v1")
    call = respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("qwen-27b")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert docs.call_count == 1
    sent = call.calls.last.request
    assert sent.headers["authorization"] == "Bearer lt-trial-abc"
    assert json.loads(sent.content)["model"] == "qwen-27b"


@respx.mock
async def test_a_public_key_the_lane_refuses_fails_the_row():
    """A lane that refuses the printed key fails the row, as a keyless refusal
    does: the offer ended, or the key was replaced and a person must copy the new
    one."""
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(return_value=httpx.Response(
        401, json={"error": {"message": "Invalid API key"}}))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry(), backoff=0)
    assert result.status is ProbeStatus.FAIL
    assert "public-key lane refused" in result.detail and "HTTP 401" in result.detail


@respx.mock
async def test_a_public_key_the_vendor_no_longer_prints_is_a_note():
    """A key that still works after the vendor's page stopped printing it is a
    note: the vendor may revoke it, or has replaced it."""
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(
        200, text="<p>Shared trial key <code>lt-trial-new</code>: 2M tokens per day per address "
                  "on Qwen3.8-27B.</p>"))
    no_codex_route("https://api.trial.x.ai/v1")
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("qwen-27b")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "api.public_key is no longer printed on https://trial.x.ai/docs" in result.detail


@respx.mock
async def test_a_public_key_is_read_back_off_its_own_page_when_the_probe_reads_another():
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    keys = respx.get("https://trial.x.ai/keys").mock(return_value=httpx.Response(
        200, text="<pre>Authorization: Bearer lt-trial-abc</pre>"))
    no_codex_route("https://api.trial.x.ai/v1")
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("qwen-27b")))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, public_key_entry("https://trial.x.ai/keys"), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert keys.called


@respx.mock
async def test_a_public_key_whose_page_cannot_be_read_is_said_so():
    respx.get("https://trial.x.ai/docs").mock(return_value=httpx.Response(200, text=TRIAL_DOCS))
    respx.get("https://trial.x.ai/keys").mock(return_value=httpx.Response(503))
    no_codex_route("https://api.trial.x.ai/v1")
    respx.post("https://api.trial.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("qwen-27b")))
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
    """Keywords are read against the rendered page: an id inside a <script> (an
    OpenAPI enum, a response sample) outlives the offer it anchored."""
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
    """A keyword deliberately read in the page's data rather than its prose is
    declared in probe.machinery_keywords and matched against the raw bytes."""
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
    """JSON-LD survives the script stripping: structured data is the vendor
    answering a question, and a page can carry part of its evidence nowhere else
    (Freebuff's FAQ answers)."""
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
    """A missing keyword says whether the raw bytes carried it, and the failure
    gives the page's size: the runner keeps no copy of the page, and these tell a
    served shell from our own stripping."""
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
    """`data_use.quote` is read back off `data_use.url`, typography flattened as
    freetier-quotes does; a quote that is gone, or a page that cannot be read, is
    a note on a row that stays verified."""
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
