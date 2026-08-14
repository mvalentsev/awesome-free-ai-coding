from datetime import date, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

import yaml

from freetier_radar.models import (SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Entry, Watched,
                                    is_anchor, is_source_current, known_domains, load_registry,
                                    load_sources, load_watchlist, save_registry, watch_match)


def save_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


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


def watched(**kw) -> dict:
    return {"domains": ["example.ai"], "name": "Example",
            "checked_on": "2026-08-01", "reason": "no free tier today",
            "reopen_if": "they publish one", **kw}


def test_a_watch_verdict_covers_subdomains_and_every_spelling(tmp_path: Path):
    path = tmp_path / "watchlist.yaml"
    save_yaml(path, {"watched": [watched(domains=["modelscope.cn", "modelscope.ai"])]})
    wl = load_watchlist(path)
    today = date(2026, 8, 14)
    assert watch_match("api-inference.modelscope.cn", wl, today) is not None
    assert watch_match("modelscope.ai", wl, today) is not None
    assert watch_match("modelscope.com", wl, today) is None


def test_a_watch_verdict_expires_instead_of_burying_the_service(tmp_path: Path):
    """The whole difference between this file and blocklist.yaml. A verdict that
    kept suppressing forever would be a blocklist entry with softer wording."""
    path = tmp_path / "watchlist.yaml"
    save_yaml(path, {"watched": [watched(checked_on="2026-05-01")]})
    wl = load_watchlist(path)
    last_day = date(2026, 5, 1) + timedelta(days=WATCH_RECHECK_DAYS)
    assert watch_match("example.ai", wl, last_day) is not None
    assert watch_match("example.ai", wl, last_day + timedelta(days=1)) is None


def test_a_missing_watchlist_is_an_empty_one(tmp_path: Path):
    assert load_watchlist(tmp_path / "nope.yaml") == []


def test_a_watch_entry_needs_a_domain():
    with pytest.raises(ValidationError):
        Watched.model_validate(watched(domains=[]))


def read_source(**kw) -> dict:
    return {"url": "https://github.com/someone/a-list", "name": "someone/a-list",
            "checked_on": "2026-08-01", "reason": "carries no provider-level data",
            "reopen_if": "it starts publishing endpoints", **kw}


def test_a_source_verdict_expires_so_a_list_gets_re_read(tmp_path: Path):
    """watchlist.yaml's clock, one level up. A list that carried nothing in
    August can be carrying a provider by February, and nobody re-opens a file
    of verdicts on their own."""
    path = tmp_path / "sources.yaml"
    save_yaml(path, {"read": [read_source(checked_on="2026-05-01")]})
    (source,) = load_sources(path)
    last_day = date(2026, 5, 1) + timedelta(days=SOURCE_RECHECK_DAYS)
    assert is_source_current(source, last_day)
    assert not is_source_current(source, last_day + timedelta(days=1))


def test_a_source_is_read_less_often_than_an_offer_is_rechecked():
    """Different subject, different clock: a vendor can open a free tier any
    week, but a directory rarely changes what kind of directory it is."""
    assert SOURCE_RECHECK_DAYS > WATCH_RECHECK_DAYS


def test_a_missing_sources_file_is_an_empty_one(tmp_path: Path):
    assert load_sources(tmp_path / "nope.yaml") == []


def test_known_domains_covers_where_an_entry_is_actually_reached():
    """NVIDIA is the case that made this a function. The registry reaches it at
    build.nvidia.com while models.dev lists integrate.api.nvidia.com, and a
    known-domain set built from the url alone reported our own entry as a new
    lead. An entry is known at every host it publishes."""
    e = Entry.model_validate({
        **sample_entry(),
        "url": "https://build.nvidia.com",
        "source_urls": ["https://docs.api.nvidia.com/nim/"],
        "api": {"base_url": "https://integrate.api.nvidia.com/v1", "auth": "api-key"},
    })
    assert known_domains([e]) == {
        "build.nvidia.com", "docs.api.nvidia.com", "integrate.api.nvidia.com",
    }


def test_known_domains_of_an_entry_without_an_api_block():
    e = Entry.model_validate(sample_entry())
    assert known_domains([e]) == {"openrouter.ai"}
