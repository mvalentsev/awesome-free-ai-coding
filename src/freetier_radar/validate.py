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
import re
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from .discovery import CURATED_FEEDS
from .history import EventType, deleted_row_problem, deleted_rows, load_history
from .models import (Entry, is_archived, is_blocked, load_blocklist, load_dismissed,
                     load_registry, load_sources, load_watchlist, save_registry)

__all__ = ["check", "check_repository", "registry_form_problems", "main"]

# The most a row's prose may run to, in characters: a README cell and a provider
# page, not a research log.
PROSE_LIMITS = {"offering": 300, "limits": 1200, "api.note": 600, "api.notice": 500,
                "delisted.reason": 300}

_GITHUB_HOSTS = {"github.com", "raw.githubusercontent.com"}

# How a delisting's reason says the service itself was rejected (CONTRIBUTING,
# "How a row leaves the list"): the words the Archive prints first.
FOR_CAUSE = "rejected for cause"

# Text a Markdown renderer takes for an HTML tag: `<` straight into a letter, a
# slash or a bang. "a < b" is left alone.
_TAG = re.compile(r"<[A-Za-z/!][^<>]*>")


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

    # Two rows for one service. A row is never deleted, so the second one is
    # folded instead: it keeps its id, which is its page's URL, and names the
    # row that holds the offer, the evidence and the history. Pointed at an id
    # the registry does not have, the fold sends a reader to a page that is not
    # built; pointed at another fold, to a pointer.
    held = {e.id: e for e in entries}
    for e in entries:
        if e.duplicate_of is None:
            continue
        target = held.get(e.duplicate_of)
        if target is None:
            problems.append(
                f"registry: {e.id} is folded into {e.duplicate_of!r}, which the registry does "
                f"not hold — duplicate_of names the row that keeps the service")
        elif target.duplicate_of is not None:
            problems.append(
                f"registry: {e.id} is folded into {target.id}, itself folded into "
                f"{target.duplicate_of} — duplicate_of names the row that keeps the service, "
                f"not another pointer to it")

    # And the way two rows for one service got here: MiMo Code and MiMoCode sat
    # in the Archive two lines apart for two months — Xiaomi's agent, whose own
    # README prints the name as one word, and a placeholder from the first day's
    # seed at mimocode.ai, a domain that has never resolved. A spelling is not a
    # service, and nothing compared the two names.
    by_name: dict[str, Entry] = {}
    for e in entries:
        first = by_name.setdefault(re.sub(r"[^a-z0-9]", "", e.name.lower()), e)
        if first is e or first.duplicate_of == e.id or e.duplicate_of == first.id:
            continue
        problems.append(
            f"registry: {first.name!r} ({first.id}) and {e.name!r} ({e.id}) read as one name — if "
            f"they are one service, fold one into the other with duplicate_of; if they are "
            f"two, give them names a reader can tell apart")

    # One family, one tier. The scout assigns the tier per proposal and nothing
    # ever compared two rows, so the same model could be frontier on one vendor
    # and strong on the next — nemotron-3-ultra was, across four rows, until
    # 2026-08-19. It reads as a judgement about the vendor when it is a
    # judgement about the model, and any page that ever sorts by it would sort
    # the same model two ways.
    tiers: dict[str, tuple[str, str]] = {}
    for e in entries:
        for m in e.models:
            tier = m.tier.value if m.tier else "no tier"
            first = tiers.get(m.family)
            if first is None:
                tiers[m.family] = (tier, e.id)
            elif first[0] != tier:
                problems.append(
                    f"registry: family {m.family!r} is {first[0]} on {first[1]} and "
                    f"{tier} on {e.id} — a family carries one tier")

    # And the tier is a measurement: nineteen of twenty-two frontier marks were
    # below the bar by 2026-09-16, because nothing recorded what had been read.
    # A family that carries a tier names the Artificial Analysis model it was
    # read from, so `freetier-tiers` can read it again — and a family is one
    # model, so every row names the same one.
    measured_as: dict[str, tuple[str, str]] = {}
    for e in entries:
        for m in e.models:
            if m.tier is not None and not m.aa_model:
                problems.append(
                    f"registry: family {m.family!r} on {e.id} is {m.tier.value} with no aa_model — "
                    f"a tier is read from Artificial Analysis, so name the model it was read from")
            if not m.aa_model:
                continue
            first = measured_as.get(m.family)
            if first is None:
                measured_as[m.family] = (m.aa_model, e.id)
            elif first[0] != m.aa_model:
                problems.append(
                    f"registry: family {m.family!r} is measured as {first[0]} on {first[1]} and "
                    f"{m.aa_model} on {e.id} — a family is one model")

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
                            ("name", e.name), ("api.note", e.api.note if e.api else ""),
                            ("api.notice", e.api.notice.text if e.api and e.api.notice else ""),
                            ("delisted.reason", e.delisted.reason if e.delisted else "")):
            if "{{" in text or "{%" in text:
                problems.append(
                    f"registry: {e.id} has Liquid delimiters in {field} — GitHub Pages "
                    f"renders README.md with Jekyll and would fail to build it")

    # GitHub's sanitizer drops anything shaped like an HTML tag from README.md, and
    # Jekyll passes it through to the provider page as markup nobody sees. opencode's
    # note read "inside OpenCode the ids are opencode/<model-id>" in the registry and
    # "opencode/." on the page for a week. Inside backticks it is code and survives.
    for e in entries:
        for field, text in (("offering", e.offering), ("limits", e.limits), ("name", e.name),
                            ("api.note", e.api.note if e.api else ""),
                            ("api.notice", e.api.notice.text if e.api and e.api.notice else ""),
                            ("delisted.reason", e.delisted.reason if e.delisted else "")):
            for tag in _TAG.findall(re.sub(r"`[^`]*`", "", text)):
                problems.append(
                    f"registry: {e.id} {field} has {tag} outside backticks — GitHub drops it from "
                    f"the page as an HTML tag; put it in backticks")

    # A row's prose is for the reader deciding whether to use the offer: the
    # quota, the conditions, what happens to the data. By 2026-09-16 it had become
    # the maintainer's log — the median `limits` grew from 87 characters in July
    # to 813, the longest to 3,712, dated lane counts and which id left when —
    # and README.md reached 260 KB. History lives in history.jsonl and git log.
    for e in entries:
        for field, text, limit in (("offering", e.offering, PROSE_LIMITS["offering"]),
                                   ("limits", e.limits, PROSE_LIMITS["limits"]),
                                   ("api.note", e.api.note if e.api else "", PROSE_LIMITS["api.note"]),
                                   ("api.notice", e.api.notice.text if e.api and e.api.notice else "",
                                    PROSE_LIMITS["api.notice"]),
                                   ("delisted.reason", e.delisted.reason if e.delisted else "",
                                    PROSE_LIMITS["delisted.reason"])):
            if len(text) > limit:
                problems.append(
                    f"registry: {e.id} {field} is {len(text)} characters, over {limit} — "
                    f"keep what a reader needs to use the offer, and leave its history to history.jsonl")
        # A notice records a problem that has started; one dated after today is a
        # typo, and it would hold a refusal for longer than NOTICE_HOLD_DAYS.
        if e.api and e.api.notice and e.api.notice.since > today:
            problems.append(f"registry: {e.id} api.notice is dated {e.api.notice.since.isoformat()}, "
                            f"after today ({today.isoformat()})")
        # The day a reviewer took the row off: not one that has not come, and
        # not one before the list carried the row at all.
        if e.delisted and e.delisted.on > today:
            problems.append(f"registry: {e.id} delisted.on {e.delisted.on.isoformat()} is in the future")
        if e.delisted and e.delisted.on < e.first_seen:
            problems.append(f"registry: {e.id} delisted.on {e.delisted.on.isoformat()} is before "
                            f"first_seen {e.first_seen.isoformat()}")

    # ---- registry against blocklist.yaml
    # We list it and we say it must never be proposed. One of the two is wrong.
    # Archived rows are exempt for the watchlist's reason below: a row taken off
    # the list and then rejected for cause — Kenari — is the intended sequence.
    for e in entries:
        if is_archived(e, today):
            continue
        if is_blocked(_domain(e.url), blocklist):
            problems.append(f"registry: {e.id} sits on blocklisted domain {_domain(e.url)}")

    # ---- a delisting and the verdict behind it
    # A row a reviewer takes off keeps one line in the Archive; the account of
    # why lives in the file the scout reads before it proposes the vendor again —
    # the blocklist for a service rejected for cause, the watchlist for an offer
    # that ended or never qualified. Kenari and easy-gonka-api each took three
    # edits in one commit (delisted, blocklisted, api block dropped), and nothing
    # held the three together.
    watched_domains = {d.lower() for w in watchlist for d in w.domains}
    for e in entries:
        if e.delisted is None or e.duplicate_of is not None:
            continue
        d = _domain(e.url)
        for_cause = e.delisted.reason.lower().startswith(FOR_CAUSE)
        if for_cause and not is_blocked(d, blocklist):
            problems.append(f"registry: {e.id} is delisted for cause and {d} is not on the "
                            "blocklist — the verdict about the service goes to blocklist.yaml")
        if for_cause and e.api is not None:
            problems.append(f"registry: {e.id} is delisted for cause and still carries an api "
                            "block — a row rejected for cause keeps no connection details")
        if not for_cause and is_blocked(d, blocklist):
            problems.append(f"registry: {e.id} sits on blocklisted domain {d} and its delisting "
                            f"says `{e.delisted.reason}` — a row on the blocklist is delisted as "
                            f"`{FOR_CAUSE} — …`")
        elif not for_cause and not any(d == wd or d.endswith("." + wd) for wd in watched_domains):
            problems.append(f"registry: {e.id} is delisted and no watchlist verdict covers {d} — "
                            "the account of why the offer ended goes to watchlist.yaml (or, for "
                            "cause, blocklist.yaml)")

    # ---- registry against watchlist.yaml
    # A live row and a "no free tier here" verdict are the same contradiction,
    # one file apart. Archived rows are exempt: burying an entry and then
    # recording why its offer is gone is the intended sequence, not a conflict.
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
    # A row leaves the list through the Archive, never by leaving the registry.
    for entry_id in deleted_rows(entries, history):
        problems.append(f"registry: {deleted_row_problem(entry_id)}")

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


