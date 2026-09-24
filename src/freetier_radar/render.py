from __future__ import annotations

import argparse
import json
import re
import tempfile
import textwrap
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .history import (Event, EventType, archive_reason, load_history, pending_changes,
                      record_changes, refuse_deleted_rows)
from .models import (ARCHIVE_AFTER_DAYS, ARCHIVE_AFTER_FAILURES, PROBE_WEEKDAYS,
                     SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Category, Entry, Notice,
                     ProbeType, Tier, Watched, _id_squash, domain_of, family_names, folded_into,
                     is_archived,
                     is_archived_for_good, is_blocked, is_watch_current, live_families,
                     load_blocklist, load_registry, load_watchlist, probe_frequency)
# How the probe decides which of a row's families a catalog id is: the configs
# group ids by tier with the same rule, so the two can never disagree. The
# promotion day is the probe's too, and the pages say how far off it is.
from .prober import PROVISIONAL_PROMOTE_DAYS
# The bar a family's score must clear to be called frontier, which the picks
# table states beside the answer.
from .tiers import FRONTIER_WITHIN
# The map of the repository, which CONTRIBUTING.md prints.
from .gate import committed_log
from .layout import MAP, markdown_table

__all__ = ["ARCHIVE_AFTER_DAYS", "ARCHIVE_AFTER_FAILURES", "FEED_ENTRIES", "FEED_URL",
           "README_CHANGES", "README_MODELS", "README_PICKS", "README_STARTERS", "badge_colour",
           "is_archived", "build_context", "build_feed", "build_index", "check_rendered",
           "build_opencode_config", "build_env_example", "build_claude_code_sh", "env_var",
           "build_provider_page", "build_folded_page", "build_providers_index",
           "provider_page_url", "PAGES_URL",
           "build_llms_txt",
           "picks",
           "SITE_PAGE", "build_site_context", "render_site",
           "CONFIGS_README", "README_BUDGET", "render_configs_readme",
           "render_readme", "render_artifacts", "render_all", "render_contributing", "main"]

CATEGORY_TITLES: dict[Category, str] = {
    Category.AGENT_CLI: "🤖 Coding agents & CLIs",
    Category.API_FREE_TIER: "🔌 LLM APIs with free tier",
    Category.TRIAL: "🎁 Trials (no card when possible)",
    Category.AGGREGATOR: "🧭 Aggregators (one key, many providers)",
}

REPO_URL = "https://github.com/mvalentsev/awesome-free-ai-coding"
# GitHub Pages rather than raw.githubusercontent.com, which serves every file as
# text/plain and is documented as not being a CDN — a feed is polled hourly by
# every subscriber, which is exactly the hotlinking that asks for. The URL is
# baked into the feed's own <id> and <link rel="self">, so it cannot be changed
# later without breaking every subscription that ever read it.
FEED_URL = "https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml"
# The Pages site the feed lives on, and where each row gets a page of its own.
# A reader arrives from a search with a question about one vendor — "groq free
# tier limits" — and a README row is not a URL. The pages are generated from the
# same registry, so a page can never outlive its row or say what the row does not.
PAGES_URL = "https://mvalentsev.github.io/awesome-free-ai-coding"
PROVIDERS_DIR = "providers"
FEED_ENTRIES = 50
README_CHANGES = 10
# Where a prose cell stops showing and starts folding. The teaser is a cut at a
# word boundary, so the gap between the two is what keeps a row from folding away
# a line and a half of text to save half a line. The README's own rows no longer
# fold anything: `limits` left the page for the row's own page and the site on
# 2026-09-21, and `offering` prints whole. The archive's reasons and the
# connection notes still fold at these marks.
README_LIMITS_TEASER = 150
README_LIMITS_COLLAPSE = 260
# The README is the landing page and the site is the reference. On 2026-09-20
# the README ran to 161 KB — 83 KB of it inside 93 <details> folds, the median
# `limits` cell 926 characters — which was thirty-one desktop screens and
# fifty-one on a phone, sixteen and thirty-one of them tables. A row is one line
# now — 54 KB with 77 rows on 2026-09-21, about 400 bytes a row — so the page
# grows a line per row, and the budget is what keeps the reference job from
# creeping back: sixty rows of headroom, and less than the connection table
# alone (38 KB) or the limits column (83 KB) would put back. A test renders the
# committed registry against it.
README_BUDGET = 80_000
# The connection table lives beside the files it describes. GitHub renders a
# folder's README under its file list, so a reader who opens configs/ for the
# opencode config finds the base URLs and key names on the same screen.
CONFIGS_README = "configs/README.md"
CONFIGS_TEMPLATE = "configs-README.md.j2"
# A code span as CommonMark reads one: a run of backticks, closed only by a run
# of the same length.
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", re.S)
# The connection table's note sits in the same cell as the vendor's name, and is
# the cell that grows: a rotating lane, an id spelling, a caveat about which of
# two endpoints the probe reads. Kenari's reached 1,364 characters against a
# median of 280, four times the width of the median row. Folded a little later
# than `limits`, because half of these notes are one sentence and a fold that
# hides a single line is worse than the line.
README_NOTE_TEASER = 150
README_NOTE_COLLAPSE = 300
# How many agents the page answers "what do I code with, then?" by name before
# the reference table starts. Four is what fits above the fold beside the
# quickstart; the fifth-ranked agent is one section down either way.
README_STARTERS = 4
# How many names answer each "I want…" line of the picks table. Three reads as
# a choice; a fourth is the section itself, which starts one heading down.
README_PICKS = 3
# How many of a row's model families a README line names before it links the
# rest: a lane that rotates names every model it has served free for two weeks,
# fourteen on OpenRouter on 2026-09-24, and a README row is one line. The row's
# page, the site and the list of who serves each model name them all.
README_MODELS = 8
# What the README's quickstart curl calls itself on a lane that asks every client
# for a User-Agent of its own: the command is this page's, so it says so, in the
# name/version shape the vendors' own example uses.
QUICKSTART_USER_AGENT = "awesome-free-ai-coding-quickstart/1.0"

# The freshness badge carries the age of the *oldest* live verification, and
# its colour has to be able to disagree with it. Probes run Mondays and
# Thursdays, so a healthy floor is three or four days old and one missed run
# puts it at a week; three consecutive FAILs bury a row, which caps a failing
# row's drag at about ten days. A floor older than that is being held back by
# something no probe result clears on its own — a row answering INCONCLUSIVE
# run after run keeps its date frozen for the full sixty days before staleness
# archives it, and a workflow that stopped firing looks exactly the same. A
# hard-coded green read "fresh" for a floor of any age, which is the one thing
# a freshness badge must never do.
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


_WEEKS = {7: "a week", 14: "two weeks", 21: "three weeks", 28: "four weeks"}


def _weeks(days: int) -> str:
    return _WEEKS.get(days, f"{days} days")


def _by_rank(e: Entry) -> tuple[int, bool, str]:
    """The order rows are read in wherever the list prints more than one of
    them: `rank`, then a row that asks for no card before one that does
    (CONTRIBUTING: a row that needs a card never leads the no-card rows it ties
    with), then the name."""
    return e.rank, e.card_required, e.name.lower()


def _ordered(active: list[Entry], category: Category) -> list[Entry]:
    """One section of the list, in the order every page prints it."""
    return sorted((e for e in active if e.category is category), key=_by_rank)


# What each event is called wherever a human reads it: the row's page, the
# "What changed" tables, the feed and the monthly digest. One word each — until
# 2026-09-24 four tables named the five events, and "Added to the list", "New"
# and "➕ Added" were one event. The tables put a mark before the word.
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


def _families(e: Entry) -> list[str]:
    return live_families(e)


def _readme_families(e: Entry) -> tuple[list[str], int]:
    """The families a README line names, in the row's own order and at most
    README_MODELS of them, and how many more the row's page names."""
    fams = _families(e)
    return fams[:README_MODELS], max(0, len(fams) - README_MODELS)


