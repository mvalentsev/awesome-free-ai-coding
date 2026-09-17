"""Every rule here is a contradiction a human can hold in two files without
noticing. Each was found by hand at least once before it was written down."""
import json
from datetime import date, timedelta
from pathlib import Path

import yaml

from freetier_radar.discovery import CURATED_FEEDS
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


def event(**kw) -> dict:
    return {"ts": "2026-08-10T05:23:00Z", "event": "added", "id": "x", "name": "X", **kw}


SOURCE = {"url": "https://github.com/someone/a-list", "name": "someone/a-list",
          "checked_on": "2026-08-01", "reason": "carries no provider-level data",
          "reopen_if": "it starts publishing endpoints"}


def build(tmp_path: Path, *, entries=None, blocklist=None, watched=None, dismissed=None,
          history=None, sources=None) -> Path:
    (tmp_path / "registry.yaml").write_text(
        yaml.safe_dump({"entries": entries if entries is not None else [ENTRY]}), encoding="utf-8")
    (tmp_path / "blocklist.yaml").write_text(yaml.safe_dump(blocklist or []), encoding="utf-8")
    (tmp_path / "watchlist.yaml").write_text(
        yaml.safe_dump({"watched": watched or []}), encoding="utf-8")
    (tmp_path / "dismissed.yaml").write_text(
        yaml.safe_dump({"dismissed": dismissed or []}), encoding="utf-8")
    (tmp_path / "sources.yaml").write_text(
        yaml.safe_dump({"read": sources or []}), encoding="utf-8")
    if history is not None:
        (tmp_path / "history.jsonl").write_text(
            "".join(json.dumps(e) + "\n" for e in history), encoding="utf-8")
    return tmp_path


def test_a_consistent_repository_reports_nothing(tmp_path: Path):
    assert check(build(tmp_path, watched=[WATCHED]), TODAY) == []


def test_a_rows_prose_stays_a_readers_length(tmp_path: Path):
    """The median `limits` went from 87 characters in July to 813 by 2026-09-16,
    the longest 3,712 — a research log in a README cell. The history belongs to
    history.jsonl; the row keeps what a reader needs to use the offer."""
    from freetier_radar.validate import PROSE_LIMITS
    long = {**ENTRY, "limits": "x" * (PROSE_LIMITS["limits"] + 1),
            "offering": "y" * PROSE_LIMITS["offering"]}
    problems = check(build(tmp_path, entries=[long]), TODAY)
    assert [p for p in problems if "characters" in p] == [
        f"registry: x limits is {PROSE_LIMITS['limits'] + 1} characters, over {PROSE_LIMITS['limits']} — "
        "keep what a reader needs to use the offer, and leave its history to history.jsonl"]


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
                 watched=[{**WATCHED, "checked_on": ahead}],
                 sources=[{**SOURCE, "checked_on": ahead}])
    problems = check(root, TODAY)
    assert any("last_verified" in p and "future" in p for p in problems)
    assert any("watchlist" in p and "checked_on" in p and "future" in p for p in problems)
    assert any("sources" in p and "checked_on" in p and "future" in p for p in problems)


def test_duplicate_ids_urls_and_base_urls_are_caught(tmp_path: Path):
    twin = {**ENTRY, "id": "y", "api": {"base_url": "https://api.x.ai/v1"}}
    root = build(tmp_path, entries=[{**ENTRY, "api": {"base_url": "https://api.x.ai/v1"}}, twin])
    problems = check(root, TODAY)
    assert any("duplicate url" in p for p in problems)
    assert any("duplicate api.base_url" in p for p in problems)


def test_one_family_carries_one_tier(tmp_path: Path):
    """The scout assigns a tier per proposal, so the same model arrived frontier
    on one vendor and strong on the next — a judgement about the model recorded
    as a judgement about the vendor."""
    measured = {"family": "nemotron-3-ultra", "aa_model": "nvidia-nemotron-3-ultra-550b-a55b"}
    root = build(tmp_path, entries=[
        {**ENTRY, "models": [{**measured, "tier": "frontier"}]},
        {**ENTRY, "id": "y", "url": "https://y.ai", "models": [{**measured, "tier": "strong"}]},
        {**ENTRY, "id": "z", "url": "https://z.ai", "models": [measured]},
    ])
    problems = check(root, TODAY)
    assert any("is frontier on x and strong on y — a family carries one tier" in p for p in problems)
    assert any("is frontier on x and no tier on z — a family carries one tier" in p for p in problems)

    agreeing = build(tmp_path, entries=[
        {**ENTRY, "models": [{**measured, "tier": "frontier"}]},
        {**ENTRY, "id": "y", "url": "https://y.ai", "models": [{**measured, "tier": "frontier"}]},
    ])
    assert check(agreeing, TODAY) == []


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


# ---- sources.yaml against discovery.py ------------------------------------

