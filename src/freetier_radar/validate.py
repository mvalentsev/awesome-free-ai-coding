"""Repository consistency check — every file this repo curates by hand, and the
rules that hold *between* them.

Why this exists as its own entry point rather than as more tests: `registry.yaml`
was already validated on every push, because `freetier-render` loads it through
pydantic and CI renders. `blocklist.yaml`, `dismissed.yaml` and `watchlist.yaml`
were not loaded by anything except the scout — the optional half of the run,
wrapped in a catch-all so an upstream failure cannot sink it. So a malformed one
reached main and turned into a green workflow that had quietly done nothing
(2026-08-14: a colon inside a plain YAML scalar).

The cross-file rules are the second half. Each one is a contradiction that a
human can hold in two files without noticing, and each one was found by hand at
least once before it was written down here.

`history.jsonl` joined them for a stronger reason: it is the one file here that
cannot be regenerated from any other, and the only one whose line *order* is
part of its meaning.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from .discovery import CURATED_FEEDS
from .history import EventType, load_history
from .models import (Entry, is_archived, is_blocked, load_blocklist, load_dismissed,
                     load_registry, load_sources, load_watchlist)

__all__ = ["check", "main"]

_GITHUB_HOSTS = {"github.com", "raw.githubusercontent.com"}


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _source_key(url: str) -> str:
    """One identity for a source however it happens to be spelled.

    CURATED_FEEDS holds the raw.githubusercontent URL the scout actually
    fetches, down to the branch and the file; a human writes down the
    github.com link they were sent. Same list, and comparing the strings would
    never say so.
    """
    parsed = urlparse(url)
    host = _domain(url)
    parts = [p for p in parsed.path.split("/") if p]
    if host in _GITHUB_HOSTS and len(parts) >= 2:
        return f"github:{parts[0].lower()}/{parts[1].lower()}"
    return f"{host}{parsed.path.rstrip('/')}".lower()


def check(root: Path, today: date | None = None) -> list[str]:
    """Every problem found, as human-readable lines. Empty means clean."""
    today = today or date.today()
    problems: list[str] = []

    entries: list[Entry] = load_registry(root / "registry.yaml")
    blocklist = load_blocklist(root / "blocklist.yaml")
    dismissed = load_dismissed(root / "dismissed.yaml")
    watchlist = load_watchlist(root / "watchlist.yaml")
    sources = load_sources(root / "sources.yaml")

    # ---- within registry.yaml
    for field, values in (("id", [e.id for e in entries]),
                          ("url", [e.url for e in entries]),
                          ("api.base_url", [e.api.base_url for e in entries
                                            if e.api and e.api.base_url])):
        seen: set[str] = set()
        for v in values:
            if v in seen:
                problems.append(f"registry: duplicate {field} {v!r}")
            seen.add(v)

    # One family, one tier. The scout assigns the tier per proposal and nothing
    # ever compared two rows, so the same model could be frontier on one vendor
    # and strong on the next — nemotron-3-ultra was, across four rows, until
    # 2026-08-19. It reads as a judgement about the vendor when it is a
    # judgement about the model, and any page that ever sorts by it would sort
    # the same model two ways.
    tiers: dict[str, tuple[str, str]] = {}
    for e in entries:
        for m in e.models:
            first = tiers.get(m.family)
            if first is None:
                tiers[m.family] = (m.tier.value, e.id)
            elif first[0] != m.tier.value:
                problems.append(
                    f"registry: family {m.family!r} is {first[0]} on {first[1]} and "
                    f"{m.tier.value} on {e.id} — a family carries one tier")

    for e in entries:
        if e.last_verified > today:
            problems.append(f"registry: {e.id} last_verified {e.last_verified} is in the future")
        if e.first_seen > e.last_verified:
            problems.append(
                f"registry: {e.id} first_seen {e.first_seen} is after "
                f"last_verified {e.last_verified}")
        # README.md is published through GitHub Pages, which builds it with
        # Jekyll — measured, not assumed: the root of the Pages site serves the
        # README rendered by jekyll-readme-index even with a .nojekyll file
        # beside it. So every vendor sentence copied into an entry passes through
        # Liquid, and two adjacent braces in one of them fail the build. A failed
        # build is the quiet kind: the previous deploy keeps serving, so the
        # Atom feed simply stops moving with nothing on the page to say why.
        for field, text in (("offering", e.offering), ("limits", e.limits),
                            ("name", e.name), ("api.note", e.api.note if e.api else "")):
            if "{{" in text or "{%" in text:
                problems.append(
                    f"registry: {e.id} has Liquid delimiters in {field} — GitHub Pages "
                    f"renders README.md with Jekyll and would fail to build it")

    # ---- registry against blocklist.yaml
    # We list it and we say it must never be proposed. One of the two is wrong.
    for e in entries:
        if is_blocked(_domain(e.url), blocklist):
            problems.append(f"registry: {e.id} sits on blocklisted domain {_domain(e.url)}")

    # ---- registry against watchlist.yaml
    # A live row and a "no free tier here" verdict are the same contradiction,
    # one file apart. Archived rows are exempt: burying an entry and then
    # recording why its offer is gone is the intended sequence, not a conflict.
    watched_domains = {d.lower() for w in watchlist for d in w.domains}
    for e in entries:
        if is_archived(e, today):
            continue
        d = _domain(e.url)
        for wd in watched_domains:
            if d == wd or d.endswith("." + wd):
                problems.append(
                    f"registry: live entry {e.id} ({d}) is also on the watchlist as "
                    f"having no free tier")

    # ---- blocklist against watchlist
    # "Rejected for cause, permanently" and "legitimate, just nothing free today"
    # are contradictory verdicts, and the scout would apply whichever it reached
    # first.
    for w in watchlist:
        for d in w.domains:
            if is_blocked(d.lower(), blocklist):
                problems.append(
                    f"watchlist: {w.name} ({d}) is also blocklisted — a domain gets one verdict")

    # ---- within watchlist.yaml
    seen_domains: set[str] = set()
    for w in watchlist:
        if w.checked_on > today:
            problems.append(f"watchlist: {w.name} checked_on {w.checked_on} is in the future")
        if not w.reopen_if.strip():
            problems.append(
                f"watchlist: {w.name} has no reopen_if — a verdict with no way back "
                f"is a blocklist entry in the wrong file")
        # Both fields render as cells of a Markdown table, where an unescaped
        # pipe silently splits the row into extra columns.
        for field, text in (("reason", w.reason), ("reopen_if", w.reopen_if)):
            if "|" in text:
                problems.append(
                    f"watchlist: {w.name} has a pipe in {field} — it would break the "
                    f"README table row it renders into")
        for d in w.domains:
            if d.lower() in seen_domains:
                problems.append(f"watchlist: duplicate domain {d}")
            seen_domains.add(d.lower())

    # ---- sources.yaml against discovery.py
    # A list is either read on every run or written down as not worth reading.
    # Holding both is the same contradiction the blocklist and the watchlist
    # can hold about a vendor, and it costs a fetch twice a week to keep.
    feed_keys = {_source_key(f) for f in CURATED_FEEDS}
    seen_sources: set[str] = set()
    for s in sources:
        if s.checked_on > today:
            problems.append(f"sources: {s.name} checked_on {s.checked_on} is in the future")
        if not s.reopen_if.strip():
            problems.append(
                f"sources: {s.name} has no reopen_if — a source that could never be worth "
                f"re-reading belongs in the blocklist, not here")
        key = _source_key(s.url)
        if key in feed_keys:
            problems.append(
                f"sources: {s.name} is written down as declined and is also read every run "
                f"as a curated feed")
        if key in seen_sources:
            problems.append(f"sources: duplicate source {s.url}")
        seen_sources.add(key)

    # ---- history.jsonl
    # The only file here that cannot be regenerated from another one, and the
    # only one whose *order* carries meaning. Everything below is a way the log
    # can stop being a faithful account of what was published — a replay built
    # on a broken log silently re-announces events subscribers have already had.
    history = load_history(root / "history.jsonl")
    live_ids: set[str] = set()
    previous = None
    for ev in history:
        if ev.ts.date() > today:
            problems.append(f"history: {ev.id} {ev.event.value} at {ev.ts} is in the future")
        if previous is not None and ev.ts < previous:
            problems.append(
                f"history: {ev.id} {ev.event.value} at {ev.ts} is out of order — "
                f"it follows an event at {previous}")
        previous = ev.ts
        if ev.event is EventType.REMOVED:
            if ev.id not in live_ids:
                problems.append(
                    f"history: {ev.id} is removed without ever having been recorded")
            live_ids.discard(ev.id)
        elif ev.event is EventType.ADDED:
            if ev.id in live_ids:
                problems.append(f"history: {ev.id} is added while already recorded")
            live_ids.add(ev.id)
        else:
            live_ids.add(ev.id)

    # ---- announced.jsonl
    # The announcer's ledger: append-only like the history, and read every run
    # to decide what has already been said. A line that will not parse would
    # stop the announce step; a line missing its key or channel would let the
    # same post go out again. Checked here for the same reason history is —
    # nothing regenerates it.
    ledger = root / "announced.jsonl"
    if ledger.exists():
        for number, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                problems.append(f"announced: line {number} is not JSON")
                continue
            missing = [k for k in ("key", "channel", "ts") if not row.get(k)]
            if missing:
                problems.append(
                    f"announced: line {number} lacks {', '.join(missing)} — a post with no key "
                    f"or channel would be sent again")

    # ---- dismissed.yaml against the registry
    ids = {e.id for e in entries}
    for entry_id, family, target in sorted(dismissed):
        if entry_id not in ids:
            problems.append(
                f"dismissed: {entry_id} is not an entry id — the suppression matches nothing")
        elif not any(m.family == family for e in entries if e.id == entry_id for m in e.models):
            problems.append(
                f"dismissed: {entry_id} has no family {family!r} — the suppression "
                f"matches nothing")

    return problems


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate registry.yaml, blocklist.yaml, dismissed.yaml, "
                    "watchlist.yaml, sources.yaml and history.jsonl, and the "
                    "rules that hold between them.")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    problems = check(args.root)
    for p in problems:
        print(f"✗ {p}")
    if problems:
        raise SystemExit(f"{len(problems)} problem(s) found")
    print("✓ registry, blocklist, dismissed, watchlist, sources and history are consistent")
