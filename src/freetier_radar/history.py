"""What this list published, and when it changed.

Every other file here answers "what is true today". This one answers "what
happened", which is the question a reader who already knows the list keeps
asking: did anything arrive, did anything die, did a provider quietly drop half
its free models. `README.md` and `index.json` are regenerated from scratch on
every run and carry no memory at all, so until now the only record of a
withdrawn free tier was a line in `git log`.

The diff is against the HISTORY, not against the registry as it was at the start
of the run. That matters for three reasons, each of which a before/after diff of
the file gets wrong:

- most of this registry is edited by hand and merged through a pull request, so
  the run that first *sees* an entry is not the run that added it — a
  within-run diff would never report a hand-added row at all;
- an entry can be archived by the calendar alone, without a byte of the registry
  changing, when it goes unverified past the staleness limit;
- a state machine cannot report the same transition twice, so a feed built on it
  cannot ping a subscriber about the same event on two consecutive runs.

The file is append-only and is the first thing the cron commits that cannot be
regenerated from `registry.yaml`. It is written one line at a time, never
rewritten, so two branches that both appended merge by keeping both sides.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel

from .models import Entry, is_archived, live_families, load_registry

__all__ = ["EventType", "Event", "State", "archive_reason", "registry_state", "replay",
           "diff_state", "load_history", "append_history", "record_changes"]


class EventType(str, Enum):
    ADDED = "added"          # a row a reader could not see before
    ARCHIVED = "archived"    # it stopped verifying, or its vendor announced the end
    RESTORED = "restored"    # it started passing again
    REMOVED = "removed"      # deleted from the registry by hand — usually to the watchlist
    MODELS = "models"        # the free-model list of a live row changed


class Event(BaseModel):
    """One line of `history.jsonl`.

    `models` carries the entry's published families *after* the event, not the
    delta: it is what lets the file be replayed into the state the history
    believes the list is in, which is the whole basis of the next diff.
    """
    ts: datetime      # when the event was recorded, UTC — the run's clock, not the vendor's
    event: EventType
    id: str
    name: str
    url: str = ""
    models: list[str] = []
    detail: str = ""


class Status(str, Enum):
    LIVE = "live"
    ARCHIVED = "archived"


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
    if entry.retired_on and today >= entry.retired_on:
        return f"vendor-announced shutdown on {entry.retired_on.isoformat()}"
    if entry.probe_failures >= 3:
        return f"{entry.probe_failures} failed probes"
    return (f"unverified for {(today - entry.last_verified).days} days "
            f"(last passed {entry.last_verified.isoformat()})")


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
            state.pop(ev.id, None)
            continue
        status = Status.ARCHIVED if ev.event is EventType.ARCHIVED else Status.LIVE
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
            events.append(Event(ts=now, event=EventType.REMOVED, id=entry_id,
                                name=was.name, url=was.url, models=list(was.models)))
        elif was is None:
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
            # shows a name and a date and no models at all.
            events.append(Event(ts=now, event=EventType.MODELS, id=entry_id,
                                name=now_.name, url=now_.url, models=list(now_.models),
                                detail=_model_delta(was.models, now_.models)))
    return events


def load_history(path: Path) -> list[Event]:
    """Missing file means no history — the same reading every other curated file
    here gets. A malformed line is an error and names itself: this file is the
    only one in the repository that cannot be regenerated, so a line that will
    not parse must stop a run rather than be skipped past."""
    if not path.exists():
        return []
    events: list[Event] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(Event.model_validate(json.loads(line)))
        except Exception as exc:
            raise ValueError(f"{path}: line {number} is not a history event: {exc}") from exc
    return events


def append_history(path: Path, events: list[Event]) -> None:
    """Append, never rewrite. `save_registry` re-serialises its whole file and
    would be the obvious model to copy here; it is the wrong one — rewriting a
    log turns every concurrent append into a merge conflict and every bug into
    a lost month."""
    if not events:
        return
    with path.open("a", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev.model_dump(mode="json"), ensure_ascii=False) + "\n")


def record_changes(registry_path: Path, history_path: Path,
                   today: date, now: datetime) -> list[Event]:
    """Compare the registry against the history and write the difference.

    Called by the two commands that write `registry.yaml` — the prober and the
    scout — rather than from `save_registry` itself, which is also called by
    tests and by anything that just wants the file on disk. A saver with a side
    effect is a saver that eventually writes history nobody asked for.
    """
    events = diff_state(replay(load_history(history_path)),
                        registry_state(load_registry(registry_path), today), now)
    append_history(history_path, events)
    return events
