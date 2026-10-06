from __future__ import annotations

import argparse
import json
import re
import unicodedata
import tempfile
import textwrap
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .borders import SHARED, beyond_shared, left_out_of, load_yardstick, share
from .countries import COUNTRIES, country_name
from .history import (Event, EventType, archive_reason, load_history, pending_changes,
                      record_changes, refuse_deleted_rows)
from .models import (ARCHIVE_AFTER_DAYS, ARCHIVE_AFTER_FAILURES, CHECKED_PAGE,
                     CODEX_LITELLM_PROFILE, PROBE_WEEKDAYS, PROVIDERS_INDEX_PAGE,
                     WATCH_RECHECK_DAYS, Category, Entry, FreePart,
                     ModelFamily, Notice, ProbeType, Tier, Watched, domain_of,
                     folded_into, id_family, is_archived,
                     is_archived_for_good, is_blocked, is_watch_current, lane_ids, live_families,
                     load_blocklist, load_registry, load_watchlist, probe_frequency,
                     access_words, expire_entries, family_access, id_access, requires_payment,
                     save_registry, preferred_ids, family_names)
# The promotion day is the probe's, and the pages say how far off it is.
from .prober import PROVISIONAL_PROMOTE_DAYS
# The bars a family's score must clear to be called frontier or strong, which
# the pages state beside the answer, and the scores the tiers were read off.
from .tiers import FRONTIER_WITHIN, SCORES_PATH, STRONG_WITHIN
# The README's pictures, drawn from the figures below.
from .pictures import (DARK, LIGHT, NARROW_UNTIL, VARIANTS, Arc, Bar, Chart, Hero, chart_svg,
                       chart_words, hero_svg, hero_words, radar_svg)
# How a figure is put into words, shared with the checks that hold the
# hand-written files to the same constants.
from .words import clip, number, series, weeks
from .page_catalog import catalog_words, family_condition, limits_text
# The log a commit will be made on, and the map of the repository, which
# CONTRIBUTING.md prints.
from .gate import committed_log
from .layout import MAP, markdown_table

__all__ = ["FEED_ENTRIES", "FEED_URL",
           "README_CHANGES", "README_MODELS", "README_PICKS", "README_STARTERS",
           "README_STARTER_MODELS", "README_STRONG",
           "badge_colour",
           "build_context", "build_feed", "build_index", "check_rendered",
           "build_opencode_config", "build_env_example", "build_claude_code_sh", "env_var",
           "build_provider_page", "build_folded_page", "build_providers_index",
           "provider_page_url", "PAGES_URL",
           "MODELS_DIR", "MODEL_PAGE_ROWS", "build_model_page", "build_models_index",
           "model_page_url",
           "build_llms_txt",
           "picks",
           "SITE_MODELS", "SITE_PAGE", "build_site_context", "render_site",
           "CONFIGS_README", "README_BUDGET", "render_configs_readme",
           "render_readme", "render_artifacts", "render_all", "render_contributing", "sections",
           "main"]

CATEGORY_TITLES: dict[Category, str] = {
    Category.AGENT_CLI: "🤖 Coding agents & CLIs",
    Category.API_FREE_TIER: "🔌 LLM APIs with free tier",
    Category.TRIAL: "🎁 Trials (no card when possible)",
    Category.AGGREGATOR: "🧭 Aggregators (one key, many providers)",
}

REPO_URL = "https://github.com/mvalentsev/awesome-free-ai-coding"
# GitHub Pages rather than raw.githubusercontent.com, which serves the feed as
# text/plain, for a file every subscriber polls. The URL is the feed's own <id> and <link rel="self">: changing it breaks
# every subscription.
FEED_URL = "https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml"
# The Pages site the feed lives on, where each row gets a page of its own
# (`build_provider_page`).
PAGES_URL = "https://mvalentsev.github.io/awesome-free-ai-coding"
PROVIDERS_DIR = "providers"
# And where a model gets one (`build_model_page`).
MODELS_DIR = "models"
# Which models get a page of their own: those this many live rows serve free,
# and those that measure notable, strong or frontier (`_has_model_page`). A page
# earns its place by saying what no row's page says alone — who else serves the
# model — or by covering a model readers come for, which the index's upper half
# stands for. Any other model would get a page repeating its one row's; it stays
# on the index of every model, beside its row.
MODEL_PAGE_ROWS = 2
FEED_ENTRIES = 50
README_CHANGES = 10
# Where a prose cell stops showing and starts folding: the README's Archive
# reasons, and every long cell on the site (`_site_fold`). The teaser is a cut at
# a word boundary, so the gap between the two is what keeps a cell from folding
# away a line and a half of text to save half a line.
# A page's <meta> description, cut at a word to fit in this many characters.
DESCRIPTION_ROOM = 300
README_LIMITS_TEASER = 150
README_LIMITS_COLLAPSE = 260
# The README is the landing page and the site is the reference. A row is one
# line, so the page grows a line per row, and the budget keeps what the site
# carries — the limits, the connection table, the index of every model — from
# creeping back: what the page carries has to grow with the rows and no faster.
# A test renders the committed registry against it.
README_BUDGET = 80_000
# Where the README's pictures are drawn, beside the README and relative to it:
# GitHub serves an image the README names by a relative path from the same
# commit, so the picture and the page it tops are always the same render.
README_PICTURES = "assets/readme"
# The site's mark beside its name: the README hero's radar, drawn with it.
SITE_RADAR = f"{README_PICTURES}/radar.svg"
# How far back the top of the README names the rows the list added.
NEW_ROWS_DAYS = 7
# The width the README asks for a picture at; GitHub scales it to the column.
PICTURE_WIDTH = 860
# The radar's sections, in the list's order: the word the legend uses and the
# colour (pictures.TONES) a section's dots take.
HERO_ARCS: dict[Category, tuple[str, str]] = {
    Category.AGENT_CLI: ("agents", "agents"),
    Category.API_FREE_TIER: ("APIs", "apis"),
    Category.TRIAL: ("trials", "trials"),
    Category.AGGREGATOR: ("aggregators", "aggregators"),
}
# The connection table, beside the files it describes (`render_configs_readme`).
CONFIGS_README = "configs/README.md"
CONFIGS_TEMPLATE = "configs-README.md.j2"
# A code span as CommonMark reads one: a run of backticks, closed only by a run
# of the same length.
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", re.S)
# The connection table's note sits in the same cell as the vendor's name, and is
# the cell that grows: a rotating lane, an id spelling, a caveat about which of
# two endpoints the probe reads. It folds a little later than a prose cell,
# because half of these notes are one sentence and a fold that hides a single
# line is worse than the line.
README_NOTE_TEASER = 150
README_NOTE_COLLAPSE = 300
# How many agents the page answers "what do I code with, then?" by name before
# the list starts. Four is what fits above the fold beside the quickstart; the
# fifth-ranked agent is one section down either way.
README_STARTERS = 4
# How many of a starter's families Start here names, the strongest first, before
# it links the row's page for the rest: a phone shows the line at a glance.
README_STARTER_MODELS = 4
# How many names answer each "I want…" line of the picks table. Three reads as
# a choice; a fourth is the section itself, which starts one heading down.
README_PICKS = 3
# How many of a row's model families a README line names before it links the
# rest: a lane that rotates names every model it has served free for two weeks,
# and a README row is one line. The row's page and the site name them all.
README_MODELS = 8
# The separator between names on a line. The no-break space keeps the dot with the
# name before it, so a wrapped line never starts with one.
DOT = "\u00a0· "
# How many strong models the README names in its Start here, frontier first and
# then the most widely served (`_strong_models`). The tier bar keeps the set
# short and the cap keeps it short whatever the bar lets through; the rest are
# one click away in the site's model index.
README_STRONG = 20
# What the README's quickstart curl calls itself on a lane that asks every client
# for a User-Agent of its own: the command is this page's, so it says so, in the
# name/version shape the vendors' own example uses.
QUICKSTART_USER_AGENT = "awesome-free-ai-coding-quickstart/1.0"

# The freshness badge dates the list by its *oldest* live verification, and its
# colour says whether that age is healthy. Probes run twice a week, so a healthy
# floor is three or four days old and one missed run puts it at a week; three
# failed probes in a row bury a row, which caps a failing row's drag at about
# ten days. A floor older than that is held back by something no probe result
# clears on its own: a row answering INCONCLUSIVE run after run keeps its date
# until staleness archives it, and a workflow that stopped firing looks the same.
BADGE_FRESH_DAYS = 11
BADGE_AGEING_DAYS = 30
BADGE_GREEN, BADGE_AMBER, BADGE_RED = "3fb950", "d29922", "f85149"


def badge_colour(verified_through: date, today: date) -> str:
    """GitHub's own green/yellow/red, so the badge sits with the workflow ones."""
    age = (today - verified_through).days
    if age <= BADGE_FRESH_DAYS:
        return BADGE_GREEN
    return BADGE_AMBER if age <= BADGE_AGEING_DAYS else BADGE_RED


def _schedule() -> str:
    """How often every row is probed, as each page says it — read when a page is
    built rather than when this module loads, so it is always the schedule the
    run keeps."""
    return probe_frequency(PROBE_WEEKDAYS)


def _by_rank(e: Entry) -> tuple[int, bool, str]:
    """The order rows are read in wherever the list prints more than one of
    them: `rank`, then a row that asks for no card before one that does
    (CONTRIBUTING: a row that needs a card never leads the no-card rows it ties
    with), then the name."""
    return e.rank, e.card_required or requires_payment(e), e.name.lower()


def _ordered(active: list[Entry], category: Category) -> list[Entry]:
    """One section of the list, in the order every page prints it."""
    return sorted((e for e in active if e.category is category), key=_by_rank)


def sections(active: list[Entry]) -> list[tuple[str, list[Entry]]]:
    """The list's non-empty sections as a page prints them: (title, rows), in
    CATEGORY_TITLES' order, each section's rows in _ordered's. The README and
    the site keep an empty section to count it; a page that only lists rows
    reads these."""
    return [(title, rows) for cat, title in CATEGORY_TITLES.items()
            if (rows := _ordered(active, cat))]


# What each event is called wherever a human reads it — the row's page, the
# "What changed" tables, the feed and the monthly digest — one word each, from
# this table alone. The tables put a mark before the word.
EVENT_WORDS: dict[EventType, str] = {
    EventType.ADDED: "Added",
    EventType.ARCHIVED: "Archived",
    EventType.RESTORED: "Restored",
    EventType.REMOVED: "Delisted",
    EventType.MODELS: "Free models changed",
}
_EVENT_MARKS: dict[EventType, str] = {
    EventType.ADDED: "➕", EventType.ARCHIVED: "📦", EventType.RESTORED: "↩",
    EventType.REMOVED: "➖", EventType.MODELS: "🔄",
}
CHANGE_LABELS: dict[EventType, str] = {
    kind: f"{_EVENT_MARKS[kind]} {word}" for kind, word in EVENT_WORDS.items()}


def _readme_families(e: Entry) -> tuple[list[str], int]:
    """The families a README line names, in the row's own order and at most
    README_MODELS of them, and how many more the row's page names."""
    fams = live_families(e)
    return fams[:README_MODELS], max(0, len(fams) - README_MODELS)


def _fold(text: str, teaser_at: int, collapse_over: int, small: bool = False) -> str:
    """A long cell without the wall: what it says first, then all of it, in a
    <details> fold that keeps every character; `small` sets both in <sub>.

    The teaser is a cut at a word boundary (`_cut`), not a summary: no sentence
    is composed here.
    """
    open_, close = ("<sub>", "</sub>") if small else ("", "")
    if len(text) <= collapse_over:
        return f"{open_}{text}{close}"
    return (f"<details><summary>{open_}{_cut(text, teaser_at)} …{close}</summary>"
            f"{open_}{text}{close}</details>")


def _cut(text: str, at: int) -> str:
    """The teaser: a cut at the last word boundary before `at`, never a summary.

    A space inside a code span is not a word boundary. GitHub pairs a backtick
    the teaser leaves open with the next one it meets — the same span's opening
    backtick in the full text — and makes code of everything between them, the
    `</sub></summary>` that closes the teaser included: the fold then prints the
    whole cell, its tags as text. A span that runs past `at` with no word before
    it is kept whole, because a teaser has to show something.
    """
    spans = [m.span() for m in _CODE_SPAN.finditer(text)]
    words = [i for i, ch in enumerate(text[:at])
             if ch == " " and i > 0 and not any(s < i < e for s, e in spans)]
    cut = words[-1] if words else next((e for s, e in spans if s < at < e), at)
    return text[:cut].rstrip(" ,;:.—-")


def provider_page_url(entry_id: str) -> str:
    return f"{PAGES_URL}/{PROVIDERS_DIR}/{entry_id}/"


def model_page_url(family: str) -> str:
    return f"{PAGES_URL}/{MODELS_DIR}/{family}/"


def providers_index_url() -> str:
    return f"{PAGES_URL}/{PROVIDERS_DIR}/"


def models_index_url() -> str:
    return f"{PAGES_URL}/{MODELS_DIR}/"


def _permalink(url: str) -> str:
    """The path Jekyll serves a page at, read off the URL every link to it
    uses: one spelling of each address, so no page is published anywhere its
    links, the sitemap and IndexNow do not point."""
    if not url.startswith(PAGES_URL + "/"):
        raise ValueError(f"{url} is not a page of this site")
    return url.removeprefix(PAGES_URL)


def _model_page_rule() -> str:
    """Which models have a page, as every page that says so says it — from the
    constant that decides it."""
    return (f"{number(MODEL_PAGE_ROWS)} rows or more serve it "
            "free, or it measures notable, strong or frontier, or it has a dated free promotion")


# How a row's page and llms.txt say what the vendor does with what a reader
# sends, before the vendor's own sentence.
DATA_USE_WORDS = {
    "yes": "What you send may be used to train or improve models.",
    "opt-out": "What you send may be used to train or improve models unless you turn that off.",
    "no": "What you send is not used to train models.",
}


def _trains(e: Entry) -> bool:
    """Whether, by the vendor's account, what a reader sends may be used to train
    models — its own or an upstream provider's behind a gateway — by default, so
    an opt-out counts: the reader who never reads the setting is trained on."""
    return e.data_use is not None and e.data_use.trains in ("yes", "opt-out")


# Where a border's share is counted, as the pages cite it.
INNOVATION_GRAPH_URL = "https://innovationgraph.github.com/"
# How many countries a page names before it counts the rest: the provider page's
# section, and the one-line flag the top of a page, a model page and llms.txt use.
BORDER_NAMES = 8
BORDER_FLAG_NAMES = 3


def _percent(fraction: float) -> str:
    """"11.1%"; a share too small to show as a figure, as such."""
    p = 100 * fraction
    return "under 0.1%" if 0 < p < 0.05 else f"{p:.1f}%"


def _places(codes: list[str], most: int) -> str:
    """"mainland China, Russia and 12 more places" — the first `most` by name."""
    names = [country_name(c) for c in codes[:most]]
    rest = len(codes) - len(names)
    return series(names + ([f"{rest} more place" + ("s" if rest > 1 else "")] if rest else []))


def _left_out_order(codes: set[str]) -> list[str]:
    """The most developers first — the countries a reader is likeliest to be in."""
    devs = load_yardstick().developers
    return sorted(codes, key=lambda c: (-devs.get(c, 0), country_name(c)))


def _border_flag(e: Entry) -> str:
    """The border in one line, for the top of a page and a row elsewhere:
    "not offered in mainland China, Russia, Hong Kong and 25 more places". Empty
    where the offer leaves out no more than the countries under comprehensive US
    embargo."""
    if e.border is None:
        return ""
    yardstick = load_yardstick()
    if not beyond_shared(e.border, yardstick):
        return ""
    if _served_only(e.border):
        return "offered only in " + series([country_name(c) for c in
                                            _left_out_order(set(e.border.served))])
    return "not offered in " + _places(_left_out_order(left_out_of(e.border, yardstick)),
                                       BORDER_FLAG_NAMES)


def _served_only(b) -> bool:
    """An allow-list short enough to name whole — a sign-up for one market —
    which a page says as where the offer is, not as the world it leaves out."""
    return b.served is not None and len(b.served) <= BORDER_NAMES


def border_words(e: Entry) -> str:
    """The provider page's account of where the offer reaches: the countries
    it serves or leaves out, the share of developers that is, and the vendor's
    words it rests on with the day they were read."""
    b = e.border
    yardstick = load_yardstick()
    left = _left_out_order(left_out_of(b, yardstick))
    beyond = beyond_shared(b, yardstick)
    shared = sorted(set(left) & SHARED, key=country_name)
    if _served_only(b):
        where = f"Offered only in {series([country_name(c) for c in _left_out_order(set(b.served))])}"
    elif b.served is not None:
        where = (f"Offered in the {len(b.served)} countries and territories its list names"
                 + (f", not in {_places(left, BORDER_NAMES)}" if left else ""))
    elif beyond:
        where = f"Not offered in {_places(left, BORDER_NAMES)}"
    elif shared:
        where = (f"Not offered in {series([country_name(c) for c in shared], 'or')}, under "
                 f"comprehensive US embargo, and in no other country the vendor names")
    else:
        where = "The vendor names no country it keeps the offer from"
    # A border measured by DNS is a resolver's answer from inside each country,
    # and the link is the question as it was asked, not a vendor's page.
    source = "the host's DNS answer" if b.read == "dns" else "source"
    said = [f"{where} ([{source}]({b.source}), read {b.on.isoformat()})."]
    if beyond:
        said.append(f"That leaves out {_percent(share(b, yardstick))} of the developers GitHub "
                    f"counts, beyond the countries under comprehensive US embargo "
                    f"([Innovation Graph]({INNOVATION_GRAPH_URL}), {yardstick.label}).")
    if b.quote:
        said.append(f"In the vendor's words: “{b.quote}”.")
    return " ".join(said)


def _row_models(e: Entry, pages: set[str]) -> str:
    """A row's models as a Markdown line names them — the README's list and the
    provider index alike: the first README_MODELS, each linking its own page
    where it has one (what a reader who stops on a model name came for), then
    a count linking the row's page for the rest."""
    shown, more = _readme_families(e)
    return DOT.join(([_entry_family_links(e, shown, pages, DOT)] if shown else [])
                      + ([f"[+{more}\u00a0more]({provider_page_url(e.id)})"] if more else []))


