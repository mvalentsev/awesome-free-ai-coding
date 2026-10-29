"""Tier marks, measured against the Artificial Analysis Intelligence Index.

A tier on a model family reaches the top of the README — the "Frontier-tier
models on a $0 plan" answer is built from it — so it is read, not written. Each
family that carries one names the Artificial Analysis model it is measured as
(`aa_model`, the slug of its page), and this reads every score off the
leaderboard the site publishes, so a model's mark follows the index as models
come out:

- `frontier` — within FRONTIER_WITHIN points of the top of the index;
- `strong` — within STRONG_WITHIN points;
- `notable` — below that, but at or above the median of the current models
  the index scores: its upper half, where a model readers still look for sits
  once the top has moved on. It earns the model a page of its own, not a
  strong mark;
- no tier — further down, or not measured at all.

The top and the median count current models only: a deprecated model is not a
bar anything can be expected to reach, nor one of the models a score is
measured among. Run it with `--write` and the marks that moved are re-written
on every row that carries the family, since a family carries one tier, and a
bare family the board scores by its own name is measured (see `unmeasured`). A
model explicitly published without a current score loses its tier. A slug the
leaderboard no longer knows keeps its mark and fails the run: a guess is not
a measurement.
"""
from __future__ import annotations

import argparse
import asyncio
import gzip
import hashlib
import io
import json
import re
import statistics
import sys
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import httpx
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .models import Entry, Tier, is_archived, load_registry, save_registry
from .prober import UA

LEADERBOARD_URL = "https://artificialanalysis.ai/leaderboards/models"
# What --write keeps of the board it read: the day, the top, the median and the
# score of every family the list measures. The README draws the strong models
# against the top of the index from it, and the render reads no network.
SCORES_PATH = Path(__file__).with_name("intelligence-index.json")
TIMEOUT = httpx.Timeout(60.0, connect=10.0)
FRONTIER_WITHIN = 10.0
STRONG_WITHIN = 25.0

# Artificial Analysis /leaderboards/models, checked 2026-10-19: Next.js ships
# string chunks; scored rows use initialModels, older pages used models.
_FLIGHT_CHUNK = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')
_MODELS_ARRAY = re.compile(r'"(?:models|initialModels)"\s*:\s*(\[)')
_MANIFEST = re.compile(r'"manifest"\s*:\s*')
TABLE_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class Scored:
    slug: str
    name: str
    index: float | None
    deprecated: bool
    estimated: bool


def _flight_payload(page: str) -> str:
    return "".join(json.loads(chunk) for chunk in _FLIGHT_CHUNK.findall(page))


def _scored_models(rows: object) -> dict[str, Scored]:
    if not isinstance(rows, list):
        return {}
    models = {}
    seen = set()
    for row in rows:
        if (not isinstance(row, dict) or not isinstance(row.get("slug"), str)
                or not row["slug"]):
            continue
        if row["slug"] in seen:
            raise ValueError("leaderboard carries duplicate model scores")
        seen.add(row["slug"])
        if "intelligenceIndex" not in row:
            continue
        score = row["intelligenceIndex"]
        if score is not None and type(score) not in (int, float):
            continue
        # AA's complete table and model cards publish null/N/A for a missing
        # current measurement (leaderboard/model cards, checked 2026-10-29).
        models[row["slug"]] = Scored(
            slug=row["slug"], name=row.get("name") or row["slug"],
            index=float(score) if score is not None else None,
            deprecated=bool(row.get("deprecated")),
            estimated=bool(row.get("intelligenceIndexIsEstimated")))
    return models