def _fold(text: str, teaser_at: int, collapse_over: int, small: bool = False) -> str:
    """A long cell without the wall: what it says first, then all of it.

    The two prose columns carry what this list is worth — what the offer is, and
    the vendor's own figures with the page and date they were read on — and they
    run to 251 and 1,268 characters. Six of those stacked in one column is not a
    table anyone scans. Folding the tail keeps every character and gives the
    page back its shape.

    The teaser is a cut, not a summary: no sentence is composed here, and the cut
    lands on a word boundary. It works because these rows are written
    figure-first and subject-first — "20 requests per minute on any :free id",
    "Open-source TUI/desktop coding agent with seven zero-priced models" — so
    what a reader came for survives the cut and the sourcing is one click away.
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
    whole cell, its tags as text. opencode's lane notice and then its limits
    did that from 2026-09-17, both cut inside `403 FreeTierError: …`. A span
    that runs past `at` with no word before it is kept whole, because a teaser
    has to show something.
    """
    spans = [m.span() for m in _CODE_SPAN.finditer(text)]
    words = [i for i, ch in enumerate(text[:at])
             if ch == " " and i > 0 and not any(s < i < e for s, e in spans)]
    cut = words[-1] if words else next((e for s, e in spans if s < at < e), at)
    return text[:cut].rstrip(" ,;:.—-")


def provider_page_url(entry_id: str) -> str:
    return f"{PAGES_URL}/{PROVIDERS_DIR}/{entry_id}/"


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


def _row(e: Entry) -> dict[str, str]:
    fams, more = _readme_families(e)
    return {
        "name": e.name,
        "url": e.url,
        "page": provider_page_url(e.id),
        # Whole, never folded: freetier-check holds it to 300 characters, and the
        # README's row is this sentence, the models and the date. The quota is on
        # the row's page, one click from the date.
        "offering": e.offering,
        # The one column that was 39 identical ticks out of 41 rows. What a
        # reader needs from it is the exception, and an exception is easier to
        # see beside the name than in a column of agreement — the section
        # headings carry the count in words.
        "card_flag": " 💳" if e.card_required else "",
        # Both markers sit beside the name for the same reason: they are facts
        # about the row, not values of a column, and the date column is the
        # narrowest on the page — a second glyph in it wrapped the date onto two
        # lines in every row that carried one.
        "new_flag": " 🧪" if e.provisional else "",
        # What the reader pays besides money: the vendor may train on what they
        # send. One glyph like the card's; the vendor's sentence is on the page.
        "data_flag": " 👁" if _trains(e) else "",
        "verified": e.last_verified.isoformat(),
        # Backticked, because a model id is something the reader will paste into
        # a config rather than read as prose.
        "models": (", ".join([f"`{f}`" for f in fams]
                             + ([f"[+{more} more]({provider_page_url(e.id)})"] if more else []))
                   if fams else "—"),
    }


def _departure(e: Entry) -> date:
    """The day the reason a row is archived for names — what the Archive is
    ordered by, latest first."""
    if e.delisted is not None:
        return e.delisted.on
    return e.retired_on or e.last_verified


def _archive(entries: list[Entry], today: date) -> list[Entry]:
    """The archived rows a reader is shown: one line per service.

    A row folded into another (`duplicate_of`) named a service the Archive
    already holds — MiMoCode and MiMo Code were Xiaomi's agent twice, two lines
    apart, from the list's first day until 2026-09-20 — so it is left out of
    every list that counts services. Nothing is lost by that: the row stays in
    the registry, its page stays at its own URL pointing at the row that holds
    the service, and that row names it back."""
    return [e for e in entries if is_archived(e, today) and e.duplicate_of is None]


def _archived_rows(entries: list[Entry], today: date) -> list[dict[str, str]]:
    """The Archive: each row's name linking its own page, and why it left.

    The name used to link the vendor and the second column showed the row's
    last probe pass. On 2026-09-17 all three archived rows showed a pass later
    than the day their vendors had ended the offers — probes anchored on pages
    that outlived the offers — and two of the rows had been added after that
    day. The page carries the evidence; a vendor link for a row that left is at
    best dead and at worst, for a row rejected for cause, a referral."""
    gone = sorted(_archive(entries, today),
                  key=lambda e: (_departure(e), e.name.lower()), reverse=True)
    return [{"name": e.name, "page": provider_page_url(e.id),
             "why": _fold(archive_reason(e, today), README_LIMITS_TEASER,
                          README_LIMITS_COLLAPSE, small=True)}
            for e in gone]


def env_var(entry_id: str) -> str:
    return entry_id.removesuffix("-free").replace("-", "_").replace(".", "_").upper() + "_API_KEY"


def needs_no_account(e: Entry) -> bool:
    """Whether a reader calls the lane without making an account: it takes no
    key, or the vendor prints one for anyone (`api.public_key`)."""
    return bool(e.api) and (e.api.auth == "none" or e.api.public_key is not None)


def _connectable(entries: list[Entry], today: date) -> list[Entry]:
    return sorted(
        (e for e in entries
         if not is_archived(e, today) and e.api and e.api.base_url and e.api.openai_compatible),
        key=_by_rank,
    )


def _configurable(entries: list[Entry], today: date) -> list[Entry]:
    """The connectable rows a config written once can actually call.

    A lane that wants a stable id per conversation in a header of its own
    (`api.session_header`) is not one of them. A litellm.yaml entry is static:
    it either omits the header — opencode Zen's free ids answered that with 400
    MissingSessionID — or pins one id for every conversation, which is not what
    the vendor asked for. OpenCode does send x-opencode-session, but only for
    its own built-in provider, which a reader of opencode.json already has, and
    it sends no other vendor's header. Those rows are connected by a client that
    sends the header, and the connection table, the provider page, the env
    example and llms.txt say which header."""
    return [e for e in _connectable(entries, today) if not e.api.session_header]


def _session_note(header: str) -> str:
    return f"`{header}` per conversation"


def _notice_since(notice: Notice) -> str:
    """The notice's date, linked to where the problem is followed when the row
    names a place — the same idiom as the README's verified dates, which link
    to their evidence."""
    since = notice.since.isoformat()
    return f"[{since}]({notice.url})" if notice.url else since


