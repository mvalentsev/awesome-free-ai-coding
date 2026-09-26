"""Tier marks, measured against the Artificial Analysis Intelligence Index.

A tier on a model family is a claim that reaches the top of the README — the
"Frontier-tier models on a $0 plan" answer is built from it — and until
2026-09-17 it was typed once and never read again. The 2026-09-16 audit found
nineteen of twenty-two `frontier` marks below the bar CONTRIBUTING had just
written down, and `strong` on every other family whatever it scored: Apertus
70B at 5 points beside GLM 5.3 Flash at 42.

So a tier is read, not written. Each family that carries one names the
Artificial Analysis model it was measured as (`aa_model`, the slug of its page),
and this reads every score off the leaderboard the site publishes:

- `frontier` — within FRONTIER_WITHIN points of the top of the index;
- `strong` — within STRONG_WITHIN points;
- `notable` — below that, but at or above the median of the current models
  the index scores: its upper half, where a model readers still look for sits
  once the top has moved on (Claude Opus 4.6 at 26.4 when the top was 57.6).
  It earns the model a page of its own, not a strong mark;
- no tier — further down, or not measured at all.

The top and the median count current models only: a deprecated model is not a
bar anything can be expected to reach, nor one of the models a score is
measured among. Run it with `--write` and the marks that moved are
re-written on every row that carries the family, since a family carries one
tier. A slug the leaderboard no longer knows keeps its mark and fails the run:
a guess is not a measurement.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
import sys
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

import httpx

from .models import Entry, Tier, is_archived, load_registry, save_registry
from .prober import UA

LEADERBOARD_URL = "https://artificialanalysis.ai/leaderboards/models"
TIMEOUT = httpx.Timeout(60.0, connect=10.0)
FRONTIER_WITHIN = 10.0
STRONG_WITHIN = 25.0

# Next.js ships the page's data as string chunks pushed to self.__next_f; the
# leaderboard's table is a JSON array inside their concatenation.
_FLIGHT_CHUNK = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')
_MODELS_ARRAY = re.compile(r'\{"models":\s*\[')


@dataclass(frozen=True)
class Scored:
    slug: str
    name: str
    index: float
    deprecated: bool
    estimated: bool


def parse_leaderboard(page: str) -> dict[str, Scored]:
    """Every scored model on the leaderboard page, by slug.

    The page carries more than one `models` array — a picker without scores
    comes first — so the one read is the array with the most scored rows."""
    payload = "".join(json.loads(chunk) for chunk in _FLIGHT_CHUNK.findall(page))
    decoder = json.JSONDecoder()
    best: list[dict] = []
    for match in _MODELS_ARRAY.finditer(payload):
        try:
            data, _ = decoder.raw_decode(payload, match.start())
        except ValueError:
            continue
        rows = [r for r in data.get("models") or []
                if isinstance(r, dict) and r.get("slug")
                and isinstance(r.get("intelligenceIndex"), (int, float))]
        if len(rows) > len(best):
            best = rows
    if not best:
        raise ValueError(f"{LEADERBOARD_URL} carries no scored models — the page changed shape, "
                         "and no tier can be read from it")
    return {r["slug"]: Scored(slug=r["slug"], name=r.get("name") or r["slug"],
                              index=float(r["intelligenceIndex"]),
                              deprecated=bool(r.get("deprecated")),
                              estimated=bool(r.get("intelligenceIndexIsEstimated")))
            for r in best}


def index_top(models: dict[str, Scored]) -> Scored:
    return max((m for m in models.values() if not m.deprecated), key=lambda m: m.index)


def _current(models: dict[str, Scored]) -> list[float]:
    return [m.index for m in models.values() if not m.deprecated]


def index_median(models: dict[str, Scored]) -> float:
    """The median score of the current models on the board: where its upper
    half, and the `notable` mark, begins."""
    return statistics.median(_current(models))


def measured_tier(score: float, top: float, median: float) -> Tier | None:
    if score >= top - FRONTIER_WITHIN:
        return Tier.FRONTIER
    if score >= top - STRONG_WITHIN:
        return Tier.STRONG
    if score >= median:
        return Tier.NOTABLE
    return None


@dataclass(frozen=True)
class Mark:
    family: str
    aa_model: str
    registered: Tier | None
    measured: Tier | None = None
    score: Scored | None = None

    @property
    def unknown(self) -> bool:
        return self.score is None

    @property
    def moved(self) -> bool:
        return not self.unknown and self.registered is not self.measured


def review(entries: list[Entry], models: dict[str, Scored]) -> tuple[Scored, list[Mark]]:
    """The top of the index, and one mark per family that names an aa_model —
    families that name none have nothing to measure and carry no tier.

    A family's registered mark is the one a row carries against the
    measurement, if any row does: read off the first row alone, a new row that
    came in bare beside an older, correct one was never re-marked (Dahl
    Inference's deepseek-v4-flash, 2026-09-21)."""
    top, median = index_top(models), index_median(models)
    marks: dict[str, Mark] = {}
    for e in entries:
        for m in e.models:
            if m.aa_model is None:
                continue
            mark = marks.get(m.family)
            if mark is None:
                scored = models.get(m.aa_model)
                marks[m.family] = Mark(
                    family=m.family, aa_model=m.aa_model, registered=m.tier,
                    measured=measured_tier(scored.index, top.index, median) if scored else None,
                    score=scored)
            elif not mark.moved and m.tier is not mark.registered:
                marks[m.family] = replace(mark, registered=m.tier)
    return top, sorted(marks.values(), key=lambda k: k.family)


def unmeasured(entries: list[Entry], models: dict[str, Scored]) -> list[tuple[str, Scored]]:
    """Families no row measures (no row names an aa_model for them) whose name,
    read the way the board spells a slug — a hyphen for a dot, GLM-5.3 as
    glm-5-3 — is a model the board scores into a tier.

    A family added bare carries no tier, so a new strong model stayed off the
    strong list, and off a page of its own while one row served it, until a
    reviewer remembered to measure it. This names it on the next run. Only a
    slug the board lists is offered — never a guess — and only a score that
    reaches a tier, `notable` included, since that one decides whether the
    model has a page (twenty families sat bare on 2026-09-26, twelve of them in
    the index's upper half, Qwen3.7 Max at 29.5 among them); below the median,
    measuring changes nothing a page says. The reviewer names, as the family's
    aa_model, the variant the lane actually serves."""
    top, median = index_top(models), index_median(models)
    measured = {m.family for e in entries for m in e.models if m.aa_model}
    found: dict[str, Scored] = {}
    for e in entries:
        for m in e.models:
            if m.superseded_by is None and m.family not in measured and m.family not in found:
                scored = models.get(m.family.replace(".", "-"))
                if scored is not None and measured_tier(scored.index, top.index, median) is not None:
                    found[m.family] = scored
    return sorted(found.items())


def _tier_name(tier: Tier | None) -> str:
    return tier.value if tier else "no tier"


async def _amain(registry: Path, write: bool) -> int:
    entries = load_registry(registry)
    async with httpx.AsyncClient(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(LEADERBOARD_URL)
    resp.raise_for_status()
    board = parse_leaderboard(resp.text)
    top, marks = review(entries, board)
    live = [e for e in entries if not is_archived(e, date.today())]
    median = index_median(board)
    print(f"top of the index: {top.name}, {top.index:.1f} — frontier from "
          f"{top.index - FRONTIER_WITHIN:.1f}, strong from {top.index - STRONG_WITHIN:.1f}, "
          f"notable from {median:.1f}, the median of its {len(_current(board))} current models")
    moved = [m for m in marks if m.moved]
    unknown = [m for m in marks if m.unknown]
    for m in moved:
        estimated = ", estimated" if m.score.estimated else ""
        print(f"  {m.family}: {_tier_name(m.registered)} → {_tier_name(m.measured)} "
              f"({m.score.index:.1f} on {m.aa_model}{estimated})")
    for m in unknown:
        print(f"  {m.family}: {m.aa_model} is not on the leaderboard — the mark stays "
              f"{_tier_name(m.registered)} until the family names a model that is")
    bare = unmeasured(live, board)
    for family, scored in bare:
        print(f"  {family}: no aa_model — the leaderboard scores {scored.slug} at "
              f"{scored.index:.1f} ({_tier_name(measured_tier(scored.index, top.index, median))}); name it "
              "as the family's aa_model if that is the model the lane serves")
    if write and moved:
        tiers = {m.family: m.measured for m in moved}
        for e in entries:
            for fam in e.models:
                if fam.family in tiers:
                    fam.tier = tiers[fam.family]
        save_registry(registry, entries)
    print(f"{len(marks)} families measured, {len(moved)} marks "
          f"{'re-written' if write else 'moved'}, {len(unknown)} not on the leaderboard, "
          f"{len(bare)} unmeasured that would reach a tier")
    return 1 if unknown or (moved and not write) else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--write", action="store_true",
                        help="re-write the marks that moved on every row carrying the family")
    args = parser.parse_args()
    sys.exit(asyncio.run(_amain(args.registry, args.write)))