def parse_leaderboard(page: str) -> dict[str, Scored]:
    """The scored table, including models explicitly without a current score.

    The page also carries unscored picker arrays. Read the supported table
    property with the most scored rows, regardless of its position in props."""
    payload = _flight_payload(page)
    decoder = json.JSONDecoder()
    best: dict[str, Scored] = {}
    best_scored = 0
    for match in _MODELS_ARRAY.finditer(payload):
        try:
            data, _ = decoder.raw_decode(payload, match.start(1))
        except ValueError:
            continue
        rows = _scored_models(data)
        scored = sum(m.index is not None for m in rows.values())
        if scored > best_scored:
            best, best_scored = rows, scored
    if not best:
        raise ValueError(f"{LEADERBOARD_URL} carries no scored models — the page changed shape, "
                         "and no tier can be read from it")
    return best


async def read_leaderboard(client: httpx.AsyncClient, page: str) -> dict[str, Scored]:
    """Read the full table when the initial HTML contains only current models."""
    payload = _flight_payload(page)
    matches = list(_MANIFEST.finditer(payload))
    if not matches:
        return parse_leaderboard(page)
    if len(matches) != 1:
        raise ValueError("leaderboard carries ambiguous table manifests")
    manifest, _ = json.JSONDecoder().raw_decode(payload, matches[0].end())
    if not isinstance(manifest, dict):
        raise ValueError("leaderboard manifest has an unsupported shape")
    path, key_hex = manifest.get("path"), manifest.get("key")
    if not isinstance(path, str) or not re.fullmatch(r'/data/[\w-]+\.(?:txt|json)', path, re.ASCII):
        raise ValueError("leaderboard manifest does not name a same-origin data file")
    if key_hex is not None and (not isinstance(key_hex, str)
                               or not re.fullmatch(r'[0-9a-fA-F]{64}', key_hex)):
        raise ValueError("leaderboard manifest has an invalid public decoding key")
    response = await client.get(urljoin(LEADERBOARD_URL, path))
    response.raise_for_status()
    body = response.content
    if len(body) > TABLE_BYTES:
        raise ValueError("leaderboard data exceeds the read budget")
    if key_hex is not None:
        # artificialanalysis.ai/leaderboards/models publishes the key and client
        # decoder (chunk68697, module57455), checked 2026-10-19. This is public data.
        key = bytes.fromhex(key_hex)
        try:
            body = AESGCM(key).decrypt(hashlib.sha256(key).digest()[:12], body, None)
            with gzip.GzipFile(fileobj=io.BytesIO(body)) as data:
                body = data.read(TABLE_BYTES + 1)
        except (InvalidTag, OSError, EOFError) as exc:
            raise ValueError("leaderboard data could not be decoded and authenticated") from exc
        if len(body) > TABLE_BYTES:
            raise ValueError("decoded leaderboard data exceeds the read budget")
    board = _scored_models(json.loads(body))
    if not any(m.index is not None and not m.deprecated for m in board.values()):
        raise ValueError("leaderboard manifest carries no scored models")
    return board


def index_top(models: dict[str, Scored]) -> Scored:
    current = [m for m in models.values() if not m.deprecated and m.index is not None]
    if not current:
        raise ValueError("leaderboard carries no current scored models")
    return max(current, key=lambda m: m.index)


def _current(models: dict[str, Scored]) -> list[float]:
    return [m.index for m in models.values() if not m.deprecated and m.index is not None]


def index_median(models: dict[str, Scored]) -> float:
    """The median score of the current models on the board: where its upper
    half, and the `notable` mark, begins."""
    return statistics.median(_current(models))


