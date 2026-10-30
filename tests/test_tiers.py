"""A tier is a measurement: the Artificial Analysis Intelligence Index, read
back off the leaderboard, decides it. These tests pin the reading and the rule."""
import json
import gzip
import hashlib
from datetime import date
from pathlib import Path

import httpx
import pytest
import respx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
    payload = json.dumps({"name": "Artificial Analysis Intelligence Index v5.0"})
    payload += "".join(f'{i}:["$","$L3c",null,{json.dumps({"models": a})}]\n'
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


@pytest.mark.parametrize('version', ['6.0', None, 'ambiguous'])
@respx.mock
async def test_an_unreviewed_index_revision_cannot_overwrite_tiers_or_measurements(tmp_path, version):
    metadata = '' if version is None else json.dumps({'name':
        'Artificial Analysis Intelligence Index v' +
        ('5.0' if version == 'ambiguous' else version)})
    if version == 'ambiguous':
        metadata += json.dumps({'name': 'Artificial Analysis Intelligence Index v6.0'})
    payload = metadata + json.dumps({'models': SCORED})
    body = '<script>self.__next_f.push([1,' + json.dumps(payload) + '])</script>'
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=body))
    registry, scores = tmp_path / 'registry.yaml', tmp_path / 'scores.json'
    save_registry(registry, [entry('a', {
        'family': 'glm-5.3', 'aa_model': 'glm-5-3', 'tier': 'strong'})])
    previous = registry.read_bytes()
    scores.write_text('previous measurement')
    with pytest.raises(ValueError, match='version'):
        await _amain(registry, write=True, scores=scores)
    assert registry.read_bytes() == previous
    assert scores.read_text() == 'previous measurement'


def test_the_scores_are_read_from_the_table_the_page_ships():
    models = parse_leaderboard(page())
    assert models["glm-5-3"].index == 44.9 and not models["glm-5-3"].deprecated
    assert models["agnes-3-0-flash"].estimated
    assert models["no-score-yet"].index is None


def test_a_page_with_no_scored_table_is_an_error_not_an_empty_index():
    import pytest
    with pytest.raises(ValueError, match="no scored models"):
        parse_leaderboard("<html><body>a redesign</body></html>")


@pytest.mark.asyncio
@pytest.mark.parametrize("table_key", ["models", "initialModels"])
@respx.mock
async def test_scored_table_props_are_read_through_the_http_writer(tmp_path, table_key):
    # Artificial Analysis /leaderboards/models, checked 2026-10-19: scored rows
    # now arrive in initialModels beside className, not as an object's first key.
    payload = '0:["$","div",null,' + json.dumps({
        "className": "container", table_key: SCORED,
        "name": "Artificial Analysis Intelligence Index v5.0",
    }) + ']\n'
    body = '<script>self.__next_f.push([1,' + json.dumps(payload) + '])</script>'
    route = respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=body))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [entry("a", {
        "family": "glm-5.3", "aa_model": "glm-5-3", "tier": "strong",
    })])

    assert await _amain(registry, write=True, scores=scores) == 0
    assert route.called
    assert load_registry(registry)[0].models[0].tier is Tier.FRONTIER
    measured = json.loads(scores.read_text())
    assert measured["top"]["slug"] == "claude-fable-5-1"
    assert measured["families"]["glm-5.3"]["index"] == 44.9


def manifest_page(key):
    # The current page's initialModels omits older models; its own manifest
    # supplies the complete table. Artificial Analysis, checked 2026-10-19.
    props = {"name": "Artificial Analysis Intelligence Index v5.0",
             "initialModels": [m for m in SCORED if not m["deprecated"]],
             "manifest": {"path": "/data/0123456789abcdef.txt"}}
    if key is not None:
        props["manifest"]["key"] = key.hex()
    payload = '0:["$","div",null,' + json.dumps(props) + ']\n'
    return '<script>self.__next_f.push([1,' + json.dumps(payload) + '])</script>'


