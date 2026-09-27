"""The README's pictures, drawn as SVG from figures the render already has.

The README opened on a banner drawn by hand in August — a radar with four
decorative contacts — then a table of four counters and a six-line paragraph.
On a phone that was the whole first screen: GitHub scales an image to the
column, so the 1160-unit banner arrived 358 pixels wide with its tagline at six
pixels, and the counters sat in a table GitHub pads thirteen pixels a cell.

So the top of the page is one picture, and every mark in it is a fact the
registry backs. The radar is the list: one dot per live offer, a section to a
colour, the offers that get the most work done for free nearest the centre, so
a row that dies takes its dot with it on the next render. The counters are the
same figures the README's text states, and nothing here is typed.

Two widths, because one aspect ratio cannot serve both screens: the wide hero
for a desktop column, the narrow one — served to a phone through the README's
`<picture>` — with the radar above the words and every word drawn large enough
to read at the width a phone shows it. The wide pair holds one palette each and
the README picks between them the way GitHub documents; the narrow one holds
both and follows the reader's theme itself, because a `<source>` that asked for
a width and a theme at once would be two conditions for GitHub's theme switcher
to rewrite, and it rewrites only the one it knows.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from xml.sax.saxutils import escape

__all__ = ["BEAM_PERIOD", "WIDE_SHOWN", "NARROW_SHOWN", "NARROW_BARS", "Palette", "LIGHT", "DARK",
           "TONES", "Arc", "Hero", "hero_svg", "Bar", "Chart", "chart_svg"]

# One turn of the beam, in seconds — the same as the hand-drawn banners'.
BEAM_PERIOD = 6.0
# The width GitHub shows a README image at: the desktop column (1280-pixel
# window) and a 390-pixel phone. The tests hold every word to eleven pixels at
# these widths.
WIDE_SHOWN = 830
NARROW_SHOWN = 358
# A phone scrolls a picture a screen at a time: its chart draws the strongest
# ten and names how many more the list under it has.
NARROW_BARS = 10

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
# The golden ratio spreads a section's dots around its arc: consecutive dots,
# which sit at nearly the same distance from the centre, land far apart.
GOLDEN = (math.sqrt(5) - 1) / 2


@dataclass(frozen=True)
class Palette:
    """GitHub's own colours (Primer), so the picture sits in the page."""
    canvas: str
    border: str
    text: str
    muted: str
    ring: str
    green: str
    blue: str
    amber: str
    purple: str


LIGHT = Palette(canvas="#ffffff", border="#d1d9e0", text="#1f2328", muted="#59636e",
                ring="#1a7f37", green="#1a7f37", blue="#0969da", amber="#9a6700",
                purple="#8250df")
DARK = Palette(canvas="#0d1117", border="#3d444d", text="#f0f6fc", muted="#9198a1",
               ring="#3fb950", green="#3fb950", blue="#4493f8", amber="#d29922",
               purple="#ab7df8")
# What colour a section's dots are, by the name the render gives the section.
TONES = {"agents": "green", "apis": "blue", "trials": "amber", "aggregators": "purple"}


@dataclass(frozen=True)
class Arc:
    """A section of the list: its name in the legend, its colour, its live rows."""
    label: str
    tone: str
    count: int


@dataclass(frozen=True)
class Hero:
    live: int
    no_card: int
    models: int
    strong: int
    last_run: date
    schedule: str
    # In the list's own order; a section's rows in its own order too, since the
    # first of them sit nearest the centre.
    arcs: tuple[Arc, ...]


@dataclass(frozen=True)
class _Frame:
    """Where things go at one width."""
    width: int
    height: int
    cx: float
    cy: float
    radius: float
    dot: float


_WIDE = _Frame(width=1160, height=330, cx=178, cy=165, radius=128, dot=4.5)
_NARROW = _Frame(width=600, height=820, cx=300, cy=200, radius=160, dot=5.5)


