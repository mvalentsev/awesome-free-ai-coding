"""freetier-bars: when a model a rotating lane serves free is owed its family.

CONTRIBUTING's rule for a lane that rotates: a new id is callable from the read
that finds it and joins `models[]` two weeks later. Until 2026-09-24 the dates
lived in a maintainer's notes, and the ids that came before the notes were never
dated at all. OpenRouter served north-mini-code free from July while its Models
column named two families, and the list of who serves each model free left
OpenRouter off it. The registry's own history already knows when each id
entered a row's `api.model_ids` — or `client_lane.model_ids`, for a lane served
only inside the vendor's own client — because every committed registry.yaml is
in git. So the dates are read from there, and the report says which ids are owed a
family today and when the rest fall due. Where the vendor dates the free id
itself, the earlier of the two days counts: NVIDIA created glm-5.3's free
endpoint on 2026-09-15 and the row listed it on 09-22, so counted from the row
alone the bar fell a week after the rule's. The report reads those dates off
the same free list the probe reads (`probe.free_list`), and a list it cannot
read is named in the report rather than silently counted from the row.

It is a report, not a check. The calendar moves an id from waiting to due
without anyone touching the file, and a commit gate that failed on a date would
stop an unrelated fix. The scheduled run prints it in its summary.
`freetier-check` holds only what does not move: an id kept out of the column on
purpose (`api.no_family_ids`) is one the row lists and no family names.
"""
from __future__ import annotations

import argparse
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
import yaml

from .models import Entry, ProbeType, family_names, is_archived, lane_ids, load_registry
from .prober import TIMEOUT, UA, free_list_dates

__all__ = ["BAR_DAYS", "Waiting", "arrivals", "vendor_dates", "waiting", "report", "main"]

# Two weeks in the lane before a model joins the Models column: long enough
# that an id which came and went within days never became a family, short
# enough that a lane's steady models are named while they are there.
BAR_DAYS = 14

_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def arrivals(repo: Path, path: str = "registry.yaml") -> dict[tuple[str, str], date]:
    """(row id, model id) → the UTC day of the commit from which the id has stood
    in the row's `api.model_ids` — or `client_lane.model_ids`, for a lane no API
    serves — without a break. An id is added on the read that finds it and
    taken out when the run says it left, so an id that came back is dated from
    its return."""
    log = subprocess.run(["git", "log", "--reverse", "--format=%H %ct", "--", path],
                         cwd=repo, capture_output=True, text=True, check=True).stdout
    since: dict[tuple[str, str], date] = {}
    for line in log.splitlines():
        sha, stamp = line.split()
        text = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=repo,
                              capture_output=True, text=True).stdout
        try:
            data = yaml.load(text, Loader=_LOADER) or {}
        except yaml.YAMLError:
            continue
        rows = (data.get("entries") or []) if isinstance(data, dict) else []
        present = {(row.get("id"), model_id) for row in rows if isinstance(row, dict)
                   for block in ("api", "client_lane")
                   for model_id in ((row.get(block) or {}).get("model_ids") or [])}
        day = datetime.fromtimestamp(int(stamp), timezone.utc).date()
        since = {key: when for key, when in since.items() if key in present}
        for key in present:
            since.setdefault(key, day)
    return since


def _free_lane(e: Entry) -> bool:
    """Whether a row's ids are a lane of named free models: its column names
    families, or its probe reads each model's own free mark. A credit or an
    allowance names no free model, and its ids are examples to paste."""
    p = e.probe
    return bool(e.models) or (p.type is ProbeType.API_MODELS
                              and bool(p.require_zero_price or p.free_marker or p.lane or p.free_list))


@dataclass(frozen=True)
class Waiting:
    row: str
    model_id: str
    listed: date  # the day the row's own record took the id in
    vendor: date | None = None  # the vendor's own date for the free id, where it gives one
    field: str = "api"  # the block the id is listed in: api, or client_lane

    @property
    def since(self) -> date:
        """The day the two weeks count from: the read that found the id, or the
        vendor's own date for the free id where that is earlier."""
        return min(self.listed, self.vendor) if self.vendor else self.listed

    @property
    def due_on(self) -> date:
        return self.since + timedelta(days=BAR_DAYS)


def vendor_dates(entries: list[Entry], fetch: Callable[[str], httpx.Response],
                 today: date) -> tuple[dict[tuple[str, str], date], list[str]]:
    """(row id, model id) → the day the vendor's own free list dates the free id,
    for every live row that reads one (`probe.free_list`), and a line for each
    list that could not be read. One read per list: the probe reads the same
    document, and a list is the vendor's word on which endpoints are free."""
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
            vendor: dict[tuple[str, str], date] | None = None) -> list[Waiting]:
    """Every id a live row's free lane lists that no family names and no decision
    keeps out, soonest due first. An id the history has not seen, on a row edited
    and not yet committed, arrives today."""
    vendor = vendor or {}
    out = []
    for e in entries:
        lane = lane_ids(e)
        if lane is None or is_archived(e, today) or not _free_lane(e):
            continue
        for model_id in lane.model_ids:
            if model_id in lane.no_family_ids or any(family_names(m.family, model_id)
                                                     for m in e.models):
                continue
            out.append(Waiting(e.id, model_id, since.get((e.id, model_id), today),
                               vendor.get((e.id, model_id)), lane.field))
    return sorted(out, key=lambda w: (w.due_on, w.row, w.model_id))


def _dated(w: Waiting) -> str:
    listed = f"in {w.field}.model_ids since {w.listed}"
    if w.vendor is not None and w.vendor < w.listed:
        return f"free on the vendor's list since {w.vendor}, {listed}"
    return listed


def report(entries: list[Entry], since: dict[tuple[str, str], date], today: date,
           vendor: dict[tuple[str, str], date] | None = None,
           unread: list[str] | tuple[str, ...] = ()) -> str:
    rows = waiting(entries, since, today, vendor)
    due = [w for w in rows if w.due_on <= today]
    later = [w for w in rows if w.due_on > today]
    lines = ["## Models owed a family", ""]
    if not rows:
        lines.append("Every id a free lane lists has a family or a reason in `api.no_family_ids`.")
    if due:
        lines += ["**Due**, two weeks in the lane: re-read the lane, then add the family, or list "
                  "the id in `api.no_family_ids` with the reason in `api.note`.", ""]
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
    ap = argparse.ArgumentParser(description=(
        "Which ids a rotating lane has served free for two weeks without a Models-column "
        "family, dated from the registry's git history."))
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--registry", default="registry.yaml",
                    help="path of the registry inside the repository")
    ap.add_argument("--today", type=date.fromisoformat,
                    default=datetime.now(timezone.utc).date())
    args = ap.parse_args(argv)
    entries = load_registry(args.repo / args.registry)
    with httpx.Client(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
        vendor, unread = vendor_dates(entries, client.get, args.today)
    print(report(entries, arrivals(args.repo, args.registry), args.today, vendor, unread), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
