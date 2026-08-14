from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timezone
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .history import Event, EventType, load_history
from .models import (ARCHIVE_AFTER_DAYS, WATCH_RECHECK_DAYS, Category, Entry, Watched,
                     is_archived, is_watch_current, live_families, load_registry,
                     load_watchlist)

__all__ = ["ARCHIVE_AFTER_DAYS", "FEED_ENTRIES", "FEED_URL", "README_CHANGES",
           "is_archived", "build_context", "build_feed", "build_index",
           "build_opencode_config", "build_env_example", "env_var",
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
FEED_ENTRIES = 50
README_CHANGES = 10

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


def _row(e: Entry) -> dict[str, str]:
    fams = _families(e)
    return {
        "name": e.name,
        "url": e.url,
        "offering": e.offering,
        "limits": e.limits or "—",
        "card": "💳 Yes" if e.card_required else "✅ No",
        "verified": e.last_verified.isoformat() + (" 🧪" if e.provisional else ""),
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


def _quickstart(connectable: list[Entry]) -> dict | None:
    """The one call a reader can make before deciding to trust any of this:
    keyless, OpenAI-compatible, with a model id the registry knows is callable.

    Generated rather than typed, so the snippet is archived along with its entry
    instead of sitting on the page as a command that stopped working.
    """
    for e in connectable:
        if e.api.auth == "none" and e.api.model_ids:
            return {"name": e.name, "url": e.url,
                    "base_url": e.api.base_url.rstrip("/"),
                    "model_id": e.api.model_ids[0]}
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
    sections = [
        {"title": title,
         "rows": [_row(e) for e in sorted((e for e in active if e.category is cat),
                                          key=lambda e: (e.rank, e.name.lower()))]}
        for cat, title in CATEGORY_TITLES.items()
    ]
    connectable = _connectable(entries, today)
    connections = [
        {"name": e.name, "base_url": e.api.base_url,
         "auth": "—" if e.api.auth == "none" else f"`{env_var(e.id)}`",
         "key_url": e.api.key_url or "", "note": e.api.note}
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
            "no_signup_count": sum(1 for e in connectable if e.api.auth == "none"),
            "endpoint_count": len(connections),
            "model_index": _model_index(active),
            "quickstart": _quickstart(connectable),
            # The answer to "why isn't X here?", which a list like this is asked
            # more often than anything else. Rendered from the same file the
            # scout filters proposals with, so the page and the machinery can
            # never drift apart.
            "watchlist": _watch_rows(watchlist or [], today),
            "watch_recheck_days": WATCH_RECHECK_DAYS,
            # The only part of this page that is not a statement about today.
            # Everything else is regenerated from scratch each run and remembers
            # nothing, which left "did anything change?" answerable only from
            # git log.
            "changes": _change_rows(history or []),
            "feed_url": FEED_URL}


def build_index(entries: list[Entry], today: date,
                watchlist: list[Watched] | None = None) -> dict:
    return {
        "generated": today.isoformat(),
        "source": REPO_URL,
        "feed": FEED_URL,
        "entries": [
            {**e.model_dump(mode="json", exclude_none=True), "archived": is_archived(e, today)}
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
    (root / "feed.xml").write_text(
        build_feed(_history_beside(registry_path), today), encoding="utf-8")
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
    print(f"rendered {args.out}, index.json, feed.xml, configs/")