def _num(v: float) -> str:
    return f"{v:.1f}"


def _point(frame: _Frame, bearing: float, r: float) -> tuple[float, float]:
    """A bearing in degrees clockwise from north, as the beam turns."""
    a = math.radians(bearing)
    return frame.cx + r * math.sin(a), frame.cy - r * math.cos(a)


def _dots(frame: _Frame, arcs: tuple[Arc, ...]) -> list[tuple[str, float, float, float]]:
    """(tone, x, y, bearing) for every live row.

    Each section takes a share of the circle as large as its share of the
    rows. Within it the k-th row sits at the k-th distance of an even spread
    over the disc's area — the best offers nearest the centre — at a bearing the
    golden ratio picks. Where a dot would touch one already placed it moves
    along its arc, then outward, in fixed steps: a picture is compared byte by
    byte, so nothing here may depend on anything but the counts."""
    total = sum(a.count for a in arcs)
    placed: list[tuple[str, float, float, float]] = []
    if not total:
        return placed
    gap = 2 * frame.dot + 2
    start = 0.0
    for arc in arcs:
        width = 360 * arc.count / total
        pad = min(4.0, width / 4)
        span = width - 2 * pad
        for k in range(arc.count):
            base_r = frame.radius * (0.26 + 0.66 * math.sqrt((k + 0.5) / arc.count))
            base_t = ((k + 1) * GOLDEN) % 1
            spot = None
            for attempt in range(240):
                t = (base_t + (attempt % 24) * GOLDEN / 7) % 1
                r = min(frame.radius * 0.94, base_r + (attempt // 24) * frame.dot * 0.9)
                bearing = start + pad + t * span
                x, y = _point(frame, bearing, r)
                if all(math.dist((x, y), (px, py)) >= gap for _, px, py, _ in placed):
                    spot = (arc.tone, x, y, bearing)
                    break
            placed.append(spot or (arc.tone, *_point(frame, start + pad + base_t * span, base_r),
                                   start + pad + base_t * span))
        start += width
    return placed


def _arrival(bearing: float) -> float:
    """When the beam's leading edge, at north at time zero, reaches a bearing."""
    return (bearing % 360) / 360 * BEAM_PERIOD


def _rules(p: Palette) -> str:
    return (f".card{{fill:{p.canvas};stroke:{p.border}}}"
            f".t{{fill:{p.text}}}.m{{fill:{p.muted}}}"
            f".ring{{stroke:{p.ring}}}.hub{{fill:{p.ring}}}.beam{{stroke:{p.ring}}}"
            f".s0,.s1,.g0,.g1{{stop-color:{p.ring}}}.a0{{stop-color:{p.green}}}.a1{{stop-color:{p.blue}}}"
            + "".join(f".dot.{tone},.key.{tone}{{fill:{getattr(p, colour)}}}"
                      f".rim.{tone}{{stroke:{getattr(p, colour)}}}"
                      for tone, colour in TONES.items()))


def _colours(palette: Palette | None, rules) -> str:
    """One palette, or both with the reader's theme choosing — the narrow
    pictures, which a phone is served whatever its theme."""
    if palette is not None:
        return rules(palette)
    return rules(LIGHT) + "@media (prefers-color-scheme: dark) {" + rules(DARK) + "}"


def _style(palette: Palette | None) -> str:
    colours = _colours(palette, _rules)
    return ("<style>" + colours
            + ".rim{fill:none}.s0{stop-opacity:.5}.s1,.g1{stop-opacity:0}.g0{stop-opacity:.12}"
            # A dot lights up as the beam passes it; the delay is that moment.
            + f".dot{{opacity:.45;animation:ping {BEAM_PERIOD:g}s linear infinite}}"
            + "@keyframes ping{0%,4%{opacity:1}55%,100%{opacity:.45}}"
            # The flashing is what a reader who asked for less motion wants
            # stopped, so every dot stays lit instead. The beam's slow turn is
            # SMIL, which no stylesheet can stop.
            + "@media (prefers-reduced-motion: reduce) {.dot { animation: none; opacity: 1 }}"
            + "</style>")


def _radar(frame: _Frame, arcs: tuple[Arc, ...]) -> list[str]:
    cx, cy, R = frame.cx, frame.cy, frame.radius
    out = [f'<defs><radialGradient id="glow"><stop class="g0" offset="0"/>'
           f'<stop class="g1" offset="1"/></radialGradient></defs>',
           f'<circle cx="{_num(cx)}" cy="{_num(cy)}" r="{_num(R)}" fill="url(#glow)"/>']
    out += [f'<circle class="ring" cx="{_num(cx)}" cy="{_num(cy)}" r="{_num(R * f)}" '
           f'fill="none" stroke-width="2" stroke-opacity="{o}"/>'
           for f, o in ((1 / 3, ".5"), (2 / 3, ".35"), (1, ".25"))]
    out.append(f'<path class="ring" d="M{_num(cx - R)} {_num(cy)}H{_num(cx + R)}'
               f'M{_num(cx)} {_num(cy - R)}V{_num(cy + R)}" stroke-width="2" '
               f'stroke-opacity=".15"/>')
    # A rim segment per section, as long as its share of the rows.
    total = sum(a.count for a in arcs) or 1
    start, rim = 0.0, R + frame.dot + 5
    for arc in arcs:
        width = 360 * arc.count / total
        if arc.count and width > 3:
            a0, a1 = start + 1.2, start + width - 1.2
            (x0, y0), (x1, y1) = _point(frame, a0, rim), _point(frame, a1, rim)
            large = 1 if a1 - a0 > 180 else 0
            out.append(f'<path class="rim {arc.tone}" d="M{_num(x0)} {_num(y0)}A{_num(rim)} '
                       f'{_num(rim)} 0 {large} 1 {_num(x1)} {_num(y1)}" stroke-width="5" '
                       f'stroke-linecap="round"/>')
        start += width
    # The beam: its leading edge at north, the glow trailing forty degrees.
    (tx, ty), (lx, ly) = _point(frame, -40, R), _point(frame, 0, R)
    (gx0, gy0), (gx1, gy1) = _point(frame, 0, R * 0.7), _point(frame, -40, R * 0.7)
    out.append(f'<defs><linearGradient id="sweep" gradientUnits="userSpaceOnUse" '
               f'x1="{_num(gx0)}" y1="{_num(gy0)}" x2="{_num(gx1)}" y2="{_num(gy1)}">'
               f'<stop class="s0" offset="0"/><stop class="s1" offset="1"/></linearGradient></defs>')
    out.append(f'<g><animateTransform attributeName="transform" type="rotate" '
               f'from="0 {_num(cx)} {_num(cy)}" to="360 {_num(cx)} {_num(cy)}" '
               f'dur="{BEAM_PERIOD:g}s" repeatCount="indefinite"/>'
               f'<path fill="url(#sweep)" d="M{_num(cx)} {_num(cy)}L{_num(tx)} {_num(ty)}'
               f'A{_num(R)} {_num(R)} 0 0 1 {_num(lx)} {_num(ly)}Z"/>'
               f'<line class="beam" x1="{_num(cx)}" y1="{_num(cy)}" x2="{_num(lx)}" '
               f'y2="{_num(ly)}" stroke-width="3" stroke-linecap="round"/></g>')
    for tone, x, y, bearing in _dots(frame, arcs):
        out.append(f'<circle class="dot {tone}" cx="{_num(x)}" cy="{_num(y)}" '
                   f'r="{_num(frame.dot)}" style="animation-delay:{_arrival(bearing):.2f}s"/>')
    out.append(f'<circle class="hub" cx="{_num(cx)}" cy="{_num(cy)}" r="{_num(frame.dot + 1)}"/>')
    return out


def _legend(arcs: tuple[Arc, ...]) -> str:
    return " ".join(f'<tspan class="key {a.tone}">●</tspan> {escape(a.label)}'
                    for a in arcs if a.count)


def _counters(hero: Hero) -> list[tuple[str, str]]:
    return [(str(hero.live), "live offers"), (str(hero.no_card), "need no card"),
            (str(hero.models), "free models"), (str(hero.strong), "strong models")]


def _title(hero: Hero) -> str:
    return (f"awesome-free-ai-coding: {hero.live} live offers, {hero.no_card} need no card, "
            f"{hero.models} free models, {hero.strong} strong models; every offer probed "
            f"{hero.schedule}, last run {hero.last_run.isoformat()}; one dot per live offer")


def _wide_words(hero: Hero) -> list[str]:
    x = 352
    out = [f'<text class="t" x="{x}" y="86" font-family="{MONO}" font-size="46" '
           f'font-weight="700">awesome-free-ai-coding</text>',
           f'<rect x="{x + 2}" y="102" width="600" height="5" rx="2.5" fill="url(#accent)"/>',
           f'<text class="m" x="{x}" y="142" font-family="{SANS}" font-size="22">Legal free LLM '
           f'APIs &amp; coding agents, probed {escape(hero.schedule)}</text>']
    for i, (figure, label) in enumerate(_counters(hero)):
        cx = x + i * 200
        out.append(f'<text class="t" x="{cx}" y="222" font-family="{SANS}" font-size="54" '
                   f'font-weight="700">{figure}</text>')
        out.append(f'<text class="m" x="{cx}" y="252" font-family="{SANS}" '
                   f'font-size="18">{label}</text>')
    out.append(f'<text class="m" x="{x}" y="300" font-family="{SANS}" font-size="17">one dot '
               f'per live offer: {_legend(hero.arcs)} · last run '
               f'{hero.last_run.isoformat()}</text>')
    return out


def _narrow_words(hero: Hero) -> list[str]:
    mid = _NARROW.width / 2
    out = [f'<text class="m" x="{_num(mid)}" y="412" text-anchor="middle" font-family="{SANS}" '
           f'font-size="22">{_legend(hero.arcs)}</text>',
           f'<text class="t" x="{_num(mid)}" y="478" text-anchor="middle" font-family="{MONO}" '
           f'font-size="38" font-weight="700">awesome-free-ai-coding</text>',
           f'<rect x="{_num(mid - 200)}" y="494" width="400" height="5" rx="2.5" '
           f'fill="url(#accent)"/>',
           f'<text class="t" x="{_num(mid)}" y="540" text-anchor="middle" font-family="{SANS}" '
           f'font-size="26">Legal free LLM APIs &amp; coding agents</text>',
           f'<text class="m" x="{_num(mid)}" y="574" text-anchor="middle" font-family="{SANS}" '
           f'font-size="22">probed {escape(hero.schedule)} · last run '
           f'{hero.last_run.isoformat()}</text>']
    for i, (figure, label) in enumerate(_counters(hero)):
        cx = mid + (-135 if i % 2 == 0 else 135)
        top = 668 + (i // 2) * 104
        out.append(f'<text class="t" x="{_num(cx)}" y="{top}" text-anchor="middle" '
                   f'font-family="{SANS}" font-size="60" font-weight="700">{figure}</text>')
        out.append(f'<text class="m" x="{_num(cx)}" y="{top + 32}" text-anchor="middle" '
                   f'font-family="{SANS}" font-size="22">{label}</text>')
    return out


def hero_svg(hero: Hero, palette: Palette | None, narrow: bool = False) -> str:
    """The top of the README. `palette` None draws both palettes and lets the
    reader's theme choose, which is what the narrow hero is served as."""
    frame = _NARROW if narrow else _WIDE
    title = escape(_title(hero))
    accent_to = frame.width - 60
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{frame.width}" '
             f'height="{frame.height}" viewBox="0 0 {frame.width} {frame.height}" role="img" '
             f'aria-labelledby="title">',
             f'<title id="title">{title}</title>',
             _style(palette),
             f'<defs><linearGradient id="accent" gradientUnits="userSpaceOnUse" x1="0" y1="0" '
             f'x2="{accent_to}" y2="0"><stop class="a0" offset="0"/><stop class="a1" offset="1"/>'
             f'</linearGradient></defs>',
             f'<rect class="card" x="1" y="1" width="{frame.width - 2}" '
             f'height="{frame.height - 2}" rx="18" stroke-width="2"/>',
             *_radar(frame, hero.arcs),
             *(_narrow_words(hero) if narrow else _wide_words(hero)),
             "</svg>"]
    return "\n".join(parts) + "\n"


@dataclass(frozen=True)
class Bar:
    """A model a live offer serves free: its score, and how many offers serve it."""
    family: str
    score: float
    offers: int
    frontier: bool
    estimated: bool


@dataclass(frozen=True)
class Chart:
    bars: tuple[Bar, ...]
    top_name: str
    top_score: float
    read_on: date
    frontier_within: float
    strong_within: float

    def ranked(self) -> list[Bar]:
        """The bars as the chart draws them: the highest score first."""
        return sorted(self.bars, key=lambda b: (-b.score, b.family))


def _chart_rules(p: Palette) -> str:
    return (f".card{{fill:{p.canvas};stroke:{p.border}}}.t{{fill:{p.text}}}.m{{fill:{p.muted}}}"
            f".bar.strong{{fill:{p.blue}}}.bar.frontier{{fill:{p.green}}}"
            f".band{{fill:{p.green};fill-opacity:.12}}"
            f".guide{{stroke:{p.muted};stroke-dasharray:4 5}}.top{{stroke:{p.text}}}")


def _offers(n: int) -> str:
    return f"{n} offer" if n == 1 else f"{n} offers"


def _value(bar: Bar) -> str:
    return (f'<tspan class="t" font-weight="700">{bar.score:.1f}{"*" if bar.estimated else ""}'
            f'</tspan><tspan class="m"> · {_offers(bar.offers)}</tspan>')


def chart_svg(chart: Chart, palette: Palette | None, narrow: bool = False) -> str:
    """The strong models the list serves free, each as long as its score on
    the Artificial Analysis Intelligence Index, on an axis from zero to the top
    of the index: the gap to the frontier drawn as it is, not stretched. The
    frontier band and the strong bar are the tiers' own thresholds."""
    ranked = chart.ranked()
    shown = ranked[:NARROW_BARS] if narrow else ranked
    width = 600 if narrow else 1160
    # The phone chart keeps the right edge for the figures, clear of the guides.
    x0, x1 = (30.0, 380.0) if narrow else (370.0, 1000.0)
    top = chart.top_score or 1.0
    scale = (x1 - x0) / top

    def at(score: float) -> float:
        return x0 + max(0.0, score) * scale

    first, row = (196, 62) if narrow else (150, 32)
    end = first + len(shown) * row - (row - 24 if narrow else 14)
    notes = []
    if narrow and len(ranked) > len(shown):
        notes.append(f"+{len(ranked) - len(shown)} more in the list below")
    if any(b.estimated for b in shown):
        notes.append("* estimated by Artificial Analysis")
    if not narrow:
        notes.append("each bar: a model a live offer on this list serves free — where, in the "
                     "list below")
    height = end + 30 * len(notes) + 36
    guide_top, label_y = (156, 148) if narrow else (112, 124)
    size = 19 if narrow else 16
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
             f'<title id="title">Strong models you can use for $0, scored on the Artificial '
             f'Analysis Intelligence Index on {chart.read_on.isoformat()}: '
             + escape("; ".join(f"{b.family} {b.score:.1f}, free on {_offers(b.offers)}"
                                for b in ranked)) + "</title>",
             "<style>" + _colours(palette, _chart_rules) + "</style>",
             f'<rect class="card" x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" '
             f'stroke-width="2"/>']
    if narrow:
        parts += [f'<text class="t" x="30" y="56" font-family="{SANS}" font-size="30" '
                  f'font-weight="700">Strong models, free</text>',
                  f'<text class="m" x="30" y="92" font-family="{SANS}" font-size="20">scored on the '
                  f'Artificial Analysis Intelligence Index,</text>',
                  f'<text class="m" x="30" y="120" font-family="{SANS}" font-size="20">read '
                  f'{chart.read_on.isoformat()} · top: {escape(chart.top_name)}, '
                  f'{chart.top_score:.1f}</text>']
    else:
        parts += [f'<text class="t" x="40" y="58" font-family="{SANS}" font-size="30" '
                  f'font-weight="700">Strong models you can use for $0</text>',
                  f'<text class="m" x="40" y="90" font-family="{SANS}" font-size="18">scored on the '
                  f'Artificial Analysis Intelligence Index, read {chart.read_on.isoformat()} · the '
                  f'top: {escape(chart.top_name)}, {chart.top_score:.1f}</text>']
    frontier, strong = at(top - chart.frontier_within), at(top - chart.strong_within)
    parts += [f'<rect class="band" x="{_num(frontier)}" y="{guide_top}" '
              f'width="{_num(x1 - frontier)}" height="{end - guide_top}"/>',
              f'<line class="guide" x1="{_num(strong)}" y1="{guide_top}" x2="{_num(strong)}" '
              f'y2="{end}" stroke-width="1.5"/>',
              f'<line class="top" x1="{_num(x1)}" y1="{guide_top}" x2="{_num(x1)}" y2="{end}" '
              f'stroke-width="2"/>',
              f'<text class="m" x="{_num(strong + 5)}" y="{label_y}" font-family="{SANS}" '
              f'font-size="{size}">strong</text>',
              f'<text class="m" x="{_num(frontier + 5)}" y="{label_y}" font-family="{SANS}" '
              f'font-size="{size}">frontier</text>']
    parts.append(f'<text class="m" x="{_num(x1 + 6)}" y="{label_y}" font-family="{SANS}" '
                 f'font-size="{size}">top</text>')
    for i, bar in enumerate(shown):
        tier = "frontier" if bar.frontier else "strong"
        if narrow:
            y = first + i * row
            parts += [f'<text class="t label" x="30" y="{y}" font-family="{MONO}" '
                      f'font-size="21">{escape(bar.family)}</text>',
                      f'<rect class="bar {tier}" x="{_num(x0)}" y="{y + 12}" '
                      f'width="{_num(at(bar.score) - x0)}" height="16" rx="4"/>',
                      f'<text x="570" y="{y + 27}" text-anchor="end" font-family="{SANS}" '
                      f'font-size="20">{_value(bar)}</text>']
        else:
            y = first + i * row
            parts += [f'<text class="t label" x="350" y="{y + 6}" text-anchor="end" '
                      f'font-family="{MONO}" font-size="19">{escape(bar.family)}</text>',
                      f'<rect class="bar {tier}" x="{_num(x0)}" y="{y - 9}" '
                      f'width="{_num(at(bar.score) - x0)}" height="18" rx="4"/>',
                      f'<text x="{_num(at(bar.score) + 8)}" y="{y + 6}" font-family="{SANS}" '
                      f'font-size="17">{_value(bar)}</text>']
    for i, note in enumerate(notes):
        x = 30 if narrow else 40
        parts.append(f'<text class="m" x="{x}" y="{end + 40 + i * 30}" font-family="{SANS}" '
                     f'font-size="{size}">{escape(note)}</text>')
    return "\n".join(parts + ["</svg>"]) + "\n"
