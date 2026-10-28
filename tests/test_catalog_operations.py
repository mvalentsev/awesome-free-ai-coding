from datetime import date

import httpx
import pytest
import respx

from freetier_radar.models import Entry
from freetier_radar.prober import ProbeStatus, probe_entry


@pytest.mark.parametrize("field, paths, incompatible", [
    ("supported_endpoints", ["decisions"], True),
    ("supported_endpoints", ["fim.completions", "edit.completions"], True),
    ("endpoints", ["/v1/embeddings"], True),
    ("supported_endpoints", ["chat.completions"], False),
    ("endpoints", ["/v1/chat/completions", "/v1/responses"], False),
    ("supported_endpoints", [], False),
    ("supported_endpoints", None, False),
])
@respx.mock
async def test_chat_config_ids_are_held_to_catalog_operations(field, paths, incompatible):
    # Inception's public catalog distinguishes chat.completions from decisions:
    # https://api.inceptionlabs.ai/v1/models, checked 2026-10-28.
    # A shared signup budget does not make a decision/edit model a chat model.
    entry = Entry.model_validate({
        "id": "wallet", "name": "Wallet", "category": "trial",
        "url": "https://wallet.example", "offering": "A shared signup budget",
        "first_seen": date(2026, 1, 1), "last_verified": date(2026, 1, 1),
        "free_part": "sum", "models": [],
        "api": {"base_url": "https://wallet.example/v1", "model_ids": ["candidate"]},
        "probe": {"type": "page-keywords", "endpoint": "https://wallet.example/pricing",
                  "keywords": ["100 million free tokens"],
                  "catalog": "https://wallet.example/v1/models"},
    })
    respx.get(entry.probe.endpoint).respond(200, text="100 million free tokens on signup")
    catalog = respx.get(entry.probe.catalog).respond(
        200, json={"data": [{"id": "candidate", **({field: paths} if paths is not None else {})}]})
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, attempts=1, backoff=0)
    assert catalog.called
    if incompatible:
        assert result.status is ProbeStatus.STALE_IDS
        assert "candidate" in result.detail
        assert "chat completions" in result.detail
    else:
        assert result.status is ProbeStatus.PASS, result.detail