def _row(e: Entry, pages: set[str]) -> dict[str, str]:
    return {
        "name": e.name,
        "url": e.url,
        "page": provider_page_url(e.id),
        # Whole, never folded: freetier-check holds it to 300 characters, and the
        # README's row is this sentence, the models and the date. The quota is on
        # the row's page, one click from the date.
        "offering": e.offering,
        # A mark beside the name: the card is the exception, easier to see there
        # than in a column of agreement, and the section headings count it in
        # words.
        "card_flag": _card_flag(e) + _access_flag(e),
        # Beside the name too: a fact about the row, not a value beside the date.
        "new_flag": " 🧪" if e.provisional else "",
        # What the reader pays besides money: the vendor may train on what they
        # send. One glyph like the card's; the vendor's sentence is on the page.
        "data_flag": " 👁" if _trains(e) else "",
        "verified": e.last_verified.isoformat(),
        # The step between reading a row and calling it: where to get the key,
        # for a lane that takes one (a vendor's printed key is on that page too).
        "key_url": e.api.key_url if e.api and e.api.key_url and e.api.key_kind != "none" else "",
        # The row's families, as `_row_models` names them; a row that names none
        # has the date alone on its small line.
        "models": _row_models(e, pages),
    }


def _departure(e: Entry) -> date:
    """The day the reason a row is archived for names — what the Archive is
    ordered by, latest first."""
    if e.delisted is not None:
        return e.delisted.on
    return e.retired_on or e.last_verified


def _archive(entries: list[Entry], today: date) -> list[Entry]:
    """The archived rows a reader is shown: one line per service.

    A row folded into another (`duplicate_of`) names a service the Archive
    already holds, so it is left out of every list that counts services. It
    stays in the registry, its page stays at its own URL pointing at the row
    that holds the service (`build_folded_page`), and that row names it back.
    The latest departure comes first, as every Archive prints it."""
    return sorted((e for e in entries if is_archived(e, today) and e.duplicate_of is None),
                  key=lambda e: (_departure(e), e.name.lower()), reverse=True)


def _archived_rows(entries: list[Entry], today: date) -> list[dict[str, str]]:
    """The Archive: each row's name linking its own page, and why it left, the
    latest departure first.

    The page carries the evidence; a vendor link for a row that left is at best
    dead and at worst, for a row rejected for cause, a referral. No last probe
    pass either: a probe anchored on a page that outlives the offer goes on
    passing after the vendor's end date."""
    gone = _archive(entries, today)
    return [{"name": e.name, "page": provider_page_url(e.id),
             "why": _fold(archive_reason(e, today), README_LIMITS_TEASER,
                          README_LIMITS_COLLAPSE, small=True)}
            for e in gone]


def _card_flag(e: Entry) -> str:
    """The mark beside a name, wherever a page lists rows: 💳 for a row that
    wants a card on file, nothing for one that does not."""
    return " 💳" if e.card_required else ""


def _card_words(e: Entry) -> str:
    """The same fact where a page says it in words."""
    return "card required" if e.card_required else "no card"


def _access_flag(e: Entry, family: str | None = None, *, compact: bool = True) -> str:
    words = _access_description(e, family, compact=compact)
    return f" ({words})" if words else ""


def _access_description(e: Entry, family: str | None = None, *, compact: bool = True) -> str:
    return "; ".join(text for text in (
        access_words(family_access(e, family) if family else e.access, compact=compact),
        family_condition(e, family) if family else "") if text)


def _entry_family_links(e: Entry, families: list[str], pages: set[str], sep: str = ", ") -> str:
    return sep.join(_family_links([f], pages) + _access_flag(e, f) for f in families)


def _provisional_words(e: Entry) -> str:
    return f"provisional since {e.first_seen.isoformat()}"


def _notice_quote(notice: Notice) -> str:
    """A lane that does not work as published, as the pages that quote the
    notice whole say it: first, above the offer and above the base URL."""
    return f"> ⚠️ **Does not work as published since {_notice_since(notice)}.** {notice.text}"


def env_var(entry_id: str) -> str:
    return entry_id.removesuffix("-free").replace("-", "_").replace(".", "_").upper() + "_API_KEY"


def needs_no_account(e: Entry) -> bool:
    """Whether a reader calls the lane without making an account: there is a
    lane to call, and it takes no key or the vendor prints one for anyone
    (`api.public_key`). The README's picks, the LiteLLM group and the site's
    filter all ask this."""
    return bool(e.api and e.api.base_url) and e.api.key_kind in ("none", "public")


# Why a config written once — litellm.yaml, opencode.json, claude-code.sh —
# cannot carry an ask (models.ASKS), or None where it can: a client names
# itself on every request it sends, but a stable id per conversation is the
# calling client's to make up, and a static file would pin one id for every
# conversation. Every table keyed by the asks is held to ASKS by the tests.
ASK_CONFIG: dict[str, str | None] = {
    "user-agent": None,
    "session-header": ("every request needs a stable id per conversation in {}, which a static "
                       "config cannot supply"),
}


def _static_blockers(e: Entry) -> list[str]:
    """Why a config written once cannot call the row's lane; none where it can."""
    return [ASK_CONFIG[name].format(value) for name, value in e.api.asks() if ASK_CONFIG[name]]


def _connectable(entries: list[Entry], today: date) -> list[Entry]:
    return sorted(
        (e for e in entries
         if not is_archived(e, today) and e.api and e.api.base_url and e.api.openai_compatible),
        key=_by_rank,
    )


def _configurable(entries: list[Entry], today: date) -> list[Entry]:
    """The connectable rows a config written once can actually call: none whose
    ask it cannot carry (`_static_blockers`). OpenCode sends x-opencode-session
    only to a provider whose id starts with "opencode", its own, and
    opencode.json names each provider after its row, so a session header rules
    out opencode.json too. Those rows are connected by a
    client that sends the header, which the connection table, the provider page,
    the env example and llms.txt name."""
    return [e for e in _connectable(entries, today) if not _static_blockers(e)]


def _notice_data(notice: Notice | None) -> dict | None:
    """A notice as a template reads it, or None."""
    return ({"since": notice.since.isoformat(), "text": notice.text, "url": notice.url or ""}
            if notice else None)


def _notice_since(notice: Notice) -> str:
    """The notice's date, linked to where the problem is followed when the row
    names a place — the same idiom as the README's verified dates, which link
    to their evidence."""
    since = notice.since.isoformat()
    return f"[{since}]({notice.url})" if notice.url else since


def _model_index(active: list[Entry], pages: set[str]) -> list[dict]:
    """Model family → everyone who serves it free, most-served first
    (`_rows_by_family`), with the family's page and tier where it has them.

    A row that needs a card carries its 💳 here too: "free at" beside a name
    with no mark reads as free without one.
    """
    out = []
    for family, ps in _rows_by_family(active).items():
        mark = _measured(family, ps)
        out.append({"family": family,
                    "page": model_page_url(family) if family in pages else "",
                    "tier": mark.tier.value if mark is not None else "",
                    "providers": [{"id": p.id, "name": p.name, "url": p.url,
                                   "card_flag": _card_flag(p) + _access_flag(p, family)}
                                  for p in ps]})
    return out


def _rows_by_family(active: list[Entry]) -> dict[str, list[Entry]]:
    """Every family the live rows publish, and the rows that serve it free —
    the most widely served family first, then by name, and each family's rows
    in the order the list reads them. The one grouping behind the model index,
    the model pages and index.json's `models`, so the three name the same
    families with the same rows."""
    by_family: dict[str, list[Entry]] = {}
    for e in active:
        for family in live_families(e):
            by_family.setdefault(family, []).append(e)
    return {family: sorted(rows, key=lambda e: (requires_payment(e, family), *_by_rank(e)))
            for family, rows in sorted(by_family.items(), key=lambda kv: (-len(kv[1]), kv[0]))}


# Best first: where two lanes serve variants that measure apart, a page says
# the better of the two.
_TIER_ORDER = (Tier.FRONTIER, Tier.STRONG, Tier.NOTABLE)


def _measured(family: str, rows: list[Entry]) -> ModelFamily | None:
    """The tier mark a family carries on its rows — the same model measured
    the same way, so the rows agree — the best of them where they do not."""
    marks = [m for e in rows for m in e.models
             if m.family == family and m.superseded_by is None and m.tier is not None]
    return min(marks, key=lambda m: _TIER_ORDER.index(m.tier), default=None)


def _has_model_page(family: str, rows: list[Entry]) -> bool:
    return (len(rows) >= MODEL_PAGE_ROWS or _measured(family, rows) is not None
            or any(a and a.until for e in rows if (a := family_access(e, family))))


def model_pages(entries: list[Entry], events: list[Event], today: date,
                published: frozenset[str] = frozenset()) -> set[str]:
    """Every model with a page: each the rule gives one today
    (`_has_model_page`), and each page already published whose family the list
    has named.

    The second half keeps an address: a model that drops below the rule, or
    that no row serves free any more, keeps its page, which says what became of
    the model, rather than turning a URL a search engine indexed into a 404.
    `published` is the directory of pages the repository holds
    (`_published_beside`), which freetier-gate never lets a commit shrink; a
    file there whose family no row and no history line ever named is nobody's
    page, and the render takes it away."""
    active = [e for e in entries if not is_archived(e, today)]
    pages = {f for f, rows in _rows_by_family(active).items() if _has_model_page(f, rows)}
    named = ({m.family for e in entries for m in e.models}
             | {f for ev in events for f in ev.models})
    return pages | (set(published) & named)


def _published_beside(registry_path: Path) -> frozenset[str]:
    """The model pages the repository already publishes, read from models/
    beside the registry the way the history and the watchlist are — so
    `--check`, rendering into a scratch directory, keeps the same pages the
    render keeps in the repository."""
    return frozenset(p.stem for p in (registry_path.parent / MODELS_DIR).glob("*.md")
                     if p.stem != "index")


def _new_rows(active: list[Entry], history: list[Event], today: date) -> list[dict]:
    """The live rows the list added in the last NEW_ROWS_DAYS, newest first: a
    list is worth a second visit when it moves, and its changes table sits at
    the foot of the list, folded."""
    live = {e.id: e for e in active}
    since = today - timedelta(days=NEW_ROWS_DAYS)
    added = sorted((ev for ev in history if ev.event is EventType.ADDED and ev.id in live
                    and since < ev.ts.date() <= today), key=lambda ev: ev.ts, reverse=True)
    seen: dict[str, dict] = {}
    for ev in added:
        # The name without its gloss — "(formerly Vertex AI)", "(free models)" — on a
        # line that names up to a week of rows; the row itself keeps it. A name that
        # fits a phone's line is kept on one.
        name = re.sub(r"\s*\([^()]*\)$", "", live[ev.id].name)
        if len(name) <= 24:
            name = name.replace(" ", "\u00a0")
        seen.setdefault(ev.id, {"name": name, "page": provider_page_url(ev.id)})
    return list(seen.values())


def _hero(active: list[Entry], shared: dict) -> Hero:
    """What the picture at the top of the README shows: the counters the text
    states, and a dot per live row in its section. No date: the badge under it
    carries the list's one date, its floor (`_floor`)."""
    return Hero(live=shared["active_count"], no_card=shared["no_card_count"],
                models=shared["family_count"], strong=len(shared["strong_models"]),
                schedule=shared["schedule"],
                arcs=tuple(Arc(label, tone, sum(1 for e in active if e.category is cat))
                           for cat, (label, tone) in HERO_ARCS.items()))


def load_scores(path: Path = SCORES_PATH) -> dict | None:
    """The scores freetier-tiers last read off the index, or None before the
    first --write has kept any."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _plain_model(name: str) -> str:
    """The board names a model with its settings — "Claude Opus 5.5 (Adaptive
    Reasoning, Max Effort, Default Fallback)" — and a label needs the model."""
    return re.sub(r"\s*\(.*\)\s*$", "", name)


def _chart(strong: list[dict], scores: dict | None) -> Chart | None:
    """The strong models the README names, each with the score its tier was read
    off; None where no score is kept for any of them, and the page stays a list."""
    if not scores:
        return None
    kept = scores.get("families") or {}
    bars = tuple(Bar(m["family"], kept[m["family"]]["index"], len(m["providers"]),
                     m["frontier"], bool(kept[m["family"]].get("estimated")))
                 for m in strong if m["family"] in kept)
    if not bars:
        return None
    return Chart(bars=bars, top_name=_plain_model(scores["top"]["name"]),
                 top_score=scores["top"]["index"], read_on=date.fromisoformat(scores["read_on"]),
                 frontier_within=FRONTIER_WITHIN, strong_within=STRONG_WITHIN)


def readme_pictures(hero: Hero, chart: Chart | None = None) -> dict[str, str]:
    """Every picture the README names, by its path beside the README, in each
    of its VARIANTS: the wide pair one palette each, the narrow one with both —
    and the site's mark, the hero's radar alone (SITE_RADAR)."""
    drawers = {"hero": lambda palette, narrow: hero_svg(hero, palette, narrow=narrow)}
    if chart is not None:
        drawers["strong"] = lambda palette, narrow: chart_svg(chart, palette, narrow=narrow)
    palettes = {"light": (LIGHT, False), "dark": (DARK, False), "narrow": (None, True)}
    pictures = {f"{README_PICTURES}/{name}-{variant}.svg": draw(*palettes[variant])
                for name, draw in drawers.items() for variant in VARIANTS}
    pictures[SITE_RADAR] = radar_svg(hero)
    return pictures


def _in_chart_order(strong: list[dict], scores: dict | None) -> list[dict]:
    """The strong models as the chart ranks them (Chart.ranked) — the highest
    score first, each with its `score` — and a model no score is kept for after
    them, in its own order: one ranking for the README's chart, the list under
    it and the site."""
    kept = (scores or {}).get("families") or {}
    scored = [{**m, "score": kept[m["family"]]["index"] if m["family"] in kept else None}
              for m in strong]
    return sorted(scored, key=lambda m: (m["score"] is None, -(m["score"] or 0),
                                         m["family"] if m["score"] is not None else ""))


def _strong_models(active: list[Entry]) -> list[dict]:
    """The models a reader comes for, and every row that serves each one free.

    The frontier and strong families, their tier marks measured against the
    Artificial Analysis index and never typed; the bar keeps the set short.
    Frontier first, then the most widely served — every row beside a model is
    one more free quota of it — and the name to break a tie. A family, its rows
    and its mark are the ones its model page prints (`_rows_by_family`,
    `_measured`). A row that needs a card carries its 💳 here as in the list."""
    strong = []
    for family, rows in _rows_by_family(active).items():
        mark = _measured(family, rows)
        if mark is not None and mark.tier in (Tier.FRONTIER, Tier.STRONG):
            # Every family here measures strong or better, so every one has a page.
            strong.append({"family": family, "frontier": mark.tier is Tier.FRONTIER,
                           "page": model_page_url(family),
                           "providers": [{"name": p.name, "url": p.url,
                                          "card_required": p.card_required,
                                          "card_flag": _card_flag(p) + _access_flag(p, family)} for p in rows]})
    # Stable: each tier keeps _rows_by_family's order, the most widely served first.
    return sorted(strong, key=lambda m: not m["frontier"])


def _starters(active: list[Entry]) -> list[dict]:
    """The agents a reader can code with today, named before the list.

    The answer to "what do I actually use?" is the agents that run on a $0 plan,
    not the keyless quickstart, a rate-limited demo: live agent rows that ask for
    no card, in `rank` order, at most README_STARTERS of them. Nothing here is
    typed by hand, so the promise cannot outlive the row.

    A row with no families is skipped rather than ranked down: the block exists
    to name models.
    """
    rows = [e for e in active
            if e.category is Category.AGENT_CLI and not e.card_required
            and not requires_payment(e) and live_families(e)]
    return [_starter(e) for e in sorted(rows, key=_by_rank)[:README_STARTERS]]


# The order a starter names its families in: the tiers a reader comes for first.
_TIER_FIRST = {Tier.FRONTIER: 0, Tier.STRONG: 1, Tier.NOTABLE: 2}


def _starter(e: Entry) -> dict:
    tiers = {m.family: m.tier for m in e.models}
    families = sorted((f for f in live_families(e) if not requires_payment(e, f)),
                      key=lambda f: _TIER_FIRST.get(tiers.get(f), len(_TIER_FIRST)))
    return {"name": e.name, "url": e.url, "families": families[:README_STARTER_MODELS],
            "more": max(0, len(families) - README_STARTER_MODELS),
            "page": provider_page_url(e.id)}


def _codex_command(e: Entry) -> str:
    """How a reader starts Codex CLI on a row's own profile."""
    return f"codex -p {e.id}"


def _pick(e: Entry, families: list[str] | None = None) -> dict:
    return {"name": e.name, "url": e.url, "families": families or []}


def _picks(active: list[Entry], connectable: list[Entry]) -> dict[str, list[dict]]:
    """The answers to "which one, for me": the strongest models for nothing, the
    key that gets the most work done, no account at all, a trial that will not
    ask for a card. A section's answer is its own `rank` order with the
    card-required rows removed, capped at README_PICKS, so a row that stops
    verifying leaves the table on the run it leaves the list.

    "Frontier" crosses sections. It names the families that earned the tier
    mark (one tier per family, enforced by freetier-check), and since `rank`
    orders a row only within its own category, it is ordered by how many
    frontier families the entry hands over, and only then by rank.

    Keyless rows come from the connection table's order rather than a section's,
    card rows not taken out: "no account" is a property of the endpoint, the
    same one the quickstart is chosen by.
    """
    ranked = [e for e in sorted(active, key=_by_rank) if not e.card_required and not requires_payment(e)]

    def top(category: Category) -> list[dict]:
        return [_pick(e) for e in ranked if e.category is category][:README_PICKS]

    frontier = []
    for e in ranked:
        families = [m.family for m in e.models
                    if m.superseded_by is None and m.tier is Tier.FRONTIER
                    and not requires_payment(e, m.family)]
        if families:
            frontier.append((len(families), e.rank, e.name.lower(), _pick(e, families)))
    frontier.sort(key=lambda row: (-row[0], row[1], row[2]))
    return {
        "frontier": [row[3] for row in frontier[:README_PICKS]],
        "apis": top(Category.API_FREE_TIER),
        "aggregators": top(Category.AGGREGATOR),
        "keyless": [_pick(e) for e in connectable if needs_no_account(e)][:README_PICKS],
        "trials": top(Category.TRIAL),
        # A gateway whose vendor documents an Anthropic-format route, across
        # sections, in rank order.
        "claude_code": [_pick(e) for e in ranked
                        if e.api and e.api.anthropic_base_url][:README_PICKS],
        # Codex's answer: a lane Codex calls directly with the row's own
        # profile (api.codex), in rank order across sections.
        "codex": [{**_pick(e), "command": _codex_command(e)}
                  for e in ranked if codex_ready(e)][:README_PICKS],
    }


