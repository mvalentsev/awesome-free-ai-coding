from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timezone
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .history import Event, EventType, archive_reason, load_history
from .models import (ARCHIVE_AFTER_DAYS, SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Category,
                     Entry, ProbeType, Tier, Watched, domain_of, is_archived, is_watch_current,
                     live_families, load_registry, load_watchlist)

__all__ = ["ARCHIVE_AFTER_DAYS", "FEED_ENTRIES", "FEED_URL", "README_CHANGES", "README_PICKS",
           "README_STARTERS",
           "is_archived", "build_context", "build_feed", "build_index",
           "build_opencode_config", "build_env_example", "build_claude_code_sh", "env_var",
           "build_provider_page", "build_providers_index", "provider_page_url", "PAGES_URL",
           "picks",
           "render_readme", "render_artifacts", "main"]

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
# a line and a half of text to save half a line.
README_LIMITS_TEASER = 150
README_LIMITS_COLLAPSE = 260
README_OFFERING_TEASER = 130
README_OFFERING_COLLAPSE = 200
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

# What each event is called where a human reads it. The feed titles stand alone
# in a reader's inbox, so they name the thing that happened; the README labels
# sit in a column beside the name and can be shorter.
FEED_TITLES: dict[EventType, str] = {
    EventType.ADDED: "New: {name}",
    EventType.ARCHIVED: "Archived: {name}",
    EventType.RESTORED: "Back: {name}",
    EventType.REMOVED: "Delisted: {name}",
    EventType.MODELS: "Free models changed: {name}",
}
CHANGE_LABELS: dict[EventType, str] = {
    EventType.ADDED: "➕ Added",
    EventType.ARCHIVED: "📦 Archived",
    EventType.RESTORED: "↩ Restored",
    EventType.REMOVED: "➖ Delisted",
    EventType.MODELS: "🔄 Free models",
}


def _families(e: Entry) -> list[str]:
    return live_families(e)


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
    cut = text.rfind(" ", 0, teaser_at)
    teaser = text[:cut if cut > 0 else teaser_at].rstrip(" ,;:.—-")
    return (f"<details><summary>{open_}{teaser} …{close}</summary>"
            f"{open_}{text}{close}</details>")


def provider_page_url(entry_id: str) -> str:
    return f"{PAGES_URL}/{PROVIDERS_DIR}/{entry_id}/"


def _row(e: Entry) -> dict[str, str]:
    fams = _families(e)
    return {
        "name": e.name,
        "url": e.url,
        "page": provider_page_url(e.id),
        "offering": _fold(e.offering, README_OFFERING_TEASER, README_OFFERING_COLLAPSE),
        "limits": (_fold(e.limits, README_LIMITS_TEASER, README_LIMITS_COLLAPSE, small=True)
                   if e.limits else "<sub>—</sub>"),
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
        "verified": e.last_verified.isoformat(),
        # Backticked, because a model id is something the reader will paste into
        # a config rather than read as prose.
        "models": ", ".join(f"`{f}`" for f in fams) if fams else "—",
    }


def env_var(entry_id: str) -> str:
    return entry_id.removesuffix("-free").replace("-", "_").replace(".", "_").upper() + "_API_KEY"


def _connectable(entries: list[Entry], today: date) -> list[Entry]:
    return sorted(
        (e for e in entries
         if not is_archived(e, today) and e.api and e.api.base_url and e.api.openai_compatible),
        key=lambda e: (e.rank, e.name.lower()),
    )


