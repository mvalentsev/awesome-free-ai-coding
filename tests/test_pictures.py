import math
import re
from datetime import date

import pytest

from freetier_radar.pictures import (
    BEAM_PERIOD, DARK, LIGHT, NARROW_SHOWN, WIDE_SHOWN, Arc, Hero, hero_svg, hero_words,
    radar_svg,
)

HERO = Hero(live=80, no_card=76, models=150, strong=17, schedule="twice a week",
            arcs=(Arc("agents", "agents", 8), Arc("APIs", "apis", 31),
                  Arc("trials", "trials", 26), Arc("aggregators", "aggregators", 15)))

_DOT = re.compile(r'<circle class="dot (\w+)" cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" '
                  r'style="animation-delay:([\d.]+)s"/>')


def _dots(svg: str) -> list[tuple[str, float, float, float, float]]:
    return [(tone, float(x), float(y), float(r), float(d))
            for tone, x, y, r, d in _DOT.findall(svg)]


def _centre(svg: str) -> tuple[float, float]:
    x, y = re.search(r'<circle class="hub" cx="([\d.]+)" cy="([\d.]+)"', svg).groups()
    return float(x), float(y)


def _view_width(svg: str) -> float:
    return float(re.search(r'viewBox="0 0 ([\d.]+) [\d.]+"', svg).group(1))


@pytest.mark.parametrize("narrow", [False, True])
def test_the_radar_draws_one_dot_per_live_offer_in_its_section_colour(narrow):
    """The radar is the list: a dot is a live row, so a row that dies takes its
    dot with it on the next render, and the colours are the sections."""
    dots = _dots(hero_svg(HERO, LIGHT, narrow=narrow))
    assert len(dots) == 80
    assert {tone: sum(1 for d in dots if d[0] == tone) for tone in
            ("agents", "apis", "trials", "aggregators")} == {
        "agents": 8, "apis": 31, "trials": 26, "aggregators": 15}


def test_the_sites_mark_is_the_heros_radar_without_its_words():
    """The site's mark beside its name is the hero's radar alone: a dot per live
    offer in its section's colour, both palettes in one file for the reader's
    theme, and no word to shrink on a phone."""
    svg = radar_svg(HERO)
    dots = _dots(svg)
    assert len(dots) == 80 and {d[0] for d in dots} == {"agents", "apis", "trials", "aggregators"}
    assert "@media (prefers-color-scheme: dark)" in svg
    assert "<text" not in svg
    assert re.search(r"<title[^>]*>(.*?)</title>", svg).group(1) == hero_words(HERO)
    x, y = _centre(svg)
    assert (x, y) == (_view_width(svg) / 2, _view_width(svg) / 2)


@pytest.mark.parametrize("narrow", [False, True])
def test_a_dot_lights_up_when_the_beam_reaches_its_bearing(narrow):
    """The beam's leading edge starts at north and turns clockwise once a
    period; each dot's delay is the moment it passes, not decoration."""
    svg = hero_svg(HERO, DARK, narrow=narrow)
    cx, cy = _centre(svg)
    for _, x, y, _, delay in _dots(svg):
        bearing = math.degrees(math.atan2(x - cx, cy - y)) % 360
        assert delay == pytest.approx(bearing / 360 * BEAM_PERIOD, abs=0.02)


@pytest.mark.parametrize("counts", [(8, 31, 26, 15), (1, 1, 1, 77), (40, 0, 40, 0), (3, 0, 0, 0)])
def test_no_two_dots_overlap(counts):
    """A dot hidden under another is a row the picture does not show."""
    hero = Hero(live=sum(counts), no_card=0, models=0, strong=0, schedule="twice a week",
                arcs=tuple(Arc(t, t, n) for t, n in zip(
                    ("agents", "apis", "trials", "aggregators"), counts)))
    for narrow in (False, True):
        dots = _dots(hero_svg(hero, LIGHT, narrow=narrow))
        assert len(dots) == sum(counts)
        for i, a in enumerate(dots):
            for b in dots[i + 1:]:
                assert math.dist(a[1:3], b[1:3]) >= a[3] + b[3], (narrow, a, b)


@pytest.mark.parametrize("narrow", [False, True])
def test_the_counters_are_the_figures_they_are_given(narrow):
    svg = hero_svg(HERO, LIGHT, narrow=narrow)
    for figure, label in (("80", "live offers"), ("76", "need no card"),
                          ("150", "free models"), ("17", "strong models")):
        assert f">{figure}</text>" in svg and f">{label}</text>" in svg
    assert "twice a week" in svg


def test_every_word_reads_at_the_width_a_reader_sees_it():
    """GitHub scales an image down to the column: 823 pixels in a 1280-pixel
    desktop window and 324 on a 390-point iPhone, signed out, on 2026-09-28.
    Scaled that far, a label drawn at fifteen units in the wide hero would be
    ten pixels on the desktop — so
    the wide hero draws nothing that lands under eleven on the desktop, and
    the narrow one, the only one a phone is served, nothing under eleven there."""
    for narrow, shown in ((False, WIDE_SHOWN), (True, NARROW_SHOWN)):
        svg = hero_svg(HERO, LIGHT, narrow=narrow)
        scale = shown / _view_width(svg)
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', svg)]
        assert sizes and min(sizes) * scale >= 11, (narrow, min(sizes) * scale)