def picks(entries: list[Entry], today: date) -> dict[str, list[dict]]:
    """The README's "I want…" answers, for anything else that publishes them."""
    active = [e for e in entries if not is_archived(e, today)]
    return _picks(active, _connectable(entries, today))


def _quickstart(connectable: list[Entry]) -> dict | None:
    """The one call a reader can make before deciding to trust any of this: the
    first connectable lane that takes no key and lists a callable id, or None.
    Generated, so the command is archived along with its row.

    It carries the lane's api note: a keyless lane is rate-limited instead, and
    the README's first command is where a reader meets that limit.
    """
    for e in connectable:
        if e.api.key_kind == "none" and e.api.model_ids:
            notice = e.api.notice
            start = {"name": e.name, "url": e.url,
                     "base_url": e.api.base_url.rstrip("/"),
                     "model_id": preferred_ids(e)[0],
                     "note": e.api.note,
                     "asks": e.api.asks(),
                     # The command stays on the page while the list waits for the
                     # vendor, so the page says, right under it, that it does not
                     # work and since when.
                     "notice": _notice_data(notice)}
            return {**start, "curl": _quickstart_curl(start)}
    return None


def _quickstart_curl(start: dict) -> str:
    """The command itself, built once for both pages that print it.

    The site prints it twice, in a <pre> and in the copy button's attribute, and
    it carries both quote characters: assembled by the template, a fragment
    Jinja had marked safe would close the attribute on the first of them. Built
    as one string here, it prints as it is in the README's code block and
    escaped correctly in both places on the site.
    """
    return _curl(start["base_url"], start["model_id"], start["asks"])


def _curl(base_url: str, model_id: str, asks: list[tuple[str, str]],
          key: str | None = None) -> str:
    """One chat call to a lane, as a shell command: the quickstart's, and the
    one each provider page offers for checking a key — with the key read from
    the reader's own environment, since a key belongs in their terminal and
    nowhere else (`_try_it`)."""
    lines = [f"curl -s {base_url.rstrip('/')}/chat/completions \\"]
    if key:
        lines.append(f'  -H "Authorization: Bearer {key}" \\')
    lines.append("  -H 'Content-Type: application/json' \\")
    lines += [_ASK_CURL[name].format(value) for name, value in asks]
    lines.append(f"""  -d '{{"model":"{model_id}","messages":"""
                 """[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'""")
    return "\n".join(lines)


# Each ask as a header line of the quickstart's curl.
_ASK_CURL = {"user-agent": "  -H 'User-Agent: " + QUICKSTART_USER_AGENT + "' \\",
             "session-header": '  -H "{}: quickstart-$RANDOM$RANDOM" \\'}


def _watch_rows(watchlist: list[Watched], today: date) -> list[dict]:
    """Newest verdict first, so the freshest reading is the one a reader meets."""
    return [
        {"name": w.name, "reason": w.reason.strip(), "reopen_if": w.reopen_if.strip(),
         "checked_on": w.checked_on.isoformat(), "current": is_watch_current(w, today)}
        for w in sorted(watchlist, key=lambda w: (-w.checked_on.toordinal(), w.name.lower()))
    ]


def _newest_first(events: list[Event], limit: int) -> list[Event]:
    return sorted(events, key=lambda e: e.ts, reverse=True)[:limit]


def _event_link(ev: Event, entries: list[Entry] | None, today: date) -> str:
    """Where an event sends a reader: the vendor while the row is live, the row's
    own page once it is in the Archive — the vendor of a row that left is dead,
    or for a row rejected for cause, somewhere this list sends no one."""
    row = next((e for e in entries or [] if e.id == ev.id), None)
    if row is not None and is_archived(row, today):
        return provider_page_url(row.id)
    return ev.url or REPO_URL


def event_detail(ev: Event, entries: list[Entry] | None) -> str:
    """What an event says after its name: its detail, or, for a delisting that
    carries none (a row deleted before rows were archived), the reason the
    row's `delisted` keeps — on every page that lists events of many rows. The
    row's own page says it once, in its header."""
    if ev.detail or ev.event is not EventType.REMOVED:
        return ev.detail
    row = next((e for e in entries or [] if e.id == ev.id), None)
    return row.delisted.reason if row is not None and row.delisted is not None else ""


def _change_rows(events: list[Event], entries: list[Entry] | None = None,
                 today: date | None = None, limit: int = README_CHANGES) -> list[dict]:
    """The tail of the log, newest first, as Markdown table cells: the site's
    rows with the detail made safe for a table.

    Pipes are escaped here rather than rejected in `freetier-check`: an event's
    detail is copied out of an entry's own `offering`, so a pipe in it is a
    perfectly good sentence that only this one table would trip over.
    """
    return [{**row, "detail": row["detail"].replace("|", r"\|") or "—"}
            for row in _site_changes(events, entries, today or date.today(), limit)]


def _rfc3339(stamp: datetime) -> str:
    """A full timestamp with an offset, as Atom demands. A naive one can only
    have come from a hand-written line, and is read as UTC, never as the
    runner's local time."""
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _feed_entry_id(ev: Event) -> str:
    """A tag URI, per RFC 4151 — permanent, unique, and not a promise that
    anything is served at that address.

    The timestamp is part of it because the same entry legitimately produces the
    same kind of event more than once: a gateway rotates its free lane, and
    `models` fires again a fortnight later. A reader that has seen this id must
    never be shown the row again, so nothing here may be derived from anything
    a later run can change — not the entry's name, not its url, not its position
    in the file.
    """
    when = _rfc3339(ev.ts).replace("-", "").replace(":", "")
    return f"tag:mvalentsev.github.io,2026:awesome-free-ai-coding/{ev.event.value}/{ev.id}/{when}"


def build_feed(events: list[Event], today: date, limit: int = FEED_ENTRIES,
               entries: list[Entry] | None = None) -> str:
    """The change log as Atom.

    Hand-written rather than templated, because the escaping is the substance:
    an entry's name and a vendor's own sentence about its free tier both reach
    this file verbatim, and an unescaped ampersand in either makes the whole feed
    unparseable rather than one row wrong.
    """
    recent = _newest_first(events, limit)
    updated = max((e.ts for e in recent),
                  default=datetime.combine(today, time.min, tzinfo=timezone.utc))
    out = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        "  <title>awesome-free-ai-coding — what changed</title>",
        "  <subtitle>Free LLM APIs and coding agents arriving, changing and dying, "
        f"as the probes that run {_schedule()} see it.</subtitle>",
        f"  <id>{FEED_URL}</id>",
        f"  <link rel=\"self\" href={quoteattr(FEED_URL)}/>",
        f"  <link rel=\"alternate\" href={quoteattr(REPO_URL)}/>",
        f"  <updated>{_rfc3339(updated)}</updated>",
        "  <author><name>freetier-radar</name></author>",
    ]
    for ev in recent:
        title = f"{EVENT_WORDS[ev.event]}: {ev.name}"
        summary = event_detail(ev, entries) or title
        # Only where the list is what the event is about. An entry on its way
        # out carries its last known families too, and appending them to
        # "Delisted" reads as an offer rather than as an epitaph.
        if ev.models and ev.event in (EventType.ADDED, EventType.RESTORED, EventType.MODELS):
            summary += " · free models: " + ", ".join(ev.models)
        out += [
            "  <entry>",
            f"    <id>{escape(_feed_entry_id(ev))}</id>",
            f"    <title>{escape(title)}</title>",
            f"    <link rel=\"alternate\" href={quoteattr(_event_link(ev, entries, today))}/>",
            f"    <updated>{_rfc3339(ev.ts)}</updated>",
            f"    <summary type=\"text\">{escape(summary)}</summary>",
            "  </entry>",
        ]
    out.append("</feed>")
    return "\n".join(out) + "\n"


# Each ask as the connection table's cell says it, beside the key.
_ASK_CELL = {"user-agent": "your client's own `User-Agent`",
             "session-header": "`{}` per conversation"}


def _auth_cell(e: Entry) -> str:
    """What a client sends to be let in: the key, or none, the key the vendor
    prints for anyone where it prints one, and whatever else the vendor asks
    every request to carry."""
    kind = e.api.key_kind
    cell = "—" if kind == "none" else f"`{env_var(e.id)}`"
    subs = []
    if kind == "public":
        subs.append(f"no account: the vendor prints one for anyone, `{e.api.public_key}`")
    asks = [_ASK_CELL[name].format(value) for name, value in e.api.asks()]
    if asks:
        subs.append(("" if kind == "none" else "and ") + " and ".join(asks))
    if not subs:
        return cell
    return cell + "<br><sub>" + "; ".join(subs) + "</sub>"


def _connection_note(e: Entry) -> str:
    """The cell under a provider's name in the connection table: a notice first,
    since it is what a reader copying the base URL most needs to know, then the
    note, each folded at the README_NOTE_* marks."""
    parts = []
    if e.api.notice:
        parts.append(f"⚠️ <sub>**Does not work as published since {_notice_since(e.api.notice)}.**</sub>"
                     "<br>" + _fold(e.api.notice.text, README_NOTE_TEASER, README_NOTE_COLLAPSE,
                                    small=True))
    if e.api.note:
        parts.append(_fold(e.api.note, README_NOTE_TEASER, README_NOTE_COLLAPSE, small=True))
    return "<br>".join(parts)


def _shared_facts(entries: list[Entry], today: date,
                  watchlist: list[Watched] | None = None,
                  pages: set[str] | None = None) -> dict:
    """Every figure and every stated rule the README and the site both print,
    worked out once: a figure computed in one place cannot be two figures, and a
    rule the code applies — the frontier bar, the provisional fortnight, how
    often a row is probed, how a row leaves — is printed from the constant that
    applies it.
    """
    active = [e for e in entries if not is_archived(e, today)]
    connectable = _connectable(entries, today)
    # The badge dates the evidence, not the render: the oldest passing probe
    # among live rows, a floor every row on the page meets, in `_floor`'s words.
    colour = badge_colour(_oldest_verified(active, today), today)
    pages = model_pages(entries, [], today) if pages is None else pages
    model_index = _model_index(active, pages)
    anthropic = _anthropic_ready(entries, today)
    return {
        "date": today.isoformat(),
        "verified_floor": _floor(active, today),
        "verified_colour": colour,
        "verified_word": BADGE_WORDS[colour],
        # The headline counts.
        "active_count": len(active),
        "no_card_count": sum(1 for e in active if not e.card_required),
        "card_count": sum(1 for e in active if e.card_required),
        "no_signup_count": sum(1 for e in connectable if needs_no_account(e)),
        "endpoint_count": len(connectable),
        "family_count": len(model_index),
        "model_index": model_index,
        "models_url": models_index_url(),
        "model_page_rule": _model_page_rule(),
        # Every model with a page and its address: each place a page names a
        # model links its page (the site's `chip` macro reads this).
        "model_pages": {f: model_page_url(f) for f in sorted(pages)},
        "strong_models": _strong_models(active),
        "starters": _starters(active),
        "picks": _picks(active, connectable),
        "quickstart": _quickstart(connectable),
        # Every verdict on the page of services checked and not listed, a
        # verdict due for a fresh look included — that page lists them all.
        "watch_count": len(watchlist or []),
        # The LiteLLM groups the config defines today, and the shell function a
        # reader is shown as the example: both are read off the files they name.
        "litellm_groups": litellm_groups(entries, today),
        "litellm_command": litellm_command(),
        "claude_example": f"claude-{anthropic[0].id}" if anthropic else "",
        # Codex's profile over litellm.yaml: its path from the repository's root
        # and from configs/, the name `codex -p` takes, and the versions it needs.
        "codex": {"path": CODEX_LITELLM_PATH,
                  "here": CODEX_LITELLM_PATH.removeprefix("configs/"),
                  "name": CODEX_LITELLM_PROFILE, "since": CODEX_SINCE,
                  "litellm_since": LITELLM_BRIDGE_SINCE},
        "has_provisional": any(e.provisional for e in active),
        "has_trains": any(_trains(e) for e in active),
        "schedule": _schedule(),
        "frontier_within": f"{FRONTIER_WITHIN:g}",
        "strong_within": f"{STRONG_WITHIN:g}",
        "provisional_weeks": weeks(PROVISIONAL_PROMOTE_DAYS),
        "archive_after_failures": ARCHIVE_AFTER_FAILURES,
        "archive_after_days": ARCHIVE_AFTER_DAYS,
        "watch_recheck_days": WATCH_RECHECK_DAYS,
        "checked_url": checked_page_url(),
        "feed_url": FEED_URL,
        "pages_url": PAGES_URL,
        "repo_url": REPO_URL,
    }


def _card_counts(rows: list[Entry]) -> dict:
    """A section's figures: its rows, how many ask for no card, and whether all
    of them do — a section that is all no-card says so in words rather than
    leaving the reader to compare two figures."""
    no_card = sum(1 for e in rows if not e.card_required)
    return {"count": len(rows), "no_card": no_card,
            "all_no_card": bool(rows) and no_card == len(rows)}


def build_context(entries: list[Entry], today: date,
                  watchlist: list[Watched] | None = None,
                  history: list[Event] | None = None,
                  pages: set[str] | None = None,
                  scores: dict | None = None) -> dict:
    active = [e for e in entries if not is_archived(e, today)]
    pages = model_pages(entries, history or [], today) if pages is None else pages
    sections = []
    for cat, title in CATEGORY_TITLES.items():
        rows = _ordered(active, cat)
        sections.append({"title": title, "rows": [_row(e, pages) for e in rows],
                         **_card_counts(rows)})
    connections = [
        {"name": e.name, "base_url": e.api.base_url,
         "page": provider_page_url(e.id),
         "anthropic_base_url": e.api.anthropic_base_url or "",
         "codex": _codex_command(e) if codex_ready(e) else "",
         "codex_profile": (codex_profile_path(e).removeprefix("configs/")
                           if codex_ready(e) else ""),
         "auth": _auth_cell(e),
         "key_url": e.api.key_url or "",
         "keyless": e.api.key_kind == "none",
         "note": _connection_note(e)}
        for e in _connectable(entries, today)
    ]
    shared = _shared_facts(entries, today, watchlist, pages)
    hero = _hero(active, shared)
    scores = load_scores() if scores is None else scores
    # The list folded under the chart answers "where" for the same bars, in
    # the same order.
    strong = _in_chart_order(shared["strong_models"][:README_STRONG], scores)
    chart = _chart(strong, scores)
    return {**shared,
            "dot": DOT,
            "hero": hero,
            "hero_alt": hero_words(hero),
            "chart": chart,
            "chart_alt": chart_words(chart) if chart else "",
            # How the README's <picture> serves each file readme_pictures draws.
            "pictures_dir": README_PICTURES,
            "narrow_until": NARROW_UNTIL,
            "picture_width": PICTURE_WIDTH,
            # The README names the first README_STRONG strong models and links
            # the rest; the site has no budget and names them all.
            "readme_strong": strong,
            "strong_more": max(0, len(shared["strong_models"]) - README_STRONG),
            "sections": sections,
            "new_rows": _new_rows(active, history or [], today),
            "archived": _archived_rows(entries, today),
            "connections": connections,
            # The answer to "why isn't X here?", read from the file the scout
            # filters proposals with. The README only asks whether there is
            # one and links the checked page (`build_checked_page`).
            "watchlist": _watch_rows(watchlist or [], today),
            # The only part of the page that is not a statement about today:
            # the tail of history.jsonl.
            "changes": _change_rows(history or [], entries, today)}


def _country_key(name: str) -> str:
    """Where a reader looks for a country in a list: "mainland China" under C,
    Åland under A."""
    plain = unicodedata.normalize("NFKD", name.removeprefix("mainland ")).encode("ascii", "ignore")
    return plain.decode().casefold()


def _index_countries() -> list[dict]:
    """Every country and territory a border can name, under the name a reader
    looks for — "United Arab Emirates", not the article a sentence needs — in
    the order a reader scans."""
    named = [{"code": code, "name": country_name(code).removeprefix("the ")} for code in COUNTRIES]
    return sorted(named, key=lambda c: _country_key(c["name"]))


def build_index(entries: list[Entry], today: date,
                watchlist: list[Watched] | None = None,
                pages: set[str] | None = None) -> dict:
    from .quotas import structured_quotas
    return {
        "generated": today.isoformat(),
        "source": REPO_URL,
        "feed": FEED_URL,
        "entries": [
            {**e.model_dump(mode="json", exclude_none=True), "limits": limits_text(e),
             **({"quotas": structured_quotas(e)} if structured_quotas(e) else {}),
             "archived": is_archived(e, today),
             **({"access_labels": {"offer": access_words(e.access, compact=True),
                                   "models": {f: _access_description(e, f, compact=True)
                                              for f in live_families(e)}}}
                if e.access or e.page_catalog or ((lane := e.api or e.client_lane) and lane.model_access) else {}),
             **({"archived_because": archive_reason(e, today)} if is_archived(e, today) else {}),
             "page": provider_page_url(e.id)}
            for e in entries
        ],
        # Every country a border can name, for a page that asks where the reader
        # is (browse.html's picker): the codes the borders are recorded in.
        "countries": _index_countries(),
        # Additive, like the watchlist: which rows serve each model free, the
        # question a machine asks of this list as often as a reader does, and
        # the page a model has where it has one.
        "models": _index_models(entries, today,
                                model_pages(entries, [], today) if pages is None else pages),
        # Additive: a consumer reading .entries is unaffected. "Considered and
        # not listed, on this date, for this reason" is an answer worth
        # publishing in machine-readable form too.
        "watchlist": [
            {**w.model_dump(mode="json"), "current": is_watch_current(w, today)}
            for w in (watchlist or [])
        ],
    }


# The site's own front page. GitHub Pages renders Markdown with kramdown, which
# does not read Markdown inside a block-level <div>, does not know GitHub's
# alert syntax and escapes a <summary> it meets inside a table cell, so the
# README, written for GitHub's renderer, cannot be the site's front page.
# index.html at the repository root is: Pages serves it in place of the README
# (jekyll-readme-index only steps in where no index exists), and it is rendered
# from the same registry on the same run, held to it by `freetier-render --check`.
SITE_TEMPLATE = "index.html.j2"
SITE_PAGE = "index.html"
# What the page's nav bar calls each section. The bar is one line at every width
# — the tables' sticky headers are positioned under it, and a bar that wrapped
# would cover the first row of every table — so it carries the short name and
# the heading it jumps to carries the full one. Beside CATEGORY_TITLES rather
# than in the template, so a new category is one edit and a test can hold the
# two dicts to the same keys.
SITE_NAV_LABELS: dict[Category, str] = {
    Category.AGENT_CLI: "Agents",
    Category.API_FREE_TIER: "APIs",
    Category.TRIAL: "Trials",
    Category.AGGREGATOR: "Aggregators",
}
# What the page's search understands as a filter rather than as text: each
# section by the words a reader types for it, and the four answers a row's tags
# carry. A reader who types "no card" or "claude code" is asking for rows
# that are so, not for rows whose prose says it.
SEARCH_SECTION_WORDS: dict[Category, tuple[str, ...]] = {
    Category.AGENT_CLI: ("agents", "agent", "cli"),
    Category.API_FREE_TIER: ("apis", "api"),
    Category.TRIAL: ("trials", "trial"),
    Category.AGGREGATOR: ("aggregators", "aggregator", "gateways", "gateway", "routers", "router"),
}
SEARCH_FILTERS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("nocard", "No card", ("no card", "nocard", "no credit card", "without a card")),
    ("nokey", "No key", ("no key", "keyless", "no account", "no signup", "anonymous")),
    ("claude", "Claude Code", ("claude code", "claude-code")),
    ("strong", "Strong models", ("strong models", "strong", "frontier")),
)