def test_a_source_may_not_be_declined_and_still_read_every_run(tmp_path: Path):
    """The contradiction this file exists to catch. CURATED_FEEDS is a raw
    githubusercontent URL and a human writes down the github.com one they were
    actually sent, so a plain string compare would never notice."""
    feed = CURATED_FEEDS[0]
    owner_repo = "/".join(feed.split("/")[3:5])
    root = build(tmp_path, sources=[{**SOURCE, "url": f"https://github.com/{owner_repo}"}])
    assert any("is also read every run" in p for p in check(root, TODAY))


def test_a_source_verdict_needs_a_way_back(tmp_path: Path):
    root = build(tmp_path, sources=[{**SOURCE, "reopen_if": ""}])
    assert any("no reopen_if" in p for p in check(root, TODAY))


def test_the_same_source_may_not_be_read_and_declined_twice(tmp_path: Path):
    root = build(tmp_path, sources=[SOURCE, {**SOURCE, "checked_on": "2026-08-10"}])
    assert any("duplicate source" in p for p in check(root, TODAY))


def test_a_missing_sources_file_is_not_a_problem(tmp_path: Path):
    root = build(tmp_path, watched=[WATCHED])
    (root / "sources.yaml").unlink()
    assert check(root, TODAY) == []


# ---- history.jsonl — the one file here that cannot be regenerated ----------

def test_a_repository_with_a_history_reports_nothing(tmp_path: Path):
    root = build(tmp_path, watched=[WATCHED], history=[event()])
    assert check(root, TODAY) == []


def test_a_history_event_may_not_be_dated_in_the_future(tmp_path: Path):
    ahead = (TODAY + timedelta(days=1)).isoformat() + "T00:00:00Z"
    root = build(tmp_path, history=[event(ts=ahead)])
    assert any("history" in p and "future" in p for p in check(root, TODAY))


def test_history_events_must_be_in_the_order_they_happened(tmp_path: Path):
    """An append-only log read back out of order means someone edited it by hand
    or a merge interleaved two runs — either way the replay it feeds is wrong."""
    root = build(tmp_path, history=[event(ts="2026-08-10T05:23:00Z"),
                                    event(id="y", name="Y", ts="2026-08-09T05:23:00Z")])
    assert any("out of order" in p for p in check(root, TODAY))


def test_removing_something_the_history_never_recorded_is_a_contradiction(tmp_path: Path):
    root = build(tmp_path, history=[event(event="removed", id="ghost", name="Ghost")])
    assert any("removed" in p and "ghost" in p for p in check(root, TODAY))


def test_adding_something_the_history_already_has_is_a_contradiction(tmp_path: Path):
    root = build(tmp_path, history=[event(), event(ts="2026-08-11T05:23:00Z")])
    assert any("added" in p and "already" in p for p in check(root, TODAY))


def test_a_row_the_history_recorded_may_not_be_deleted_from_the_registry(tmp_path: Path):
    """Twelve rows left the list by deletion before 2026-09-17 — Cerebras,
    Novita, LongCat, Kenari among them — and none of them reached the Archive;
    the page kept only a "Delisted" line with nothing after it. A row leaves
    through the Archive, so a registry missing a row the history knows is refused."""
    root = build(tmp_path, history=[event(), event(id="gone", name="Gone")])
    assert ("registry: gone is in history.jsonl and missing from registry.yaml — a row leaves "
            "the list through the Archive: give it `delisted` (or `retired_on`) instead of "
            "deleting it") in check(root, TODAY)


def test_an_archived_row_may_sit_on_a_blocklisted_domain(tmp_path: Path):
    """Taking a row off the list and then rejecting its service for cause is the
    intended sequence — Kenari's — and the row is the record of what was listed."""
    kept = {**ENTRY, "delisted": {"on": "2026-08-10", "reason": "rejected for cause"}}
    root = build(tmp_path, entries=[kept], blocklist=[{"domain": "x.ai", "reason": "rejected"}])
    assert check(root, TODAY) == []


def test_a_delisting_is_dated_between_the_rows_arrival_and_today(tmp_path: Path):
    ahead = {**ENTRY, "delisted": {"on": "2026-08-15", "reason": "taken off"}}
    before = {**ENTRY, "id": "y", "url": "https://y.ai",
              "delisted": {"on": "2025-12-31", "reason": "taken off"}}
    problems = check(build(tmp_path, entries=[ahead, before]), TODAY)
    assert "registry: x delisted.on 2026-08-15 is in the future" in problems
    assert "registry: y delisted.on 2025-12-31 is before first_seen 2026-01-01" in problems


def test_a_delisting_reason_is_a_readers_length(tmp_path: Path):
    """It is the sentence the Archive prints beside the row; the long account
    belongs to the watchlist or the blocklist."""
    from freetier_radar.validate import PROSE_LIMITS
    long = {**ENTRY, "delisted": {"on": "2026-08-10",
                                  "reason": "r" * (PROSE_LIMITS["delisted.reason"] + 1)}}
    problems = check(build(tmp_path, entries=[long]), TODAY)
    assert any("delisted.reason is" in p and "characters" in p for p in problems)