@pytest.mark.parametrize("encrypted", [False, True])
@respx.mock
async def test_writer_reads_the_complete_manifest_including_older_models(tmp_path, encrypted):
    key = bytes(range(32)) if encrypted else None
    body = json.dumps(SCORED).encode()
    if key is not None:
        body = AESGCM(key).encrypt(hashlib.sha256(key).digest()[:12], gzip.compress(body), None)
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=manifest_page(key)))
    data = respx.get("https://artificialanalysis.ai/data/0123456789abcdef.txt").mock(
        return_value=httpx.Response(200, content=body))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [entry("a", {"family": "old-giant", "aa_model": "old-giant", "tier":"frontier"})])

    assert await _amain(registry, write=True, scores=scores) == 0
    assert data.called
    measured = json.loads(scores.read_text())
    assert "old-giant" not in measured["families"]
    assert measured["unscored"]["old-giant"] == {"slug":"old-giant", "reason":"deprecated"}
    assert measured["version"] == "5.0"
    model=load_registry(registry)[0].models[0]
    assert model.family == 'old-giant' and model.aa_model == 'old-giant'
    assert model.tier is None
    assert measured["top"]["slug"] == "claude-fable-5-1"
    assert measured["median"] == 41.2


@pytest.mark.parametrize("failure", ["unreadable", "tampered"])
@respx.mock
async def test_failed_manifest_read_preserves_the_registry_and_scores(tmp_path, failure):
    key = bytes(range(32))
    body = AESGCM(key).encrypt(hashlib.sha256(key).digest()[:12], gzip.compress(json.dumps(SCORED).encode()), None)
    tampered = body[:-1] + bytes([body[-1] ^ 1])
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=manifest_page(key)))
    respx.get("https://artificialanalysis.ai/data/0123456789abcdef.txt").mock(
        return_value=httpx.Response(403 if failure == "unreadable" else 200, content=tampered))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [entry("a", {"family": "glm-5.3", "aa_model": "glm-5-3", "tier": "strong"})])
    previous = registry.read_bytes()
    scores.write_text("previous scores")

    with pytest.raises((ValueError, httpx.HTTPStatusError)):
        await _amain(registry, write=True, scores=scores)
    assert registry.read_bytes() == previous
    assert scores.read_text() == "previous scores"


@pytest.mark.parametrize("path", ["https://other.example/data/models.json", "//127.0.0.1/private", "/data/../private.json"])
@respx.mock
async def test_manifest_cannot_redirect_the_reader_to_an_arbitrary_source(tmp_path, path):
    page = manifest_page(None).replace('/data/0123456789abcdef.txt', path)
    route = respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=page))
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [entry("a", {"family": "glm-5.3", "aa_model": "glm-5-3"})])
    with pytest.raises(ValueError, match="same-origin data file"):
        await _amain(registry, write=False)
    assert route.call_count == 1


@pytest.mark.parametrize("manifest", [None, []])
@respx.mock
async def test_unknown_manifest_shape_cannot_fall_back_to_a_partial_table(tmp_path, manifest):
    props = {"initialModels": SCORED, "manifest": manifest}
    payload = '0:["$","div",null,' + json.dumps(props) + ']\n'
    body = '<script>self.__next_f.push([1,' + json.dumps(payload) + '])</script>'
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=body))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [entry("a", {"family": "glm-5.3", "aa_model": "glm-5-3"})])
    previous = registry.read_bytes()
    scores.write_text("previous scores")
    with pytest.raises(ValueError, match="manifest"):
        await _amain(registry, write=True, scores=scores)
    assert registry.read_bytes() == previous
    assert scores.read_text() == "previous scores"


