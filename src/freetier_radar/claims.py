"""What the hand-written files say about the code and the data, held to them.

The pages are generated, and state every rule from the constant that applies
it. CONTRIBUTING.md, the site's config, the banners and browse.html are written
by hand and cannot: CONTRIBUTING said "Three rows use it (`trae`, `upstage`,
`siliconflow-cn`)" for a week after hpc-ai became the fourth, and "twice a
week" is painted into three images. So each sentence that states a figure the
code applies is listed here with the constant it states, the schedule is read
off every hand-written file, and `freetier-check` refuses the sentence — or the
constant — the day the two part. A claim whose sentence was reworded is
reported too, since a claim that matches nothing checks nothing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from .announce import MAX_AGE_DAYS, POSTS_PER_RUN
from .bars import BAR_DAYS
from .gate import EARNED
from .layout import MAP, Kind
from .models import (ANCHOR_PHRASE_WORDS, ARCHIVE_AFTER_DAYS, ARCHIVE_AFTER_FAILURES, NOTICE_HOLD_DAYS,
                     PROBE_WEEKDAYS, SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, load_registry,
                     probe_frequency)
from .prober import ANTHROPIC_GONE, KEYLESS_IDS_TRIED, PROVISIONAL_PROMOTE_DAYS, UA
from .quotes import MIN_WORDS
from .render import (CATEGORY_TITLES, MODEL_PAGE_ROWS, PAGES_URL, QUICKSTART_USER_AGENT,
                     README_MODELS, README_PICKS, README_STARTERS, README_STRONG)
from .tiers import FRONTIER_WITHIN, STRONG_WITHIN
from .validate import PROSE_LIMITS
# The render's own words for a figure, so a sentence held here and the page
# printing the same constant can never spell it two ways.
from .words import number as _word, ordinal as _ordinal, weeks as _weeks

__all__ = ["Claim", "CLAIMS", "SCHEDULED", "check_claims"]

@dataclass(frozen=True)
class Claim:
    """A sentence in a hand-written file, found by `pattern`, whose groups — or
    what `read` takes out of the match — state the values `truth` returns."""
    file: str
    pattern: str
    truth: Callable[[Path], tuple[str, ...]]
    source: str
    read: Callable[[re.Match], tuple[str, ...]] = re.Match.groups


def _no_row_sets(field: str) -> Callable[[Path], tuple[str, ...]]:
    """"No row sets the field today" is true while no row does."""
    def truth(root: Path) -> tuple[str, ...]:
        rows = [e.id for e in load_registry(root / "registry.yaml")
                if e.api and getattr(e.api, field)]
        return ("No",) if not rows else (", ".join(rows),)
    return truth


def _keys(found: re.Match) -> tuple[str, ...]:
    """The keys of a JavaScript object literal, in the order written."""
    return tuple(re.findall(r'"([a-z-]+)":', found.group(1)))


def _site_url() -> tuple[str, str]:
    """PAGES_URL as Jekyll's `url` and `baseurl`."""
    host, base = PAGES_URL.rsplit("/", 1)
    return host, "/" + base