def _model_index(active: list[Entry]) -> list[dict]:
    """Model family → everyone who serves it free, most-served first.

    Answers the question the per-provider tables cannot: a reader who wants
    `qwen3` does not know, and should not have to scan twenty rows to learn,
    which five entries carry it.
    """
    by_family: dict[str, list[Entry]] = {}
    for e in active:
        for family in _families(e):
            by_family.setdefault(family, []).append(e)
    return [
        {"family": family,
         "providers": [{"name": p.name, "url": p.url}
                       for p in sorted(ps, key=lambda p: (p.rank, p.name.lower()))]}
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
    return [{"name": e.name, "url": e.url, "families": live_families(e)}
            for e in sorted(rows, key=lambda e: (e.rank, e.name.lower()))[:README_STARTERS]]


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
    ranked = [e for e in sorted(active, key=lambda e: (e.rank, e.name.lower()))
              if not e.card_required]

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
        "keyless": [_pick(e) for e in connectable if e.api.auth == "none"][:README_PICKS],
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
            return {"name": e.name, "url": e.url,
                    "base_url": e.api.base_url.rstrip("/"),
                    "model_id": e.api.model_ids[0],
                    "note": e.api.note}
    return None


def _watch_rows(watchlist: list[Watched], today: date) -> list[dict]:
    """Newest verdict first, so the freshest reading is the one a reader meets."""
    return [
        {"name": w.name, "reason": w.reason.strip(), "reopen_if": w.reopen_if.strip(),
         "checked_on": w.checked_on.isoformat(), "current": is_watch_current(w, today)}
        for w in sorted(watchlist, key=lambda w: (-w.checked_on.toordinal(), w.name.lower()))
    ]


def _newest_first(events: list[Event], limit: int) -> list[Event]:
    return sorted(events, key=lambda e: e.ts, reverse=True)[:limit]


def _change_rows(events: list[Event], limit: int = README_CHANGES) -> list[dict]:
    """The tail of the log, newest first, as Markdown table cells.

    Pipes are escaped here rather than rejected in `freetier-check`: an event's
    detail is copied out of an entry's own `offering`, so a pipe in it is a
    perfectly good sentence that only this one table would trip over.
    """
    return [
        {"date": ev.ts.date().isoformat(),
         "label": CHANGE_LABELS[ev.event],
         "name": ev.name,
         "url": ev.url or REPO_URL,
         "detail": ev.detail.replace("|", r"\|") or "—"}
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


def build_feed(events: list[Event], today: date, limit: int = FEED_ENTRIES) -> str:
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
        "as the twice-weekly probes see it.</subtitle>",
        f"  <id>{FEED_URL}</id>",
        f"  <link rel=\"self\" href={quoteattr(FEED_URL)}/>",
        f"  <link rel=\"alternate\" href={quoteattr(REPO_URL)}/>",
        f"  <updated>{_rfc3339(updated)}</updated>",
        "  <author><name>freetier-radar</name></author>",
    ]
    for ev in recent:
        title = FEED_TITLES[ev.event].format(name=ev.name)
        summary = ev.detail or title
        # Only where the list is what the event is about. An entry on its way
        # out carries its last known families too, and appending them to
        # "Delisted" reads as an offer rather than as an epitaph.
        if ev.models and ev.event in (EventType.ADDED, EventType.RESTORED, EventType.MODELS):
            summary += " · free models: " + ", ".join(ev.models)
        out += [
            "  <entry>",
            f"    <id>{escape(_feed_entry_id(ev))}</id>",
            f"    <title>{escape(title)}</title>",
            f"    <link rel=\"alternate\" href={quoteattr(ev.url or REPO_URL)}/>",
            f"    <updated>{_rfc3339(ev.ts)}</updated>",
            f"    <summary type=\"text\">{escape(summary)}</summary>",
            "  </entry>",
        ]
    out.append("</feed>")
    return "\n".join(out) + "\n"


def build_context(entries: list[Entry], today: date,
                  watchlist: list[Watched] | None = None,
                  history: list[Event] | None = None) -> dict:
    active = [e for e in entries if not is_archived(e, today)]
    archived = [e for e in entries if is_archived(e, today)]
    sections = []
    for cat, title in CATEGORY_TITLES.items():
        rows = sorted((e for e in active if e.category is cat),
                      key=lambda e: (e.rank, e.name.lower()))
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
    connectable = _connectable(entries, today)
    connections = [
        {"name": e.name, "base_url": e.api.base_url,
         "anthropic_base_url": e.api.anthropic_base_url or "",
         "auth": "—" if e.api.auth == "none" else f"`{env_var(e.id)}`",
         "key_url": e.api.key_url or "",
         "note": (_fold(e.api.note, README_NOTE_TEASER, README_NOTE_COLLAPSE, small=True)
                  if e.api.note else "")}
        for e in connectable
    ]
    return {"date": today.isoformat(), "sections": sections,
            # The badge dates the evidence, not the render. Using today's date
            # moved it forward whenever the README was regenerated without a
            # probe run — claiming a freshness no entry had. The oldest passing
            # probe among live entries is the honest reading: everything on this
            # page has been confirmed at least this recently.
            "verified_through": min((e.last_verified for e in active),
                                    default=today).isoformat(),
            "archived": [_row(e) for e in archived], "active_count": len(active),
            "has_provisional": any(e.provisional for e in active),
            "connections": connections,
            # The headline counts. Every one of them is derived, so the page can
            # never advertise a number the registry stopped backing.
            "no_card_count": sum(1 for e in active if not e.card_required),
            "card_count": sum(1 for e in active if e.card_required),
            "no_signup_count": sum(1 for e in connectable if e.api.auth == "none"),
            "endpoint_count": len(connections),
            "model_index": _model_index(active),
            "starters": _starters(active),
            "picks": _picks(active, connectable),
            "quickstart": _quickstart(connectable),
            # The answer to "why isn't X here?", which a list like this is asked
            # more often than anything else. Rendered from the same file the
            # scout filters proposals with, so the page and the machinery can
            # never drift apart.
            "watchlist": _watch_rows(watchlist or [], today),
            "watch_recheck_days": WATCH_RECHECK_DAYS,
            # sources.yaml itself is not rendered — the page says how the
            # verdicts work and the file holds them, the way it does for
            # dismissed.yaml.
            "source_recheck_days": SOURCE_RECHECK_DAYS,
            # The only part of this page that is not a statement about today.
            # Everything else is regenerated from scratch each run and remembers
            # nothing, which left "did anything change?" answerable only from
            # git log.
            "changes": _change_rows(history or []),
            "feed_url": FEED_URL,
            "pages_url": PAGES_URL}


def build_index(entries: list[Entry], today: date,
                watchlist: list[Watched] | None = None) -> dict:
    return {
        "generated": today.isoformat(),
        "source": REPO_URL,
        "feed": FEED_URL,
        "entries": [
            {**e.model_dump(mode="json", exclude_none=True), "archived": is_archived(e, today),
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


def build_opencode_config(entries: list[Entry], today: date) -> dict:
    providers = {}
    for e in _connectable(entries, today):
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


def build_litellm_config(entries: list[Entry], today: date) -> dict:
    """LiteLLM proxy config — the same providers, for everything that speaks to
    a proxy rather than to a provider.

    `openai/<id>` is how LiteLLM is told an endpoint is OpenAI-compatible, and
    `api_key: none` is its documented spelling for an endpoint that wants no key
    at all — which several entries here genuinely do not. Aliases are prefixed
    with the entry id because two providers routinely serve the same model id.
    """
    models = []
    for e in _connectable(entries, today):
        ids = e.api.model_ids or [m.family for m in e.models if m.superseded_by is None]
        for model_id in ids:
            models.append({
                "model_name": f"{e.id}/{model_id}",
                "litellm_params": {
                    "model": f"openai/{model_id}",
                    "api_base": e.api.base_url,
                    "api_key": ("none" if e.api.auth == "none"
                                else f"os.environ/{env_var(e.id)}"),
                },
            })
    return {"model_list": models}


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
        else:
            key_hint = f" · get a key: {e.api.key_url}" if e.api.key_url else ""
            lines.append(f"# ── {e.name} — base: {e.api.base_url}{key_hint}")
            lines.append(f'export {env_var(e.id)}=""')
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
        key=lambda e: (e.rank, e.name.lower()),
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
    lines = [
        "# Claude Code on a free lane — generated from registry.yaml, do not edit by hand.",
        "# Each function points Claude Code at a gateway this list verifies twice a week:",
        "# the vendor documents the Anthropic-format route, and the probe confirms it still",
        "# answers. Usage:  source configs/free-llm.env.example  (fill the key you use),",
        "# then  source configs/claude-code.sh  and run the function named after the row,",
        "# e.g. claude-openrouter-free. Works in bash and zsh.",
        "",
    ]
    for e in _anthropic_ready(entries, today):
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


PAGE_LABELS: dict[EventType, str] = {
    EventType.ADDED: "Added to the list",
    EventType.ARCHIVED: "Archived",
    EventType.RESTORED: "Restored",
    EventType.REMOVED: "Delisted",
    EventType.MODELS: "Free models changed",
}


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


def build_provider_page(e: Entry, events: list[Event], today: date) -> str:
    """One page per row on the Pages site, in the row's own words.

    It exists for the reader who arrives with a question about one vendor and
    for the crawler that indexes that question: a title that names the vendor,
    the tier and the date, a description that carries the figures, and a body
    that is the row — offer, models, limits quoted from the vendor, connection
    details, the evidence the probe reads, the row's history. Nothing here is
    typed; it is rendered from the registry and the history on every run, and
    `render_artifacts` deletes the page of a row that leaves.

    The body sits inside {% raw %}: GitHub Pages builds this with Jekyll, and
    a vendor sentence with two braces in it would otherwise fail the whole
    site's build, quietly, with the previous deploy still serving.
    """
    archived = is_archived(e, today)
    verified = e.last_verified.isoformat()
    if archived:
        title = f"{e.name} free tier (archived): what it offered, and when it stopped verifying"
    else:
        title = f"{e.name} free tier: limits, free models, verified {verified}"
    out = [_front_matter({"layout": "default", "title": title,
                          "description": _page_description(e),
                          "permalink": f"/{PROVIDERS_DIR}/{e.id}/"}),
           "{% raw %}", "", f"# {e.name}", ""]
    flags = [CATEGORY_TITLES[e.category]]
    flags.append("card required" if e.card_required else "no card")
    if e.provisional:
        flags.append("provisional — added recently, two weeks of probes still to pass")
    if archived:
        flags.append(f"**archived** — {archive_reason(e, today)}")
    else:
        flags.append(f"**live** — last verified by a probe on {verified}")
    out.append(" · ".join(flags) + f" · [{domain_of(e.url)}]({e.url}) · "
               f"[back to the whole list]({PAGES_URL}/)")
    out += ["", "## What you get", "", e.offering, ""]
    fams = live_families(e)
    out += ["## Free models", "",
            (", ".join(f"`{f}`" for f in fams) if fams
             else "The page this row is verified against names no free model, so the column stays "
                  "empty; callable ids, where the row has them, are under Connect."), ""]
    out += ["## Limits, in the vendor's words", "",
            e.limits if e.limits else "The vendor publishes no figure for this tier.", ""]
    out += ["## Connect", ""]
    if e.api and e.api.base_url:
        out.append(f"- Base URL: `{e.api.base_url}`"
                   + ("" if e.api.openai_compatible else " (not OpenAI-shaped)"))
        if e.api.auth == "none":
            out.append("- Key: none — the lane is anonymous")
        else:
            key = f"- Key: `{env_var(e.id)}`"
            if e.api.key_url:
                key += f" — get one at <{e.api.key_url}>"
            out.append(key)
        if e.api.anthropic_base_url:
            out.append(f"- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): "
                       f"`{e.api.anthropic_base_url}`")
        if e.api.model_ids:
            out.append("- Callable ids: " + ", ".join(f"`{i}`" for i in e.api.model_ids))
        if e.api.note:
            out.append(f"- Note: {e.api.note}")
    else:
        out.append("No API endpoint to paste: this row is a tool you install or sign in to.")
    out += ["", "## Evidence", ""]
    probe = e.probe
    if probe.type is ProbeType.API_MODELS:
        how = f"- Probe: the models catalog at <{probe.endpoint}>"
        if probe.free_marker:
            how += f", free rows carrying `{probe.free_marker}`"
        if probe.require_zero_price:
            how += ", every listed family required at a zero price"
    else:
        how = f"- Probe: the page at <{probe.endpoint}>, anchored on " + ", ".join(
            f"`{k}`" for k in probe.keywords)
        if probe.catalog:
            how += f"; ids checked in <{probe.catalog}>"
    out.append(how)
    for u in e.source_urls:
        out.append(f"- Source: <{u}>")
    out += ["", "## History", ""]
    own = [ev for ev in events if ev.id == e.id]
    if own:
        for ev in reversed(own):
            line = f"- `{ev.ts.date().isoformat()}` — {PAGE_LABELS[ev.event]}"
            if ev.detail:
                line += f": {ev.detail}"
            elif ev.models:
                line += ": " + ", ".join(ev.models)
            out.append(line)
    else:
        out.append("No recorded event yet — the first scheduled run after a row lands writes its "
                   "`added` line.")
    out += ["", "---", "",
            f"Generated from `registry.yaml` on {today.isoformat()} and re-verified twice a week; "
            f"the full list, the Atom feed and the machinery are at <{REPO_URL}>.",
            "", "{% endraw %}", ""]
    return "\n".join(out)


def build_providers_index(entries: list[Entry], today: date) -> str:
    """The page that links every provider page — live rows first, in section
    order, the archive after — so a crawler that lands anywhere finds the rest."""
    out = [_front_matter({"layout": "default",
                          "title": "Every free LLM API and coding agent on the list, with its evidence",
                          "description": "One page per provider: the free tier in the vendor's own "
                                         "words, connection details, the evidence a live probe reads "
                                         "twice a week, and the row's history.",
                          "permalink": f"/{PROVIDERS_DIR}/"}),
           "{% raw %}", "", "# Every provider, one page each", "",
           f"Each page is generated from the same registry as [the list]({PAGES_URL}/) and "
           "re-verified twice a week.", ""]
    live = [e for e in entries if not is_archived(e, today)]
    archived = [e for e in entries if is_archived(e, today)]
    out += ["| Provider | Section | Free models | Last verified |", "|---|---|---|---|"]
    for cat, title in CATEGORY_TITLES.items():
        for e in sorted((e for e in live if e.category is cat),
                        key=lambda e: (e.rank, e.name.lower())):
            fams = ", ".join(f"`{f}`" for f in live_families(e)) or "—"
            out.append(f"| [{e.name}]({provider_page_url(e.id)}) | {title} | {fams} "
                       f"| `{e.last_verified.isoformat()}` |")
    if archived:
        out += ["", "## Archived", "", "| Provider | Last verified | Why |", "|---|---|---|"]
        for e in sorted(archived, key=lambda e: e.name.lower()):
            out.append(f"| [{e.name}]({provider_page_url(e.id)}) | `{e.last_verified.isoformat()}` "
                       f"| {archive_reason(e, today)} |")
    out += ["", "{% endraw %}", ""]
    return "\n".join(out)


def _watchlist_beside(registry_path: Path, watchlist_path: Path | None) -> list[Watched]:
    """The watchlist that belongs to this registry — its sibling unless told
    otherwise. Missing file means an empty list, so a caller that has no
    watchlist (tests, a bare registry) renders exactly as it did before."""
    return load_watchlist(watchlist_path or registry_path.parent / "watchlist.yaml")


def _history_beside(registry_path: Path) -> list[Event]:
    """The change log of this registry, read the same way — a sibling file, and
    missing means nothing has been recorded yet."""
    return load_history(registry_path.parent / "history.jsonl")


def render_readme(registry_path: Path, template_dir: Path, out_path: Path,
                  today: date | None = None, watchlist_path: Path | None = None) -> str:
    today = today or date.today()
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    context = build_context(load_registry(registry_path), today,
                            _watchlist_beside(registry_path, watchlist_path),
                            _history_beside(registry_path))
    text = env.get_template("README.md.j2").render(**context)
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
    (root / "feed.xml").write_text(build_feed(history, today), encoding="utf-8")
    # A page per row, and the page of a row that left goes with it: only the
    # .md files this function wrote are ever removed, so a stray file someone
    # drops in the directory is not this function's to delete.
    providers = root / PROVIDERS_DIR
    providers.mkdir(parents=True, exist_ok=True)
    wanted = {"index.md"}
    for e in entries:
        (providers / f"{e.id}.md").write_text(build_provider_page(e, history, today),
                                              encoding="utf-8")
        wanted.add(f"{e.id}.md")
    (providers / "index.md").write_text(build_providers_index(entries, today), encoding="utf-8")
    for stale in providers.glob("*.md"):
        if stale.name not in wanted:
            stale.unlink()
    (root / "index.json").write_text(
        json.dumps(build_index(entries, today, watchlist), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
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
        "# registry.yaml, do not edit by hand. Run: litellm --config litellm.yaml\n"
        "# Keys come from the environment (see free-llm.env.example); entries\n"
        "# marked `api_key: none` need no account at all.\n"
        + yaml.safe_dump(build_litellm_config(entries, today), sort_keys=False,
                         allow_unicode=True),
        encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--out", type=Path, default=Path("README.md"))
    parser.add_argument("--watchlist", type=Path, default=None,
                        help="defaults to watchlist.yaml beside the registry")
    args = parser.parse_args()
    render_readme(args.registry, args.templates, args.out, watchlist_path=args.watchlist)
    render_artifacts(args.registry, args.out.parent if args.out.parent != Path("") else Path("."),
                     watchlist_path=args.watchlist)
    print(f"rendered {args.out}, index.json, feed.xml, configs/, {PROVIDERS_DIR}/")
