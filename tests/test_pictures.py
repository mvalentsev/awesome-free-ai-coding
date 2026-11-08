import math
import re
from datetime import date

import pytest

from freetier_radar.pictures import (
    BEAM_PERIOD, DARK, LIGHT, NARROW_SHOWN, WIDE_SHOWN, Arc, Hero, hero_svg, hero_words,
    radar_svg,
)

HERO = Hero(live=80, no_card=76, models=150, endpoints=17, schedule="twice a week",
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
    hero = Hero(live=sum(counts), no_card=0, models=0, endpoints=0, schedule="twice a week",
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
                          ("150", "free models"), ("17", "OpenAI-compatible")):
        assert f">{figure}</text>" in svg and f">{label}</text>" in svg
    assert "twice a week" in svg


@pytest.mark.parametrize("narrow", [False, True])
def test_hero_connection_coverage_is_independent_of_benchmark_classification(narrow):
    from freetier_radar.render import _hero
    facts = {"active_count": 8, "no_card_count": 6, "family_count": 12,
             "endpoint_count": 5, "strong_models": [], "schedule": "twice a week"}
    before = hero_svg(_hero([], facts), LIGHT, narrow=narrow)
    after = hero_svg(_hero([], {**facts, "strong_models": ["new leader"]}), LIGHT, narrow=narrow)
    assert before == after
    assert "5 OpenAI-compatible" in hero_words(_hero([], facts))


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


@pytest.mark.parametrize("narrow", [False, True])
def test_each_layout_follows_the_readers_theme_and_fixed_palette_links_stay_fixed(narrow):
    """Both layouts follow the theme; existing fixed-palette URLs retain theirs."""
    adaptive = hero_svg(HERO, None, narrow=narrow)
    assert "@media (prefers-color-scheme: dark)" in adaptive
    assert LIGHT.canvas in adaptive and DARK.canvas in adaptive
    for palette, other in ((LIGHT, DARK), (DARK, LIGHT)):
        wide = hero_svg(HERO, palette)
        assert "prefers-color-scheme" not in wide
        assert palette.canvas in wide and other.canvas not in wide


def test_a_reader_who_asked_for_less_motion_gets_a_still_picture():
    """The beam stops at north and every dot stays lit. The beam turns by a CSS
    animation for that: SMIL's <animate…> runs whatever the reader asked for.
    It turns about the hub, the point its group's style names."""
    for svg in (hero_svg(HERO, LIGHT), hero_svg(HERO, None, narrow=True), radar_svg(HERO)):
        still = re.search(r"@media \(prefers-reduced-motion: reduce\) (\{.*?\}\})", svg).group(1)
        assert re.search(r"\.dot \{ animation: none; opacity: 1 \}", still)
        assert re.search(r"\.turning \{ animation: none \}", still)
        assert "<animate" not in svg
        hub = re.search(r'<circle class="hub" cx="([\d.]+)" cy="([\d.]+)"', svg).groups()
        turning = re.search(r'<g class="turning" style="transform-origin:([\d.]+)px ([\d.]+)px">',
                            svg).groups()
        assert turning == hub


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
              bars=(Bar("qwen3.8-27b", 33.7, 7, False), Bar("glm-5.3", 44.8, 2, False),
                    Bar("qwen3.8-max", 45.4, 1, False), Bar("kimi-k3", 43.6, 2, True),
                    Bar("gemini-3.8-flash", 40.9, 2, False),
                    Bar("gemini-3.7-flash", 39.1, 2, False),
                    Bar("gemini-3.6-flash", 34.0, 2, False), Bar("glm-5.2", 33.7, 2, False),
                    Bar("gpt-6-luna", 37.3, 1, False),
                    Bar("deepseek-v4-pro", 36.0, 1, False),
                    Bar("muse-spark-1.2", 39.6, 1, False),
                    Bar("frontier-x", 49.0, 3, False)))

_BAR = re.compile(r'<rect class="bar" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)"')
_LABEL = re.compile(r'<text class="t label"[^>]*>([^<]+)</text>')


@pytest.mark.parametrize("narrow", [False, True])
def test_free_comparison_geometry_does_not_depend_on_an_unavailable_leader(narrow):
    from dataclasses import replace
    def widths(chart):
        return re.findall(r'<rect class="bar[^\"]*"[^>]*width="([\d.]+)"',
                          chart_svg(chart, LIGHT, narrow=narrow))
    assert widths(CHART) == widths(replace(CHART, top_name="New leader", top_score=100))


