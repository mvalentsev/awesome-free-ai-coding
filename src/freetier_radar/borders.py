"""How far a border reaches: the share of the world's developers a row's free
offer leaves out, counted on GitHub's Innovation Graph, and the command that
refreshes the count and prints every row's.

CONTRIBUTING's "A border counts like a wall" ranks an offer lower the more of
the list's readers it leaves out, and counts readers as developers. On
2026-09-25 that count was done in a scratchpad, for three rows, and a rank argued
from it could be reproduced by nobody who did not redo it. It is code now, over
a snapshot of the Innovation Graph committed beside it — the render never
reaches the network — so every share a page prints and every rank argued from
one can be read again with `freetier-borders`.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from .countries import country_name
from .models import Border, Category, is_archived, load_registry

__all__ = ["SHARED", "YARDSTICK_PATH", "Yardstick", "snapshot_from_csv", "load_yardstick",
           "left_out_of", "beyond_shared", "share", "main"]

YARDSTICK_URL = "https://raw.githubusercontent.com/github/innovationgraph/main/data/developers.csv"
YARDSTICK_SOURCE = "https://github.com/github/innovationgraph/blob/main/data/developers.csv"
YARDSTICK_PATH = Path(__file__).with_name("developers.json")

# The exclusions that set no row apart: the countries under comprehensive US
# embargo, which a sanctions clause covers whether it names them or not — seventeen
# live rows carry one that names no country, and the rows that name any name
# these first. CONTRIBUTING's rule says "an exclusion most vendors share", and
# until the sweep of 2026-09-26 its example, "the countries under US sanctions",
# was read to take in Russia, Belarus and Venezuela as well. The sweep counted
# the vendors' own words: fifteen of eighty live rows leave Russia out, and no
# embargo clause reaches it — not most, so a border that leaves out Russia is
# counted. The suite holds the set to the registry: no country outside it is
# left out by most rows.
SHARED = frozenset({"CU", "IR", "KP", "SY"})


@dataclass(frozen=True)
class Yardstick:
    """One quarter of the Innovation Graph's developer counts, by ISO code."""
    year: int
    quarter: int
    read_on: str
    developers: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.developers.values())

    @property
    def label(self) -> str:
        return f"{self.year} Q{self.quarter}"

    @classmethod
    def from_snapshot(cls, snap: dict) -> Yardstick:
        return cls(year=snap["year"], quarter=snap["quarter"], read_on=snap["read_on"],
                   developers=dict(snap["developers"]))


def snapshot_from_csv(text: str, today: date) -> dict:
    """The latest quarter of `developers.csv`, the EU's line left out: it
    repeats its member states, which the file counts one by one."""
    rows = list(csv.DictReader(io.StringIO(text)))
    latest = max((int(r["year"]), int(r["quarter"])) for r in rows)
    developers = {r["iso2_code"]: int(r["developers"]) for r in rows
                  if (int(r["year"]), int(r["quarter"])) == latest and r["iso2_code"] != "EU"}
    return {"source": YARDSTICK_SOURCE, "year": latest[0], "quarter": latest[1],
            "read_on": today.isoformat(), "developers": dict(sorted(developers.items()))}


@lru_cache(maxsize=4)
def load_yardstick(path: Path = YARDSTICK_PATH) -> Yardstick:
    return Yardstick.from_snapshot(json.loads(path.read_text(encoding="utf-8")))


def left_out_of(border: Border, yardstick: Yardstick) -> set[str]:
    """Every economy the border keeps the offer from: a deny-list as it is, an
    allow-list as everything the yardstick counts that it does not name."""
    if border.served is not None:
        return set(yardstick.developers) - set(border.served)
    return set(border.left_out or [])


def beyond_shared(border: Border, yardstick: Yardstick) -> list[str]:
    """The codes left out beyond the shared exclusions, the most developers first."""
    codes = left_out_of(border, yardstick) - SHARED
    return sorted(codes, key=lambda c: (-yardstick.developers.get(c, 0), c))


def share(border: Border, yardstick: Yardstick) -> float:
    """The part of the world's developers the border leaves out beyond the
    shared exclusions — the figure a rank is argued from."""
    counted = sum(yardstick.developers.get(c, 0) for c in beyond_shared(border, yardstick))
    return counted / yardstick.total


def _refresh(path: Path, today: date) -> Yardstick:
    import httpx

    resp = httpx.get(YARDSTICK_URL, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    snap = snapshot_from_csv(resp.text, today)
    path.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    load_yardstick.cache_clear()
    return Yardstick.from_snapshot(snap)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="freetier-borders",
        description="Print the share of developers each live row's border leaves out, "
                    "counted on GitHub's Innovation Graph — the figure CONTRIBUTING's border "
                    "rule argues a rank from.")
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--refresh", action="store_true",
                        help="read the Innovation Graph's latest quarter into the committed "
                             "snapshot first")
    args = parser.parse_args()
    today = date.today()
    yardstick = _refresh(YARDSTICK_PATH, today) if args.refresh else load_yardstick()
    print(f"Innovation Graph {yardstick.label}: {yardstick.total:,} developers in "
          f"{len(yardstick.developers)} economies, read {yardstick.read_on}; shared "
          f"exclusions {', '.join(sorted(SHARED))}\n")
    live = [e for e in load_registry(args.registry) if not is_archived(e, today)]
    order = {c: i for i, c in enumerate(Category)}
    for e in sorted(live, key=lambda e: (order[e.category], e.rank, e.id)):
        if e.border is None:
            print(f"{e.category.value:14} {e.rank:>3} {e.id:24} no border recorded")
            continue
        codes = beyond_shared(e.border, yardstick)
        named = ", ".join(country_name(c) for c in codes[:6]) + (
            f" and {len(codes) - 6} more" if len(codes) > 6 else "")
        print(f"{e.category.value:14} {e.rank:>3} {e.id:24} {100 * share(e.border, yardstick):5.1f}%"
              + (f"  {named}" if codes else ""))


if __name__ == "__main__":
    main()
