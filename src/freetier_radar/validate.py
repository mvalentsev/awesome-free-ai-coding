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
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from .models import (Entry, is_archived, is_blocked, load_blocklist, load_dismissed,
                     load_registry, load_watchlist)

__all__ = ["check", "main"]


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def check(root: Path, today: date | None = None) -> list[str]:
    """Every problem found, as human-readable lines. Empty means clean."""
    today = today or date.today()
    problems: list[str] = []

    entries: list[Entry] = load_registry(root / "registry.yaml")
    blocklist = load_blocklist(root / "blocklist.yaml")
    dismissed = load_dismissed(root / "dismissed.yaml")
    watchlist = load_watchlist(root / "watchlist.yaml")

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

    for e in entries:
        if e.last_verified > today:
            problems.append(f"registry: {e.id} last_verified {e.last_verified} is in the future")
        if e.first_seen > e.last_verified:
            problems.append(
                f"registry: {e.id} first_seen {e.first_seen} is after "
                f"last_verified {e.last_verified}")

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
        description="Validate registry.yaml, blocklist.yaml, dismissed.yaml and "
                    "watchlist.yaml, and the rules that hold between them.")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    problems = check(args.root)
    for p in problems:
        print(f"✗ {p}")
    if problems:
        raise SystemExit(f"{len(problems)} problem(s) found")
    print("✓ registry, blocklist, dismissed and watchlist are consistent")