@pytest.mark.parametrize("narrow", [False, True])
def test_the_chart_ranks_the_models_by_score_and_draws_each_to_scale(narrow):
    """The numeric axis starts at zero; bar lengths preserve score ratios,
    with identical ticks in both widths and no implicit percent normalization."""
    svg = chart_svg(CHART, LIGHT, narrow=narrow)
    labels = _LABEL.findall(svg)
    ranked = sorted(CHART.bars, key=lambda b: (-b.score, b.family))
    shown = ranked[:NARROW_BARS] if narrow else ranked
    assert labels == [b.family for b in shown]
    bars = _BAR.findall(svg)
    widths = [float(w) for *_, w in bars]
    for bar, width in zip(shown, widths):
        assert width / widths[0] == pytest.approx(bar.score / shown[0].score, rel=0.01)
    ticks = re.findall(r'<text class="m tick" x="([\d.]+)"[^>]*>([\d.]+)</text>', svg)
    assert [float(value) for _, value in ticks] == [0, 20, 40, 60]
    left, right = float(ticks[0][0]), float(ticks[-1][0])
    assert all(float(bar[0]) == left for bar in bars)
    assert widths[0] / (right - left) == pytest.approx(49 / 60, rel=0.01)


def test_the_phone_chart_names_what_it_leaves_for_the_list():
    svg = chart_svg(CHART, LIGHT, narrow=True)
    assert f"+{len(CHART.bars) - NARROW_BARS} more in the list below" in svg
    assert "more in the list below" not in chart_svg(CHART, LIGHT)


def test_a_low_scoring_comparison_keeps_its_measurement_and_room_for_the_full_identity():
    chart=Chart(bars=(Bar('nemotron-3.5-super-vl-120b-a12b', 13.6, 5, False),),
                top_name='Leader',top_score=59.4,read_on=date(2026,10,31),
                version='5.0')
    svg=chart_svg(chart,LIGHT)
    assert 'class="bar"' in svg
    label=re.search(r'<text class="t label" x="([\d.]+)"',svg)
    assert float(label[1]) >= 40 + len(chart.bars[0].family)*11.5
    assert 'Index v5.0' in svg and '13.6' in svg


def test_display_rounding_does_not_change_bar_geometry():
    chart = Chart(bars=(Bar('rounded-score', 34.44, 1, False),),
                  top_name='Leader', top_score=59.4, read_on=date(2026, 10, 31),
                  version='5.0')
    svg = chart_svg(chart, LIGHT)
    assert '>34.4</text>' in svg
    tick = re.search(r'<text class="m tick" x="([\d.]+)"[^>]*>40</text>', svg)
    left, _, width = map(float, _BAR.findall(svg)[0])
    assert width / (float(tick[1]) - left) == pytest.approx(34.44 / 40, rel=0.001)


@pytest.mark.parametrize("highest", [0, 0.1, 1.3, 33.6, 40, 40.1, 59.4, 100])
def test_axis_handles_zero_scores_and_new_score_ranges_without_clipping(highest):
    from dataclasses import replace
    from freetier_radar.pictures import _chart_ticks
    ticks = _chart_ticks(highest)
    assert ticks[0] == 0 and ticks[-1] >= highest and ticks[-1] > 0
    assert 2 <= len(ticks) <= 6
    assert all(b - a == pytest.approx(ticks[1]) for a, b in zip(ticks, ticks[1:]))
    chart = replace(CHART, bars=(Bar('measured', highest, 1, False),))
    for narrow in (False, True):
        svg = chart_svg(chart, LIGHT, narrow=narrow)
        left, _, width = map(float, _BAR.findall(svg)[0])
        end = float(re.findall(r'<text class="m tick" x="([\d.]+)"', svg)[-1])
        assert 0 <= width <= end - left
        assert width / (end - left) == pytest.approx(highest / ticks[-1], abs=0.001)


@pytest.mark.parametrize("narrow", [False, True])
def test_each_bar_says_its_score_and_how_many_offers_serve_it_free(narrow):
    svg = chart_svg(CHART, DARK, narrow=narrow)
    assert ">45.4<" in svg and 'class="m offers"' in svg
    assert re.search(r'class="m offers"[^>]*>1</text>', svg)
    assert re.search(r'class="m offers"[^>]*>2</text>', svg)
    # the phone's ten leave the twelfth, the one seven offers serve, to the list
    assert bool(re.search(r'class="m offers"[^>]*>7</text>', svg)) is not narrow
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
