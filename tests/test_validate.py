"""Every rule here is a contradiction a human can hold in two files without
noticing. Each was found by hand at least once before it was written down."""
from datetime import date, timedelta
from pathlib import Path

import yaml

from freetier_radar.validate import check

TODAY = date(2026, 8, 14)

ENTRY = {
    "id": "x", "name": "X", "category": "api-free-tier", "url": "https://x.ai",
    "offering": "stuff", "first_seen": "2026-01-01", "last_verified": "2026-08-14",
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai",
              "keywords": ["x-mini-2", "free"]},
    "models": [{"family": "x-mini"}],
}

WATCHED = {"domains": ["watched.ai"], "name": "Watched Co", "checked_on": "2026-08-01",
           "reason": "nothing free today", "reopen_if": "a free lane appears"}


def build(tmp_path: Path, *, entries=None, blocklist=None, watched=None, dismissed=None) -> Path:
    (tmp_path / "registry.yaml").write_text(
        yaml.safe_dump({"entries": entries if entries is not None else [ENTRY]}), encoding="utf-8")
    (tmp_path / "blocklist.yaml").write_text(yaml.safe_dump(blocklist or []), encoding="utf-8")
    (tmp_path / "watchlist.yaml").write_text(
        yaml.safe_dump({"watched": watched or []}), encoding="utf-8")
    (tmp_path / "dismissed.yaml").write_text(
        yaml.safe_dump({"dismissed": dismissed or []}), encoding="utf-8")
    return tmp_path


def test_a_consistent_repository_reports_nothing(tmp_path: Path):
    assert check(build(tmp_path, watched=[WATCHED]), TODAY) == []


def test_a_listed_entry_may_not_sit_on_a_blocklisted_domain(tmp_path: Path):
    root = build(tmp_path, blocklist=[{"domain": "x.ai", "reason": "rejected"}])
    assert any("blocklisted domain" in p for p in check(root, TODAY))


def test_a_live_entry_may_not_also_be_watched_as_having_no_free_tier(tmp_path: Path):
    root = build(tmp_path, watched=[{**WATCHED, "domains": ["x.ai"]}])
    assert any("is also on the watchlist" in p for p in check(root, TODAY))


def test_an_archived_entry_may_be_watched(tmp_path: Path):
    """Burying a row and then recording why its offer is gone is the intended
    sequence, not a contradiction."""
    dead = {**ENTRY, "retired_on": "2026-06-01"}
    root = build(tmp_path, entries=[dead], watched=[{**WATCHED, "domains": ["x.ai"]}])
    assert check(root, TODAY) == []


def test_a_domain_gets_one_verdict_not_two(tmp_path: Path):
    root = build(tmp_path, blocklist=[{"domain": "watched.ai", "reason": "rejected"}],
                 watched=[WATCHED])
    assert any("a domain gets one verdict" in p for p in check(root, TODAY))


def test_a_watch_verdict_needs_a_way_back(tmp_path: Path):
    root = build(tmp_path, watched=[{**WATCHED, "reopen_if": ""}])
    assert any("no reopen_if" in p for p in check(root, TODAY))


def test_dates_may_not_run_ahead_of_today(tmp_path: Path):
    ahead = (TODAY + timedelta(days=1)).isoformat()
    root = build(tmp_path, entries=[{**ENTRY, "last_verified": ahead}],
                 watched=[{**WATCHED, "checked_on": ahead}])
    problems = check(root, TODAY)
    assert any("last_verified" in p and "future" in p for p in problems)
    assert any("checked_on" in p and "future" in p for p in problems)


def test_duplicate_ids_urls_and_base_urls_are_caught(tmp_path: Path):
    twin = {**ENTRY, "id": "y", "api": {"base_url": "https://api.x.ai/v1"}}
    root = build(tmp_path, entries=[{**ENTRY, "api": {"base_url": "https://api.x.ai/v1"}}, twin])
    problems = check(root, TODAY)
    assert any("duplicate url" in p for p in problems)
    assert any("duplicate api.base_url" in p for p in problems)


def test_a_dismissal_that_matches_nothing_is_dead_weight(tmp_path: Path):
    root = build(tmp_path, dismissed=[
        {"entry": "ghost", "family": "a", "superseded_by": "b"},
        {"entry": "x", "family": "not-a-family", "superseded_by": "b"},
    ])
    problems = check(root, TODAY)
    assert any("ghost is not an entry id" in p for p in problems)
    assert any("has no family" in p for p in problems)


def test_a_pipe_would_break_the_readme_table(tmp_path: Path):
    root = build(tmp_path, watched=[{**WATCHED, "reason": "free | not free"}])
    assert any("has a pipe in reason" in p for p in check(root, TODAY))