def _model_index(active: list[Entry]) -> list[dict]:
    """Model family → everyone who serves it free, most-served first.

    Answers the question the per-provider tables cannot: a reader who wants
    `qwen3` does not know, and should not have to scan twenty rows to learn,
    which five entries carry it. A row that needs a card carries its 💳 here
    too: "free at" beside a name with no mark reads as free without one.
    """
    by_family: dict[str, list[Entry]] = {}
    for e in active:
        for family in _families(e):
            by_family.setdefault(family, []).append(e)
    return [
        {"family": family,
         "providers": [{"name": p.name, "url": p.url,
                        "card_flag": " 💳" if p.card_required else ""}
                       for p in sorted(ps, key=_by_rank)]}
        for family, ps in sorted(by_family.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]


def _starters(active: list[Entry]) -> list[dict]:
    """The agents a reader can code with today, named before the reference table.

    The page used to open on the keyless curl alone, and that reads as an offer:
    the one lane on this list that needs no account is also the weakest thing on
    it — a demo rate-limited to a couple of requests a minute — so the first
    impression of "free AI coding" became a toy nobody would write code with.
    The answer to "what do I actually use?" is the agents that run on a $0 plan,
    and it is already in the registry: category, `rank` (the maintainer's order
    within it), `card_required`, and the model families a probe re-reads twice a
    week. Nothing here is typed by hand, so the promise cannot outlive the row.

    A row with no families is skipped rather than ranked down. CodeGPT and Charm
    Hyper are free and good and say nothing about which models they route to,
    and the whole point of this block is naming models.
    """
    rows = [e for e in active
            if e.category is Category.AGENT_CLI and not e.card_required and live_families(e)]
    return [_starter(e) for e in sorted(rows, key=_by_rank)[:README_STARTERS]]


def _starter(e: Entry) -> dict:
    families, more = _readme_families(e)
    return {"name": e.name, "url": e.url, "families": families, "more": more,
            "page": provider_page_url(e.id)}


def _pick(e: Entry, families: list[str] | None = None) -> dict:
    return {"name": e.name, "url": e.url, "families": families or []}


def _picks(active: list[Entry], connectable: list[Entry]) -> dict[str, list[dict]]:
    """The answers to "which one, for me", each the top of a section.

    A reader arrives with a need, not with time to read fifty rows: the
    strongest models for nothing, the key that gets the most work done, no
    account at all, a trial that will not ask for a card. Every list in this
    space answers that with a table someone typed once, and it is the first
    thing on those pages to rot — a recommendation outlives the offer behind it
    by months. Here each cell is derived: the section's own `rank` order with
    the card-required rows removed, capped at README_PICKS, so a row that stops
    verifying leaves the table on the same run it leaves the list.

    "Frontier" is the one answer that crosses sections. It is the registry's own
    tier mark on a family — one tier per family, enforced by freetier-check —
    and the row carries the families that earned it, because "frontier models
    free" is only an answer if it says which. Across sections `rank` compares
    nothing (it orders a row within its own category), so this row is ordered
    by how many frontier families the entry hands over, and only then by rank:
    an agent bundling five is a better answer than a gateway bundling one.

    Keyless rows come from the connection table's order rather than a category:
    "no account" is a property of the endpoint, and it is the same property the
    quickstart curl below the table is chosen by.
    """
    ranked = [e for e in sorted(active, key=_by_rank) if not e.card_required]

    def top(category: Category) -> list[dict]:
        return [_pick(e) for e in ranked if e.category is category][:README_PICKS]

    frontier = []
    for e in ranked:
        families = [m.family for m in e.models
                    if m.superseded_by is None and m.tier is Tier.FRONTIER]
        if families:
            frontier.append((len(families), e.rank, e.name.lower(), _pick(e, families)))
    frontier.sort(key=lambda row: (-row[0], row[1], row[2]))
    return {
        "frontier": [row[3] for row in frontier[:README_PICKS]],
        "apis": top(Category.API_FREE_TIER),
        "aggregators": top(Category.AGGREGATOR),
        "keyless": [_pick(e) for e in connectable if needs_no_account(e)][:README_PICKS],
        "trials": top(Category.TRIAL),
        # The question the 27,000-star routers answer by re-exposing paid
        # sessions. The legal answer is a gateway whose vendor documents an
        # Anthropic-format route, and the row names it — across sections, in
        # rank order, since a free lane behind that route is what matters.
        "claude_code": [_pick(e) for e in ranked
                        if e.api and e.api.anthropic_base_url][:README_PICKS],
    }


def picks(entries: list[Entry], today: date) -> dict[str, list[dict]]:
    """The README's "I want…" answers, for anything else that publishes them."""
    active = [e for e in entries if not is_archived(e, today)]
    return _picks(active, _connectable(entries, today))


def _quickstart(connectable: list[Entry]) -> dict | None:
    """The one call a reader can make before deciding to trust any of this:
    keyless, OpenAI-compatible, with a model id the registry knows is callable.

    Generated rather than typed, so the snippet is archived along with its entry
    instead of sitting on the page as a command that stopped working.

    The entry's api note rides along with it. A keyless lane is keyless because
    it is rate-limited instead, and the first command in the README is exactly
    where a reader meets that limit — an unexplained 429 on the one call the
    page promises reads as "this list is stale", which is the opposite of what
    it is. The caveat belongs in the registry beside the evidence for it, not
    typed into the template, or it would outlive the entry it describes.
    """
    for e in connectable:
        if e.api.auth == "none" and e.api.model_ids:
            notice = e.api.notice
            start = {"name": e.name, "url": e.url,
                     "base_url": e.api.base_url.rstrip("/"),
                     "model_id": e.api.model_ids[0],
                     "note": e.api.note,
                     "session_header": e.api.session_header or "",
                     "user_agent": QUICKSTART_USER_AGENT if e.api.client_user_agent else "",
                     # The command stays on the page while the list waits for the
                     # vendor, so the page says, right under it, that it does not
                     # work and since when.
                     "notice": ({"since": notice.since.isoformat(), "text": notice.text,
                                 "url": notice.url or ""} if notice else None)}
            return {**start, "curl": _quickstart_curl(start)}
    return None


def _quickstart_curl(start: dict) -> str:
    """The command itself, written once for both pages that print it.

    The README printed it from its template and the site from here, so the
    question it asks was typed twice and a test held the two copies together.
    The site shows it twice more — in a <pre> and in the copy button's
    attribute — and an attribute is the one place a shell command must not be
    assembled by a template: this one carries both quote characters, and a
    fragment Jinja had already marked safe would close the attribute on the
    first of them. Built as one string here, it is printed as it is in the
    README's code block and escaped correctly in both places on the site.
    """
    lines = [f"curl -s {start['base_url']}/chat/completions \\",
             "  -H 'Content-Type: application/json' \\"]
    if start["user_agent"]:
        lines.append(f"  -H 'User-Agent: {start['user_agent']}' \\")
    if start["session_header"]:
        lines.append(f'  -H "{start["session_header"]}: quickstart-$RANDOM$RANDOM" \\')
    lines.append(f"""  -d '{{"model":"{start['model_id']}","messages":"""
                 """[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'""")
    return "\n".join(lines)


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
    """What an event says after its name. A row deleted before rows were
    archived carries no detail in the history — "➖ Delisted Kenari —" was all
    the page said about four rows on 2026-09-17 — and the row is back in the
    registry as delisted, so the reason the Archive keeps answers for it, on
    every page that lists events of many rows. The row's own page says it once,
    in its header."""
    if ev.detail or ev.event is not EventType.REMOVED:
        return ev.detail
    row = next((e for e in entries or [] if e.id == ev.id), None)
    return row.delisted.reason if row is not None and row.delisted is not None else ""


def _change_rows(events: list[Event], entries: list[Entry] | None = None,
                 today: date | None = None, limit: int = README_CHANGES) -> list[dict]:
    """The tail of the log, newest first, as Markdown table cells.

    Pipes are escaped here rather than rejected in `freetier-check`: an event's
    detail is copied out of an entry's own `offering`, so a pipe in it is a
    perfectly good sentence that only this one table would trip over.
    """
    return [
        {"date": ev.ts.date().isoformat(),
         "label": CHANGE_LABELS[ev.event],
         "name": ev.name,
         "url": _event_link(ev, entries, today or date.today()),
         "detail": event_detail(ev, entries).replace("|", r"\|") or "—"}
        for ev in _newest_first(events, limit)
    ]


def _rfc3339(stamp: datetime) -> str:
    """Atom demands a full timestamp with an offset. A naive one can only have
    come from a hand-written line; read it as UTC rather than as this runner's
    local time, which is the one thing it certainly is not."""
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


def _auth_cell(e: Entry) -> str:
    """What a client sends to be let in: the key, or none, the key the vendor
    prints for anyone where it prints one, and whatever else the vendor asks
    every request to carry."""
    cell = "—" if e.api.auth == "none" else f"`{env_var(e.id)}`"
    subs = []
    if e.api.public_key:
        subs.append(f"no account: the vendor prints one for anyone, `{e.api.public_key}`")
    asks = []
    if e.api.client_user_agent:
        asks.append("your client's own `User-Agent`")
    if e.api.session_header:
        asks.append(_session_note(e.api.session_header))
    if asks:
        subs.append(("" if e.api.auth == "none" else "and ") + " and ".join(asks))
    if not subs:
        return cell
    return cell + "<br><sub>" + "; ".join(subs) + "</sub>"


def _connection_note(e: Entry) -> str:
    """The cell under a provider's name in the connection table: a notice first,
    since it is what a reader copying the base URL most needs to know, then the
    note, each folded like the prose columns."""
    parts = []
    if e.api.notice:
        parts.append(f"⚠️ <sub>**Does not work as published since {_notice_since(e.api.notice)}.**</sub>"
                     "<br>" + _fold(e.api.notice.text, README_NOTE_TEASER, README_NOTE_COLLAPSE,
                                    small=True))
    if e.api.note:
        parts.append(_fold(e.api.note, README_NOTE_TEASER, README_NOTE_COLLAPSE, small=True))
    return "<br>".join(parts)


def _shared_facts(entries: list[Entry], today: date,
                  watchlist: list[Watched] | None = None) -> dict:
    """Every figure and every stated rule the README and the site both print,
    worked out once.

    Each page used to count for itself: the site kept its own tally of the
    services checked (the current verdicts only, where the README and the page
    both link counted them all), and the README typed `free/strong` into its
    file table after the configs README, llms.txt and litellm.yaml had started
    reading the groups off the config. A figure computed in one place cannot be
    two figures, and a rule the code applies — the frontier bar, the provisional
    fortnight, how often a row is probed, how a row leaves — is printed from
    the constant that applies it.
    """
    active = [e for e in entries if not is_archived(e, today)]
    connectable = _connectable(entries, today)
    # The badge dates the evidence, not the render. Using today's date moved it
    # forward whenever the README was regenerated without a probe run —
    # claiming a freshness no entry had. The oldest passing probe among live
    # entries is the honest reading: everything on this page has been confirmed
    # at least this recently. It is a floor, and the badge has to say so — read
    # as a single check date it understates the page badly, because one lagging
    # row drags the whole claim back. On 2026-09-12 it read 2026-09-07 while
    # fifty-four of fifty-six rows had passed a probe two days earlier and only
    # trae and inception-labs, both mid-re-anchor, were holding it there.
    verified_through = min((e.last_verified for e in active), default=today)
    colour = badge_colour(verified_through, today)
    model_index = _model_index(active)
    anthropic = _anthropic_ready(entries, today)
    return {
        "date": today.isoformat(),
        "verified_through": verified_through.isoformat(),
        "verified_colour": colour,
        "verified_word": BADGE_WORDS[colour],
        # The headline counts. Every one of them is derived, so the page can
        # never advertise a number the registry stopped backing.
        "active_count": len(active),
        "no_card_count": sum(1 for e in active if not e.card_required),
        "card_count": sum(1 for e in active if e.card_required),
        "no_signup_count": sum(1 for e in connectable if needs_no_account(e)),
        "endpoint_count": len(connectable),
        "family_count": len(model_index),
        "model_index": model_index,
        "starters": _starters(active),
        "picks": _picks(active, connectable),
        "quickstart": _quickstart(connectable),
        # Every verdict on the page of services checked and not listed, a
        # verdict due for a fresh look included — that page lists them all.
        "watch_count": len(watchlist or []),
        # The LiteLLM groups the config defines today, and the shell function a
        # reader is shown as the example: both are read off the files they name.
        "litellm_groups": litellm_groups(entries, today),
        "claude_example": f"claude-{anthropic[0].id}" if anthropic else "",
        "has_provisional": any(e.provisional for e in active),
        "has_trains": any(_trains(e) for e in active),
        "schedule": _schedule(),
        "frontier_within": f"{FRONTIER_WITHIN:g}",
        "provisional_weeks": _weeks(PROVISIONAL_PROMOTE_DAYS),
        "archive_after_failures": ARCHIVE_AFTER_FAILURES,
        "archive_after_days": ARCHIVE_AFTER_DAYS,
        "watch_recheck_days": WATCH_RECHECK_DAYS,
        "checked_url": checked_page_url(),
        "feed_url": FEED_URL,
        "pages_url": PAGES_URL,
    }


def build_context(entries: list[Entry], today: date,
                  watchlist: list[Watched] | None = None,
                  history: list[Event] | None = None) -> dict:
    active = [e for e in entries if not is_archived(e, today)]
    sections = []
    for cat, title in CATEGORY_TITLES.items():
        rows = _ordered(active, cat)
        # Counted here rather than in the template: the "no card" number is the
        # one a reader is actually shopping for, and a section where it equals
        # the row count should say so in those words instead of making them
        # compare two figures.
        no_card = sum(1 for e in rows if not e.card_required)
        sections.append({
            "title": title,
            "rows": [_row(e) for e in rows],
            "count": len(rows),
            "no_card": no_card,
            "all_no_card": bool(rows) and no_card == len(rows),
        })
    connections = [
        {"name": e.name, "base_url": e.api.base_url,
         "page": provider_page_url(e.id),
         "anthropic_base_url": e.api.anthropic_base_url or "",
         "auth": _auth_cell(e),
         "key_url": e.api.key_url or "",
         "keyless": e.api.auth == "none",
         "note": _connection_note(e)}
        for e in _connectable(entries, today)
    ]
    return {**_shared_facts(entries, today, watchlist),
            "sections": sections,
            "archived": _archived_rows(entries, today),
            "connections": connections,
            # The answer to "why isn't X here?", which a list like this is asked
            # more often than anything else. Rendered from the same file the
            # scout filters proposals with, so the page and the machinery can
            # never drift apart.
            "watchlist": _watch_rows(watchlist or [], today),
            # sources.yaml itself is not rendered — the page says how the
            # verdicts work and the file holds them, the way it does for
            # dismissed.yaml.
            "source_recheck_days": SOURCE_RECHECK_DAYS,
            # The only part of this page that is not a statement about today.
            # Everything else is regenerated from scratch each run and remembers
            # nothing, which left "did anything change?" answerable only from
            # git log.
            "changes": _change_rows(history or [], entries, today)}


def build_index(entries: list[Entry], today: date,
                watchlist: list[Watched] | None = None) -> dict:
    return {
        "generated": today.isoformat(),
        "source": REPO_URL,
        "feed": FEED_URL,
        "entries": [
            {**e.model_dump(mode="json", exclude_none=True), "archived": is_archived(e, today),
             **({"archived_because": archive_reason(e, today)} if is_archived(e, today) else {}),
             "page": provider_page_url(e.id)}
            for e in entries
        ],
        # Additive: a consumer reading .entries is unaffected. Here because
        # "considered and not listed, on this date, for this reason" is an answer
        # worth publishing in machine-readable form, not only in the README.
        "watchlist": [
            {**w.model_dump(mode="json"), "current": is_watch_current(w, today)}
            for w in (watchlist or [])
        ],
    }


# The site's own front page. GitHub renders README.md with its own Markdown
# parser; GitHub Pages renders it with kramdown, which does not read Markdown
# inside a block-level <div>, does not know GitHub's alert syntax, and escapes a
# <summary> it meets inside a table cell. The README is written for GitHub and
# stays that way — which is why, served through Jekyll, its whole hero (banner,
# badges, nav, the counters) arrived as literal `[![pipeline](…)]` text, its
# warning as the word "[!WARNING]", and every one of its 117 folded cells as a
# wall of prose.
#
# So the site gets a page of its own: index.html at the repository root, which
# Pages serves in place of the README (jekyll-readme-index only steps in where
# no index exists). It is rendered from the same registry on the same run as
# everything else published here and held to it by `freetier-render --check`, so
# nothing on it is typed by hand and no claim on it can outlive a row.
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
# Shorter than the README's ten: the page shows the changes as cards rather than
# table rows, and the feed is one click away under them.
SITE_CHANGES = 8
# How fresh the floor date reads in words, beside the colour badge_colour gives
# it — a colour alone is not an answer for a reader who cannot see it.
BADGE_WORDS = {BADGE_GREEN: "fresh", BADGE_AMBER: "ageing", BADGE_RED: "stale"}


def _site_fold(text: str) -> dict[str, str]:
    """A long cell as data, not as markup: what the page shows first, and all of
    it. The template decides the markup and escapes both halves, so a vendor's
    own sentence — angle brackets, ampersands and all — is data here, the way it
    is inside the provider pages' `{% raw %}`."""
    if len(text) <= README_LIMITS_COLLAPSE:
        return {"text": text, "teaser": ""}
    return {"text": text, "teaser": f"{_cut(text, README_LIMITS_TEASER)} …"}


def _site_row(e: Entry) -> dict:
    """A row of a section table: the facts, with every judgement already made.

    The same five answers browse.html filters on — card, key, OpenAI-compatible,
    an Anthropic route, a frontier family — because a reader who narrows the
    filterable table and a reader who scans this page are asking one question.
    """
    families = [m for m in e.models if m.superseded_by is None]
    api = e.api
    return {
        "id": e.id,
        "name": e.name,
        "url": e.url,
        "page": provider_page_url(e.id),
        "offering": _site_fold(e.offering),
        "limits": _site_fold(e.limits) if e.limits else None,
        "models": [{"family": m.family, "tier": m.tier.value if m.tier else ""}
                   for m in families],
        "verified": e.last_verified.isoformat(),
        "card": e.card_required,
        "provisional": e.provisional,
        "trains": e.data_use.trains if _trains(e) else "",
        "no_key": bool(api and api.base_url and api.auth == "none"),
        "public_key": bool(api and api.base_url and api.public_key),
        "openai": bool(api and api.base_url and api.openai_compatible),
        "claude_code": bool(api and api.anthropic_base_url),
        "frontier": any(m.tier is Tier.FRONTIER for m in families),
        # A row whose published lane is known not to work says so where it is
        # read, not only on its own page: the notice is the one thing a reader
        # about to copy a base URL needs before the base URL.
        "notice": ({"since": api.notice.since.isoformat(), "text": api.notice.text,
                    "url": api.notice.url or ""} if api and api.notice else None),
    }


def _site_sections(active: list[Entry]) -> list[dict]:
    sections = []
    for cat, title in CATEGORY_TITLES.items():
        rows = _ordered(active, cat)
        emoji, _, name = title.partition(" ")
        no_card = sum(1 for e in rows if not e.card_required)
        sections.append({
            "id": cat.value, "emoji": emoji, "title": name, "short": SITE_NAV_LABELS[cat],
            "rows": [_site_row(e) for e in rows], "count": len(rows),
            "no_card": no_card, "all_no_card": bool(rows) and no_card == len(rows),
        })
    return sections


def _site_connections(connectable: list[Entry]) -> list[dict]:
    """The connection table as data: what to paste, and what the vendor asks
    every request to carry beside it."""
    rows = []
    for e in connectable:
        asks = []
        if e.api.client_user_agent:
            asks.append("your client's own User-Agent")
        if e.api.session_header:
            asks.append(f"{e.api.session_header} per conversation")
        rows.append({
            "name": e.name, "page": provider_page_url(e.id),
            "base_url": e.api.base_url, "anthropic_base_url": e.api.anthropic_base_url or "",
            "keyless": e.api.auth == "none", "env_var": env_var(e.id),
            "public_key": e.api.public_key or "",
            "key_url": e.api.key_url or "", "asks": asks,
            "note": _site_fold(e.api.note) if e.api.note else None,
            "notice": ({"since": e.api.notice.since.isoformat(), "text": e.api.notice.text,
                        "url": e.api.notice.url or ""} if e.api.notice else None),
        })
    return rows


def _site_archived_rows(entries: list[Entry], today: date) -> list[dict]:
    gone = sorted(_archive(entries, today),
                  key=lambda e: (_departure(e), e.name.lower()), reverse=True)
    return [{"name": e.name, "page": provider_page_url(e.id),
             "when": _departure(e).isoformat(), "why": _site_fold(archive_reason(e, today))}
            for e in gone]


def _site_changes(events: list[Event], entries: list[Entry] | None,
                  today: date, limit: int = SITE_CHANGES) -> list[dict]:
    """The same events as the README's table, without its pipe escaping: HTML
    has no cell separator to protect a vendor's sentence from."""
    return [{"date": ev.ts.date().isoformat(), "label": CHANGE_LABELS[ev.event],
             "name": ev.name, "url": _event_link(ev, entries, today),
             "detail": event_detail(ev, entries)}
            for ev in _newest_first(events, limit)]


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
    return json.dumps(graph, ensure_ascii=False, indent=2).replace("<", "\\u003c")


def build_site_context(entries: list[Entry], today: date,
                       watchlist: list[Watched] | None = None,
                       history: list[Event] | None = None) -> dict:
    """Everything index.html shows, derived from the registry the README is.

    The figures, the picks, the quickstart and the rules the page states are
    the README's own (`_shared_facts`). The rows are a second reading of the
    same entries rather than a reshaping of `build_context`'s: that context is
    Markdown — folded cells, backticked ids, escaped pipes — and an HTML page
    that unpicked it would be one renderer's output squeezed through another's,
    which is the very failure this page exists to end.
    """
    active = [e for e in entries if not is_archived(e, today)]
    facts = _shared_facts(entries, today, watchlist)
    return {
        **facts,
        "sections": _site_sections(active),
        "jsonld": _site_jsonld(facts["active_count"], facts["family_count"], today),
        "connections": _site_connections(_connectable(entries, today)),
        "archived": _site_archived_rows(entries, today),
        "changes": _site_changes(history or [], entries, today),
        "providers_url": f"{PAGES_URL}/{PROVIDERS_DIR}/",
        "repo_url": REPO_URL,
    }


def _plain_title(title: str) -> str:
    """The README's section titles lead with an emoji; a text file does not."""
    head, _, rest = title.partition(" ")
    return rest if rest and not head[:1].isalnum() else title


def _llms_line(e: Entry) -> str:
    parts = [e.offering.strip().rstrip(".")]
    parts.append("card required" if e.card_required else "no card")
    if e.data_use is not None:
        parts.append({"yes": "what you send may be used to train models",
                      "opt-out": "what you send may be used to train models unless you opt out",
                      "no": "what you send is not used to train models"}[e.data_use.trains])
    api = e.api
    if api and api.base_url:
        if api.auth == "none":
            parts.append("no key")
        elif api.public_key:
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
        if api.client_user_agent:
            parts.append("every request names its client in its own User-Agent")
        if api.session_header:
            parts.append(f"every request needs a stable id per conversation in `{api.session_header}`")
        if api.anthropic_base_url:
            parts.append(f"Anthropic Messages at {api.anthropic_base_url}")
    fams = _families(e)
    if fams:
        parts.append("free models: " + ", ".join(f"`{f}`" for f in fams))
    if e.provisional:
        parts.append(f"provisional since {e.first_seen.isoformat()}")
    return f"- [{e.name}]({provider_page_url(e.id)}): " + "; ".join(parts)


def build_llms_txt(entries: list[Entry], today: date) -> str:
    """The list as one text file in the llms.txt shape — a title, a summary in a
    blockquote, then sections of links with a note each.

    An LLM answering "is there a free API for X" reads a page the way a
    crawler does, and the README is 60 KB of tables built for eyes; this is
    the same registry in the form that reads best as text, one line per
    offer with what it needs (card, key) and where it answers. Search that
    runs on a model already sends readers here, and this is the page to
    hand it.
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
    for category, title in CATEGORY_TITLES.items():
        rows = _ordered(live, category)
        if not rows:
            continue
        lines += ["", f"## {_plain_title(title)}", ""]
        lines += [_llms_line(e) for e in rows]
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
        f"- [Provider pages]({PAGES_URL}/{PROVIDERS_DIR}/): one page per row, live and archived",
        f"- [Filterable table]({PAGES_URL}/browse.html): the same rows filtered by category, "
        "card, key and API format",
        f"- [configs/opencode.json]({REPO_URL}/blob/main/configs/opencode.json): opencode "
        "config with every OpenAI-compatible row wired up",
        f"- [configs/claude-code.sh]({REPO_URL}/blob/main/configs/claude-code.sh): one shell "
        "function per gateway that serves the Anthropic Messages format, for Claude Code",
        f"- [configs/litellm.yaml]({REPO_URL}/blob/main/configs/litellm.yaml): LiteLLM proxy "
        "config over the same rows"
        + (f", with one-name fallback groups ({', '.join(groups)})" if groups else ""),
        f"- [README]({REPO_URL}): the list itself, with the picks table and how it stays fresh",
        f"- [CONTRIBUTING]({REPO_URL}/blob/main/CONTRIBUTING.md): what qualifies, how rows are "
        "ranked, how the probes work",
    ]
    return "\n".join(lines) + "\n"


def build_opencode_config(entries: list[Entry], today: date) -> dict:
    providers = {}
    for e in _configurable(entries, today):
        options: dict = {"baseURL": e.api.base_url}
        if e.api.auth != "none":
            options["apiKey"] = "{env:" + env_var(e.id) + "}"
        ids = e.api.model_ids or [m.family for m in e.models if m.superseded_by is None]
        models = {mid: {"name": mid} for mid in ids}
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


def _litellm_lanes(entries: list[Entry], today: date) -> list[Entry]:
    """The configurable rows LiteLLM can call. It sends a bearer token on every
    call — `api_key: none` goes out as "Bearer none" — so a keyless lane that
    refuses one (`api.refuses_bearer`) cannot be reached through it at all."""
    return [e for e in _configurable(entries, today) if not e.api.refuses_bearer]


def _litellm_ids(e: Entry) -> list[str]:
    return e.api.model_ids or [m.family for m in e.models if m.superseded_by is None]


def _tier_of_id(e: Entry, model_id: str) -> Tier | None:
    """The measured tier of the family an id belongs to: the most specific of
    the row's families the id names, matched the way the probe matches a family
    against a catalog id (zai-org/GLM-5.3-Flash is glm-5.3-flash, not glm-5.3)."""
    named = [m for m in e.models if m.superseded_by is None
             and family_names(m.family, model_id)]
    best = max(named, key=lambda m: len(_id_squash(m.family)), default=None)
    return best.tier if best else None


def _litellm_key(e: Entry) -> str:
    return "none" if e.api.auth == "none" else f"os.environ/{env_var(e.id)}"


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
    lane of that tier and falls back down the list when they run out — what
    OmniRoute sells as "never stop coding", on lanes this list vouches for. A
    group deployment benches itself after its first failure: a key the reader
    never set fails before any request leaves, and a 429 means that quota is
    spent. A model asked for by name keeps LiteLLM's defaults, because one 429
    on a lone deployment benched with the same policy shut it for the whole
    cooldown (LiteLLM 1.102, 2026-09-21). Each deployment carries a dict of its
    own: a shared one is written as a YAML anchor, and LiteLLM then gives every
    deployment the same id.
    """
    models: list[dict] = []
    groups: dict[str, list[dict]] = {name: [] for name in FREE_GROUPS}
    for e in _litellm_lanes(entries, today):
        for model_id in _litellm_ids(e):
            params = {"model": f"openai/{model_id}", "api_base": e.api.base_url,
                      "api_key": _litellm_key(e)}
            models.append({"model_name": f"{e.id}/{model_id}", "litellm_params": params})
            tier = _tier_of_id(e, model_id)
            names = ([f"free/{tier.value}"] if tier else []) + (
                ["free/nokey"] if e.api.auth == "none" or e.api.public_key else [])
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

    A group is there only while some lane is measured at its tier. On
    2026-09-22 Claude Opus 5.5 took the top of the index to 57.6, no free lane
    stayed within ten points of it, and free/frontier left the config — while
    the config's own header, llms.txt and the configs README went on offering
    it, a name LiteLLM answers with "model not found". Every page that names a
    group reads it from here."""
    names = {d["model_name"] for d in build_litellm_config(entries, today)["model_list"]}
    return [name for name in FREE_GROUPS if name in names]


def _either(names: list[str]) -> str:
    """"a", "a or b", "a, b or c"."""
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]


def _litellm_groups_note(groups: list[str]) -> str:
    """The header's paragraph on the groups, for the ones the file defines."""
    if not groups:
        return ""
    how = (" pools every lane of that tier" if len(groups) == 1 else
           " pool every lane of that tier, and a call falls back down that order when a "
           "lane runs out of quota or has no key set here")
    sentence = (f"Or ask for a group instead of a model: {_either(groups)}{how} — set only "
                "the keys you have, and a lane without one is skipped.")
    lines = textwrap.wrap(sentence, width=73, break_long_words=False, break_on_hyphens=False)
    return "#\n" + "".join(f"# {line}\n" for line in lines)


def build_env_example(entries: list[Entry], today: date) -> str:
    lines = [
        "# Free LLM providers — generated from registry.yaml, do not edit by hand.",
        "# Fill the keys you use, then `source` this file. Every endpoint is",
        "# OpenAI-compatible: point any SDK/agent at the base URL next to the key.",
        "",
    ]
    for e in _connectable(entries, today):
        if e.api.auth == "none":
            lines.append(f"# ── {e.name} — no key needed · base: {e.api.base_url}")
        elif e.api.public_key:
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
        if e.api.session_header:
            lines.append(f"#    header: every request needs a stable id per conversation in "
                         f"{e.api.session_header} — send it from your client")
        if e.api.note:
            lines.append(f"#    note: {e.api.note}")
        lines.append("")
    return "\n".join(lines)


def _anthropic_ready(entries: list[Entry], today: date) -> list[Entry]:
    """Every live row that publishes an Anthropic-format route, in rank order —
    card-required rows included, since the file is a menu rather than a
    recommendation and the card is stated beside the name."""
    return sorted(
        (e for e in entries
         if not is_archived(e, today) and e.api and e.api.anthropic_base_url),
        key=_by_rank,
    )


def build_claude_code_sh(entries: list[Entry], today: date) -> str:
    """One shell function per gateway that serves the Anthropic Messages
    format, so `source configs/claude-code.sh` and `claude-<id>` runs Claude
    Code on that lane. Functions rather than exports because only one gateway
    can be current: a file of exports would leave the last block winning
    silently, while a function scopes the four variables to one invocation —
    the shape Vercel's own docs recommend. ANTHROPIC_API_KEY is emptied on
    purpose in every block: Claude Code reads it before ANTHROPIC_AUTH_TOKEN,
    and a stale value there wins. The key comes from the same variable
    free-llm.env.example declares, so the two files are one setup.

    The model is the first id the row lists, which on a rotating lane is the
    registry's own order; a row that lists none leaves ANTHROPIC_MODEL to the
    reader and says so."""
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
        "",
    ]
    for e in ready:
        card = " · card required" if e.card_required else ""
        key_hint = f" · get a key: {e.api.key_url}" if e.api.key_url else ""
        lines.append(f"# ── {e.name}{card}{key_hint}")
        if not e.api.model_ids:
            lines.append("#    the row lists no callable id: pass ANTHROPIC_MODEL=<a free id> "
                         "before the function, or set it inside")
        else:
            lines.append(f"#    free ids: {', '.join(e.api.model_ids)}")
        lines.append(f"claude-{e.id}() {{")
        lines.append(f'  ANTHROPIC_BASE_URL="{e.api.anthropic_base_url}" \\')
        if e.api.auth == "none":
            lines.append('  ANTHROPIC_AUTH_TOKEN="none" \\')
        else:
            lines.append(f'  ANTHROPIC_AUTH_TOKEN="${env_var(e.id)}" \\')
        lines.append('  ANTHROPIC_API_KEY="" \\')
        if e.api.model_ids:
            lines.append(f'  ANTHROPIC_MODEL="{e.api.model_ids[0]}" \\')
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


