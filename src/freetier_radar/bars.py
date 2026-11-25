"""freetier-bars: when a model a rotating lane serves free is owed its family.

CONTRIBUTING's rule for a lane that rotates: a new id is callable from the read
that finds it and joins `models[]` two weeks later. A documented dated promotion
is due immediately, with its deadline beside it. The day an id entered a
row's `api.model_ids` — or `client_lane.model_ids`, for a lane served only
inside the vendor's own client — is read from the registry's git history, and
the report says which ids are owed a family today and when the rest fall due.
An earlier day counts where one is known: the vendor's own date for the free
id, read off the free list the probe reads (`probe.free_list`; a list that
cannot be read is named in the report), or an older record the row names in
`free_since` — a Wayback snapshot of the vendor's free list, the vendor's own
snapshot of its lane.

It is a report, not a check. The calendar moves an id from waiting to due
without anyone touching the file, and a commit gate that failed on a date would
stop an unrelated fix. The scheduled run prints it in its summary.
`freetier-check` holds only what does not move: an id kept out of the column on
purpose (`api.no_family_ids`) is one the row lists and no family names.
"""
from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import httpx
import yaml

from . import git
from .models import (Entry, FreePart, expire_entries, family_access, entry_id_family, id_access,
                     is_archived, lane_ids, load_registry, withdrawal_rule)
from .prober import TIMEOUT, UA, free_list_dates
from .words import weeks
from .models import QUALIFICATION_DAYS as BAR_DAYS
from .yaml_data import load_yaml

__all__ = ["BAR_DAYS", "Waiting", "arrivals", "vendor_dates", "waiting", "report", "main"]


def _published_lanes(rows: list, through: date) -> dict[tuple[str, str], str]:
    lanes = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("free_part") != FreePart.MODELS.value:
            continue
        retired_on = row.get("retired_on")
        if isinstance(retired_on, str):
            retired_on = date.fromisoformat(retired_on)
        if withdrawal_rule(row.get("delisted") is not None, retired_on, through):
            continue
        field = "api" if row.get("api") is not None else "client_lane"
        for model_id in (row.get(field) or {}).get("model_ids") or []:
            lanes[(row["id"], model_id)] = field
    return lanes


def arrivals(repo: Path, path: str = "registry.yaml", *,
             lanes: dict[tuple[str, str], str] | None = None,
             today: date | None = None) -> dict[tuple[str, str], date]:
    """Date each exact ID from its uninterrupted run in the same named Free lane.

    Read the first-parent history backward, stopping at each ID's first gap.
    Callers can supply the current lanes they need, including uncommitted IDs.
    A dated shutdown can break continuity between two registry commits.
    """
    if lanes == {}:
        return {}
    since: dict[tuple[str, str], date] = {}
    through = today
    for sha, stamp in git.commits(repo, "--first-parent", "HEAD", "--", path, field="%ct", check=True):
        day = datetime.fromtimestamp(int(stamp), timezone.utc).date()
        try:
            data = load_yaml(git.show(repo, sha, path) or "") or {}
        except yaml.YAMLError:
            raise ValueError(f"cannot read {path} in {sha}") from None
        rows = (data.get("entries") or []) if isinstance(data, dict) else []
        present = _published_lanes(rows, max(day, through) if through else day)
        lanes = present if lanes is None else {key: field for key, field in lanes.items()
                                                if present.get(key) == field}
        if not lanes:
            break
        since.update(dict.fromkeys(lanes, day))
        through = day
    return since


def _free_lane(e: Entry) -> bool:
    """Whether a row's ids are a lane of named free models, which the row says
    itself: its free part is models. A credit or an allowance names no free
    model, nor does a free part the vendor names none for, and their ids are
    examples to paste."""
    return e.free_part is FreePart.MODELS


@dataclass(frozen=True)
class Waiting:
    row: str
    model_id: str
    listed: date  # the day the row's own record took the id in
    vendor: date | None = None  # the vendor's own date for the free id, where it gives one
    field: str = "api"  # the block the id is listed in: api, or client_lane
    # Where `vendor` was read: the vendor's free list, or the record a row's
    # free_since names for the id.
    vendor_source: str = "the vendor's list"
    until: datetime | date | None = None

    @property
    def since(self) -> date:
        """The day the two weeks count from: the read that found the id, or the
        vendor's own date for the free id where that is earlier."""
        return min(self.listed, self.vendor) if self.vendor else self.listed

    @property
    def due_on(self) -> date:
        return self.since if self.until else self.since + timedelta(days=BAR_DAYS)


def vendor_dates(entries: list[Entry], fetch: Callable[[str], httpx.Response],
                 today: date) -> tuple[dict[tuple[str, str], date], list[str]]:
    """(row id, model id) → the day the vendor's own free list dates the free id,
    for every live row that reads one (`probe.free_list`, the document the probe
    reads), and a line for each list that could not be read. Each row's list is
    fetched once, with no retry."""
    dates: dict[tuple[str, str], date] = {}
    unread: list[str] = []
    for e in entries:
        url, lane = e.probe.free_list, lane_ids(e)
        if url is None or lane is None or is_archived(e, today):
            continue
        try:
            resp = fetch(url)
        except httpx.HTTPError as exc:
            read: dict[str, date] | str = type(exc).__name__
        else:
            read = (free_list_dates(resp, lane.model_ids) if resp.is_success
                    else f"answered HTTP {resp.status_code}")
        if isinstance(read, str):
            unread.append(f"{e.id}: the free list at {url} could not be read ({read}), so its "
                          "ids are counted from the registry's history alone")
            continue
        dates.update({(e.id, model_id): day for model_id, day in read.items()})
    return dates, unread