@pytest.mark.parametrize("value", [None, 0, "N/A", False, "missing-field"])
@respx.mock
async def test_current_null_score_clears_a_tier_without_guessing_missing_scores(tmp_path, value):
    # AA's complete v5 table explicitly uses null for N/A, while a missing or
    # malformed measurement remains inconclusive (leaderboard/model cards, 2026-10-29).
    rows = [dict(m) for m in SCORED]
    target = next(m for m in rows if m["slug"] == "no-score-yet")
    if value == "missing-field":
        del target["intelligenceIndex"]
    else:
        target["intelligenceIndex"] = value
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=manifest_page(None)))
    route = respx.get("https://artificialanalysis.ai/data/0123456789abcdef.txt").mock(
        return_value=httpx.Response(200, json=rows))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [entry("a", {
        "family": "unscored", "aa_model": "no-score-yet", "tier": "strong",
    })])
    known = value is None or type(value) is int
    assert await _amain(registry, write=True, scores=scores) == (0 if known else 1)
    assert route.called
    model = load_registry(registry)[0].models[0]
    assert model.family == "unscored" and model.aa_model == "no-score-yet"
    assert model.tier is (None if known else Tier.STRONG)
    measured = json.loads(scores.read_text())["families"]
    if type(value) is int:
        assert measured["unscored"]["index"] == 0
    else:
        assert "unscored" not in measured


@pytest.mark.parametrize("rows", [
    [SCORED[-1]],
    [SCORED[1], SCORED[-1]],
    SCORED + [{**SCORED[-1], "intelligenceIndex": 42}],
    SCORED + [{"slug": "no-score-yet"}],
    SCORED + [{**SCORED[-1], "intelligenceIndex": "N/A"}],
])
@respx.mock
async def test_unusable_or_ambiguous_table_cannot_clear_existing_tiers(tmp_path, rows):
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=manifest_page(None)))
    respx.get("https://artificialanalysis.ai/data/0123456789abcdef.txt").mock(
        return_value=httpx.Response(200, json=rows))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [entry("a", {
        "family": "unscored", "aa_model": "no-score-yet", "tier": "strong",
    })])
    previous = registry.read_bytes()
    scores.write_text("previous scores")
    with pytest.raises(ValueError):
        await _amain(registry, write=True, scores=scores)
    assert registry.read_bytes() == previous
    assert scores.read_text() == "previous scores"


def test_the_top_of_the_index_counts_current_models_only():
    """A deprecated model scoring higher would set a bar nothing current can reach."""
    assert index_top(parse_leaderboard(page())).slug == "claude-fable-5-1"


def test_a_tier_is_how_close_the_lane_s_model_scores_to_the_top():
    top, median = 53.37, 13.2
    assert measured_tier(top - FRONTIER_WITHIN, top, median) is Tier.FRONTIER
    assert measured_tier(top - FRONTIER_WITHIN - 0.01, top, median) is Tier.STRONG
    assert measured_tier(top - STRONG_WITHIN, top, median) is Tier.STRONG
    assert measured_tier(top - STRONG_WITHIN - 0.01, top, median) is Tier.NOTABLE


def test_below_the_strong_bar_the_upper_half_of_the_index_is_notable():
    """Below the strong bar, a score at or above the median of the current models
    is `notable` and one below it has no tier: a model readers still look for
    gets a page, and a catalog's weakest models stay unmarked."""
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
    """A family carries one tier, so --write moves a mark on every row that carries
    the family; a run without --write only reports the move, and fails."""
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
    assert ("Intelligence Index v5.0; top: Claude Fable 5.1 (max), 53.4 — frontier from 43.4, strong from 28.4, "
            "notable from 41.2, the median of its 5 current models") in out
    assert "gemini-3.8-flash: frontier → strong (41.2 on gemini-3-8-flash)" in out


@respx.mock
async def test_a_row_that_disagrees_with_the_measurement_moves_whatever_the_file_order(
        tmp_path: Path):
    """Any row whose mark is off the measurement moves the family, wherever it sits
    in the file: a new bare row beside an older, correct one is re-marked too."""
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
    """The review names each family no row measures whose name, spelled as a slug
    (a hyphen for a dot), is a model the board scores into a tier: only a listed
    slug is offered, never a guess."""
    from freetier_radar.tiers import unmeasured
    entries = [
        entry("a", {"family": "glm-5.3"}, {"family": "gemini-3.8-flash", "aa_model": "gemini-3-8-flash"},
              {"family": "no-such-model"}, {"family": "nvidia-nemotron-3-ultra-550b-a55b"}),
        entry("b", {"family": "gemini-3.8-flash"}),
    ]
    found = unmeasured(entries, parse_leaderboard(page()))
    # Measurements remain useful in the comparison below every tier boundary.
    assert [(family, scored.slug) for family, scored in found] == [
        ("glm-5.3", "glm-5-3"),
        ("nvidia-nemotron-3-ultra-550b-a55b", "nvidia-nemotron-3-ultra-550b-a55b")]


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
    assert [(f, s.slug) for f, s in unmeasured(entries, board)] == [
        ("qwen3.7-max", "qwen3-7-max"), ("tiny-1b", "tiny-1b")]