CLAIMS: tuple[Claim, ...] = (
    Claim("CONTRIBUTING.md", r"and it\s+expires after (\d+) days, at which point the scout",
          lambda root: (str(WATCH_RECHECK_DAYS),), "models.WATCH_RECHECK_DAYS"),
    Claim("CONTRIBUTING.md", r"Those verdicts expire after (\d+)\s+days",
          lambda root: (str(SOURCE_RECHECK_DAYS),), "models.SOURCE_RECHECK_DAYS"),
    Claim("CONTRIBUTING.md",
          r"after (\w+) failed\s+probes in a row, or after (\d+) days without a passing probe",
          lambda root: (_word(ARCHIVE_AFTER_FAILURES), str(ARCHIVE_AFTER_DAYS)),
          "models.ARCHIVE_AFTER_FAILURES and ARCHIVE_AFTER_DAYS"),
    Claim("CONTRIBUTING.md",
          r"scores within (\d+) points of the top\s+of the index, counting current models only,"
          r"\s+`strong` within (\d+)",
          lambda root: (f"{FRONTIER_WITHIN:g}", f"{STRONG_WITHIN:g}"),
          "tiers.FRONTIER_WITHIN and STRONG_WITHIN"),
    Claim("CONTRIBUTING.md", r"vendor output in backticks, (\d+) characters\s+at most",
          lambda root: (str(PROSE_LIMITS["api.notice"]),), "validate.PROSE_LIMITS['api.notice']"),
    Claim("CONTRIBUTING.md", r"holds a refusal off the failure count for (\d+) days from `since`",
          lambda root: (str(NOTICE_HOLD_DAYS),), "models.NOTICE_HOLD_DAYS"),
    Claim("CONTRIBUTING.md", r"only events from the last (\d+) days, at most (\w+) per channel",
          lambda root: (str(MAX_AGE_DAYS), _word(POSTS_PER_RUN)),
          "announce.MAX_AGE_DAYS and POSTS_PER_RUN"),
    Claim("CONTRIBUTING.md",
          r"`freetier-check` holds `offering` to ([\d,]+) characters, `limits` to ([\d,]+) and"
          r"\s+`api.note` to ([\d,]+)",
          lambda root: tuple(f"{PROSE_LIMITS[f]:,}" for f in ("offering", "limits", "api.note")),
          "validate.PROSE_LIMITS"),
    Claim("CONTRIBUTING.md", r"The first (\w+) no-card agents are also the top of the README",
          lambda root: (_word(README_STARTERS),), "render.README_STARTERS"),
    Claim("CONTRIBUTING.md", r"read (\w+) names deep per section",
          lambda root: (_word(README_PICKS),), "render.README_PICKS"),
    Claim("CONTRIBUTING.md", r"A lane that rotates names a model once it has stayed (\w+ weeks|a week)",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS"),
    Claim("CONTRIBUTING.md", r"and joins `models\[\]` (\w+ weeks|a week) later",
          lambda root: (_weeks(BAR_DAYS),), "bars.BAR_DAYS"),
    Claim("CONTRIBUTING.md", r"`offering`, the first (\w+)\s+model families and the date",
          lambda root: (_word(README_MODELS),), "render.README_MODELS"),
    Claim("CONTRIBUTING.md", r"every family past the (\w+), one click from their count",
          lambda root: (_ordinal(README_MODELS),), "render.README_MODELS"),
    Claim("CONTRIBUTING.md", r"the most widely served first and at most (\w+);",
          lambda root: (_word(README_STRONG),), "render.README_STRONG"),
    Claim("CONTRIBUTING.md", r"a page for every model (\w+) rows or more serve",
          lambda root: (_word(MODEL_PAGE_ROWS),), "render.MODEL_PAGE_ROWS"),
    Claim("CONTRIBUTING.md", r"sends the check on to the next id, up to\s+(\w+),",
          lambda root: (_word(KEYLESS_IDS_TRIED),), "prober.KEYLESS_IDS_TRIED"),
    Claim("CONTRIBUTING.md", r"always calls under this\s+project's own `([^`]+)`",
          lambda root: (UA["User-Agent"],), "prober.UA"),
    Claim("CONTRIBUTING.md", r"sends `User-Agent: ([^`]+)`",
          lambda root: (QUICKSTART_USER_AGENT,), "render.QUICKSTART_USER_AGENT"),
    Claim("CONTRIBUTING.md", r"\| a sentence of (\d+)\+ words quoted from the page \|",
          lambda root: (str(ANCHOR_PHRASE_WORDS),), "models.ANCHOR_PHRASE_WORDS"),
    Claim("CONTRIBUTING.md", r"reports every quote of (\w+) words or more",
          lambda root: (_word(MIN_WORDS),), "quotes.MIN_WORDS"),
    Claim("CONTRIBUTING.md", r"is a route, a (\d+), (\d+) or (\d+)\s+is reported",
          lambda root: tuple(str(c) for c in ANTHROPIC_GONE), "prober.ANTHROPIC_GONE"),
    Claim("CONTRIBUTING.md", r"beside the (\w+) config files it describes",
          lambda root: (_word(len([n for n in MAP if n.kind is Kind.GENERATED
                                   and n.path.startswith("configs/")
                                   and n.path != "configs/README.md"])),),
          "the configs layout.MAP marks generated"),
    Claim("CONTRIBUTING.md",
          r"a hand edit of `(\w+)`,\s+`(\w+)`, `(\w+)` or `(\w+)`, which only the run's probe",
          lambda root: tuple(sorted(EARNED)), "gate.EARNED",
          read=lambda found: tuple(sorted(found.groups()))),
    Claim("CONTRIBUTING.md", r"(No) row sets\s+the field today",
          _no_row_sets("session_header"), "the rows that set api.session_header"),
    Claim("browse.html", r"listed for less than (\w+ weeks|a week)",
          lambda root: (_weeks(PROVISIONAL_PROMOTE_DAYS),),
          "prober.PROVISIONAL_PROMOTE_DAYS"),
    Claim("browse.html", r'<link rel="canonical" href="([^"]+)/browse\.html">',
          lambda root: (PAGES_URL,), "render.PAGES_URL"),
    Claim("browse.html", r"var ORDER = \{([^}]*)\}",
          lambda root: tuple(c.value for c in CATEGORY_TITLES), "render.CATEGORY_TITLES",
          read=_keys),
    Claim("browse.html", r"var LABEL = \{([^}]*)\}",
          lambda root: tuple(c.value for c in CATEGORY_TITLES), "render.CATEGORY_TITLES",
          read=_keys),
    Claim("_config.yml", r"(?m)^url: (\S+)\nbaseurl: (\S+)$",
          lambda root: _site_url(), "render.PAGES_URL"),
)


# The hand-written files that say how often the list is checked.
SCHEDULED = ("CONTRIBUTING.md", "_config.yml", "browse.html", "assets/banner-dark.svg",
             "assets/banner-light.svg", "assets/social-preview.svg")
_FREQUENCY = re.compile(r"\b(?:once|twice|three times|four times|five times|six times) a week\b"
                        r"|\bevery day\b")


def _line(text: str, at: int) -> int:
    return text.count("\n", 0, at) + 1


def _cron_weekdays(root: Path) -> tuple[int, ...] | None:
    workflow = yaml.safe_load((root / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    # PyYAML reads a bare `on:` as the boolean true.
    trigger = workflow.get("on", workflow.get(True)) or {}
    days: set[int] = set()
    for entry in trigger.get("schedule") or []:
        field = str(entry["cron"]).split()[4]
        if field == "*":
            days |= set(range(7))
        else:
            days |= {int(d) % 7 for d in field.split(",")}
    return tuple(sorted(days)) or None


def check_claims(root: Path, claims: tuple[Claim, ...] = CLAIMS,
                 scheduled: tuple[str, ...] = SCHEDULED) -> list[str]:
    problems = []
    for claim in claims:
        text = (root / claim.file).read_text(encoding="utf-8")
        found = re.search(claim.pattern, text)
        if found is None:
            problems.append(f"{claim.file} no longer has the sentence stating {claim.source} "
                            f"(claims.CLAIMS: `{claim.pattern}`) — point the claim at the sentence "
                            "that states it now")
            continue
        truth = claim.truth(root)
        if claim.read(found) != truth:
            said = " ".join(found.group(0).split())
            problems.append(f"{claim.file}:{_line(text, found.start())} says `{said}` and "
                            f"{claim.source} says {', '.join(truth)} — change the sentence or the "
                            "constant, never one of them alone")
    expected = probe_frequency(PROBE_WEEKDAYS)
    for name in scheduled:
        text = (root / name).read_text(encoding="utf-8")
        for m in _FREQUENCY.finditer(text):
            if m.group(0) != expected:
                problems.append(f"{name}:{_line(text, m.start())} says `{m.group(0)}` and the "
                                f"scheduled run probes {expected} (models.PROBE_WEEKDAYS)")
    cron = _cron_weekdays(root)
    if cron is not None and set(cron) != set(PROBE_WEEKDAYS):
        problems.append(
            f".github/workflows/update.yml runs on weekdays {','.join(map(str, cron))} and "
            f"models.PROBE_WEEKDAYS says {','.join(map(str, PROBE_WEEKDAYS))} — the pages would "
            f"say {expected}")
    return problems
