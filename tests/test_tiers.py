"""A tier is a measurement: the Artificial Analysis Intelligence Index, read
back off the leaderboard, decides it. These tests pin the reading and the rule."""
import json
from datetime import date
from pathlib import Path

import httpx
import respx

from freetier_radar.models import Entry, Tier, load_registry, save_registry
from freetier_radar.tiers import (FRONTIER_WITHIN, LEADERBOARD_URL, STRONG_WITHIN, Scored, _amain,
                                  index_median, index_top, measured_tier, parse_leaderboard,
                                  review)

SCORED = [
    {"slug": "claude-fable-5-1", "name": "Claude Fable 5.1 (max)", "deprecated": False,
     "intelligenceIndex": 53.37, "intelligenceIndexIsEstimated": False},
    {"slug": "old-giant", "name": "Old Giant", "deprecated": True,
     "intelligenceIndex": 60.0, "intelligenceIndexIsEstimated": False},
    {"slug": "glm-5-3", "name": "GLM-5.3 (max)", "deprecated": False,
     "intelligenceIndex": 44.9, "intelligenceIndexIsEstimated": False},
    {"slug": "gemini-3-8-flash", "name": "Gemini 3.8 Flash (high)", "deprecated": False,
     "intelligenceIndex": 41.2, "intelligenceIndexIsEstimated": False},
    {"slug": "agnes-3-0-flash", "name": "Agnes 3.0 Flash", "deprecated": False,
     "intelligenceIndex": 35.5, "intelligenceIndexIsEstimated": True},
    {"slug": "nvidia-nemotron-3-ultra-550b-a55b", "name": "Nemotron 3 Ultra", "deprecated": False,
     "intelligenceIndex": 23.4, "intelligenceIndexIsEstimated": False},
    {"slug": "no-score-yet", "name": "Unscored", "deprecated": False, "intelligenceIndex": None},
]


def flight_page(*arrays: list[dict]) -> str:
    """The leaderboard as Next.js ships it: the data inside escaped strings
    pushed to self.__next_f, split across chunks at arbitrary points."""
    payload = "".join(f'{i}:["$","$L3c",null,{json.dumps({"models": a})}]\n'
                      for i, a in enumerate(arrays))
    cut = len(payload) // 2
    return "<html><body>" + "".join(
        f"<script>self.__next_f.push([1,{json.dumps(part)}])</script>"
        for part in (payload[:cut], payload[cut:])) + "</body></html>"


def page() -> str:
    # The real page ships a models list without scores first — the selector —
    # and the scored table after it.
    unscored = [{"slug": m["slug"], "name": m["name"], "deprecated": m["deprecated"]} for m in SCORED]
    return flight_page(unscored, SCORED)


def test_the_scores_are_read_from_the_table_the_page_ships():
    models = parse_leaderboard(page())
    assert models["glm-5-3"].index == 44.9 and not models["glm-5-3"].deprecated
    assert models["agnes-3-0-flash"].estimated
    assert "no-score-yet" not in models


def test_a_page_with_no_scored_table_is_an_error_not_an_empty_index():
    import pytest
    with pytest.raises(ValueError, match="no scored models"):
        parse_leaderboard("<html><body>a redesign</body></html>")


def test_the_top_of_the_index_counts_current_models_only():
    """A deprecated model scoring higher would set a bar nothing current can
    reach, which is how a tier stops meaning anything."""
    assert index_top(parse_leaderboard(page())).slug == "claude-fable-5-1"


def test_a_tier_is_how_close_the_lane_s_model_scores_to_the_top():
    top, median = 53.37, 13.2
    assert measured_tier(top - FRONTIER_WITHIN, top, median) is Tier.FRONTIER
    assert measured_tier(top - FRONTIER_WITHIN - 0.01, top, median) is Tier.STRONG
    assert measured_tier(top - STRONG_WITHIN, top, median) is Tier.STRONG
    assert measured_tier(top - STRONG_WITHIN - 0.01, top, median) is Tier.NOTABLE


def test_below_the_strong_bar_the_upper_half_of_the_index_is_notable():
    """A model below the strong bar can still be one readers come looking for:
    on 2026-09-26 the top was Claude Opus 5.5 at 57.6, and Claude Opus 4.6
    (26.4), Claude Sonnet 4.6 (24.7) and Gemini 3.5 Flash (32.6, a hair under
    the bar) each had no page. `notable` is a score at or above the median of
    the current models the index scores — its upper half — and below that no
    tier at all, so the weakest models a catalog lists stay marks-free."""
    top, median = 57.6, 13.2
    assert measured_tier(26.4, top, median) is Tier.NOTABLE
    assert measured_tier(median, top, median) is Tier.NOTABLE
    assert measured_tier(median - 0.01, top, median) is None
    # a median above the strong bar leaves no room between them: strong wins
    assert measured_tier(40.0, 53.37, 41.2) is Tier.STRONG


def test_the_median_counts_current_models_only():
    """The same population as the top: a deprecated model is on the board as
    history, not as one of the models a score is measured against."""
    assert index_median(parse_leaderboard(page())) == 41.2


def entry(id: str, *families: dict) -> Entry:
    return Entry.model_validate({
        "id": id, "name": id, "category": "aggregator", "url": f"https://{id}.example",
        "offering": "stuff", "first_seen": date(2026, 9, 1), "last_verified": date(2026, 9, 17),
        "models": list(families),
        "probe": {"type": "page-keywords", "endpoint": f"https://{id}.example", "keywords": ["x-mini-2"]}})