def _search_config() -> dict:
    """The search's filters, in the page as JSON: the sections the nav names and
    the four row answers, each with the words that select it."""
    return {
        "sections": [{"id": cat.value, "label": SITE_NAV_LABELS[cat],
                      "emoji": CATEGORY_TITLES[cat].partition(" ")[0],
                      "words": list(SEARCH_SECTION_WORDS[cat])} for cat in CATEGORY_TITLES],
        "filters": [{"id": fid, "label": label, "words": list(words)}
                    for fid, label, words in SEARCH_FILTERS],
    }


# Shorter than the README's ten: the page shows the changes as cards rather than
# table rows, and the feed is one click away under them.
SITE_CHANGES = 8
# How many of a row's families the page shows before it folds the rest under
# their count — the README line's number, so the two read the same row alike.
# Every family stays in the page, where the search and a browser's find reach it.
SITE_MODELS = README_MODELS
# How fresh the floor date reads in words, beside the colour badge_colour gives
# it — a colour alone is not an answer for a reader who cannot see it.
BADGE_WORDS = {BADGE_GREEN: "fresh", BADGE_AMBER: "ageing", BADGE_RED: "stale"}


def _site_fold(text: str) -> dict[str, str]:
    """A long cell as data, not as markup: what the page shows first, and all of
    it. The template decides the markup and escapes both halves, so a vendor's
    own sentence — angle brackets, ampersands and all — is data here."""
    if len(text) <= README_LIMITS_COLLAPSE:
        return {"text": text, "teaser": ""}
    lead, separator, rest = text.partition("\n\n")
    if separator and len(lead) <= README_LIMITS_TEASER:
        return {"text": rest, "teaser": lead + " …"}
    return {"text": text, "teaser": f"{_cut(text, README_LIMITS_TEASER)} …"}


def _site_row(e: Entry) -> dict:
    """A row of a section table: the facts, with every judgement already made.

    The answers browse.html filters on that a card can show beside the name —
    card, key, an Anthropic route, a frontier family, the vendor training on
    what it is sent — because a reader who narrows the filterable table and a
    reader who scans this page are asking one question. Whether the API is
    OpenAI-compatible is the connection table's to say, where the base URL is.
    """
    families = [m for m in e.models if m.superseded_by is None]
    chips = [{"family": m.family, "tier": m.tier.value if m.tier else "",
              "access": _access_description(e, m.family, compact=True)} for m in families]
    api = e.api
    return {
        "id": e.id,
        "name": e.name,
        "url": e.url,
        "page": provider_page_url(e.id),
        "offering": _site_fold(e.offering),
        "limits": _site_fold(limits_text(e)) if limits_text(e) else None,
        "models": chips[:SITE_MODELS],
        "more_models": chips[SITE_MODELS:],
        "verified": e.last_verified.isoformat(),
        "card": e.card_required,
        "access": access_words(e.access, compact=True),
        "provisional": e.provisional,
        "trains": e.data_use.trains if _trains(e) else "",
        "no_key": bool(api and api.base_url and api.key_kind == "none"),
        "public_key": bool(api and api.base_url and api.key_kind == "public"),
        "claude_code": bool(api and api.anthropic_base_url),
        "codex": codex_ready(e),
        "frontier": any(m.tier is Tier.FRONTIER for m in families),
        # The same answers as the words the page's search filters on, one per
        # filter it offers (SEARCH_FILTERS) — held to them by a test.
        "flags": [flag for flag, on in (
            ("nocard", not e.card_required),
            ("nokey", needs_no_account(e)),
            ("claude", bool(api and api.anthropic_base_url)),
            ("strong", any(m.tier in (Tier.FRONTIER, Tier.STRONG) for m in families))) if on],
        # A row whose published lane is known not to work says so where it is
        # read, not only on its own page, before a reader copies the base URL.
        "notice": _notice_data(api.notice if api else None),
    }


def _site_sections(active: list[Entry]) -> list[dict]:
    sections = []
    for cat, title in CATEGORY_TITLES.items():
        rows = _ordered(active, cat)
        emoji, _, name = title.partition(" ")
        sections.append({
            "id": cat.value, "emoji": emoji, "title": name, "short": SITE_NAV_LABELS[cat],
            "rows": [_site_row(e) for e in rows], **_card_counts(rows),
        })
    return sections


# Each ask as the site's connection table says it, after "also sends".
_ASK_SITE = {"user-agent": "your client's own User-Agent",
             "session-header": "{} per conversation"}


def _site_connections(connectable: list[Entry]) -> list[dict]:
    """The connection table as data: what to paste, and what the vendor asks
    every request to carry beside it."""
    rows = []
    for e in connectable:
        asks = [_ASK_SITE[name].format(value) for name, value in e.api.asks()]
        rows.append({
            "name": e.name, "page": provider_page_url(e.id),
            "base_url": e.api.base_url, "anthropic_base_url": e.api.anthropic_base_url or "",
            "codex": _codex_command(e) if codex_ready(e) else "",
            "codex_profile": codex_profile_path(e) if codex_ready(e) else "",
            "keyless": e.api.key_kind == "none", "env_var": env_var(e.id),
            "public_key": e.api.public_key or "",
            "key_url": e.api.key_url or "", "asks": asks,
            "note": _site_fold(e.api.note) if e.api.note else None,
            "notice": ({"since": e.api.notice.since.isoformat(), "text": e.api.notice.text,
                        "url": e.api.notice.url or ""} if e.api.notice else None),
        })
    return rows


def _site_archived_rows(entries: list[Entry], today: date) -> list[dict]:
    gone = _archive(entries, today)
    return [{"id": e.id, "name": e.name, "page": provider_page_url(e.id),
             "when": _departure(e).isoformat(), "why": _site_fold(archive_reason(e, today))}
            for e in gone]


def _site_changes(events: list[Event], entries: list[Entry] | None,
                  today: date, limit: int = SITE_CHANGES) -> list[dict]:
    """The tail of the log, newest first, as the site prints it: the README's
    table escapes these rows' pipes, and HTML has no cell separator to protect
    a vendor's sentence from."""
    return [{"date": ev.ts.date().isoformat(), "label": CHANGE_LABELS[ev.event],
             "name": ev.name, "url": _event_link(ev, entries, today),
             "detail": event_detail(ev, entries)}
            for ev in _newest_first(events, limit)]


def _script_json(value, **dumps) -> str:
    """JSON for a <script> element: no "<" in it can end the element early."""
    return json.dumps(value, ensure_ascii=False, **dumps).replace("<", "\\u003c")


def _site_jsonld(active_count: int, family_count: int, today: date) -> str:
    """What the page is, for the engines that read structured data rather than
    prose: a site, and the dataset behind it with the three files it publishes.

    Serialised here instead of in the template because Jinja's autoescaping —
    which every other value on that page needs — would turn the quotes of a
    JSON document into entities. `<` is escaped the way JSON allows so the
    string cannot close the script element that carries it.
    """
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": f"{PAGES_URL}/#website", "url": f"{PAGES_URL}/",
             "name": "awesome-free-ai-coding", "inLanguage": "en",
             "description": "Legal free LLM APIs, coding agents and no-card trials for AI "
                            f"coding, machine-verified {_schedule()}."},
            {"@type": "Dataset", "@id": f"{PAGES_URL}/#dataset",
             "name": "awesome-free-ai-coding registry",
             "description": f"{active_count} legal free LLM APIs, coding agents and no-card "
                            f"trials, with the free models they name ({family_count} "
                            "families), the limits in the vendor's own words and the day a "
                            "live probe last confirmed each.",
             "url": f"{PAGES_URL}/", "isAccessibleForFree": True,
             "license": "https://opensource.org/licenses/MIT",
             "dateModified": today.isoformat(),
             "creator": {"@type": "Person", "name": "mvalentsev",
                         "url": "https://github.com/mvalentsev"},
             "keywords": ["free LLM API", "free tier", "AI coding agent", "no credit card",
                          "OpenAI-compatible", "Claude Code", "free models"],
             "distribution": [
                 {"@type": "DataDownload", "encodingFormat": "application/json",
                  "contentUrl": f"{PAGES_URL}/index.json"},
                 {"@type": "DataDownload", "encodingFormat": "text/plain",
                  "contentUrl": f"{PAGES_URL}/llms.txt"},
                 {"@type": "DataDownload", "encodingFormat": "application/atom+xml",
                  "contentUrl": FEED_URL},
             ]},
        ],
    }
    return _script_json(graph, indent=2)


def build_site_context(entries: list[Entry], today: date,
                       watchlist: list[Watched] | None = None,
                       history: list[Event] | None = None,
                       pages: set[str] | None = None,
                       scores: dict | None = None) -> dict:
    """Everything index.html shows, derived from the registry the README is.

    The figures, the picks, the quickstart and the rules the page states are
    the README's own (`_shared_facts`). The rows are a second reading of the
    same entries rather than a reshaping of `build_context`'s, which is
    Markdown — folded cells, backticked ids, escaped pipes — that an HTML page
    would have to unpick.
    """
    active = [e for e in entries if not is_archived(e, today)]
    facts = _shared_facts(entries, today, watchlist, pages)
    return {
        **facts,
        # The README chart's ranking, with each model's score beside it.
        "strong_models": _in_chart_order(facts["strong_models"],
                                         load_scores() if scores is None else scores),
        "sections": _site_sections(active),
        "jsonld": _site_jsonld(facts["active_count"], facts["family_count"], today),
        "connections": _site_connections(_connectable(entries, today)),
        "archived": _site_archived_rows(entries, today),
        "changes": _site_changes(history or [], entries, today),
        "providers_url": providers_index_url(),
        "radar": SITE_RADAR,
        # Serialised here, like the structured data: autoescaping would turn a
        # JSON document's quotes into entities.
        "search_config": _script_json(_search_config()),
    }


def _plain_title(title: str) -> str:
    """The README's section titles lead with an emoji; a text file does not."""
    head, _, rest = title.partition(" ")
    return rest if rest and not head[:1].isalnum() else title


# Each ask as llms.txt says it, in the row's line.
_ASK_TEXT = {"user-agent": "every request names its client in its own User-Agent",
             "session-header": "every request needs a stable id per conversation in `{}`"}


def _llms_line(e: Entry) -> str:
    parts = [e.offering.strip().rstrip(".")]
    parts.append(_card_words(e))
    if e.access:
        parts.append(access_words(e.access))
    # Where the offer reaches, beside what it asks: "is there a free API I can
    # use from here" is a question a model answers from this file.
    if _border_flag(e):
        parts.append(_border_flag(e))
    if e.data_use is not None:
        # The row page's own sentence, as a clause: one wording of what the
        # vendor does with what a reader sends, wherever the list says it.
        said = DATA_USE_WORDS[e.data_use.trains].rstrip(".")
        parts.append(said[:1].lower() + said[1:])
    api = e.api
    if api and api.base_url:
        if api.key_kind == "none":
            parts.append("no key")
        elif api.key_kind == "public":
            parts.append(f"no account: the vendor prints a key for anyone at {api.key_url}, "
                         f"`{api.public_key}`")
        elif api.key_url:
            parts.append(f"key from {api.key_url}")
        else:
            parts.append("key required")
        if api.notice:
            parts.append(f"does not work as published since {api.notice.since.isoformat()}: "
                         f"{api.notice.text.rstrip('.')}")
        parts.append(f"{'OpenAI-compatible' if api.openai_compatible else 'API'} at {api.base_url}")
        parts += [_ASK_TEXT[name].format(value) for name, value in api.asks()]
        if api.anthropic_base_url:
            parts.append(f"Anthropic Messages at {api.anthropic_base_url}")
        if codex_ready(e):
            parts.append(f"Codex CLI profile at {REPO_URL}/blob/main/{codex_profile_path(e)}")
    fams = live_families(e)
    if fams:
        parts.append("free models: " + ", ".join(f"`{f}`" + _access_flag(e, f, compact=False) for f in fams))
    if e.page_catalog:
        parts.append(" ".join(catalog_words(e.page_catalog).split()))
    if e.provisional:
        parts.append(_provisional_words(e))
    return f"- [{e.name}]({provider_page_url(e.id)}): " + "; ".join(parts)


def build_llms_txt(entries: list[Entry], today: date, pages: set[str] | None = None) -> str:
    """The list as one text file in the llms.txt shape — a title, a summary in a
    blockquote, then sections of links with a note each.

    This is the registry in the form that reads best as text, one line per
    offer with what it needs (card, key) and where it answers.
    """
    live = [e for e in entries if not is_archived(e, today)]
    groups = litellm_groups(entries, today)
    gone = sorted(_archive(entries, today), key=lambda e: e.name.lower())
    lines = [
        "# awesome-free-ai-coding",
        "",
        "> Legal free LLM APIs and coding agents for AI coding — free tiers, no-card trials "
        f"and free models, probe-verified {_schedule()} against live model catalogs and "
        f"pricing pages. Generated {today.isoformat()} from the registry; every offer above "
        f"the Archived heading passed a probe in the last {ARCHIVE_AFTER_DAYS} days and has not "
        f"failed {ARCHIVE_AFTER_FAILURES} in a row.",
        "",
        "Each offer links to a page with the free tier in the vendor's own words, the "
        "connection details (base URL, where to get a key, model ids, an Anthropic-format "
        "URL where the vendor documents one), the evidence the probe reads and the row's "
        "history. \"No card\" means the vendor asks for no payment method; \"no key\" means "
        "the endpoint answers without an account; \"no account\" means the vendor prints a "
        "key anyone may call it with. Offers the list carried and carries no more "
        "are listed last, under Archived, each with why it left.",
    ]
    for title, rows in sections(live):
        lines += ["", f"## {_plain_title(title)}", ""]
        lines += [_llms_line(e) for e in rows]
    # The same rows turned inside out, for the question that starts from a
    # model: every model with a page, and who serves it.
    pages = model_pages(entries, [], today) if pages is None else pages
    paged = [(f, rows) for f, rows in _rows_by_family(live).items() if f in pages]
    if paged:
        lines += ["", "## Free models by name", "",
                  f"A model gets a page of its own once {_model_page_rule()}: every row that "
                  "serves it, the limits in the vendor's words and the ids to call. Every other "
                  "model is named on the one row above that serves it.", ""]
        for family, rows in paged:
            mark = _measured(family, rows)
            lines.append(f"- [{family}]({model_page_url(family)}): "
                         + (f"{mark.tier.value}; " if mark is not None else "")
                         + ", ".join(e.name + (f" ({_card_words(e)})" if e.card_required else "")
                                     + _access_flag(e, family, compact=False)
                                     for e in rows))
    if gone:
        lines += ["", "## Archived", ""]
        for e in gone:
            lines.append(f"- [{e.name}]({provider_page_url(e.id)}): no longer listed — "
                         f"{archive_reason(e, today)}")
    lines += [
        "", "## Machine-readable", "",
        f"- [index.json]({PAGES_URL}/index.json): every row with its connection details and "
        "probe, plus the watchlist of services considered and not listed",
        f"- [feed.xml]({FEED_URL}): Atom feed of every change — rows arriving, leaving and "
        "changing their free models",
        f"- [Provider pages]({providers_index_url()}): one page per row, live and archived",
        f"- [Model pages]({models_index_url()}): every free model on the list and the rows "
        f"that serve it, and a page of its own for each model once {_model_page_rule()}",
        f"- [Filterable table]({PAGES_URL}/browse.html): the same rows filtered by category, "
        "card, key and API format",
        f"- [configs/opencode.json]({REPO_URL}/blob/main/configs/opencode.json): opencode "
        "config with every OpenAI-compatible row wired up",
        f"- [configs/claude-code.sh]({REPO_URL}/blob/main/configs/claude-code.sh): one shell "
        "function per gateway that serves the Anthropic Messages format, for Claude Code",
        f"- [configs/litellm.yaml]({REPO_URL}/blob/main/configs/litellm.yaml): LiteLLM proxy "
        "config over the same rows"
        + (f", with one-name fallback groups ({', '.join(groups)})" if groups else ""),
        f"- [{CODEX_LITELLM_PATH}]({REPO_URL}/blob/main/{CODEX_LITELLM_PATH}): Codex CLI "
        "profile over litellm.yaml — Codex speaks only the Responses API, which the proxy "
        "answers from each lane's chat completions",
        f"- [README]({REPO_URL}): the list itself, with the picks table and how it stays fresh",
        f"- [CONTRIBUTING]({REPO_URL}/blob/main/CONTRIBUTING.md): what qualifies, how rows are "
        "ranked, how the probes work",
    ]
    return "\n".join(lines) + "\n"


def build_opencode_config(entries: list[Entry], today: date) -> dict:
    providers = {}
    for e in _configurable(entries, today):
        options: dict = {"baseURL": e.api.base_url}
        if e.api.key_kind != "none":
            options["apiKey"] = "{env:" + env_var(e.id) + "}"
        # The ids the row lists and nothing else: a family names a model, not
        # the string a request carries (see _litellm_ids).
        models = {mid: {"name": mid + (f" ({words})" if (words := access_words(id_access(e, mid), compact=True)) else "")}
                  for mid in e.api.model_ids}
        # OpenCode's model schema requires both context and output limits.
        # https://opencode.ai/config.json, read 2026-10-04; live client recheck.
        for mid, limits in e.api.model_limits.items():
            if mid in models:
                models[mid]["limit"] = {"context": limits.context_tokens, "output": limits.output_tokens}
        providers[e.id] = {
            "npm": "@ai-sdk/openai-compatible",
            "name": e.name,
            "options": options,
            "models": models,
        }
    return {"$schema": "https://opencode.ai/config.json", "provider": providers}


