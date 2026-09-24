"""freetier-bars: when a model a rotating lane serves free is owed its family.

CONTRIBUTING's rule for a lane that rotates: a new id is callable from the read
that finds it and joins `models[]` two weeks later. Until 2026-09-24 the dates
lived in a maintainer's notes, and the ids that came before the notes were never
dated at all. OpenRouter served north-mini-code free from July while its Models
column named two families, and the list of who serves each model free left
OpenRouter off it. The registry's own history already knows when each id
entered a row's `api.model_ids`, because every committed registry.yaml is in
git. So the dates are read from there, and the report says which ids are owed a
family today and when the rest fall due. A vendor's own date for a free id
(NVIDIA's `dateCreated`) can put a family in earlier; this report only makes
sure nothing waits past its bar unseen.

It is a report, not a check. The calendar moves an id from waiting to due
without anyone touching the file, and a commit gate that failed on a date would
stop an unrelated fix. The scheduled run prints it in its summary.
`freetier-check` holds only what does not move: an id kept out of the column on
purpose (`api.no_family_ids`) is one the row lists and no family names.
"""
from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

from .models import Entry, ProbeType, family_names, is_archived, load_registry

__all__ = ["BAR_DAYS", "Waiting", "arrivals", "waiting", "report", "main"]

# Two weeks in the lane before a model joins the Models column: long enough
# that an id which came and went within days never became a family, short
# enough that a lane's steady models are named while they are there.
BAR_DAYS = 14

_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def arrivals(repo: Path, path: str = "registry.yaml") -> dict[tuple[str, str], date]:
    """(row id, model id) → the UTC day of the commit from which the id has stood
    in the row's `api.model_ids` without a break. An id is added on the read
    that finds it and taken out when the run says it left, so an id that came
    back is dated from its return."""
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
                   for model_id in ((row.get("api") or {}).get("model_ids") or [])}
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
    since: date

    @property
    def due_on(self) -> date:
        return self.since + timedelta(days=BAR_DAYS)


def waiting(entries: list[Entry], since: dict[tuple[str, str], date], today: date) -> list[Waiting]:
    """Every id a live row's free lane lists that no family names and no decision
    keeps out, soonest due first. An id the history has not seen, on a row edited
    and not yet committed, arrives today."""
    out = []
    for e in entries:
        if not e.api or is_archived(e, today) or not _free_lane(e):
            continue
        for model_id in e.api.model_ids:
            if model_id in e.api.no_family_ids or any(family_names(m.family, model_id)
                                                      for m in e.models):
                continue
            out.append(Waiting(e.id, model_id, since.get((e.id, model_id), today)))
    return sorted(out, key=lambda w: (w.due_on, w.row, w.model_id))


def report(entries: list[Entry], since: dict[tuple[str, str], date], today: date) -> str:
    rows = waiting(entries, since, today)
    due = [w for w in rows if w.due_on <= today]
    later = [w for w in rows if w.due_on > today]
    lines = ["## Models owed a family", ""]
    if not rows:
        lines.append("Every id a free lane lists has a family or a reason in `api.no_family_ids`.")
    if due:
        lines += ["**Due**, two weeks in the lane: re-read the lane, then add the family, or list "
                  "the id in `api.no_family_ids` with the reason in `api.note`.", ""]
        lines += [f"- {w.row}: `{w.model_id}`, in api.model_ids since {w.since} "
                  f"({(today - w.since).days} days)" for w in due]
        lines.append("")
    if later:
        lines += ["**Waiting:**", ""]
        lines += [f"- {w.due_on} {w.row}: `{w.model_id}`, in api.model_ids since {w.since}"
                  for w in later]
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
    print(report(entries, arrivals(args.repo, args.registry), args.today), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
