from datetime import date

import httpx
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import apply_results, probe_entry

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
        assert await probe_entry(client, api_entry()) is None


@respx.mock
async def test_api_models_missing_family():
    respx.get("https://api.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder"}]}  # нет :free
    ))
    async with httpx.AsyncClient() as client:
        detail = await probe_entry(client, api_entry())
    assert detail is not None and "qwen3-coder" in detail


@respx.mock
async def test_page_keywords_missing():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(200, text="Free tier for everyone"))
    async with httpx.AsyncClient() as client:
        detail = await probe_entry(client, page_entry())
    assert detail is not None and "no credit card" in detail


@respx.mock
async def test_http_error_is_failure():
    respx.get("https://x.ai/pricing").mock(return_value=httpx.Response(503))
    async with httpx.AsyncClient() as client:
        assert await probe_entry(client, page_entry()) is not None


def test_apply_results():
    entries = [api_entry(), page_entry()]
    failed = apply_results(entries, {"x": None, "pagey": "boom"}, date(2026, 7, 19))
    assert entries[0].last_verified == date(2026, 7, 19)
    assert entries[0].probe_failures == 0
    assert entries[1].probe_failures == 1
    assert entries[1].last_verified == date(2026, 1, 1)
    assert [e.id for e in failed] == ["pagey"]