# One name over every lane of a kind, in the order a caller falls back through
# them: the strongest models first, then any strong one, then the lanes that
# need no account at all.
FREE_GROUPS = ("free/frontier", "free/strong", "free/nokey")
# What a group pools, in the words the Codex profile explains its model with.
GROUP_WORDS = {"free/frontier": "every frontier lane", "free/strong": "every strong lane",
               "free/nokey": "the lanes that need no account"}

# Codex CLI on the free lanes. Codex speaks only the OpenAI Responses API (a
# provider given `wire_api = "chat"` is a config error, its discussion #7782),
# and LiteLLM's /v1/responses builds a call from a lane's chat completions when
# the deployment carries `use_chat_completions_api`. LiteLLM 1.88.3 and earlier
# write that flag into the vendor's request body, and 1.98.0 is the first to
# read a deployment's own allowed_fails_policy, which the groups carry; Codex
# 0.134.0 is the first whose `--profile NAME` reads $CODEX_HOME/NAME.config.toml.
LITELLM_BRIDGE_SINCE = "1.98"
CODEX_SINCE = "0.134"
CODEX_DIR = "configs/codex"
CODEX_LITELLM_PATH = f"{CODEX_DIR}/{CODEX_LITELLM_PROFILE}.config.toml"
# Where the proxy listens when started the way this repo prints the command:
# on the loopback address, at LiteLLM's own default port.
LITELLM_LOCAL_URL = "http://127.0.0.1:4000/v1"


def litellm_command(config: str = "configs/litellm.yaml") -> str:
    """The local proxy command used by every page and profile."""
    # LiteLLM 1.104.0 requires this explicit local-development opt-in when no
    # master key is set. GeneralSettings in the official release's _types.py,
    # read 2026-10-04; startup and loopback binding are held by conformance.
    # https://github.com/BerriAI/litellm/blob/v1.104.0/litellm/proxy/_types.py
    return ("env -u OPENAI_API_KEY LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true "
            f"litellm --config {config} --host 127.0.0.1")


def _litellm_lanes(entries: list[Entry], today: date) -> list[Entry]:
    """The configurable rows LiteLLM can call. It sends a bearer token on every
    call — `api_key: none` goes out as "Bearer none" — so a keyless lane that
    refuses one (`api.refuses_bearer`) cannot be reached through it at all."""
    return [e for e in _configurable(entries, today) if not e.api.refuses_bearer]


def _litellm_ids(e: Entry) -> list[str]:
    """The ids a config calls: the row's own, exactly, never its family names —
    a family names a model, and is an id only by accident. freetier-check
    refuses a connectable row whose column names families with no ids beside
    them."""
    return e.api.model_ids


def _tier_of_id(e: Entry, model_id: str) -> Tier | None:
    """The measured tier of the family an id belongs to (`id_family`:
    zai-org/GLM-5.3-Flash is glm-5.3-flash, not glm-5.3)."""
    family = id_family(live_families(e), model_id)
    return next((m.tier for m in e.models if m.family == family and m.superseded_by is None), None)


def _litellm_key(e: Entry) -> str:
    if e.api.public_key is not None:
        return e.api.public_key
    return "none" if e.api.key_kind == "none" else f"os.environ/{env_var(e.id)}"


def build_litellm_config(entries: list[Entry], today: date) -> dict:
    """LiteLLM proxy config — the same providers, for everything that speaks to
    a proxy rather than to a provider.

    `openai/<id>` is how LiteLLM is told an endpoint is OpenAI-compatible, and
    `api_key: none` is what it is given for an endpoint that wants no key — it
    sends "Bearer none", which the keyless lanes left in here answer. Aliases
    are prefixed with the entry id because two providers routinely serve the
    same model id.

    Then the groups (FREE_GROUPS): the same deployments again under one name
    each, so a caller asks for `free/strong` and LiteLLM shuffles across every
    lane of that tier and falls back down the list when they run out. A group
    deployment benches itself after its first failure: a key the reader never
    set fails before any request leaves, and a 429 means that quota is spent. A
    model asked for by name keeps LiteLLM's defaults, because under the same
    policy one 429 on a lone deployment shuts it for the whole cooldown. Each
    deployment carries a dict of its own: a shared one is written as a YAML
    anchor, and LiteLLM then gives every deployment the same id.

    Every deployment also carries `use_chat_completions_api`, for Codex CLI,
    which speaks only the Responses API. Without it LiteLLM answers
    /v1/responses for an `openai/` deployment by sending the call on to the
    lane's own /responses, which many free lanes answer with 404; with it the
    call is built from the lane's chat completions, the format every lane here
    is verified in (see LITELLM_BRIDGE_SINCE).
    """
    models: list[dict] = []
    groups: dict[str, list[dict]] = {name: [] for name in FREE_GROUPS}
    for e in _litellm_lanes(entries, today):
        for model_id in _litellm_ids(e):
            params = {"model": f"openai/{model_id}", "api_base": e.api.base_url,
                      "api_key": _litellm_key(e), "use_chat_completions_api": True}
            if limits := e.api.model_limits.get(model_id):
                params["max_tokens"] = limits.output_tokens
            access = id_access(e, model_id)
            words = access_words(access)
            models.append({"model_name": f"{e.id}/{model_id}", "litellm_params": params,
                           **({"model_info": {"access": words, "source": access.source}}
                              if words else {})})
            # notable decides a model's page, not a pool: a caller asking for
            # free/strong asked for the strong bar.
            tier = _tier_of_id(e, model_id)
            names = ([f"free/{tier.value}"] if tier in (Tier.FRONTIER, Tier.STRONG) else []) + (
                ["free/nokey"] if needs_no_account(e) else [])
            if access and access.initial_payment_usd:
                names = []
            for name in names:
                groups[name].append({
                    "model_name": name,
                    "litellm_params": dict(params),
                    "model_info": {"allowed_fails_policy": {
                        "AuthenticationErrorAllowedFails": 0,
                        "InternalServerErrorAllowedFails": 0,
                        "RateLimitErrorAllowedFails": 0}},
                })
    present = [name for name in FREE_GROUPS if groups[name]]
    fallbacks = [{name: present[i + 1:]} for i, name in enumerate(present[:-1])]
    config: dict = {"model_list": models + [d for name in present for d in groups[name]]}
    if present:
        config["router_settings"] = {"routing_strategy": "simple-shuffle", "num_retries": 3,
                                     **({"fallbacks": fallbacks} if fallbacks else {})}
    return config


def litellm_groups(entries: list[Entry], today: date) -> list[str]:
    """The groups litellm.yaml defines today, in the order a call falls back.

    A group is there only while some lane is measured at its tier, so every page
    that names a group reads it from here: a group the config lacks is a name
    LiteLLM refuses with "Invalid model name"."""
    names = {d["model_name"] for d in build_litellm_config(entries, today)["model_list"]}
    return [name for name in FREE_GROUPS if name in names]


def _litellm_groups_note(groups: list[str]) -> str:
    """The header's paragraph on the groups, for the ones the file defines."""
    if not groups:
        return ""
    how = (" pools every lane of that tier" if len(groups) == 1 else
           " pool every lane of that tier, and a call falls back down that order when a "
           "lane runs out of quota or has no key set here")
    sentence = (f"Or ask for a group instead of a model: {series(groups, 'or')}{how} — set only "
                "the keys you have, and a lane without one is skipped.")
    return "#\n" + "".join(f"{line}\n" for line in _comment(sentence))


def _comment(text: str) -> list[str]:
    """A paragraph as the lines of a `#` comment, wrapped the way the config
    headers are."""
    return [f"# {line}" for line in textwrap.wrap(text, width=76, break_long_words=False,
                                                  break_on_hyphens=False)]


def _access_comments(e: Entry) -> list[str]:
    """The same access labels and sources beside every generated client setup."""
    out = _comment(f"Access: {access_words(e.access)}; {e.access.source}") if e.access else []
    lane = e.api or e.client_lane
    if lane:
        for model_id in lane.model_ids:
            access = id_access(e, model_id)
            if access and access != e.access:
                out += _comment(f"{model_id}: {access_words(access)}; {access.source}")
    return out


def build_codex_litellm_profile(entries: list[Entry], today: date) -> str:
    """Codex CLI's profile over litellm.yaml: the file a reader copies into
    ~/.codex, after which `codex -p litellm` works on every lane the proxy
    serves.

    The proxy answers Codex's Responses calls from each lane's chat completions
    (`build_litellm_config`), and the profile carries the settings that bridge
    needs (`_codex_settings`). The provider names no key: the proxy runs without
    a master key, as its header says.

    The model is the first group the file defines, from which a call falls back
    down the rest to the lanes that need no account, so the profile answers
    before the reader has set a single key. A file without a group names the
    first model the proxy serves; one without a lane names none."""
    groups = litellm_groups(entries, today)
    served = [d["model_name"] for d in build_litellm_config(entries, today)["model_list"]]
    model = groups[0] if groups else (served[0] if served else None)
    if groups:
        falls = f" and falls back to {series(groups[1:])}" if groups[1:] else ""
        about = (f"The model is {model}: LiteLLM spreads the calls over "
                 f"{GROUP_WORDS[model]}{falls}. A lane whose key is not set is skipped"
                 + (", and free/nokey needs none, so the profile answers before you set any."
                    if "free/nokey" in groups else "."))
    elif model:
        about = f"The model is {model}, the first one litellm.yaml serves."
    else:
        about = "litellm.yaml serves no model today: name one with -m once it does."
    lines = [
        "# Codex CLI on the free lanes of litellm.yaml — generated from registry.yaml,",
        "# do not edit by hand.",
        *_comment("Codex speaks only the OpenAI Responses API, and the LiteLLM proxy "
                  "answers it for every lane in litellm.yaml by calling "
                  f"the lane's chat completions. Needs Codex CLI {CODEX_SINCE} or later and "
                  f"LiteLLM {LITELLM_BRIDGE_SINCE} or later; the file goes where Codex keeps "
                  "its config, ~/.codex unless CODEX_HOME says otherwise:"),
        "#",
        f"#   {litellm_command()}",
        f"#   cp {CODEX_LITELLM_PATH} ~/.codex/",
        f"#   codex -p {CODEX_LITELLM_PROFILE}",
        "#",
        *_comment(f"{about} Any model_name in litellm.yaml works too — codex -p "
                  f"{CODEX_LITELLM_PROFILE} -m <model_name> — as long as the model calls "
                  "tools, since every Codex turn offers them. Codex warns that it has no "
                  "metadata for the name, as it does for any model outside OpenAI's."),
        *([f"model = {json.dumps(model)}"] if model else []),
        f"model_provider = {json.dumps(CODEX_LITELLM_PROFILE)}",
        *_codex_settings(),
        *_comment("No key: the proxy runs without a master key (see litellm.yaml's header)."),
        f"[model_providers.{CODEX_LITELLM_PROFILE}]",
        'name = "LiteLLM over the free lanes"',
        f"base_url = {json.dumps(LITELLM_LOCAL_URL)}",
        'wire_api = "responses"',
    ]
    return "\n".join(lines) + "\n"


def _codex_settings() -> list[str]:
    """The three settings every Codex profile here carries, so the request Codex
    sends through any of them is the one the run sends (prober.codex_probe_body).
    Without any one of them some lane breaks — see CONTRIBUTING."""
    return [
        *_comment("The same three settings in every Codex profile here, so the request Codex "
                  "sends is the one the list's run checks; each is off for lanes that refuse it "
                  "or cannot run it. Reasoning summaries: some LiteLLM releases hand the "
                  "setting to a lane as a reasoning_effort object (1.102 does), which the "
                  "lanes tried refused."),
        'model_reasoning_summary = "none"',
        *_comment("Web search: a tool OpenAI's servers run, which LiteLLM passes on to a lane "
                  "as web_search_options."),
        'web_search = "disabled"',
        "",
        "[features]",
        *_comment("Sub-agents: Codex sends their tools as a namespace, which LiteLLM "
                  f"{LITELLM_BRIDGE_SINCE} and later pass on as plain functions; with them on, "
                  "a turn failed both through LiteLLM and on a lane called directly."),
        "multi_agent = false",
        "",
    ]


def codex_ready(e: Entry) -> bool:
    """Whether a row's lane gets a Codex profile of its own: Codex calls it
    directly (`api.codex`), and a profile written once can carry every ask it
    makes — Codex names itself in its own User-Agent, and a profile's headers
    (`http_headers`) are fixed values, so a lane that wants a new id per
    conversation (`_static_blockers`) gets none."""
    return bool(e.api and e.api.base_url and e.api.model_ids and e.api.codex and not _static_blockers(e))


def codex_profile_path(e: Entry) -> str:
    return f"{CODEX_DIR}/{e.id}.config.toml"


def _codex_direct(entries: list[Entry], today: date) -> list[Entry]:
    """The live rows Codex calls directly, in rank order."""
    return sorted((e for e in entries if not is_archived(e, today) and codex_ready(e)),
                  key=_by_rank)


def codex_unset_words(var: str) -> str:
    """What a keyed profile says Codex does while its key is missing — measured
    with Codex 0.134.0 and 0.158.0 on 2026-09-29 and checked every week by
    conformance.py: an env_key that is unset or empty stops the turn with
    "Missing environment variable" before any request, the reader's own
    OPENAI_API_KEY and auth.json beside it or not."""
    return (f"With ${var} unset or empty, Codex stops before it sends anything, so no "
            "other key of yours reaches the lane.")


def build_codex_profile(e: Entry) -> str:
    """A row's own Codex profile: its lane, called directly, with the settings
    every profile here carries. The default prefers an unfunded, undated id;
    the key comes from the variable free-llm.env.example
    exports, and a keyless lane is given none, so Codex sends no Authorization
    header, which a lane that refuses a bearer needs.

    The header says what the profile rests on: a lane without an account took
    the request Codex sends, and every run sends it again; a keyed lane is one
    whose vendor's own page sets Codex up on it, which every run reads back
    beside asking the route — a turn there needs a key the run does not have."""
    api = e.api
    var = env_var(e.id)
    if api.key_kind == "own":
        rests = (f"{e.name}'s own page sets Codex CLI up on this lane, {api.codex.source}, and "
                 "every run of the list reads it back and asks the lane's Responses route "
                 "again; only a key can run a turn there.")
        key = (f"The key comes from ${var}, the variable free-llm.env.example exports"
               + (f"; get one at {api.key_url}. " if api.key_url else ". ")
               + codex_unset_words(var))
    else:
        rests = "The lane takes the request Codex sends, and every run of the list sends it again."
        key = ("No key: the lane is anonymous." if api.key_kind == "none" else
               f"The key comes from ${var}, the variable free-llm.env.example exports; the "
               f"vendor prints one for anyone at {api.key_url}.")
    model = ("The default prefers an unfunded, undated free id; the quota and every free id are "
             if e.free_part is FreePart.MODELS else
             "The default prefers an unfunded, undated id; what the free part covers and every id "
             "are ")
    lines = [
        f"# Codex CLI on {e.name}'s free lane — generated from registry.yaml, do not",
        "# edit by hand.",
        *_comment(f"{rests} Needs Codex CLI {CODEX_SINCE} or later; the file goes where Codex "
                  "keeps its config, ~/.codex unless CODEX_HOME says otherwise:"),
        "#",
        f"#   cp {codex_profile_path(e)} ~/.codex/",
        f"#   {_codex_command(e)}",
        "#",
        *_comment(f"{key} {model}on the row's page, {provider_page_url(e.id)} — codex -p "
                  f"{e.id} -m <id> takes another."),
        *_access_comments(e),
        f"model = {json.dumps(preferred_ids(e)[0])}",
        f"model_provider = {json.dumps(e.id)}",
        *_codex_settings(),
        f"[model_providers.{e.id}]",
        f"name = {json.dumps(e.name)}",
        f"base_url = {json.dumps(api.codex.base_url)}",
        'wire_api = "responses"',
        *([f"env_key = {json.dumps(var)}"] if api.key_kind != "none" else []),
    ]
    return "\n".join(lines) + "\n"


# Each ask as the env example notes it under the row's key; empty where the
# client the reader runs makes the ask for them.
_ASK_ENV = {"user-agent": "",
            "session-header": ("#    header: every request needs a stable id per conversation in "
                               "{} — send it from your client")}


def build_env_example(entries: list[Entry], today: date) -> str:
    lines = [
        "# Free LLM providers — generated from registry.yaml, do not edit by hand.",
        "# Fill the keys you use, then `source` this file. Every endpoint is",
        "# OpenAI-compatible: point any SDK/agent at the base URL next to the key.",
        "",
    ]
    for e in _connectable(entries, today):
        if e.api.key_kind == "none":
            lines.append(f"# ── {e.name} — no key needed · base: {e.api.base_url}")
        elif e.api.key_kind == "public":
            # Filled in: the vendor prints this key for anyone, so the lane works
            # the moment the file is sourced, with no account behind it.
            lines.append(f"# ── {e.name} — no account needed · base: {e.api.base_url}")
            lines.append(f"#    the vendor prints this key for anyone at {e.api.key_url} — "
                         "put your own in its place if you have one")
            lines.append(f'export {env_var(e.id)}="{e.api.public_key}"')
        else:
            key_hint = f" · get a key: {e.api.key_url}" if e.api.key_url else ""
            lines.append(f"# ── {e.name} — base: {e.api.base_url}{key_hint}")
            lines.append(f'export {env_var(e.id)}=""')
        lines += [_ASK_ENV[name].format(value) for name, value in e.api.asks() if _ASK_ENV[name]]
        if e.api.note:
            lines.append(f"#    note: {e.api.note}")
        lines += _access_comments(e)
        lines.append("")
    return "\n".join(lines)


def _anthropic_ready(entries: list[Entry], today: date) -> list[Entry]:
    """Every live row that publishes an Anthropic-format route a shell function
    can call, in rank order — card-required rows included, since the file is a
    menu rather than a recommendation and the card is stated beside the name.

    The function is a config written once, like litellm.yaml: a lane whose ask
    it cannot carry (`_static_blockers`) is left out, and so is a keyless lane
    that refuses any Authorization header, since the function hands Claude
    Code a token of "none" and Claude Code sends it as a bearer."""
    return sorted(
        (e for e in entries
         if not is_archived(e, today) and e.api and e.api.anthropic_base_url
         and not _static_blockers(e) and not e.api.refuses_bearer),
        key=_by_rank,
    )