def test_text_that_reads_as_liquid_would_break_the_published_page(tmp_path: Path):
    """README.md is served through GitHub Pages, which renders it with Jekyll.
    A vendor sentence carrying `{{` or `{%` is a Liquid tag to that build, and a
    failed build leaves the whole site — the Atom feed with it — on the previous
    deploy without anything on this page saying so."""
    root = build(tmp_path, entries=[{**ENTRY, "limits": "1000 req/day, {{ per key }}"}])
    assert any("Liquid" in p and "limits" in p for p in check(root, TODAY))


def test_the_announcement_ledger_is_checked_like_the_history(tmp_path: Path):
    """The ledger is the only thing standing between a retried run and a
    double post; a line without its key is a line that protects nothing."""
    root = build(tmp_path)
    (root / "announced.jsonl").write_text(
        '{"key": "2026-09-06T05:30:00+00:00|added|x", "channel": "bluesky", "ts": "2026-09-06T05:31:00Z"}\n'
        '{"channel": "mastodon"}\n'
        'not json\n', encoding="utf-8")
    problems = check(root, today=date(2026, 9, 6))
    assert any("line 2 lacks key, ts" in p for p in problems)
    assert any("line 3 is not JSON" in p for p in problems)


def test_a_notice_is_short_and_not_dated_in_the_future(tmp_path: Path):
    """A notice sits in a callout under the README's first command and in a
    table cell: a reader's paragraph, not an incident log. And it records a
    problem that has started, so a date after today is a typo."""
    from freetier_radar.validate import PROSE_LIMITS
    api = {"base_url": "https://x.ai/v1", "auth": "none",
           "notice": {"since": "2026-08-15", "text": "z" * (PROSE_LIMITS["api.notice"] + 1)}}
    problems = check(build(tmp_path, entries=[{**ENTRY, "api": api}]), TODAY)
    assert f"registry: x api.notice is {PROSE_LIMITS['api.notice'] + 1} characters, over " \
           f"{PROSE_LIMITS['api.notice']} — keep what a reader needs to use the offer, and leave " \
           "its history to history.jsonl" in problems
    assert "registry: x api.notice is dated 2026-08-15, after today (2026-08-14)" in problems


def test_a_notice_carries_no_liquid_delimiters(tmp_path: Path):
    """The notice is printed into README.md, which GitHub Pages builds with Jekyll."""
    api = {"base_url": "https://x.ai/v1", "auth": "none",
           "notice": {"since": "2026-08-14", "text": "The answer is `{{ error }}`."}}
    problems = check(build(tmp_path, entries=[{**ENTRY, "api": api}]), TODAY)
    assert ("registry: x has Liquid delimiters in api.notice — GitHub Pages renders README.md "
            "with Jekyll and would fail to build it") in problems


def test_prose_keeps_angle_brackets_inside_backticks(tmp_path: Path):
    """GitHub strips anything shaped like an HTML tag from a README, so opencode's
    note told readers for a week that its ids inside OpenCode are `opencode/` —
    the `<model-id>` after the slash was never shown. In backticks it survives."""
    entry = {**ENTRY, "limits": "ids are opencode/<model-id> inside the app",
             "api": {"base_url": "https://x.ai/v1", "note": "call `vendor/<model-id>` here"}}
    problems = check(build(tmp_path, entries=[entry]), TODAY)
    assert [p for p in problems if "HTML tag" in p] == [
        "registry: x limits has <model-id> outside backticks — GitHub drops it from the page "
        "as an HTML tag; put it in backticks"]


def test_a_tier_names_the_artificial_analysis_model_it_was_read_from(tmp_path: Path):
    """A tier is a measurement (CONTRIBUTING), and nineteen of twenty-two marks
    were stale by 2026-09-16 because nothing recorded what had been measured.
    A family with a tier carries the Artificial Analysis model it was read from,
    and a family is one model, so every row agrees on it."""
    root = build(tmp_path, entries=[
        {**ENTRY, "models": [{"family": "glm-5.3", "tier": "frontier"}]},
        {**ENTRY, "id": "y", "url": "https://y.ai",
         "models": [{"family": "kimi-k3", "aa_model": "kimi-k3"}]},
        {**ENTRY, "id": "z", "url": "https://z.ai",
         "models": [{"family": "kimi-k3", "aa_model": "kimi-k3-low"}]},
    ])
    problems = check(root, TODAY)
    assert ("registry: family 'glm-5.3' on x is frontier with no aa_model — a tier is read "
            "from Artificial Analysis, so name the model it was read from") in problems
    assert ("registry: family 'kimi-k3' is measured as kimi-k3 on y and kimi-k3-low on z — "
            "a family is one model") in problems
