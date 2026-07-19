from datetime import date
from pathlib import Path

from freetier_radar.models import Entry, load_registry, save_registry


def sample_entry() -> dict:
    return {
        "id": "openrouter-free",
        "name": "OpenRouter (free models)",
        "category": "api-free-tier",
        "url": "https://openrouter.ai",
        "source_urls": ["https://openrouter.ai/docs"],
        "card_required": False,
        "offering": "Free variants of frontier models via one API",
        "limits": "50 req/day free",
        "models": [
            {"family": "deepseek", "tier": "frontier", "released": "2025-12"},
            {"family": "qwen3-coder", "tier": "strong", "released": "2025-07"},
        ],
        "probe": {
            "type": "api-models",
            "endpoint": "https://openrouter.ai/api/v1/models",
            "free_marker": ":free",
        },
        "first_seen": date(2026, 7, 19),
        "last_verified": date(2026, 7, 19),
    }


def test_entry_validates():
    e = Entry.model_validate(sample_entry())
    assert e.id == "openrouter-free"
    assert e.probe_failures == 0
    assert e.provisional is False
    assert e.models[0].superseded_by is None


def test_registry_roundtrip(tmp_path: Path):
    p = tmp_path / "registry.yaml"
    save_registry(p, [Entry.model_validate(sample_entry())])
    loaded = load_registry(p)
    assert len(loaded) == 1
    assert loaded[0].last_verified == date(2026, 7, 19)
    assert loaded[0].category.value == "api-free-tier"
    assert loaded[0].probe.type.value == "api-models"