def build_claude_code_sh(entries: list[Entry], today: date) -> str:
    """One shell function per gateway that serves the Anthropic Messages
    format, so `source configs/claude-code.sh` and `claude-<id>` runs Claude
    Code on that lane. Functions rather than exports because only one gateway
    can be current: a file of exports would leave the last block winning
    silently, while a function scopes the four variables to one invocation.
    A keyed function stops while its variable is empty: with
    ANTHROPIC_AUTH_TOKEN empty, Claude Code falls back to the next credential
    in its order — the reader's own sign-in included — and sends it to the
    gateway. ANTHROPIC_API_KEY is emptied in every block, so a key for
    Anthropic's own API is never one of them. The key comes from the same
    variable free-llm.env.example declares, so the two files are one setup.

    The default prefers an unfunded, undated id and keeps the registry order
    on ties. A row that lists none leaves ANTHROPIC_MODEL to the reader."""
    ready = _anthropic_ready(entries, today)
    example = (f",\n# e.g. claude-{ready[0].id}. Works in bash and zsh." if ready
               else ".\n# Works in bash and zsh.")
    lines = [
        "# Claude Code on a free lane — generated from registry.yaml, do not edit by hand.",
        f"# Each function points Claude Code at a gateway this list verifies {_schedule()}:",
        "# the vendor documents the Anthropic-format route, and the probe confirms it still",
        "# answers. Usage:  source configs/free-llm.env.example  (fill the key you use),",
        "# then  source configs/claude-code.sh  and run the function named after the row"
        + example,
        "# A function stops while its key is not set: without one, Claude Code sends the",
        "# gateway the next credential it holds, your own sign-in included.",
        "",
    ]
    for e in ready:
        card = " · card required" if e.card_required else ""
        key_hint = f" · get a key: {e.api.key_url}" if e.api.key_url else ""
        lines.append(f"# ── {e.name}{card}{key_hint}")
        lines += _access_comments(e)
        if not e.api.model_ids:
            lines.append("#    the row lists no callable id: pass ANTHROPIC_MODEL=<a free id> "
                         "before the function, or set it inside")
        else:
            lines.append(f"#    free ids: {', '.join(e.api.model_ids)}")
        lines.append(f"claude-{e.id}() {{")
        if e.api.key_kind != "none":
            var = env_var(e.id)
            lines += [f'  if [ -z "${{{var}:-}}" ]; then',
                      f'    echo "claude-{e.id}: set {var} first (configs/free-llm.env.example)" >&2',
                      "    return 1",
                      "  fi"]
        lines.append(f'  ANTHROPIC_BASE_URL="{e.api.anthropic_base_url}" \\')
        if e.api.key_kind == "none":
            lines.append('  ANTHROPIC_AUTH_TOKEN="none" \\')
        else:
            lines.append(f'  ANTHROPIC_AUTH_TOKEN="${env_var(e.id)}" \\')
        lines.append('  ANTHROPIC_API_KEY="" \\')
        if e.api.model_ids:
            lines.append(f'  ANTHROPIC_MODEL="{preferred_ids(e)[0]}" \\')
        lines.append('  claude "$@"')
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def _event_text(ev: Event) -> str:
    """What a row's page says about one of its events, after the date. A
    delisting says why in the page's header, with the reviewer's date; the
    families a row had are not repeated after "Delisted", where they read as
    the thing taken off."""
    if ev.detail:
        return f"{EVENT_WORDS[ev.event]}: {ev.detail}"
    if ev.models and ev.event is not EventType.REMOVED:
        return f"{EVENT_WORDS[ev.event]}: " + ", ".join(ev.models)
    return EVENT_WORDS[ev.event]


def _front_matter(fields: dict) -> str:
    """Jekyll front matter, dumped rather than typed: a title with a colon or a
    quote in it is the normal case for a vendor name."""
    return "---\n" + yaml.safe_dump(fields, allow_unicode=True, sort_keys=False,
                                    width=10000).rstrip() + "\n---\n"


def _page(fields: dict, body: list[str]) -> str:
    """A Markdown page of the site: its front matter under the site's own
    layout, and a body Liquid leaves alone. GitHub Pages builds the pages with
    Jekyll, and a vendor's sentence may carry `{{` or `{%`, so the body sits
    inside {% raw %} — freetier-check refuses a row's prose that would close it."""
    return "\n".join([_front_matter({"layout": "default", **fields}), "{% raw %}", "", *body,
                      "", "{% endraw %}", ""])


def _page_description(e: Entry) -> str:
    """The <meta> description: the offer first, then the free models, then the
    figures, cut at a word. The models come off the column, the list a probe
    reads back, since `offering` names none on a row of free models."""
    offer = e.offering.strip()
    if offer and offer[-1] not in ".!?":
        offer += "."
    shown, more = _readme_families(e)
    named = (f" Free models: {', '.join(shown)}{f' and {more} more' if more else ''}."
             if shown else "")
    terms = "\n\n".join(t for t in (e.limits, catalog_words(e.page_catalog)
                                    if e.page_catalog else "") if t)
    return clip(f"{offer}{named} {terms}", DESCRIPTION_ROOM)


def _last_modified(e: Entry, events: list[Event]) -> date:
    """The newest day a row's page changed for a reader: the last probe that
    passed it, the day its border was read or its newest history line,
    whichever came last, as a UTC day.

    It goes in the page's front matter as `last_modified_at`, which
    jekyll-sitemap writes as the URL's <lastmod> and jekyll-seo-tag as the
    page's `dateModified`, for a crawler deciding what to read again. The
    footer's render date is not it: a render changes no fact on the page."""
    # A border read is a fact the page gained that day, with no history line.
    read = [e.border.on] if e.border is not None else []
    return max([e.last_verified, *read, *(ev.ts.astimezone(timezone.utc).date()
                                          for ev in events if ev.id == e.id)])


def _family_links(families: list[str], pages: set[str], sep: str = ", ") -> str:
    """Families as the Markdown pages print them, each linking its own page
    where it has one — the row's page is a way in to the model's, as the
    model's is to the row's. The README's row line and the provider pages both
    print them this way."""
    return sep.join(f"[`{f}`]({model_page_url(f)})" if f in pages else f"`{f}`"
                    for f in families)


# Each ask as a line of Connect on the row's page and on every model page.
_ASK_PAGE = {"user-agent": ("- User-Agent: your client's own name and version, such as "
                            "`my-coding-agent/1.0` — not an SDK's or an HTTP library's, which the "
                            "vendor asks clients not to send"),
             "session-header": ("- Session header: `{}` — a stable id per conversation on every "
                                "request, which the calling client sends itself; the generated "
                                "LiteLLM, opencode, Claude Code and Codex configs leave this row "
                                "out")}


def _connect_lines(e: Entry, ids: list[str]) -> list[str]:
    """How to reach a row, a list item a fact: the base URL, the key, what every
    request carries, the Anthropic route, Codex's profile and the ids — every id
    the row lists on the row's own page, one model's ids on that model's page.
    One function for both pages, so a new way in (a key the vendor prints, a
    header every request carries) reaches every page that says how to connect,
    and none says it its own way."""
    api = e.api
    if not (api and api.base_url):
        out = ["- No API endpoint to paste: this row is a tool you install or sign in to."]
        if e.client_lane is not None and ids:
            out.append(f"- In {e.name}'s own model list: " + ", ".join(f"`{i}`" for i in ids))
        return out
    out = [f"- Base URL: `{api.base_url}`" + ("" if api.openai_compatible else " (not OpenAI-shaped)")]
    if api.key_kind == "none":
        out.append("- Key: none — the lane is anonymous")
    else:
        key = f"- Key: `{env_var(e.id)}`"
        if api.key_kind == "public":
            key += (f" — no account needed: the vendor prints one for anyone at "
                    f"<{api.key_url}>, `{api.public_key}`")
        elif api.key_url:
            key += f" — get one at <{api.key_url}>"
        out.append(key)
    out += [_ASK_PAGE[name].format(value) for name, value in api.asks()]
    if api.anthropic_base_url:
        out.append(f"- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): "
                   f"`{api.anthropic_base_url}`")
    if codex_ready(e):
        path = codex_profile_path(e)
        line = (f"- Codex CLI: [`{path}`]({REPO_URL}/blob/main/{path}) — copy it to "
                f"`~/.codex/`, then `{_codex_command(e)}`")
        if api.codex.base_url != api.base_url.rstrip("/"):
            line += f"; Codex's base is `{api.codex.base_url}`"
        if api.codex.source:
            line += (f"; set up on the lane by the vendor's own page, <{api.codex.source}>: "
                     f"\"{api.codex.quote}\"")
        out.append(line)
    if ids:
        out.append("- Callable ids: " + ", ".join(f"`{i}`" for i in ids))
        out += [f"- `{i}`: {words} ([conditions]({id_access(e, i).source}))"
                for i in ids if (words := access_words(id_access(e, i)))]
    elif api.no_ids:
        out.append(f"- Callable ids: none listed — {api.no_ids}")
    return out


def _connect_section(e: Entry) -> list[str]:
    lane = lane_ids(e)
    out = ["## Connect", "", *_connect_lines(e, lane.model_ids if lane else [])]
    if e.api and e.api.base_url and e.api.note:
        out.append(f"- Note: {e.api.note}")
    return out + [""] + _try_it(e)


def _try_it(e: Entry) -> list[str]:
    """The call that answers "does my key work here?", for a reader to paste
    into their own terminal: the command reads the key from the environment
    variable the configs name, so it never leaves the reader's machine. No page
    here takes a key itself — a form that takes a secret reads as a card
    checker whatever its code does, and OpenAI's API reference says not to
    "expose it in any client-side code"."""
    api = e.api
    if not (api and api.base_url and api.openai_compatible and (api.model_ids or api.no_ids)):
        return []
    key = (None if api.key_kind == "none" else api.public_key if api.key_kind == "public"
           else f"${env_var(e.id)}")
    if not api.model_ids:
        # No id to call: the catalog answers only a key, so it is the check.
        return [f"Check your key from your terminal — with it in `{env_var(e.id)}`, the "
                "vendor's catalog lists the models it can call:", "", "```sh",
                f"curl -s {api.base_url.rstrip('/')}/models \\\n"
                f'  -H "Authorization: Bearer {key}"', "```", ""]
    said = ("Try it from your terminal — the lane takes no key:" if key is None else
            "Try it from your terminal — the key is the vendor's printed one:"
            if api.key_kind == "public" else
            f"Try it from your terminal with your key in `{env_var(e.id)}` — "
            "it goes from your machine to the vendor and nowhere else:")
    return [said, "", "```sh", _curl(api.base_url, preferred_ids(e)[0], api.asks(), key), "```", ""]


def _evidence_section(e: Entry, blocked: bool) -> list[str]:
    def at(url: str) -> str:
        return f"`{url}`" if blocked else f"<{url}>"

    out = ["## Evidence", ""]
    probe = e.probe
    if probe.type is ProbeType.API_MODELS:
        if probe.lane:
            # The document lists paid lanes beside the free one, so naming only
            # the URL would present every model in it as the evidence.
            how = (f"- Probe: the `{probe.lane}` lane of the models document at "
                   f"{at(probe.endpoint)}, each listed family checked in that lane")
        else:
            how = f"- Probe: the models catalog at {at(probe.endpoint)}"
        if probe.free_marker:
            how += f", free rows carrying `{probe.free_marker}`"
        if probe.free_list:
            # No price to be zero: the mark is in a second document.
            how += (", each listed family checked for its free mark on the vendor's free list at "
                    + at(probe.free_list))
        elif probe.require_zero_price:
            how += ", each listed family checked for a zero price"
    else:
        # A page-keywords row can carry its whole anchor in the page's own data
        # (`machinery_keywords`), so the line names both kinds: where the
        # evidence lives is part of the evidence.
        shown = []
        if probe.keywords:
            shown.append(", ".join(f"`{k}`" for k in probe.keywords))
        if probe.machinery_keywords:
            shown.append(", ".join(f"`{k}`" for k in probe.machinery_keywords)
                         + " in the page's own data")
        if probe.follow:
            # The page moves to a new dated path each release; where the probe
            # starts and what it follows is what stays true.
            where = (f"the page the index at {at(probe.endpoint)} names in `{probe.follow.field}`"
                     + (f", followed by `{probe.follow.suffix}`" if probe.follow.suffix else ""))
        else:
            where = f"the page at {at(probe.endpoint)}"
        how = f"- Probe: {where}, anchored on " + " and ".join(shown)
        if probe.catalog:
            how += f"; ids checked in {at(probe.catalog)}"
    out.append(how)
    for u in e.source_urls:
        out.append(f"- Source: {at(u)}")
    return out


def _history_section(e: Entry, events: list[Event]) -> list[str]:
    """Every event of this row, newest first, as history.jsonl holds it.

    The render records a change before it writes the page (`render_repository`),
    so the newest line is the commit's own.
    """
    out = ["", "## History", "",
           "Each line is a change to what this page publishes, dated the day it reached "
           "the list, in UTC.", ""]
    for ev in reversed([ev for ev in events if ev.id == e.id]):
        out.append(f"- `{ev.ts.date().isoformat()}` — {_event_text(ev)}")
    return out


def build_folded_page(e: Entry, events: list[Event], today: date,
                      holder: Entry | None) -> str:
    """The page of a row folded into another: where the service is, and the
    record of the name the list once used for it.

    A row is never deleted, and this id is a published URL, so the page stays
    and says what it is. It does not repeat the offer, the limits or the
    evidence: one service is described in one place, and a claim nothing ever
    verified is not published a second time as though the list had stood
    behind it.
    """
    name = holder.name if holder else e.duplicate_of
    page = provider_page_url(e.duplicate_of)
    head = {"title": f"{e.name}: the same project as {name}",
            "description": f"{e.name} and {name} are one project. The list carried "
                           f"it twice and now keeps one row: the free tier, the "
                           f"evidence and the history are on the {name} page.",
            "permalink": _permalink(provider_page_url(e.id)),
            "last_modified_at": _last_modified(e, events),
            "crumb": e.name}
    out = [f"# {e.name}", "",
           DOT.join([CATEGORY_TITLES[e.category],
                     f"**folded into [{name}]({page})** — one project, one row",
                     f"[back to the whole list]({PAGES_URL}/)"]),
           "", f"## The same project as {name}", "",
           f"This row was {archive_reason(e, today)}. The free tier it named, the evidence "
           f"behind it and what became of it are on the [{name}]({page}) page — this id is kept "
           f"because the list published it, and nothing the list published disappears without "
           f"a word."]
    out += _history_section(e, events)
    out += ["", "---", "",
            f"Generated from `registry.yaml` on {today.isoformat()}. No probe reads this row any "
            f"more — the list keeps one row per service; the full list, the Atom feed and the "
            f"machinery are at <{REPO_URL}>."]
    return _page(head, out)


def build_provider_page(e: Entry, events: list[Event], today: date, blocked: bool = False,
                        registry: list[Entry] | None = None,
                        pages: set[str] | None = None) -> str:
    """One page per row on the Pages site, in the row's own words.

    It is for the reader who arrives with a question about one vendor and for
    the crawler that indexes that question: a title that names the vendor, the
    tier and the date, a description that carries the figures, and a body that
    is the row — offer, models, limits quoted from the vendor, connection
    details, the evidence the probe reads, the row's history. A row never leaves
    the registry, so its page stays too, as an archived one.

    The body sits inside {% raw %}: GitHub Pages builds this with Jekyll, and
    a vendor sentence with two braces in it would otherwise fail the whole
    site's build.

    An archived row's page is an epitaph, not instructions: what it offered,
    why it left, the evidence and the history — no connection details, no
    provisional flag, no claim that a probe re-reads a row none reads. On a
    blocklisted domain (`blocked`) it names the service as text and links
    nowhere near it: one of those pages plants instructions for AI agents.

    A row folded into another gets a page of its own kind, `build_folded_page`.
    """
    if e.duplicate_of is not None:
        return build_folded_page(e, events, today, folded_into(registry or [], e))
    archived = is_archived(e, today)
    verified = e.last_verified.isoformat()
    if archived:
        title = f"{e.name} free tier (archived): what it offered, and why it left the list"
    else:
        title = f"{e.name} free tier: limits, free models, verified {verified}"
    head = {"title": title,
            "description": _page_description(e),
            "permalink": _permalink(provider_page_url(e.id)),
            "last_modified_at": _last_modified(e, events),
            # The page's own name in the breadcrumb the layout writes for
            # search results.
            "crumb": e.name}
    # The page's one heading says what a search for it asks: the vendor and
    # "free tier", as the title does.
    out = [f"# {e.name} free tier" + (" (archived)" if archived else ""), ""]
    flags = [CATEGORY_TITLES[e.category]]
    flags.append(_card_words(e))
    if e.access:
        flags.append(access_words(e.access))
    # At the top, beside the card: a reader who arrives from a search about
    # this vendor learns before anything else whether it reaches them.
    if _border_flag(e) and not archived:
        flags.append(_border_flag(e))
    if e.provisional and not archived:
        promote = e.first_seen + timedelta(days=PROVISIONAL_PROMOTE_DAYS)
        flags.append(f"provisional — added on {e.first_seen.isoformat()}, a regular row from "
                     f"the first probe it passes on or after {promote.isoformat()}")
    if archived:
        flags.append(f"**archived** — {archive_reason(e, today)}")
    else:
        live = f"**live** — last verified by a probe on {verified}"
        if e.probe_failures:
            # The misses since the last pass are what a reader cannot infer
            # from the date, and the countdown to the Archive.
            n = e.probe_failures
            misses = ("the probe since has not found that evidence" if n == 1
                      else f"the {n} probes since have not found that evidence")
            live += f"; {misses}, and {ARCHIVE_AFTER_FAILURES} misses in a row archive the row"
        flags.append(live)
    site = f"`{domain_of(e.url)}`" if blocked else f"[{domain_of(e.url)}]({e.url})"
    out.append(DOT.join(flags + [site, f"[back to the whole list]({PAGES_URL}/)"]))
    # The name this service was also carried under, for the reader who arrives
    # by the other one: a folded row keeps its page, and this is the page it
    # points at.
    folds = [o for o in (registry or []) if o.duplicate_of == e.id]
    if folds:
        names = ", ".join(f"[{o.name}]({provider_page_url(o.id)})" for o in folds)
        which = "that row was" if len(folds) == 1 else "those rows were"
        out += ["", f"Also carried as {names}, until {which} folded into this one — "
                    f"one project, one row."]
    if e.api and e.api.notice and not archived:
        # Above the offer, not under Connect: a reader who arrives from a search
        # about this vendor should not have to scroll to find out the lane the
        # list publishes does not work right now.
        out += ["", _notice_quote(e.api.notice)]
    out += ["", "## What it offered" if archived else "## What you get", "", e.offering, ""]
    fams = live_families(e)
    if archived:
        named = "The row named no free model."
    elif e.free_part is FreePart.SUM:
        named = ("No model is free by itself here: the free part is an amount the account spends "
                 "across the catalog, so the column names none. The limits below say what it buys; "
                 "the ids to call, where the row has them, are under Connect.")
    elif e.free_part is FreePart.UNNAMED:
        named = ("The vendor does not say which models the free part reaches, so the column names "
                 "none.")
    elif e.newcomers:
        named = ("No free model family is listed yet; new offers must clear the two-week bar "
                 "before entering this section.")
    elif e.probe.type is ProbeType.PAGE_KEYWORDS:
        named = ("The page this row is verified against names no free model, so the column stays "
                 "empty; callable ids, where the row has them, are under Connect.")
    else:
        named = ("The row names no free model family; the ids its lane serves, where the row has "
                 "them, are under Connect.")
    out += ["## Free models it listed" if archived else "## Free models", "",
            _entry_family_links(e, fams, model_pages(registry or [], events, today) if pages is None
                                else pages) if fams else named,
            ""]
    out += ["## Limits, in the vendor's words", "",
            limits_text(e) if limits_text(e) else "The vendor publishes no figure for this tier.", ""]
    if e.border is not None and not archived:
        out += ["## Where it is offered", "", border_words(e), ""]
    if e.data_use is not None and not archived:
        out += ["## What happens to what you send", "",
                f"{DATA_USE_WORDS[e.data_use.trains]} In the vendor's words: "
                f"“{e.data_use.quote}” ([source]({e.data_use.url})).", ""]
    if not archived:
        out += _connect_section(e)
    out += _evidence_section(e, blocked)
    out += _history_section(e, events)
    if not archived:
        standing = (f"Generated from `registry.yaml` on {today.isoformat()} and re-verified "
                    f"{_schedule()}")
    elif is_archived_for_good(e, today):
        standing = (f"Generated from `registry.yaml` on {today.isoformat()}. No probe reads this row "
                    "any more — it left the list for good unless a reviewer brings it back")
    else:
        standing = (f"Generated from `registry.yaml` on {today.isoformat()}. A probe still reads it "
                    f"{_schedule()}, and the first probe it passes brings it back to the list")
    out += ["", "---", "",
            f"{standing}; the full list, the Atom feed and the machinery are at <{REPO_URL}>."]
    return _page(head, out)


