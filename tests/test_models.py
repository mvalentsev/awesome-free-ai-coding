from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from freetier_radar.models import Entry, is_anchor, load_registry, save_registry


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


def test_blind_page_probe_is_rejected():
    """Generic words alone outlive the offer — mimo-code kept passing on a
    README that still advertised a channel the client had already cut off."""
    blind = {**sample_entry(), "probe": {"type": "page-keywords",
                                         "endpoint": "https://x.ai/pricing",
                                         "keywords": ["free", "no credit card required"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(blind)

    anchored = {**blind, "probe": {**blind["probe"], "keywords": ["solar-mini", "free"]}}
    assert Entry.model_validate(anchored).probe.keywords[0] == "solar-mini"


@pytest.mark.parametrize("keyword", [
    "mistral-medium",                                   # a model id
    '"name":"free"',                                    # a JSON field of the vendor's own API
    "advanced_model_request_limit",
    '"name":"hobby","price":"0"',                       # the free plan's own price row
    "$0.10, subject to change",                         # the size of the free grant
    "anonymous users get one request every 15 seconds",  # the anonymous quota, in words
    "valid for 90 days after you activate",
    "light quota to code with agents",                  # the plan described in the vendor's words
    "codex are included in your chatgpt free",
])
def test_an_anchor_dies_with_the_offer(keyword):
    assert is_anchor(keyword)


@pytest.mark.parametrize("keyword", [
    "free", "hobby", "no signup", "free quota", "monthly credits",
    "no credit card required",
    "Free-Tier",                       # dressing a generic word up does not anchor it
    '"free"',
    "sign up for free and get started",  # long, and still says nothing
    "get started for free today",
])
def test_page_furniture_is_not_an_anchor(keyword):
    """Every one of these was live in the registry, on a page that would keep
    serving them for months after the free tier was withdrawn — `hobby` and
    `free quota` outlive any offer, and the first version of the rule only
    caught the handful of phrases listed verbatim in GENERIC_KEYWORDS."""
    assert not is_anchor(keyword)


def test_a_weak_anchor_is_rejected_even_when_it_is_not_a_listed_generic():
    weak = {**sample_entry(), "probe": {"type": "page-keywords",
                                        "endpoint": "https://cursor.com/pricing",
                                        "keywords": ["hobby", "no credit card required"]}}
    with pytest.raises(ValidationError):
        Entry.model_validate(weak)

    anchored = {**weak, "probe": {**weak["probe"],
                                  "keywords": ['"name":"hobby","price":"0"', "limited agent requests"]}}
    assert Entry.model_validate(anchored).probe.keywords[1] == "limited agent requests"


def test_zero_price_flag_belongs_to_a_models_api():
    """A pricing page publishes no machine-readable prices, so the flag would sit
    there doing nothing — silent for a check whose job is to catch a price."""
    misplaced = {**sample_entry(), "probe": {"type": "page-keywords",
                                             "endpoint": "https://x.ai/pricing",
                                             "keywords": ["solar-mini", "free"],
                                             "require_zero_price": True}}
    with pytest.raises(ValidationError):
        Entry.model_validate(misplaced)

    on_the_api = {**sample_entry(), "probe": {**sample_entry()["probe"], "require_zero_price": True}}
    assert Entry.model_validate(on_the_api).probe.require_zero_price


def test_registry_roundtrip(tmp_path: Path):
    p = tmp_path / "registry.yaml"
    save_registry(p, [Entry.model_validate(sample_entry())])
    loaded = load_registry(p)
    assert len(loaded) == 1
    assert loaded[0].last_verified == date(2026, 7, 19)
    assert loaded[0].category.value == "api-free-tier"
    assert loaded[0].probe.type.value == "api-models"