def test_the_narrow_hero_follows_the_readers_theme_and_the_wide_pair_does_not():
    """A phone is served the narrow hero whatever its theme, so that one picture
    carries both palettes and the reader's preference picks one; the wide pair
    is chosen between by the README's <picture>, so each holds one palette."""
    narrow = hero_svg(HERO, None, narrow=True)
    assert "@media (prefers-color-scheme: dark)" in narrow
    assert LIGHT.canvas in narrow and DARK.canvas in narrow
    for palette, other in ((LIGHT, DARK), (DARK, LIGHT)):
        wide = hero_svg(HERO, palette)
        assert "prefers-color-scheme" not in wide
        assert palette.canvas in wide and other.canvas not in wide


def test_a_reader_who_asked_for_less_motion_sees_every_dot_lit():
    svg = hero_svg(HERO, LIGHT)
    assert re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{[^}]*\.dot\s*\{[^}]*"
                     r"animation: none", svg)


def test_the_same_figures_draw_the_same_picture():
    """render --check compares bytes, so nothing here may depend on the run."""
    assert hero_svg(HERO, DARK) == hero_svg(HERO, DARK)
    assert hero_svg(HERO, None, narrow=True) == hero_svg(HERO, None, narrow=True)


def test_the_picture_says_what_it_shows_to_a_screen_reader():
    svg = hero_svg(HERO, LIGHT)
    title = re.search(r"<title[^>]*>(.*?)</title>", svg).group(1)
    assert "80 live offers" in title and "one dot per live offer" in title


from freetier_radar.pictures import NARROW_BARS, Bar, Chart, chart_svg  # noqa: E402

CHART = Chart(top_name="Claude Opus 5.5", top_score=57.6, read_on=date(2026, 9, 27),
              frontier_within=10.0, strong_within=25.0,
              bars=(Bar("qwen3.8-27b", 33.7, 7, False, False), Bar("glm-5.3", 44.8, 2, False, False),
                    Bar("qwen3.8-max", 45.4, 1, False, False), Bar("kimi-k3", 43.6, 2, False, True),
                    Bar("gemini-3.8-flash", 40.9, 2, False, False),
                    Bar("gemini-3.7-flash", 39.1, 2, False, False),
                    Bar("gemini-3.6-flash", 34.0, 2, False, False), Bar("glm-5.2", 33.7, 2, False, False),
                    Bar("gpt-6-luna", 37.3, 1, False, False),
                    Bar("deepseek-v4-pro", 36.0, 1, False, False),
                    Bar("muse-spark-1.2", 39.6, 1, False, False),
                    Bar("frontier-x", 49.0, 3, True, False)))

_BAR = re.compile(r'<rect class="bar (strong|frontier)" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)"')
_LABEL = re.compile(r'<text class="t label"[^>]*>([^<]+)</text>')


@pytest.mark.parametrize("narrow", [False, True])
def test_the_chart_ranks_the_models_by_score_and_draws_each_to_scale(narrow):
    """A bar is a model some live offer serves free, as long as its score on an
    axis that starts at zero and ends at the top of the index: the gap to the
    frontier is drawn as it is, not stretched."""
    svg = chart_svg(CHART, LIGHT, narrow=narrow)
    labels = _LABEL.findall(svg)
    ranked = sorted(CHART.bars, key=lambda b: (-b.score, b.family))
    shown = ranked[:NARROW_BARS] if narrow else ranked
    assert labels == [b.family for b in shown]
    bars = _BAR.findall(svg)
    assert [tier for tier, *_ in bars] == ["frontier" if b.frontier else "strong" for b in shown]
    widths = [float(w) for *_, w in bars]
    for bar, width in zip(shown, widths):
        assert width / widths[0] == pytest.approx(bar.score / shown[0].score, rel=0.01)
    axis = re.search(r'<line class="top" x1="([\d.]+)"', svg)
    left = float(bars[0][1])
    assert (float(axis.group(1)) - left) / widths[0] == pytest.approx(57.6 / 49.0, rel=0.01)


def test_the_phone_chart_names_what_it_leaves_for_the_list():
    svg = chart_svg(CHART, LIGHT, narrow=True)
    assert f"+{len(CHART.bars) - NARROW_BARS} more in the list below" in svg
    assert "more in the list below" not in chart_svg(CHART, LIGHT)


@pytest.mark.parametrize("narrow", [False, True])
def test_each_bar_says_its_score_and_how_many_offers_serve_it_free(narrow):
    svg = chart_svg(CHART, DARK, narrow=narrow)
    assert ">45.4<" in svg and " · 1 offer<" in svg and " · 2 offers<" in svg
    # the phone's ten leave the twelfth, the one seven offers serve, to the list
    assert (" · 7 offers<" in svg) is not narrow
    # Artificial Analysis marks a score it estimated; so does the chart
    assert ">43.6*<" in svg and "* estimated by Artificial Analysis" in svg
    assert "Claude Opus 5.5" in svg and "57.6" in svg and "2026-09-27" in svg


def test_no_footnote_without_an_estimate():
    plain = Chart(**{**CHART.__dict__, "bars": tuple(b for b in CHART.bars if not b.estimated)})
    assert "estimated by" not in chart_svg(plain, LIGHT)


def test_the_chart_reads_at_the_width_a_reader_sees_it():
    for narrow, shown in ((False, WIDE_SHOWN), (True, NARROW_SHOWN)):
        svg = chart_svg(CHART, LIGHT, narrow=narrow)
        scale = shown / _view_width(svg)
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', svg)]
        assert min(sizes) * scale >= 11, (narrow, min(sizes) * scale)


def test_the_phone_chart_follows_the_theme_and_the_same_bars_draw_the_same_bytes():
    assert "@media (prefers-color-scheme: dark)" in chart_svg(CHART, None, narrow=True)
    assert "prefers-color-scheme" not in chart_svg(CHART, DARK)
    assert chart_svg(CHART, None, narrow=True) == chart_svg(CHART, None, narrow=True)