def _page_description(e: Entry) -> str:
    """The <meta> description: the offer first, then the figures, cut at a word."""
    offer = e.offering.strip()
    if offer and offer[-1] not in ".!?":
        offer += "."
    text = " ".join(f"{offer} {e.limits}".split())
    return text if len(text) <= 300 else text[:297].rsplit(" ", 1)[0] + "…"


def _connect_section(e: Entry) -> list[str]:
    out = ["## Connect", ""]
    if e.api and e.api.base_url:
        out.append(f"- Base URL: `{e.api.base_url}`"
                   + ("" if e.api.openai_compatible else " (not OpenAI-shaped)"))
        if e.api.auth == "none":
            out.append("- Key: none — the lane is anonymous")
        else:
            key = f"- Key: `{env_var(e.id)}`"
            if e.api.public_key:
                key += (f" — no account needed: the vendor prints one for anyone at "
                        f"<{e.api.key_url}>, `{e.api.public_key}`")
            elif e.api.key_url:
                key += f" — get one at <{e.api.key_url}>"
            out.append(key)
        if e.api.client_user_agent:
            out.append("- User-Agent: your client's own name and version, such as `my-coding-agent/1.0` — not an "
                       "SDK's or an HTTP library's, which the vendor asks clients not to send")
        if e.api.session_header:
            out.append(f"- Session header: `{e.api.session_header}` — a stable id per "
                       "conversation on every request, which the calling client sends itself; "
                       "the generated LiteLLM and opencode configs leave this row out")
        if e.api.anthropic_base_url:
            out.append(f"- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): "
                       f"`{e.api.anthropic_base_url}`")
        if e.api.model_ids:
            out.append("- Callable ids: " + ", ".join(f"`{i}`" for i in e.api.model_ids))
        if e.api.note:
            out.append(f"- Note: {e.api.note}")
    else:
        out.append("No API endpoint to paste: this row is a tool you install or sign in to.")
    return out + [""]


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
        # A page-keywords row can carry its whole anchor in the page's data —
        # trae's plan blob, Upstage's client-rendered heading — and this line
        # named `keywords` alone, so those two rows published "anchored on "
        # and stopped. Where the evidence lives is part of the evidence.
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

    The render records a change before it writes the page, so the newest line
    is the commit's own. Until 2026-09-24 only the scheduled run recorded, and
    the page guessed at the line it would write — Cline, back on 2026-09-14,
    read "Delisted" as its newest event under a header that said live.
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

    Two rows named Xiaomi's coding agent from the list's first day — `mimocode`,
    a placeholder at a domain that publishes no site, and `mimo-code`, the row
    with the README, the models and the shutdown date. A row is never deleted,
    and this id is a published URL, so the page stays and says what it is. What
    it does not do is repeat the offer, the limits or the evidence: one service
    is described in one place, and a claim nothing ever verified is not
    published a second time as though the list had stood behind it.
    """
    name = holder.name if holder else e.duplicate_of
    page = provider_page_url(e.duplicate_of)
    out = [_front_matter({"layout": "default",
                          "title": f"{e.name}: the same project as {name}",
                          "description": f"{e.name} and {name} are one project. The list carried "
                                         f"it twice and now keeps one row: the free tier, the "
                                         f"evidence and the history are on the {name} page.",
                          "permalink": f"/{PROVIDERS_DIR}/{e.id}/"}),
           "{% raw %}", "", f"# {e.name}", "",
           " · ".join([CATEGORY_TITLES[e.category],
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
            f"machinery are at <{REPO_URL}>.", "", "{% endraw %}", ""]
    return "\n".join(out)


def build_provider_page(e: Entry, events: list[Event], today: date, blocked: bool = False,
                        registry: list[Entry] | None = None) -> str:
    """One page per row on the Pages site, in the row's own words.

    It exists for the reader who arrives with a question about one vendor and
    for the crawler that indexes that question: a title that names the vendor,
    the tier and the date, a description that carries the figures, and a body
    that is the row — offer, models, limits quoted from the vendor, connection
    details, the evidence the probe reads, the row's history. Nothing here is
    typed; it is rendered from the registry and the history on every run, and
    since a row never leaves the registry its page stays too, as an archived one.

    The body sits inside {% raw %}: GitHub Pages builds this with Jekyll, and
    a vendor sentence with two braces in it would otherwise fail the whole
    site's build, quietly, with the previous deploy still serving.

    An archived row's page is an epitaph, not instructions: what it offered,
    why it left, the evidence and the history — no connection details, no
    provisional flag, no claim that a probe re-reads a row none reads. On a
    blocklisted domain (`blocked`) it names the service as text and links
    nowhere near it: one of those pages plants instructions for AI agents.

    A row folded into another is a page of its own kind, `build_folded_page`:
    one service is described in one place, and this one points at it.
    """
    if e.duplicate_of is not None:
        return build_folded_page(e, events, today, folded_into(registry or [], e))
    archived = is_archived(e, today)
    verified = e.last_verified.isoformat()
    if archived:
        title = f"{e.name} free tier (archived): what it offered, and why it left the list"
    else:
        title = f"{e.name} free tier: limits, free models, verified {verified}"
    out = [_front_matter({"layout": "default", "title": title,
                          "description": _page_description(e),
                          "permalink": f"/{PROVIDERS_DIR}/{e.id}/"}),
           "{% raw %}", "", f"# {e.name}", ""]
    flags = [CATEGORY_TITLES[e.category]]
    flags.append("card required" if e.card_required else "no card")
    if e.provisional and not archived:
        promote = e.first_seen + timedelta(days=PROVISIONAL_PROMOTE_DAYS)
        flags.append(f"provisional — added on {e.first_seen.isoformat()}, a regular row from "
                     f"the first probe it passes on or after {promote.isoformat()}")
    if archived:
        flags.append(f"**archived** — {archive_reason(e, today)}")
    else:
        live = f"**live** — last verified by a probe on {verified}"
        if e.probe_failures:
            # A row mid-failure used to be indistinguishable from a row the
            # scheduler happened to reach later: trae and inception-labs sat on
            # the front page reading 2026-09-07 beside rows reading 2026-09-10,
            # with nothing anywhere saying their probe had stopped finding the
            # evidence. The count is the part a reader cannot infer from the
            # date, and it is also the countdown.
            n = e.probe_failures
            misses = ("the probe since has not found that evidence" if n == 1
                      else f"the {n} probes since have not found that evidence")
            live += f"; {misses}, and {ARCHIVE_AFTER_FAILURES} misses in a row archive the row"
        flags.append(live)
    site = f"`{domain_of(e.url)}`" if blocked else f"[{domain_of(e.url)}]({e.url})"
    out.append(" · ".join(flags) + f" · {site} · [back to the whole list]({PAGES_URL}/)")
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
        out += ["", f"> ⚠️ **Does not work as published since {_notice_since(e.api.notice)}.** "
                    f"{e.api.notice.text}"]
    out += ["", "## What it offered" if archived else "## What you get", "", e.offering, ""]
    fams = live_families(e)
    if archived:
        named = "The row named no free model."
    elif e.probe.type is ProbeType.PAGE_KEYWORDS:
        named = ("The page this row is verified against names no free model, so the column stays "
                 "empty; callable ids, where the row has them, are under Connect.")
    else:
        named = ("The row names no free model family; the ids its lane serves, where the row has "
                 "them, are under Connect.")
    out += ["## Free models it listed" if archived else "## Free models", "",
            ", ".join(f"`{f}`" for f in fams) if fams else named, ""]
    out += ["## Limits, in the vendor's words", "",
            e.limits if e.limits else "The vendor publishes no figure for this tier.", ""]
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
            f"{standing}; the full list, the Atom feed and the machinery are at <{REPO_URL}>.",
            "", "{% endraw %}", ""]
    return "\n".join(out)


def build_providers_index(entries: list[Entry], today: date) -> str:
    """The page that links every provider page — live rows first, in section
    order, the archive after — so a crawler that lands anywhere finds the rest."""
    out = [_front_matter({"layout": "default",
                          "title": "Every free LLM API and coding agent on the list, with its evidence",
                          "description": "One page per provider: the free tier in the vendor's own "
                                         "words, connection details, the evidence a live probe reads "
                                         f"{_schedule()}, and the row's history.",
                          "permalink": f"/{PROVIDERS_DIR}/"}),
           "{% raw %}", "", "# Every provider, one page each", "",
           f"Each page is generated from the same registry as [the list]({PAGES_URL}/); a live "
           f"row is re-verified {_schedule()}, and an archived one says why it left.", ""]
    live = [e for e in entries if not is_archived(e, today)]
    archived = _archive(entries, today)
    out += ["| Provider | Section | Free models | Last verified |", "|---|---|---|---|"]
    for cat, title in CATEGORY_TITLES.items():
        for e in _ordered(live, cat):
            fams = ", ".join(f"`{f}`" for f in live_families(e)) or "—"
            out.append(f"| [{e.name}]({provider_page_url(e.id)}) | {title} | {fams} "
                       f"| `{e.last_verified.isoformat()}` |")
    if archived:
        out += ["", "## Archived", "", "| Provider | Why it left |", "|---|---|"]
        for e in sorted(archived, key=lambda e: (_departure(e), e.name.lower()), reverse=True):
            why = archive_reason(e, today).replace("|", r"\|")
            out.append(f"| [{e.name}]({provider_page_url(e.id)}) | {why} |")
    out += ["", "{% endraw %}", ""]
    return "\n".join(out)


CHECKED_PAGE = "checked"


def checked_page_url() -> str:
    return f"{PAGES_URL}/{PROVIDERS_DIR}/{CHECKED_PAGE}/"


def build_checked_page(watchlist: list[Watched], today: date) -> str:
    """Every service checked and not listed, with its reason and what would
    change the answer — the watchlist as a page of its own.

    It used to be a collapsed table at the foot of the README, and by 2026-09-16
    it was 108 KB of that page's 260 KB: 140 verdicts under a list of 60 offers,
    loaded by everyone who opened the README for the list. A reader who wants to
    know why a service is missing follows one link to it; the README stays the
    list."""
    rows = _watch_rows(watchlist, today)
    out = [_front_matter({"layout": "default",
                          "title": "Services checked and not listed on the free AI coding list",
                          "description": "Every service this list checked and did not list, with the "
                                         "reason on the date it was read and what would change the answer.",
                          "permalink": f"/{PROVIDERS_DIR}/{CHECKED_PAGE}/"}),
           "{% raw %}", "", "# Checked and not listed", "",
           f"{len(rows)} services whose free tier [the list]({PAGES_URL}/) could not find or could not "
           "verify on the date checked. Nothing here is disqualified — domains rejected for cause are "
           f"in [`blocklist.yaml`]({REPO_URL}/blob/main/blocklist.yaml) — and each verdict expires after "
           f"{WATCH_RECHECK_DAYS} days and is asked again. The records live in "
           f"[`watchlist.yaml`]({REPO_URL}/blob/main/watchlist.yaml).", "",
           "| Service | Why it is not on the list | Checked |", "|---|---|---|"]
    for w in rows:
        reopen = f" <sub>**Reopens if:** {w['reopen_if']}</sub>" if w["reopen_if"] else ""
        stale = "" if w["current"] else " ⏰"
        out.append(f"| **{w['name']}** | {w['reason']}{reopen} | `{w['checked_on']}`{stale} |")
    out += ["", f"<sub>⏰ — the verdict is older than {WATCH_RECHECK_DAYS} days, no longer suppresses "
                "anything, and is due for a fresh look.</sub>", "", "{% endraw %}", ""]
    return "\n".join(out)


def _watchlist_beside(registry_path: Path, watchlist_path: Path | None) -> list[Watched]:
    """The watchlist that belongs to this registry — its sibling unless told
    otherwise. Missing file means an empty list, so a caller that has no
    watchlist (tests, a bare registry) renders exactly as it did before."""
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


def _markdown_env(template_dir: Path) -> Environment:
    """The environment of the pages GitHub renders: no autoescaping, because
    every cell is Markdown the template composes from the registry, and a key
    the context lacks is a render error rather than an empty cell."""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # The quickstart's caveat is the lane's own api note, and Kilo's ran to 600
    # characters under the curl. The site prints the note whole in a paragraph
    # of its own; the README folds it like the connection notes, and keeps the
    # sentence in the context so the two pages read the same registry field.
    env.filters["fold_note"] = lambda text: _fold(text, README_NOTE_TEASER,
                                                  README_NOTE_COLLAPSE, small=True)
    # A list of names as a sentence of code spans: "`a`", "`a` or `b`".
    env.filters["either_code"] = lambda names: _either([f"`{n}`" for n in names])
    return env


def _github_page_context(registry_path: Path, today: date,
                         watchlist_path: Path | None) -> dict:
    entries, history = load_registry(registry_path), _history_beside(registry_path)
    # The page is where a deleted row would quietly disappear from.
    refuse_deleted_rows(entries, history)
    return build_context(entries, today, _watchlist_beside(registry_path, watchlist_path),
                         history)


def render_readme(registry_path: Path, template_dir: Path, out_path: Path,
                  today: date | None = None, watchlist_path: Path | None = None) -> str:
    today = today or date.today()
    context = _github_page_context(registry_path, today, watchlist_path)
    text = _markdown_env(template_dir).get_template("README.md.j2").render(**context)
    out_path.write_text(text, encoding="utf-8")
    return text


def render_configs_readme(registry_path: Path, template_dir: Path, out_path: Path,
                          today: date | None = None, watchlist_path: Path | None = None) -> str:
    """configs/README.md — the connection table, beside the files it describes.

    Base URL, key name and the notes that matter for every live OpenAI-compatible
    API: 34 KB of the README's 161 on 2026-09-20, read by someone who has already
    decided, while the README's job is the visitor who has not. GitHub renders a
    folder's README under its file list, so the table now sits next to the four
    configs generated from the same rows, and every link in it is written from
    there. It is rendered from the README's own context, so the two pages cannot
    disagree about a lane, and checked and committed like everything else.
    """
    today = today or date.today()
    context = _github_page_context(registry_path, today, watchlist_path)
    text = _markdown_env(template_dir).get_template(CONFIGS_TEMPLATE).render(**context)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return text


def render_site(registry_path: Path, template_dir: Path, out_path: Path,
                today: date | None = None, watchlist_path: Path | None = None) -> str:
    """index.html — what the Pages site serves at its root.

    Autoescaping is the whole difference from the README's environment: every
    string on this page is a vendor's own sentence, a model id or a URL read out
    of the registry, and the one thing an HTML page must never do is hand a
    reader markup a vendor wrote. The provider pages get the same guarantee from
    `{% raw %}`; here Jinja gives it.
    """
    today = today or date.today()
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        autoescape=True,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    entries, history = load_registry(registry_path), _history_beside(registry_path)
    refuse_deleted_rows(entries, history)
    context = build_site_context(entries, today,
                                 _watchlist_beside(registry_path, watchlist_path), history)
    text = env.get_template(SITE_TEMPLATE).render(**context)
    out_path.write_text(text, encoding="utf-8")
    return text


def render_artifacts(registry_path: Path, root: Path, today: date | None = None,
                     watchlist_path: Path | None = None) -> None:
    """index.json + configs/ + feed.xml — the machine-usable outputs, regenerated
    with the README."""
    today = today or date.today()
    entries = load_registry(registry_path)
    watchlist = _watchlist_beside(registry_path, watchlist_path)
    history = _history_beside(registry_path)
    refuse_deleted_rows(entries, history)
    blocklist = _blocklist_beside(registry_path)
    (root / "feed.xml").write_text(build_feed(history, today, entries=entries), encoding="utf-8")
    # A page per row, and the page of a row that left goes with it: only the
    # .md files this function wrote are ever removed, so a stray file someone
    # drops in the directory is not this function's to delete.
    providers = root / PROVIDERS_DIR
    providers.mkdir(parents=True, exist_ok=True)
    wanted = {"index.md", f"{CHECKED_PAGE}.md"}
    (providers / f"{CHECKED_PAGE}.md").write_text(build_checked_page(watchlist, today),
                                                  encoding="utf-8")
    for e in entries:
        blocked = is_blocked(domain_of(e.url), blocklist)
        (providers / f"{e.id}.md").write_text(
            build_provider_page(e, history, today, blocked, registry=entries), encoding="utf-8")
        wanted.add(f"{e.id}.md")
    (providers / "index.md").write_text(build_providers_index(entries, today), encoding="utf-8")
    for stale in providers.glob("*.md"):
        if stale.name not in wanted:
            stale.unlink()
    (root / "index.json").write_text(
        json.dumps(build_index(entries, today, watchlist), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (root / "llms.txt").write_text(build_llms_txt(entries, today), encoding="utf-8")
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
        "# Run: litellm --config litellm.yaml --host 127.0.0.1\n"
        "# The proxy listens on 0.0.0.0 unless --host says otherwise, and this file\n"
        "# sets no master_key, so without that flag anyone on your network can spend\n"
        "# the keys it reads from the environment (see free-llm.env.example).\n"
        "# Entries marked `api_key: none` need no account at all.\n"
        + _litellm_groups_note(litellm_groups(entries, today))
        + "".join(f"# Left out: {e.name} — every request needs a stable id per conversation "
                  f"in {e.api.session_header}, which a static config cannot supply.\n"
                  for e in _connectable(entries, today) if e.api.session_header)
        + "".join(f"# Left out: {e.name} — its keyless lane answers only a call with no "
                  "Authorization header, and LiteLLM sends one on every call.\n"
                  for e in _configurable(entries, today) if e.api.refuses_bearer)
        + yaml.safe_dump(build_litellm_config(entries, today), sort_keys=False,
                         allow_unicode=True),
        encoding="utf-8")


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
    recorded = record_changes(registry_path, _history_path(registry_path), today,
                              now or datetime.now(timezone.utc), committed=committed)
    render_all(registry_path, template_dir, root, readme_name, today=today,
               watchlist_path=watchlist_path)
    return recorded


def _generated_on(root: Path, today: date) -> date:
    """The day the committed artifacts were rendered on, read back off them.

    Rendering stamps the day into index.json, the feed and every provider
    page's footer, so a straight re-render-and-diff would disagree on the date
    alone — every day, on a repository nobody had touched. Pinning the
    comparison to the date the artifacts themselves carry asks the only
    question worth asking: given the registry as it stands now, is this what
    that day's render produced?
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
    the README, the site's front page, index.json, the feed, llms.txt, the four
    configs and the README beside them, and a page per row. The workflow
    renders after it probes, so a scheduled run heals a forgotten render within
    three days — and for those three days the page, the JSON an LLM reads and
    the config a reader pastes all advertise a registry that has moved on. CI
    rendered to /tmp, which proved the templates parse and compared nothing.
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
    # render_artifacts deletes the page of a row that left, but only in the
    # directory it wrote; a page left behind in the repository is still served,
    # so the absent half of the comparison counts too.
    stale += [p.relative_to(root).as_posix() for p in (root / PROVIDERS_DIR).glob("*.md")
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
    args = parser.parse_args()
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
            # The remedy is one command and it is the same one every time, so
            # the failure says it rather than leaving a contributor to find it
            # in CONTRIBUTING.
            print("run `TZ=UTC uv run freetier-render` and commit what it writes")
            raise SystemExit(1)
        return
    recorded = render_repository(args.registry, args.templates, root, args.out.name,
                                 watchlist_path=args.watchlist,
                                 committed=committed_log(_history_path(args.registry)))
    for ev in recorded:
        print(f"history: {ev.event.value} {ev.id}")
    print(f"rendered {written}")


if __name__ == "__main__":
    main()