def test_review_says_which_marks_the_index_no_longer_backs():
    entries = [
        entry("a", {"family": "glm-5.3", "tier": "frontier", "aa_model": "glm-5-3"},
              {"family": "gemini-3.8-flash", "tier": "frontier", "aa_model": "gemini-3-8-flash"},
              {"family": "nemotron-3-ultra", "tier": "strong",
               "aa_model": "nvidia-nemotron-3-ultra-550b-a55b"},
              {"family": "unmeasured"}),
        entry("b", {"family": "agnes-3.0-flash", "aa_model": "agnes-3-0-flash"},
              {"family": "renamed", "tier": "strong", "aa_model": "gone-from-the-board"}),
    ]
    top, marks = review(entries, parse_leaderboard(page()))
    assert top.slug == "claude-fable-5-1"
    moved = {m.family: (m.registered, m.measured) for m in marks if m.moved}
    assert moved == {"gemini-3.8-flash": (Tier.FRONTIER, Tier.STRONG),
                     "nemotron-3-ultra": (Tier.STRONG, None),
                     "agnes-3.0-flash": (None, Tier.STRONG)}
    assert [m.family for m in marks if m.unknown] == ["renamed"]
    assert "unmeasured" not in {m.family for m in marks}


@respx.mock
async def test_write_re_marks_every_row_that_carries_the_family(tmp_path: Path, capsys):
    """One tier per family, so a mark that moves moves on every row at once —
    and a family the board no longer knows keeps its mark and fails the run,
    because a guess is not a measurement."""
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=page()))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [
        entry("a", {"family": "gemini-3.8-flash", "tier": "frontier", "aa_model": "gemini-3-8-flash"}),
        entry("b", {"family": "gemini-3.8-flash", "tier": "frontier", "aa_model": "gemini-3-8-flash"},
              {"family": "glm-5.3", "tier": "frontier", "aa_model": "glm-5-3"}),
    ])
    assert await _amain(registry, write=False) == 1
    assert [m.tier for e in load_registry(registry) for m in e.models] == [Tier.FRONTIER] * 3

    assert await _amain(registry, write=True) == 0
    tiers = {(e.id, m.family): m.tier for e in load_registry(registry) for m in e.models}
    assert tiers == {("a", "gemini-3.8-flash"): Tier.STRONG, ("b", "gemini-3.8-flash"): Tier.STRONG,
                     ("b", "glm-5.3"): Tier.FRONTIER}
    out = capsys.readouterr().out
    assert ("top of the index: Claude Fable 5.1 (max), 53.4 — frontier from 43.4, strong from 28.4, "
            "notable from 41.2, the median of its 5 current models") in out
    assert "gemini-3.8-flash: frontier → strong (41.2 on gemini-3-8-flash)" in out


@respx.mock
async def test_a_row_that_disagrees_with_the_measurement_moves_whatever_the_file_order(
        tmp_path: Path):
    """A new row carrying a family the registry already measured came in with no
    tier on 2026-09-21 (Dahl Inference, deepseek-v4-flash), and the review read
    the family's mark off the first row in the file — which agreed with the
    board — so --write left the new row bare and freetier-check refused the
    registry: one family, two marks. Any row off the measurement moves it."""
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=page()))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [
        entry("old", {"family": "glm-5.3", "tier": "frontier", "aa_model": "glm-5-3"}),
        entry("new", {"family": "glm-5.3", "aa_model": "glm-5-3"}),
    ])
    top, marks = review(load_registry(registry), parse_leaderboard(page()))
    assert [(m.family, m.registered, m.measured) for m in marks if m.moved] == [
        ("glm-5.3", None, Tier.FRONTIER)]

    assert await _amain(registry, write=True) == 0
    assert [m.tier for e in load_registry(registry) for m in e.models] == [Tier.FRONTIER] * 2


def test_a_new_model_the_board_scores_is_named_for_the_reviewer():
    """A family added with no aa_model carries no tier, and until 2026-09-26
    nothing said so: a new strong model stayed off the strong list, and off a
    page of its own while one row served it, until someone remembered. The
    review names every family no row measures whose name, read the way the
    board spells a slug — a hyphen for a dot — is a model the board scores.
    Only a slug the board lists is offered, never a guess, and the reviewer
    names the variant the lane serves."""
    from freetier_radar.tiers import unmeasured
    entries = [
        entry("a", {"family": "glm-5.3"}, {"family": "gemini-3.8-flash", "aa_model": "gemini-3-8-flash"},
              {"family": "no-such-model"}, {"family": "nvidia-nemotron-3-ultra-550b-a55b"}),
        entry("b", {"family": "gemini-3.8-flash"}),
    ]
    found = unmeasured(entries, parse_leaderboard(page()))
    # gemini-3.8-flash is measured on row a; nemotron scores below every bar,
    # so measuring it would change nothing a page says.
    assert [(family, scored.slug) for family, scored in found] == [("glm-5.3", "glm-5-3")]


def test_the_reviewer_is_told_of_a_model_that_would_be_notable():
    """Measuring a model below the strong bar changes what a page says now —
    whether the model has one — so the review names a bare family the board
    scores in its upper half, and still not one below it."""
    from freetier_radar.tiers import unmeasured

    board = {s.slug: s for s in [
        Scored("claude-opus-5-5", "Claude Opus 5.5", 57.6, False, False),
        Scored("claude-opus-4-6", "Claude Opus 4.6", 26.4, True, False),
        Scored("qwen3-7-max", "Qwen3.7 Max", 29.5, False, False),
        Scored("tiny-1b", "Tiny 1B", 4.0, False, False),
        Scored("small-3b", "Small 3B", 9.0, False, False)]}
    assert index_median(board) == 19.25  # 4, 9, 29.5, 57.6 — the deprecated one sits out
    entries = [entry("a", {"family": "qwen3.7-max"}, {"family": "tiny-1b"})]
    assert [(f, s.slug) for f, s in unmeasured(entries, board)] == [("qwen3.7-max", "qwen3-7-max")]