def registry_form_problems(root: Path) -> list[str]:
    """registry.yaml is rewritten whole by every command that saves it — the
    run, the scout, freetier-tiers — so it is kept in the form save_registry
    writes, and a hand edit in another layout is the next run's diff of every
    line it re-wrapped."""
    path = root / "registry.yaml"
    with tempfile.TemporaryDirectory() as tmp:
        again = Path(tmp) / "registry.yaml"
        save_registry(again, load_registry(path))
        if again.read_bytes() == path.read_bytes():
            return []
    return ["registry: registry.yaml is not in the form save_registry writes — run "
            "`uv run freetier-check --normalize` and commit the result"]


def check_repository(root: Path) -> list[str]:
    """The rules about the repository as a whole, beyond the curated files: the
    map (layout.MAP), what the hand-written files state (claims.CLAIMS), the
    map's own section in CONTRIBUTING.md and the registry's form."""
    # Imported here: both read the constants this module defines.
    from .claims import check_claims
    from .layout import check_layout
    from .render import CONTRIBUTING, MAP_BEGIN, MAP_END
    problems = [f"layout: {p}" for p in check_layout(root)]
    problems += [f"claims: {p}" for p in check_claims(root)]
    text = (root / CONTRIBUTING).read_text(encoding="utf-8")
    if MAP_BEGIN not in text or MAP_END not in text:
        problems.append(f"layout: {CONTRIBUTING} has lost the lines the map section is printed "
                        "between — put them back and run `uv run freetier-render`")
    return problems + registry_form_problems(root)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate registry.yaml, blocklist.yaml, dismissed.yaml, "
                    "watchlist.yaml, sources.yaml and history.jsonl, the rules that hold "
                    "between them, the map of the repository and what its hand-written "
                    "files state.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--normalize", action="store_true",
                        help="rewrite registry.yaml in the form save_registry writes, and stop")
    args = parser.parse_args()

    if args.normalize:
        path = args.root / "registry.yaml"
        save_registry(path, load_registry(path))
        print(f"rewrote {path} in the form save_registry writes")
        return
    problems = check(args.root) + check_repository(args.root)
    for p in problems:
        print(f"✗ {p}")
    if problems:
        raise SystemExit(f"{len(problems)} problem(s) found")
    print("✓ registry, blocklist, dismissed, watchlist, sources and history are consistent, "
          "every tracked file is on the map, and the hand-written files say what the code does")


if __name__ == "__main__":
    main()