def build_providers_index(entries: list[Entry], today: date,
                          events: list[Event] | None = None,
                          pages: set[str] | None = None) -> str:
    """The page that links every provider page — live rows first, in section
    order, the archive after — so a crawler that lands anywhere finds the rest."""
    head = {"title": "Every free LLM API and coding agent on the list, with its evidence",
            "description": "One page per provider: the free tier in the vendor's own "
                           "words, connection details, the evidence a live probe reads "
                           f"{_schedule()}, and the row's history.",
            "permalink": _permalink(providers_index_url()),
            "last_modified_at": max((_last_modified(e, events or [])
                                     for e in entries), default=today)}
    out = ["# Every provider, one page each", "",
           f"Each page is generated from the same registry as [the list]({PAGES_URL}/); a live "
           f"row is re-verified {_schedule()}, and an archived one says why it left. Every free "
           f"model and the rows that serve it are on [the model index]({models_index_url()}).", ""]
    live = [e for e in entries if not is_archived(e, today)]
    archived = _archive(entries, today)
    pages = model_pages(entries, events or [], today) if pages is None else pages
    # A list per section rather than one table: a table with a run of models in
    # one cell stands wider than a phone.
    for title, rows in sections(live):
        out += [f"## {title}", ""]
        for e in rows:
            fams = _row_models(e, pages)
            out.append(f"- [{e.name}]({provider_page_url(e.id)}){_card_flag(e)} — verified "
                       f"{e.last_verified.isoformat()}" + (DOT + fams if fams else ""))
        out.append("")
    if archived:
        out += ["## Archived", ""]
        for e in archived:
            out.append(f"- [{e.name}]({provider_page_url(e.id)}) — {archive_reason(e, today)}")
    return _page(head, out)


def _oldest_verified(rows: list[Entry], today: date) -> date:
    """The floor the badge dates the whole list by, and every page dates its
    rows by: the oldest verified date among them."""
    return min((e.last_verified for e in rows), default=today)


def _floor(rows: list[Entry], today: date) -> str:
    """That floor in words: the date, and "or later" where the rows carry more
    than one."""
    oldest = _oldest_verified(rows, today)
    return oldest.isoformat() + (" or later" if any(e.last_verified != oldest for e in rows) else "")


def _listed_spans(events: list[Event], entry_id: str, family: str
                  ) -> list[tuple[date, date | None]]:
    """Every stretch the row's published free models carried the family, by the
    history — the list's own dates, UTC days, never the vendor's: from the line
    that took the family in to the line that took it out (a change of the
    row's models, its archiving, its removal), the last one open while the row
    still carries it. A row the history never saw with the family has none."""
    spans: list[tuple[date, date | None]] = []
    start: date | None = None
    for ev in events:
        if ev.id != entry_id:
            continue
        day = ev.ts.astimezone(timezone.utc).date()
        carried = ev.event not in (EventType.ARCHIVED, EventType.REMOVED) and family in ev.models
        if carried and start is None:
            start = day
        elif not carried and start is not None:
            spans.append((start, day))
            start = None
    if start is not None:
        spans.append((start, None))
    return spans


def _listed_since(events: list[Event], entry_id: str, family: str) -> date | None:
    """The day the row's free models last took the family in: a family that
    left and came back counts from its return."""
    spans = _listed_spans(events, entry_id, family)
    return spans[-1][0] if spans and spans[-1][1] is None else None


def _promotion_rows(entries: list[Entry], family: str) -> set[str]:
    return {e.id for e in entries if (lane := e.api or e.client_lane)
            for i, a in lane.model_access.items() if a.until and family_names(family, i)}


def _served_before(events: list[Event], family: str, serving: set[str],
                   dated: set[str] | frozenset[str] = frozenset()) -> list[tuple[str, list[tuple[date, date]]]]:
    """The rows that carried the family and carry it no more, each with the
    stretches it did, the most recent departure first. Same-day corrections
    are omitted; a documented promotion may genuinely last less than a day.
    The list's word is "listed": a row can stop
    listing a model it still serves (a free part reread as a sum to spend), so
    the pages never say the row stopped serving it."""
    out = []
    for entry_id in dict.fromkeys(ev.id for ev in events if family in ev.models):
        if entry_id in serving:
            continue
        spans = [(start, end) for start, end in _listed_spans(events, entry_id, family)
                 if end is not None and (end > start or entry_id in dated)]
        if spans:
            out.append((entry_id, spans))
    return sorted(out, key=lambda kv: kv[1][-1][1], reverse=True)


def _model_row(e: Entry, family: str, events: list[Event]) -> list[str]:
    """One row's part of a model page: what it is, what it asks, when the list
    last confirmed it and since when it has carried the model, the limits in
    the vendor's words and how to call this model there. The evidence and the
    history stay on the row's own page, one click from its name."""
    lane = lane_ids(e)
    families = live_families(e)
    ids = [i for i in (lane.model_ids if lane else []) if id_family(families, i) == family]
    flags = [CATEGORY_TITLES[e.category]]
    if not requires_payment(e, family):
        flags.append(_card_words(e))
    if not (e.api and e.api.base_url and ids) and (words := _access_description(e, family, compact=False)):
        flags.append(words)
    if _border_flag(e):
        flags.append(_border_flag(e))
    if e.provisional:
        flags.append(_provisional_words(e))
    flags.append(f"verified {e.last_verified.isoformat()}")
    since = _listed_since(events, e.id, family)
    if since is not None:
        flags.append(f"listed since {since.isoformat()}")
    out = [f"### [{e.name}]({provider_page_url(e.id)})", "", DOT.join(flags), "", e.offering, ""]
    if e.api and e.api.notice:
        # First, as on the row's page: before a reader copies the base URL.
        out += [_notice_quote(e.api.notice), ""]
    limits = (f"- Limits, in the vendor's words: {limits_text(e)}" if limits_text(e)
              else "- The vendor publishes no figure for this tier.")
    if limits_text(e) and len(families) > 1 and len(limits_text(e)) > README_LIMITS_COLLAPSE:
        out += ['<details markdown="block">', "<summary>Provider-wide limits</summary>", "", limits, "", "</details>", ""]
    else:
        out.append(limits)
    # This model's ids and no other's — an id is the most specific of the row's
    # families that names it, as the probe reads it — then the row page's own
    # connection lines.
    out += _connect_lines(e, ids)
    if e.api and e.api.base_url and not ids:
        out.append("- Callable ids: the row lists none for this model")
    if e.data_use is not None:
        out.append(f"- {DATA_USE_WORDS[e.data_use.trains].rstrip('.')} "
                   f"([the vendor's words]({e.data_use.url})).")
    return out + [""]


def build_model_page(family: str, entries: list[Entry], events: list[Event], today: date,
                     pages: set[str] | None = None) -> str:
    """One page per model the list can say something about across its rows.

    A reader arrives with a model in mind as often as with a vendor — where is
    Kimi K3 free — and a search engine answers that with a page whose title is
    the question. This is that page: the model, "free", how many rows serve it
    and the date a probe confirmed them in the title; then every live row that
    serves it, in the list's order, with what a reader needs to use it there,
    and the rows that listed it before, with the days they did. A model no row
    serves any more keeps its page (`model_pages`), and the page says so in its
    title: no longer free, since when, which rows listed it. Every word is the
    registry's or the history's, and the body sits inside {% raw %} for the
    reason the provider pages' does.
    """
    active = [e for e in entries if not is_archived(e, today)]
    by_family = _rows_by_family(active)
    pages = model_pages(entries, events, today) if pages is None else pages
    rows = by_family.get(family, [])
    by_id = {e.id: e for e in entries}
    before = _served_before(events, family, {e.id for e in rows}, _promotion_rows(entries, family))
    if not rows and not before and family not in {m.family for e in entries for m in e.models}:
        raise ValueError(f"the list never named {family!r}, so it has no page")
    departed = [spans[-1][1] for _, spans in before]
    changed = [*(_last_modified(e, events) for e in rows), *departed]
    stem = family.split("-")[0]
    # The same name before the first hyphen — glm, gemini, qwen3.8 — is the
    # family a reader who came for one of them is likeliest to ask about next,
    # and the one to offer a reader whose model is no longer free.
    related = [f for f in by_family if f != family and f.split("-")[0] == stem and f in pages]
    nav = f"[Every free model]({models_index_url()}) · [the whole list]({PAGES_URL}/)"
    if rows:
        n, names = len(rows), [e.name for e in rows]
        floor = _floor(rows, today)
        card = [e.name for e in rows if e.card_required]
        if any(requires_payment(e, family) for e in rows):
            asks = "Free usage is subject to the access conditions below"
        elif not card:
            asks = "It asks for no card" if n == 1 else "None asks for a card"
        elif len(card) == n:
            asks = "It asks for a card on file" if n == 1 else "Each asks for a card on file"
        else:
            asks = (f"{series(card)} {'asks' if len(card) == 1 else 'ask'} for a card on file, "
                    "the rest for none")
        anonymous = [e.name for e in rows if needs_no_account(e)]
        if anonymous:
            asks += ("; it answers with no account at all" if n == 1 else
                     f"; {series(anonymous)} {'answers' if len(anonymous) == 1 else 'answer'} "
                     "with no account at all")
        asks += "."
        served = ("**One row on the list serves" if n == 1 else f"**{n} rows on the list serve")
        summary = [f"{served} `{family}` free:** {series(names)}.", asks,
                   (f"The published offer was checked on {floor} and is rechecked {_schedule()}."
                    if n == 1 else f"The published offers were checked on {floor} and are "
                                   f"rechecked {_schedule()}.")]
        mark = _measured(family, rows)
        if mark is not None:
            board = (f"https://artificialanalysis.ai/models/{mark.aa_model}" if mark.aa_model
                     else "https://artificialanalysis.ai/leaderboards/models")
            index = f"[Artificial Analysis Intelligence Index]({board})"
            if mark.tier is Tier.NOTABLE:
                where = f"in the upper half of the {index}, below its strong bar"
            else:
                within = FRONTIER_WITHIN if mark.tier is Tier.FRONTIER else STRONG_WITHIN
                where = f"within {within:g} points of the top of the {index}"
            summary.append(f"It measures **{mark.tier.value}**: {where}.")
        title = (f"{family} free: {n} provider{'' if n == 1 else 's'}, limits and ids, "
                 f"verified {floor}")
        description = clip(f"{family} is served free by {series(names)}. {asks} Each "
                           "one's limits in the vendor's words, the ids to call and the "
                           "day the published offer was last checked.", DESCRIPTION_ROOM)
        body = [f"# Where {family} is free", "", " ".join(summary), "", nav, "",
                "## Who serves it free", ""]
        for e in rows:
            body += _model_row(e, family, events)
        gone_heading = "## Rows that listed it before"
    else:
        names = [by_id[i].name if i in by_id else i for i, _ in before]
        last = max(departed).isoformat() if departed else ""
        until = f" The list carried it at {series(names)} until {last}." if before else ""
        title = f"{family} free: no longer free on the list" + (f", last listed {last}" if last else "")
        description = clip(f"No row on the list serves {family} free any more.{until} "
                           "Every model free today is on the list's model index.",
                           DESCRIPTION_ROOM)
        body = [f"# Where {family} was free", "",
                f"**No row on the list serves `{family}` free any more.**{until} Each row's page "
                "says what it offers now.", "", nav, ""]
        gone_heading = "## Rows that listed it"
    if before:
        body += [gone_heading, ""]
        for entry_id, spans in before:
            e = by_id.get(entry_id)
            listed = ", ".join(f"{start.isoformat()} to {end.isoformat()}" for start, end in spans)
            body.append(f"- [{e.name if e else entry_id}]({provider_page_url(entry_id)}) — listed "
                        f"{listed}" + ("; the row itself is archived"
                                       if e is not None and is_archived(e, today) else ""))
        body.append("")
    if related:
        body += ["## Related models", "",
                 *(f"- [`{f}`]({model_page_url(f)}) — free at "
                   f"{series([e.name + _access_flag(e, f) for e in by_family[f]])}" for f in related), ""]
    return _page({"title": title, "description": description,
                  "permalink": _permalink(model_page_url(family)),
                  "last_modified_at": max(changed, default=today),
                  "crumb": family},
                 [*body, "---", "",
                  f"Generated from `registry.yaml` on {today.isoformat()} and re-verified "
                  f"{_schedule()}; every free model on the list is at <{models_index_url()}>, and "
                  f"the full list, the Atom feed and the machinery at <{REPO_URL}>."])


def build_models_index(entries: list[Entry], today: date,
                       events: list[Event] | None = None,
                       pages: set[str] | None = None) -> str:
    """Every model the live rows serve free and every row that serves each one —
    the site's model index as a page of its own, for the reader who searched
    for a list of free models rather than for one of them. A model with a page
    links to it; any other links the row that serves it. The models no row
    serves any more, whose pages stay, follow with the day each was last
    listed."""
    events = events or []
    active = [e for e in entries if not is_archived(e, today)]
    by_family = _rows_by_family(active)
    pages = model_pages(entries, events, today) if pages is None else pages
    gone = []
    for family in pages - set(by_family):
        before = _served_before(events, family, set(), _promotion_rows(entries, family))
        last = max((spans[-1][1] for _, spans in before), default=None)
        gone.append((family, last, [entry_id for entry_id, _ in before]))
    gone.sort(key=lambda g: (g[1] or date.min, g[0]), reverse=True)
    by_id = {e.id: e for e in entries}
    title = f"Free LLM models by name: who serves each one free, verified {_floor(active, today)}"
    description = clip(
        f"{len(by_family)} model families the list's {len(active)} live rows serve free, and every "
        f"row that serves each one; {len(pages & set(by_family))} of them have a page of their own "
        "with the limits in the vendor's words and the ids to call.", DESCRIPTION_ROOM)
    changed = [*(_last_modified(e, events) for e in active), *(g[1] for g in gone if g[1])]
    head = {"title": title, "description": description,
            "permalink": _permalink(models_index_url()),
            "last_modified_at": max(changed, default=today)}
    out = ["# Every free model on the list", "",
           f"{len(by_family)} model families, and every row that serves each one free, the most "
           f"widely served first. A model gets a page of its own once {_model_page_rule()}: every "
           "row that serves it, the limits in the vendor's words and the ids to call. It keeps "
           "the page when fewer rows serve it, and when none does the page says since when and "
           f"which rows listed it. A live probe reads every row again {_schedule()}.", "",
           f"[The whole list]({PAGES_URL}/) · [Every provider]({providers_index_url()})", "",
           "| Model | Free at |", "|---|---|"]
    for family, rows in by_family.items():
        cell = f"[`{family}`]({model_page_url(family)})" if family in pages else f"`{family}`"
        mark = _measured(family, rows)
        if mark is not None:
            cell += f" · {mark.tier.value}"
        at = ", ".join("[{}]({}){}".format(e.name.replace("|", r"\|"), provider_page_url(e.id),
                                           _card_flag(e) + _access_flag(e, family)) for e in rows)
        out.append(f"| {cell} | {at} |")
    if gone:
        out += ["", "## No longer free on the list", "",
                "| Model | Last listed | Rows that listed it |", "|---|---|---|"]
        for family, last, ids in gone:
            where = ", ".join("[{}]({})".format(
                (by_id[i].name if i in by_id else i).replace("|", r"\|"), provider_page_url(i))
                for i in ids)
            out.append(f"| [`{family}`]({model_page_url(family)}) | "
                       f"{last.isoformat() if last else '—'} | {where or '—'} |")
    return _page(head, out)


def _index_models(entries: list[Entry], today: date, pages: set[str]) -> list[dict]:
    """index.json's model index: every family the live rows serve free, the ids
    of the rows that serve it, its tier where it has one and its page where it
    has one — the question a machine asks as often as a reader — and after them
    every model with a page that no row serves any more, its rows empty."""
    active = [e for e in entries if not is_archived(e, today)]
    by_family = _rows_by_family(active)
    out = []
    for family, rows in by_family.items():
        mark = _measured(family, rows)
        out.append({"family": family, "rows": [e.id for e in rows],
                    **({"tier": mark.tier.value} if mark is not None else {}),
                    **({"page": model_page_url(family)} if family in pages else {})})
    out += [{"family": family, "rows": [], "page": model_page_url(family)}
            for family in sorted(pages - set(by_family))]
    return out


def checked_page_url() -> str:
    return f"{PAGES_URL}/{PROVIDERS_DIR}/{CHECKED_PAGE}/"