def waiting(entries: list[Entry], since: dict[tuple[str, str], date], today: date,
            vendor: dict[tuple[str, str], date] | None = None,
            now: datetime | None = None) -> list[Waiting]:
    """Every id a live row's free lane lists that no family names and no decision
    keeps out, soonest due first. An id the history has not seen, on a row edited
    and not yet committed, arrives today; the vendor's date for it, or a record
    the row's free_since names, counts where it is earlier."""
    vendor = vendor or {}
    out = []
    for e in expire_entries(entries, now or datetime.combine(today, time.min, timezone.utc)):
        lane = lane_ids(e)
        if is_archived(e, today) or not _free_lane(e):
            continue
        # A page row has no ids to date: its newcomers carry their own record.
        named = {m.family for m in e.models}
        out += [Waiting(e.id, n.family, n.on, None, "newcomers", f"<{n.source}>",
                        access.until if (access := family_access(e, n.family)) else None)
                for n in e.newcomers if n.family not in named]
        if lane is None:
            continue
        recorded = {s.id: s for s in lane.free_since}
        for model_id in lane.model_ids:
            if model_id in lane.no_family_ids or entry_id_family(e, model_id) is not None:
                continue
            day, source = vendor.get((e.id, model_id)), "the vendor's list"
            record = recorded.get(model_id)
            if record is not None and (day is None or record.on < day):
                day, source = record.on, f"<{record.source}>"
            out.append(Waiting(e.id, model_id, since.get((e.id, model_id), today),
                               day, lane.field, source,
                               access.until if (access := id_access(e, model_id)) else None))
    return sorted(out, key=lambda w: (w.due_on, w.row, w.model_id))


def _dated(w: Waiting) -> str:
    if w.field == "newcomers":
        listed = f"free on {w.vendor_source} since {w.listed}"
    else:
        listed = f"in {w.field}.model_ids since {w.listed}"
    if w.field != "newcomers" and w.vendor is not None and w.vendor < w.listed:
        listed = f"free on {w.vendor_source} since {w.vendor}, {listed}"
    return listed + (f", free until {w.until.isoformat()}" if w.until else "")


def report(entries: list[Entry], since: dict[tuple[str, str], date], today: date,
           vendor: dict[tuple[str, str], date] | None = None,
           unread: list[str] | tuple[str, ...] = (), now: datetime | None = None) -> str:
    rows = waiting(entries, since, today, vendor, now)
    due = [w for w in rows if w.due_on <= today]
    later = [w for w in rows if w.due_on > today]
    lines = ["## Models owed a family", ""]
    if not rows:
        lines.append("Every id a free lane lists has a family or a reason in `api.no_family_ids`.")
    if due:
        lines += [f"**Due**, a dated promotion or {weeks(BAR_DAYS)} in the lane: re-read the lane, then add the family, or list "
                  "the id in `api.no_family_ids` with the reason in the commit message.", ""]
        lines += [f"- {w.row}: `{w.model_id}`, {_dated(w)} ({(today - w.since).days} days)"
                  for w in due]
        lines.append("")
    if later:
        lines += ["**Waiting:**", ""]
        lines += [f"- {w.due_on} {w.row}: `{w.model_id}`, {_dated(w)}" for w in later]
        lines.append("")
    if unread:
        lines += ["**Vendor dates not read:**", ""] + [f"- {line}" for line in unread]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    now = datetime.now(timezone.utc)
    ap = argparse.ArgumentParser(description=(
        f"Which ids a rotating lane has served free for {weeks(BAR_DAYS)} without a Models-column "
        "family, dated from the registry's git history."))
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--registry", default="registry.yaml",
                    help="path of the registry inside the repository")
    ap.add_argument("--today", type=date.fromisoformat,
                    default=now.date())
    ap.add_argument("--ids", nargs="+", help="report only these provider IDs")
    args = ap.parse_args(argv)
    entries = load_registry(args.repo / args.registry)
    if args.ids:
        ids = set(args.ids)
        if unknown := ids - {e.id for e in entries}:
            ap.error(f"unknown provider IDs: {', '.join(sorted(unknown))}")
        entries = [e for e in entries if e.id in ids]
    at = now if args.today == now.date() else None
    lanes = {(w.row, w.model_id): w.field for w in waiting(entries, {}, args.today, now=at)
             if w.field != "newcomers"}
    since = arrivals(args.repo, args.registry, lanes=lanes, today=args.today)
    with httpx.Client(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
        vendor, unread = vendor_dates(entries, client.get, args.today)
    print(report(entries, since, args.today, vendor, unread, now=at), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
