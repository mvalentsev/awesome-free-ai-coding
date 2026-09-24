"""What this list published, and when it changed.

Every other file here answers "what is true today". This one answers "what
happened", which is the question a reader who already knows the list keeps
asking: did anything arrive, did anything die, did a provider quietly drop half
its free models. `README.md` and `index.json` are regenerated from scratch on
every run and carry no memory at all, so until now the only record of a
withdrawn free tier was a line in `git log`.

The diff is against the HISTORY, not against the registry as it was before an
edit. That matters for three reasons, each of which a before/after diff of the
file gets wrong:

- the registry is edited by hand, by the probe run and by the scout, and the
  render that records a change is not the command that made it — a diff of
  one command's edit would never report the others;
- an entry can be archived by the calendar alone, without a byte of the registry
  changing, when it goes unverified past the staleness limit;
- a state machine cannot report the same transition twice, so a feed built on it
  cannot ping a subscriber about the same event on two consecutive runs.

The file is append-only and is the first thing here that cannot be
regenerated from `registry.yaml`. Until 2026-09-25 only the scheduled run wrote
it, so a change committed by hand reached the README the day it landed and the
log at the next run, up to four days later, dated that day. Now `freetier-render`
records every change before it writes a page — the lines a commit carries are
the changes that commit makes, at the time it makes them — and `freetier-gate`
holds each commit's lines to exactly that (`block_problems`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel

from .models import ARCHIVE_AFTER_FAILURES, Entry, is_archived, live_families, load_registry

__all__ = ["EventType", "Event", "State", "archive_reason", "registry_state", "replay",
           "diff_state", "deleted_row_problem", "deleted_rows", "refuse_deleted_rows",
           "parse_history", "load_history", "append_history", "record_changes",
           "pending_changes", "block_problems"]


class EventType(str, Enum):
    ADDED = "added"          # a row a reader could not see before
    ARCHIVED = "archived"    # it moved to the Archive: its vendor's date, its probe, or a reviewer
    RESTORED = "restored"    # it started passing again
    # Deleted from the registry by hand. Only ever read back: until 2026-09-17 a
    # reviewer took a row off this way, and since then a row leaves through the
    # Archive and a deletion is refused before it can be recorded.
    REMOVED = "removed"
    MODELS = "models"        # the free-model list of a live row changed


class Event(BaseModel):
    """One line of `history.jsonl`.

    `models` carries the entry's published families *after* the event, not the
    delta: it is what lets the file be replayed into the state the history
    believes the list is in, which is the whole basis of the next diff.
    """
    ts: datetime      # when the render recorded it, UTC — the list's clock, not the vendor's
    event: EventType
    id: str
    name: str
    url: str = ""
    models: list[str] = []
    detail: str = ""


class Status(str, Enum):
    LIVE = "live"
    ARCHIVED = "archived"
    # The history's own word for a row it last saw deleted. Such a row is back in
    # the registry as delisted, and its departure was announced when it happened,
    # so the Archive taking it in is not news the second time.
    DELETED = "deleted"


@dataclass(frozen=True)
class State:
    """How one entry stands, on one side of the comparison."""
    status: Status
    name: str
    url: str = ""
    models: tuple[str, ...] = ()
    # The sentence this row would carry if it were announced right now — what it
    # offers while it is live, why it left once it is not. Only ever read from
    # the registry side; a replayed state has no need of one and leaves it empty.
    summary: str = ""


def archive_reason(entry: Entry, today: date) -> str:
    """Why this row is in the Archive — read off the same three rules that put
    it there, so the feed cannot describe an archival the renderer disagrees
    with."""
    if entry.delisted is not None:
        return f"delisted on {entry.delisted.on.isoformat()}: {entry.delisted.reason}"
    if entry.retired_on and today >= entry.retired_on:
        return f"vendor-announced shutdown on {entry.retired_on.isoformat()}"
    if entry.probe_failures >= ARCHIVE_AFTER_FAILURES:
        return (f"{entry.probe_failures} failed probes in a row, "
                f"last passed {entry.last_verified.isoformat()}")
    return (f"unverified for {(today - entry.last_verified).days} days, "
            f"last passed {entry.last_verified.isoformat()}")


def registry_state(entries: list[Entry], today: date) -> dict[str, State]:
    """What the list publishes right now, entry by entry."""
    state: dict[str, State] = {}
    for e in entries:
        archived = is_archived(e, today)
        state[e.id] = State(
            status=Status.ARCHIVED if archived else Status.LIVE,
            name=e.name,
            url=e.url,
            models=tuple(live_families(e)),
            summary=archive_reason(e, today) if archived else e.offering,
        )
    return state


def replay(events: list[Event]) -> dict[str, State]:
    """The state the history says the list is in, folded out of its events."""
    state: dict[str, State] = {}
    for ev in events:
        if ev.event is EventType.REMOVED:
            status = Status.DELETED
        elif ev.event is EventType.ARCHIVED:
            status = Status.ARCHIVED
        else:
            status = Status.LIVE
        state[ev.id] = State(status=status, name=ev.name, url=ev.url,
                             models=tuple(ev.models))
    return state


def _model_delta(before: tuple[str, ...], after: tuple[str, ...]) -> str:
    added = sorted(set(after) - set(before))
    dropped = sorted(set(before) - set(after))
    parts = []
    if added:
        parts.append("added " + ", ".join(added))
    if dropped:
        parts.append("dropped " + ", ".join(dropped))
    return "; ".join(parts)


def diff_state(recorded: dict[str, State], current: dict[str, State],
               now: datetime) -> list[Event]:
    """Everything that has happened to the list since the history last looked.

    At most one event per entry: a row that is archived on the same run its
    model list changed has left, and that is the only thing worth saying about
    it. Ids are walked in sorted order so a run's events land in the file in a
    stable order rather than in registry order.
    """
    events: list[Event] = []
    for entry_id in sorted(set(recorded) | set(current)):
        was, now_ = recorded.get(entry_id), current.get(entry_id)

        if now_ is None:
            if was.status is not Status.DELETED:
                events.append(Event(ts=now, event=EventType.REMOVED, id=entry_id,
                                    name=was.name, url=was.url, models=list(was.models)))
        elif was is not None and was.status is Status.DELETED and now_.status is Status.ARCHIVED:
            # Deleted before rows were archived, and back as the record the
            # Archive keeps: "Delisted" already said the row left.
            continue
        elif was is None or was.status is Status.DELETED:
            kind = EventType.ADDED if now_.status is Status.LIVE else EventType.ARCHIVED
            events.append(Event(ts=now, event=kind, id=entry_id, name=now_.name,
                                url=now_.url, models=list(now_.models),
                                detail=now_.summary))
        elif was.status is not now_.status:
            kind = (EventType.ARCHIVED if now_.status is Status.ARCHIVED
                    else EventType.RESTORED)
            events.append(Event(ts=now, event=kind, id=entry_id, name=now_.name,
                                url=now_.url, models=list(now_.models),
                                detail=now_.summary))
        elif now_.status is Status.LIVE and set(was.models) != set(now_.models):
            # Set-compared: reordering a list nobody reads in order is not news.
            # Skipped entirely while a row is archived, where the Archive table
            # shows a name and why it left and no models at all.
            events.append(Event(ts=now, event=EventType.MODELS, id=entry_id,
                                name=now_.name, url=now_.url, models=list(now_.models),
                                detail=_model_delta(was.models, now_.models)))
    return events


def parse_history(text: str, where: str = "history.jsonl", first_line: int = 1) -> list[Event]:
    """A malformed line is an error and names itself: this file is the only one
    in the repository that cannot be regenerated, so a line that will not parse
    must stop a run rather than be skipped past."""
    events: list[Event] = []
    for number, line in enumerate(text.splitlines(), start=first_line):
        if not line.strip():
            continue
        try:
            events.append(Event.model_validate(json.loads(line)))
        except Exception as exc:
            raise ValueError(f"{where}: line {number} is not a history event: {exc}") from exc
    return events


def load_history(path: Path) -> list[Event]:
    """Missing file means no history — the same reading every other curated file
    here gets."""
    if not path.exists():
        return []
    return parse_history(path.read_text(encoding="utf-8"), str(path))


def _line(ev: Event) -> str:
    return json.dumps(ev.model_dump(mode="json"), ensure_ascii=False) + "\n"


def append_history(path: Path, events: list[Event]) -> None:
    """Append, never rewrite. `save_registry` re-serialises its whole file and
    would be the obvious model to copy here; it is the wrong one — rewriting a
    log turns every concurrent append into a merge conflict and every bug into
    a lost month."""
    if not events:
        return
    with path.open("a", encoding="utf-8") as fh:
        for ev in events:
            fh.write(_line(ev))


def deleted_rows(entries: list[Entry], events: list[Event]) -> list[str]:
    """Every id the history has recorded that the registry no longer holds.

    A row leaves the list through the Archive — its vendor's date, its probe, or
    a reviewer's `delisted` — and stays in the registry as the record of what
    was published. Deleting it instead is how twelve rows left before
    2026-09-17 with nothing on the page but "Delisted —", so a registry that
    has lost a row is refused wherever it would be published: `freetier-check`,
    the render's record of it and the render's pages."""
    held = {e.id for e in entries}
    return sorted(set(replay(events)) - held)


def deleted_row_problem(entry_id: str) -> str:
    return (f"{entry_id} is in history.jsonl and missing from registry.yaml — a row leaves "
            "the list through the Archive: give it `delisted` (or `retired_on`) instead of "
            "deleting it")


def refuse_deleted_rows(entries: list[Entry], events: list[Event]) -> None:
    missing = deleted_rows(entries, events)
    if missing:
        raise ValueError("; ".join(deleted_row_problem(i) for i in missing))


def _unstamped(events: list[Event]) -> list[dict]:
    return [ev.model_dump(mode="json", exclude={"ts"}) for ev in events]


def record_changes(registry_path: Path, history_path: Path, today: date, now: datetime,
                   committed: str | None = None) -> list[Event]:
    """Compare the registry against the history and write the difference.

    `freetier-render` calls it before it writes a page, so every commit that
    changes what the list publishes carries the lines for that change. With
    `committed` — the log as the commit being made will find it, read from git
    — the lines are the difference from that: whatever an earlier render of
    the same uncommitted work wrote after it is replaced, since a row added and
    taken back out before the commit never reached the list, and lines that
    already say the same thing are kept as they are, clock and all, so a second
    render changes no byte. Without it, the difference from the file as it
    stands is appended.

    A deleted row stops the render here, before anything is written: the
    history would call it delisted and the page would lose it.
    """
    entries = load_registry(registry_path)
    text = history_path.read_text(encoding="utf-8") if history_path.exists() else ""
    if committed is None or not text.startswith(committed):
        committed = text
    if committed and not committed.endswith("\n"):
        committed += "\n"
    base = parse_history(committed, str(history_path))
    tail = parse_history(text[len(committed):], str(history_path),
                         first_line=committed.count("\n") + 1)
    refuse_deleted_rows(entries, base)
    block = diff_state(replay(base), registry_state(entries, today), now)
    if _unstamped(block) == _unstamped(tail):
        return tail
    history_path.write_text(committed + "".join(_line(ev) for ev in block), encoding="utf-8")
    return block


def pending_changes(entries: list[Entry], events: list[Event], today: date) -> list[Event]:
    """What a render on `today` would record: nothing, when the log is up to
    date with the registry."""
    return diff_state(replay(events), registry_state(entries, today),
                      datetime.combine(today, time(), tzinfo=timezone.utc))


def block_problems(base: list[Event], block: list[Event], entries: list[Entry], day: date,
                   now: datetime) -> list[str]:
    """What is wrong with the lines a commit appends to the log it found: they
    are the render's own record of the changes the commit makes, or they are
    not. `day` is the day the commit's pages were rendered on (index.json's
    `generated`), `now` the latest a render of it could have run — the commit's
    own time."""
    problems = []
    stamps = sorted({ev.ts for ev in block})
    if len(stamps) > 1:
        problems.append(f"the commit appends lines with {len(stamps)} timestamps — one render "
                        "records a commit's changes at one time")
    at = stamps[-1] if stamps else now
    if block and at > now:
        problems.append(f"the commit appends lines dated {at.isoformat()}, after the commit "
                        "itself")
    if block and base and block[0].ts < base[-1].ts:
        problems.append(f"the commit appends lines dated {block[0].ts.isoformat()}, before the "
                        f"last line it found ({base[-1].ts.isoformat()}) — the log is in the "
                        "order the list changed: render again on top of it")
    expected = diff_state(replay(base), registry_state(entries, day), at)
    unmatched = _unstamped(expected)
    for number, (ev, got) in enumerate(zip(block, _unstamped(block)), start=1):
        if got in unmatched:
            unmatched.remove(got)
        else:
            problems.append(f"line {number} of what the commit appends ({ev.event.value} "
                            f"{ev.id}) is not a change this registry makes")
    if unmatched:
        problems.append("the registry makes a change the commit does not record: "
                        + ", ".join(f"{u['event']} {u['id']}" for u in unmatched))
    return problems