@respx.mock
async def test_write_measures_a_bare_family_the_board_scores_by_its_own_name(tmp_path: Path, capsys):
    """Where the board scores a model of exactly a bare family's name, --write names
    that slug on every row carrying the family and marks it, so marks follow the
    index without a reviewer; a model below every tier is still measured."""
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=page()))
    registry = tmp_path / "registry.yaml"
    gone = entry("gone", {"family": "glm-5.3"})
    gone.retired_on = date(2026, 9, 1)
    save_registry(registry, [
        entry("a", {"family": "glm-5.3"}, {"family": "nvidia-nemotron-3-ultra-550b-a55b"}),
        entry("b", {"family": "glm-5.3"}),
        # an archived row carrying the family is measured with it: a family is
        # one model, and freetier-check holds every row that names it to one slug
        gone,
    ])
    assert await _amain(registry, write=True) == 0
    marks = {(e.id, m.family): (m.aa_model, m.tier) for e in load_registry(registry) for m in e.models}
    assert marks == {("a", "glm-5.3"): ("glm-5-3", Tier.FRONTIER),
                     ("a", "nvidia-nemotron-3-ultra-550b-a55b"): ("nvidia-nemotron-3-ultra-550b-a55b", None),
                     ("b", "glm-5.3"): ("glm-5-3", Tier.FRONTIER),
                     ("gone", "glm-5.3"): ("glm-5-3", Tier.FRONTIER)}
    assert "glm-5.3: measured as glm-5-3 — 44.9, frontier" in capsys.readouterr().out


@respx.mock
async def test_write_keeps_every_score_it_read_for_the_readme_to_draw(tmp_path: Path):
    """--write keeps what it read for the render, which reads no network: the day,
    the top, the median and every measured family's score, on every run; a report
    run keeps nothing."""
    respx.get(LEADERBOARD_URL).mock(return_value=httpx.Response(200, text=page()))
    registry, scores = tmp_path / "registry.yaml", tmp_path / "scores.json"
    save_registry(registry, [
        entry("a", {"family": "glm-5.3", "tier": "frontier", "aa_model": "glm-5-3"},
              {"family": "agnes-3.0-flash", "tier": "strong", "aa_model": "agnes-3-0-flash"},
              {"family": "renamed", "tier": "strong", "aa_model": "no-longer-listed"}),
        entry("b", {"family": "gemini-3.8-flash"}),
    ])
    assert await _amain(registry, write=False, scores=scores) == 1
    assert not scores.exists()

    await _amain(registry, write=True, scores=scores)
    kept = json.loads(scores.read_text(encoding="utf-8"))
    assert kept["read_on"] == date.today().isoformat()
    assert kept["source"] == LEADERBOARD_URL
    assert kept["version"] == '5.0'
    assert kept['unscored']['renamed'] == {'slug':'no-longer-listed','reason':'missing'}
    assert kept["top"] == {"slug": "claude-fable-5-1", "name": "Claude Fable 5.1 (max)", "index": 53.4}
    assert kept["median"] == 41.2
    # measured families, the bare one measured this run included; one the board
    # lost keeps its mark in the registry and has no score to keep
    assert kept["families"] == {
        "agnes-3.0-flash": {"slug": "agnes-3-0-flash", "index": 35.5, "estimated": True},
        "gemini-3.8-flash": {"slug": "gemini-3-8-flash", "index": 41.2, "estimated": False},
        "glm-5.3": {"slug": "glm-5-3", "index": 44.9, "estimated": False}}
    assert list(kept["families"]) == sorted(kept["families"])