def measured_tier(score: float | None, top: float, median: float) -> Tier | None:
    if score is None:
        return None
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
    measurement, if any row does, so a row that came in bare beside an older,
    correct one is re-marked too."""
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
    """Unsuperseded families no row measures (no row names an aa_model for them)
    whose name, read the way the board spells a slug — a hyphen for a dot,
    GLM-5.3 as glm-5-3 — is a model the board scores into a tier.

    Only a slug the board lists is offered, never a guess, and only a score that
    reaches a tier, `notable` included, since that one decides whether the
    model has a page; below the median, measuring changes nothing a page says.
    `--write` measures each as the slug found — the model's own page, which
    CONTRIBUTING reads where the lane names no variant — and a reviewer whose
    lane serves another variant names that one instead."""
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


def keep_scores(path: Path, entries: list[Entry], board: dict[str, Scored], today: date) -> None:
    """The scores the render draws, kept on every --write run whether or not a
    mark moved: a score moves inside its tier as the index re-measures, and the
    picture should say what the board says today. A family whose aa_model the
    board no longer lists keeps its mark in the registry and has no score here."""
    top = index_top(board)
    measured = {m.family: board[m.aa_model] for e in entries for m in e.models
                if m.aa_model and m.aa_model in board and board[m.aa_model].index is not None}
    # To the tenth the pictures print: the board recomputes its decimals, and a
    # file that changed on every run would bury the day a score really moved.
    data = {"read_on": today.isoformat(), "source": LEADERBOARD_URL,
            "top": {"slug": top.slug, "name": top.name, "index": round(top.index, 1)},
            "median": round(index_median(board), 1),
            "families": {family: {"slug": s.slug, "index": round(s.index, 1),
                                  "estimated": s.estimated}
                         for family, s in sorted(measured.items())}}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _tier_name(tier: Tier | None) -> str:
    return tier.value if tier else "no tier"


async def _amain(registry: Path, write: bool, scores: Path | None = None) -> int:
    entries = load_registry(registry)
    async with httpx.AsyncClient(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(LEADERBOARD_URL)
        resp.raise_for_status()
        board = await read_leaderboard(client, resp.text)
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
        score = f"{m.score.index:.1f}" if m.score.index is not None else "no current score"
        print(f"  {m.family}: {_tier_name(m.registered)} → {_tier_name(m.measured)} "
              f"({score} on {m.aa_model}{estimated})")
    for m in unknown:
        print(f"  {m.family}: {m.aa_model} is not on the leaderboard — the mark stays "
              f"{_tier_name(m.registered)} until the family names a model that is")
    # A bare family is measured as the board's model of its name (see
    # unmeasured); an aa_model named by hand is never replaced.
    bare = unmeasured(live, board)
    for family, scored in bare:
        tier = _tier_name(measured_tier(scored.index, top.index, median))
        if write:
            print(f"  {family}: measured as {scored.slug} — {scored.index:.1f}, {tier}; name "
                  "another aa_model if the lane serves another variant")
        else:
            print(f"  {family}: no aa_model — the leaderboard scores {scored.slug} at "
                  f"{scored.index:.1f} ({tier}); --write measures it as that")
    if write and (moved or bare):
        tiers = {m.family: m.measured for m in moved}
        named = {family: scored for family, scored in bare}
        for e in entries:
            for fam in e.models:
                if fam.family in named and fam.aa_model is None:
                    fam.aa_model = named[fam.family].slug
                    fam.tier = measured_tier(named[fam.family].index, top.index, median)
                elif fam.family in tiers:
                    fam.tier = tiers[fam.family]
        save_registry(registry, entries)
    # Only where the caller names the file: the command always does, and a test
    # that measures a registry of its own never writes over the list's scores.
    if write and scores is not None:
        keep_scores(scores, entries, board, date.today())
    print(f"{len(marks)} family bindings checked, {len(moved)} marks "
          f"{'re-written' if write else 'moved'}, {len(unknown)} not on the leaderboard, "
          f"{sum(m.score is not None and m.score.index is None for m in marks)} without a current score, "
          f"{len(bare)} unmeasured that would reach a tier"
          f"{' — measured now' if write and bare else ''}")
    return 1 if unknown or (moved and not write) else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--write", action="store_true",
                        help="re-write the marks that moved on every row carrying the family, "
                             "and measure a bare family the board scores by its own name")
    parser.add_argument("--scores", type=Path, default=SCORES_PATH,
                        help="where --write keeps the scores it read (the README draws them)")
    args = parser.parse_args()
    sys.exit(asyncio.run(_amain(args.registry, args.write, args.scores)))