def build_checked_page(watchlist: list[Watched], today: date) -> str:
    """Every service checked and not listed, with its reason and what would
    change the answer — the watchlist as a page of its own. A reader who wants
    to know why a service is missing follows one link to it; the README stays
    the list."""
    rows = _watch_rows(watchlist, today)
    head = {"title": "Services checked and not listed on the free AI coding list",
            "description": "Every service this list checked and did not list, with the "
                           "reason on the date it was read and what would change the answer.",
            "permalink": _permalink(checked_page_url()),
            # The newest verdict: what a reader could see change.
            "last_modified_at": max((w.checked_on for w in watchlist), default=today)}
    out = ["# Checked and not listed", "",
           f"{len(rows)} services whose free tier [the list]({PAGES_URL}/) could not find or could not "
           "verify on the date checked. Nothing here is disqualified — domains rejected for cause are "
           f"in [`blocklist.yaml`]({REPO_URL}/blob/main/blocklist.yaml) — and each verdict expires after "
           f"{WATCH_RECHECK_DAYS} days and is asked again. The records live in "
           f"[`watchlist.yaml`]({REPO_URL}/blob/main/watchlist.yaml).", ""]
    # A list rather than a table: a reason runs to a paragraph, and a table of
    # them stands wider than a phone.
    for w in rows:
        reopen = f" <sub>**Reopens if:** {w['reopen_if']}</sub>" if w["reopen_if"] else ""
        stale = "" if w["current"] else " ⏰"
        out.append(f"- **{w['name']}**, checked `{w['checked_on']}`{stale} — {w['reason']}{reopen}")
    out += ["", f"<sub>⏰ — the verdict is older than {WATCH_RECHECK_DAYS} days, no longer suppresses "
                "anything, and is due for a fresh look.</sub>"]
    return _page(head, out)


def _watchlist_beside(registry_path: Path, watchlist_path: Path | None) -> list[Watched]:
    """The watchlist that belongs to this registry — its sibling unless told
    otherwise. A missing file is an empty list, so a bare registry renders with
    no watchlist."""
    return load_watchlist(watchlist_path or registry_path.parent / "watchlist.yaml")


def _blocklist_beside(registry_path: Path) -> dict[str, str]:
    return load_blocklist(registry_path.parent / "blocklist.yaml")


HISTORY = "history.jsonl"


def _history_path(registry_path: Path) -> Path:
    return registry_path.parent / HISTORY


def _history_beside(registry_path: Path) -> list[Event]:
    """The change log of this registry, read the same way — a sibling file, and
    missing means nothing has been recorded yet."""
    return load_history(_history_path(registry_path))


def _env(template_dir: Path, autoescape: bool) -> Environment:
    """A template environment where a key the context lacks is a render error
    rather than an empty cell."""
    return Environment(loader=FileSystemLoader(template_dir), undefined=StrictUndefined,
                       autoescape=autoescape, keep_trailing_newline=True, trim_blocks=True,
                       lstrip_blocks=True)


def _markdown_env(template_dir: Path) -> Environment:
    """The environment of the pages GitHub renders: no autoescaping, because
    every cell is Markdown the template composes from the registry."""
    env = _env(template_dir, autoescape=False)
    # The quickstart's caveat is the lane's own api note, which can run to a
    # paragraph under the curl. The site prints it whole; the README folds it
    # like the connection notes, and the context keeps the sentence whole so the
    # two pages read the same registry field.
    env.filters["fold_note"] = lambda text: _fold(text, README_NOTE_TEASER,
                                                  README_NOTE_COLLAPSE, small=True)
    # A list of names as a sentence of code spans: "`a`", "`a` or `b`".
    env.filters["either_code"] = lambda names: series([f"`{n}`" for n in names], "or")
    return env


def _github_page_context(registry_path: Path, today: date,
                         watchlist_path: Path | None, scores: dict | None = None) -> dict:
    entries, history = load_registry(registry_path), _history_beside(registry_path)
    # The page is where a deleted row would quietly disappear from.
    refuse_deleted_rows(entries, history)
    return build_context(entries, today, _watchlist_beside(registry_path, watchlist_path),
                         history, model_pages(entries, history, today,
                                              _published_beside(registry_path)), scores)


def render_readme(registry_path: Path, template_dir: Path, out_path: Path,
                  today: date | None = None, watchlist_path: Path | None = None,
                  scores: dict | None = None) -> str:
    today = today or date.today()
    context = _github_page_context(registry_path, today, watchlist_path, scores)
    text = _markdown_env(template_dir).get_template("README.md.j2").render(**context)
    out_path.write_text(text, encoding="utf-8")
    for rel, svg in readme_pictures(context["hero"], context["chart"]).items():
        picture = out_path.parent / rel
        picture.parent.mkdir(parents=True, exist_ok=True)
        picture.write_text(svg, encoding="utf-8")
    return text


def render_configs_readme(registry_path: Path, template_dir: Path, out_path: Path,
                          today: date | None = None, watchlist_path: Path | None = None) -> str:
    """configs/README.md — the connection table, beside the files it describes.

    Base URL, key name and the notes that matter for every live OpenAI-compatible
    API, read by someone who has already decided, while the README's job is the
    visitor who has not. GitHub renders a folder's README under its file list,
    so the table sits next to the configs generated from the same rows, and
    every link in it is written from there. It is rendered from the README's own
    context, so the two pages cannot disagree about a lane.
    """
    today = today or date.today()
    context = _github_page_context(registry_path, today, watchlist_path)
    text = _markdown_env(template_dir).get_template(CONFIGS_TEMPLATE).render(**context)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return text


def render_site(registry_path: Path, template_dir: Path, out_path: Path,
                today: date | None = None, watchlist_path: Path | None = None,
                scores: dict | None = None) -> str:
    """index.html — what the Pages site serves at its root.

    Unlike the README's environment, this one autoescapes: every string on the
    page is a vendor's own sentence, a model id or a URL read out of the
    registry, and none may reach a reader as markup. The provider pages keep
    Liquid off with `{% raw %}`, and freetier-check refuses a tag outside
    backticks in the prose they print.
    """
    today = today or date.today()
    env = _env(template_dir, autoescape=True)
    entries, history = load_registry(registry_path), _history_beside(registry_path)
    refuse_deleted_rows(entries, history)
    context = build_site_context(entries, today,
                                 _watchlist_beside(registry_path, watchlist_path), history,
                                 model_pages(entries, history, today,
                                             _published_beside(registry_path)), scores)
    text = env.get_template(SITE_TEMPLATE).render(**context)
    out_path.write_text(text, encoding="utf-8")
    return text


def _write_files(folder: Path, pattern: str, files: dict[str, str]) -> None:
    """Write each file into `folder` and remove the ones there that match
    `pattern` and are no longer among them. A file of another kind is not the
    render's to delete."""
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text, encoding="utf-8")
    for stale in folder.glob(pattern):
        if stale.name not in files:
            stale.unlink()


def render_artifacts(registry_path: Path, root: Path, today: date | None = None,
                     watchlist_path: Path | None = None) -> None:
    """Everything the render writes besides the README, the site's front page and
    configs/README.md: the feed, the provider and model pages, index.json,
    llms.txt, and the configs with the Codex profiles."""
    today = today or date.today()
    entries = load_registry(registry_path)
    watchlist = _watchlist_beside(registry_path, watchlist_path)
    history = _history_beside(registry_path)
    refuse_deleted_rows(entries, history)
    blocklist = _blocklist_beside(registry_path)
    # The model pages, worked out once for every file that links one: the
    # rule's, and every page already published beside the registry.
    pages = model_pages(entries, history, today, _published_beside(registry_path))
    (root / "feed.xml").write_text(build_feed(history, today, entries=entries), encoding="utf-8")
    # A page per row, the checked page and the index.
    _write_files(root / PROVIDERS_DIR, "*.md", {
        f"{CHECKED_PAGE}.md": build_checked_page(watchlist, today),
        **{f"{e.id}.md": build_provider_page(e, history, today,
                                             is_blocked(domain_of(e.url), blocklist),
                                             registry=entries, pages=pages)
           for e in entries},
        f"{PROVIDERS_INDEX_PAGE}.md": build_providers_index(entries, today, history, pages)})
    # A page per model that has one, the pages already published among them,
    # and the index of every model. The only file taken away is one no family
    # names: a page the site published stays (`model_pages`).
    _write_files(root / MODELS_DIR, "*.md", {
        **{f"{family}.md": build_model_page(family, entries, history, today, pages)
           for family in sorted(pages)},
        "index.md": build_models_index(entries, today, history, pages)})
    (root / "index.json").write_text(
        json.dumps(build_index(entries, today, watchlist, pages), indent=2,
                   ensure_ascii=False) + "\n",
        encoding="utf-8")
    (root / "llms.txt").write_text(build_llms_txt(entries, today, pages), encoding="utf-8")
    configs = root / "configs"
    configs.mkdir(parents=True, exist_ok=True)
    (configs / "opencode.json").write_text(
        json.dumps(build_opencode_config(entries, today), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (configs / "free-llm.env.example").write_text(
        build_env_example(entries, today) + "\n", encoding="utf-8")
    (configs / "claude-code.sh").write_text(
        build_claude_code_sh(entries, today) + "\n", encoding="utf-8")
    (configs / "litellm.yaml").write_text(
        "# Free LLM providers as a LiteLLM proxy config — generated from\n"
        "# registry.yaml, do not edit by hand.\n"
        f"# Run: {litellm_command('litellm.yaml')}\n"
        "# This command opts in to a keyless local-development proxy on loopback.\n"
        "# LiteLLM gives an entry whose key variable is not set the OPENAI_API_KEY it\n"
        "# runs with and sends it to that lane, so the command runs it without one.\n"
        "# The proxy listens on 0.0.0.0 unless --host says otherwise, and this file\n"
        "# sets no master_key, so without that flag anyone on your network can spend\n"
        "# the keys it reads from the environment (see free-llm.env.example).\n"
        "# Entries marked `api_key: none` need no account at all.\n"
        + "".join(f"{line}\n" for line in _comment(
            f"Needs LiteLLM {LITELLM_BRIDGE_SINCE} or later: every entry carries "
            "use_chat_completions_api, which 1.88.3 and earlier send on to the vendor, where a "
            "strict one refuses a field it does not know, and every group deployment carries "
            f"its own allowed_fails_policy, which LiteLLM reads from {LITELLM_BRIDGE_SINCE} on. "
            "The flag makes the proxy's /v1/responses — the only API Codex CLI speaks — call "
            "each lane's chat completions; codex/litellm.config.toml is Codex's profile for "
            "this file."))
        + _litellm_groups_note(litellm_groups(entries, today))
        + "".join(f"# Left out: {e.name} — {why}.\n"
                  for e in _connectable(entries, today) for why in _static_blockers(e))
        + "".join(f"# Left out: {e.name} — its keyless lane answers only a call with no "
                  "Authorization header, and LiteLLM sends one on every call.\n"
                  for e in _configurable(entries, today) if e.api.refuses_bearer)
        + yaml.safe_dump(build_litellm_config(entries, today), sort_keys=False,
                         allow_unicode=True),
        encoding="utf-8")
    # Codex's profiles: the one over litellm.yaml and one per lane it calls
    # directly. A profile whose row stopped qualifying is removed.
    _write_files(root / CODEX_DIR, "*.config.toml", {
        Path(CODEX_LITELLM_PATH).name: build_codex_litellm_profile(entries, today),
        **{Path(codex_profile_path(e)).name: build_codex_profile(e)
           for e in _codex_direct(entries, today)}})


# CONTRIBUTING.md is written by hand except for its map section, which is the
# map itself (layout.MAP) printed as a table between these two lines.
CONTRIBUTING = "CONTRIBUTING.md"
MAP_BEGIN = ("<!-- The map: printed by freetier-render from layout.MAP. "
             "Edit layout.py, not this table. -->")
MAP_END = "<!-- End of the map. -->"


def render_contributing(source: Path, out: Path) -> str | None:
    """CONTRIBUTING.md with its map section printed from the map.

    The prose is a person's; the table is layout.MAP's, so the page that
    explains which file comes from which cannot describe a map the checks no
    longer hold. A page without the two marker lines is left as it is, and
    `freetier-check` is where their absence is reported."""
    if not source.is_file():
        return None
    text = source.read_text(encoding="utf-8")
    if MAP_BEGIN not in text or MAP_END not in text:
        return None
    head, rest = text.split(MAP_BEGIN, 1)
    _, tail = rest.split(MAP_END, 1)
    text = f"{head}{MAP_BEGIN}\n\n{markdown_table()}\n\n{MAP_END}{tail}"
    out.write_text(text, encoding="utf-8")
    return text


def render_all(registry_path: Path, template_dir: Path, root: Path,
               readme_name: str = "README.md", today: date | None = None,
               watchlist_path: Path | None = None, contributing_from: Path | None = None) -> None:
    """Every file the render writes, into `root`: what `freetier-render` does to
    the repository and what `--check` does to a temporary directory, so the
    check can never compare fewer files than the render writes.
    `contributing_from` is the directory whose CONTRIBUTING.md the map is
    printed into — the repository itself, when the output is not."""
    render_readme(registry_path, template_dir, root / readme_name, today=today,
                  watchlist_path=watchlist_path)
    render_site(registry_path, template_dir, root / SITE_PAGE, today=today,
                watchlist_path=watchlist_path)
    render_configs_readme(registry_path, template_dir, root / CONFIGS_README, today=today,
                          watchlist_path=watchlist_path)
    render_artifacts(registry_path, root, today=today, watchlist_path=watchlist_path)
    render_contributing((contributing_from or root) / CONTRIBUTING, root / CONTRIBUTING)


def render_repository(registry_path: Path, template_dir: Path, root: Path,
                      readme_name: str = "README.md", today: date | None = None,
                      now: datetime | None = None, watchlist_path: Path | None = None,
                      committed: str | None = None) -> list[Event]:
    """What `freetier-render` does: record every change the registry makes in
    history.jsonl beside it, then write every page — so the commit that makes a
    change carries its line, and the pages it publishes already show it.
    `committed` is the log the commit will be made on (`gate.committed_log`);
    the lines recorded are the ones it will add."""
    today = today or date.today()
    now = now or datetime.now(timezone.utc)
    entries = load_registry(registry_path)
    current = expire_entries(entries, now)
    if current != entries:
        save_registry(registry_path, current)
    recorded = record_changes(registry_path, _history_path(registry_path), today,
                              now, committed=committed)
    render_all(registry_path, template_dir, root, readme_name, today=today,
               watchlist_path=watchlist_path)
    return recorded


def _generated_on(root: Path, today: date) -> date:
    """The day the committed artifacts were rendered on, read back off them.

    Rendering stamps the day into index.json, the feed and every provider
    page's footer, so a re-render on a later day would differ on the date alone.
    The check renders on the day the artifacts carry, and asks whether the
    registry as it stands renders to what that day's render produced.
    """
    try:
        stamped = json.loads((root / "index.json").read_text(encoding="utf-8"))["generated"]
        return date.fromisoformat(stamped)
    except (OSError, ValueError, KeyError, TypeError):
        return today


def check_rendered(registry_path: Path, template_dir: Path, root: Path,
                   readme_name: str = "README.md", today: date | None = None,
                   watchlist_path: Path | None = None) -> list[str]:
    """Paths under `root` the registry no longer renders to what is committed.

    Every published file here is generated and every one of them is committed:
    the README and its pictures, the site's front page, index.json, the feed,
    llms.txt, the configs and the README beside them, and the pages per row and
    per model. A commit that skipped the render would otherwise publish — on the
    page, in the JSON an LLM reads, in the config a reader pastes — a registry
    that has moved on, until the next scheduled run renders.
    """
    today = today or date.today()
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        pinned = _generated_on(root, today)
        # Only the outputs move: the registry, its watchlist and its history are
        # read from where they live, so this is the committed files against the
        # curated ones and not against a copy of them.
        render_all(registry_path, template_dir, tmp, readme_name, today=pinned,
                   watchlist_path=watchlist_path, contributing_from=root)
        fresh = {p.relative_to(tmp).as_posix(): p.read_bytes()
                 for p in tmp.rglob("*") if p.is_file()}
    stale = [rel for rel, data in fresh.items()
             if not (root / rel).is_file() or (root / rel).read_bytes() != data]
    # The log is the render's to write too: a registry that moves on and a log
    # that does not would publish a change no page lists and no feed announces.
    if pending_changes(load_registry(registry_path), _history_beside(registry_path), pinned):
        stale.append(HISTORY)
    # render_artifacts removes a page it no longer writes only in the directory
    # it wrote to; a page left behind in the repository is still served, so the
    # absent half of the comparison counts too.
    stale += [p.relative_to(root).as_posix()
              for pages, kind in ((PROVIDERS_DIR, "*.md"), (MODELS_DIR, "*.md"),
                                  (README_PICTURES, "*.svg"), (CODEX_DIR, "*.config.toml"))
              for p in (root / pages).glob(kind)
              if p.relative_to(root).as_posix() not in fresh]
    return sorted(stale)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--out", type=Path, default=Path("README.md"))
    parser.add_argument("--watchlist", type=Path, default=None,
                        help="defaults to watchlist.yaml beside the registry")
    parser.add_argument("--check", action="store_true",
                        help="write nothing; report the generated files that no longer "
                             "match the registry, and exit 1 if any do")
    parser.add_argument("--expire-only", action="store_true",
                        help="publish ended model promotions; write nothing if none ended")
    args = parser.parse_args()
    if args.check and args.expire_only:
        parser.error("--check and --expire-only cannot be combined")
    root = args.out.parent if args.out.parent != Path("") else Path(".")
    # What the map says the render writes, so the summary is the map's list.
    written = ", ".join(n.path for n in MAP if "freetier-render" in n.written_by)
    if args.check:
        stale = check_rendered(args.registry, args.templates, root, args.out.name,
                               watchlist_path=args.watchlist)
        for rel in stale:
            print(f"stale: {rel}")
        print(f"checked {written} — {len(stale)} out of date")
        if stale:
            # The remedy is always the same command, so the failure says it.
            print("run `TZ=UTC uv run freetier-render` and commit what it writes")
            raise SystemExit(1)
        return
    if args.expire_only:
        entries = load_registry(args.registry)
        if expire_entries(entries, datetime.now(timezone.utc)) == entries:
            print("no model promotion has ended")
            return
    recorded = render_repository(args.registry, args.templates, root, args.out.name,
                                 watchlist_path=args.watchlist,
                                 committed=committed_log(_history_path(args.registry)))
    for ev in recorded:
        print(f"history: {ev.event.value} {ev.id}")
    print(f"rendered {written}")


if __name__ == "__main__":
    main()
