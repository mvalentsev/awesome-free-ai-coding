"""Post what the history just recorded from the project's own accounts.

A post per event — every arrival, archival, return, delisting and model change,
with the row's page — on Bluesky and Mastodon, and a monthly digest article on
Dev.to, from accounts the project owns and labels as bots. Hacker News forbids
automated submissions and Reddit treats them as spam, so those are left to a
person.

A channel gets only what it has not seen (an append-only ledger keyed by event
and channel, so a retried run cannot double-post and a failed post is retried
next time), only recent events, at most a few per run, oldest first, so a
channel enabled late does not replay the whole history. With no channel
configured it says so and exits 0, which is what the workflow expects of it.
Entry point: `freetier-announce` (`main`).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from .history import Event, EventType, jsonl_lines, load_history
from .models import (Entry, access_words, family_access, is_archived, live_families,
                     load_registry, probe_frequency)
from .render import (EVENT_WORDS, REPO_URL, _access_flag, event_detail, picks, provider_page_url,
                     providers_index_url, sections)
from .words import clip

__all__ = ["MAX_AGE_DAYS", "POSTS_PER_RUN", "POST_LIMIT", "Bluesky", "Mastodon", "DevTo",
           "CREDENTIALS", "channels_from_env", "half_configured", "devto_from_env", "compose",
           "event_key", "link_facets", "load_ledger", "append_ledger", "select", "build_digest",
           "digest_key", "run", "main"]

# Older than this and an event is news to nobody: a channel switched on late
# starts from the last two weeks, not from the first line of the log.
MAX_AGE_DAYS = 14
# Per channel, per run; the rest keep until the next run.
POSTS_PER_RUN = 5
# Bluesky's limit, the tightest of the channels, applied to every post so one
# text serves them all.
POST_LIMIT = 300
TIMEOUT = 20.0
UA = {"User-Agent": "freetier-radar/0.2 (announcer; +" + REPO_URL + ")"}

_URL = re.compile(r"https?://[^\s<>()]+")


def event_key(ev: Event) -> str:
    """One string per history line: the run's clock, the kind and the row."""
    return f"{ev.ts.isoformat()}|{ev.event.value}|{ev.id}"


def _listed(prefix: str, names: list[str], room: int) -> str:
    """As many of a row's models as fit in `room` after `prefix`, then how many
    more: a Models column can run to dozens, past the channel's limit."""
    for shown in range(len(names), 0, -1):
        more = len(names) - shown
        line = prefix + ", ".join(names[:shown]) + (f" +{more} more" if more else "")
        if len(line) <= room:
            return line
    return prefix + names[0] + (f" +{len(names) - 1} more" if len(names) > 1 else "")


def compose(ev: Event, entries_by_id: dict[str, Entry], limit: int = POST_LIMIT) -> str:
    """The post: what happened, to whom, in the row's words, and one link.

    The link is the row's own page — the evidence, the limits, the history —
    or the list itself for an id the registry does not hold. The link is never
    cut: the body is what gives way, and a list of models takes at most half of
    the room the lead and the link leave.
    """
    e = entries_by_id.get(ev.id)
    link = provider_page_url(ev.id) if e is not None else REPO_URL

    def half(lead: str) -> int:
        return (limit - len(f"{lead} — .\n → {link}")) // 2

    if ev.event is EventType.ADDED:
        # The models come off the history line, the column a probe reads back:
        # on a row of free models `offering` names none.
        lead = f"New on the free-LLM radar: {ev.name}"
        body = e.offering if e is not None else ev.detail
        tail = (_listed("Free models: ", ev.models, half(lead)) if ev.models
                else "Verified by a live probe")
    elif ev.event is EventType.ARCHIVED:
        lead, body, tail = f"Archived: {ev.name}", ev.detail, "Moved to the list's Archive"
    elif ev.event is EventType.RESTORED:
        lead, body, tail = (f"Back: {ev.name}", ev.detail or "passing its probe again",
                            "Restored to the list")
    elif ev.event is EventType.REMOVED:
        lead, body, tail = (f"Delisted: {ev.name}", event_detail(ev, list(entries_by_id.values())),
                            "Taken off the list by a reviewer")
    else:
        lead = f"{ev.name}: free models changed"
        body = ev.detail
        tail = _listed("Now: ", ev.models, half(lead)) if ev.models else "The row keeps no free model"
    if (e is not None and ev.event in (EventType.ADDED, EventType.MODELS, EventType.RESTORED)
            and (e.access or any(family_access(e, f) for f in ev.models))):
        tail += "; see access conditions"
    fixed = f"{lead} — .\n{tail} → {link}"
    room = limit - len(fixed)
    text_body = clip(body, room) if body and room > 1 else ""
    first = f"{lead} — {text_body}." if text_body else f"{lead}."
    return f"{first}\n{tail} → {link}"


def link_facets(text: str) -> list[dict]:
    """Bluesky rich-text facets for every URL, addressed by UTF-8 byte."""
    facets = []
    for m in _URL.finditer(text):
        start = len(text[:m.start()].encode("utf-8"))
        end = start + len(m.group(0).encode("utf-8"))
        facets.append({"index": {"byteStart": start, "byteEnd": end},
                       "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}]})
    return facets


@dataclass
class Bluesky:
    handle: str
    app_password: str
    pds: str = "https://bsky.social"
    name: str = "bluesky"
    _session: dict | None = field(default=None, repr=False)

    def post(self, client: httpx.Client, text: str, key: str, now: datetime) -> str:
        if self._session is None:
            r = client.post(f"{self.pds}/xrpc/com.atproto.server.createSession",
                            json={"identifier": self.handle, "password": self.app_password},
                            timeout=TIMEOUT)
            r.raise_for_status()
            self._session = r.json()
        record = {"$type": "app.bsky.feed.post", "text": text, "langs": ["en"],
                  "createdAt": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                  "facets": link_facets(text)}
        r = client.post(f"{self.pds}/xrpc/com.atproto.repo.createRecord",
                        headers={"Authorization": f"Bearer {self._session['accessJwt']}"},
                        json={"repo": self._session["did"], "collection": "app.bsky.feed.post",
                              "record": record},
                        timeout=TIMEOUT)
        r.raise_for_status()
        return r.json().get("uri", "")


@dataclass
class Mastodon:
    base_url: str
    token: str
    name: str = "mastodon"

    def post(self, client: httpx.Client, text: str, key: str, now: datetime) -> str:
        # The idempotency key is the event's own: Mastodon keeps it for an hour,
        # so a run retried inside that hour cannot post the same line twice.
        r = client.post(f"{self.base_url.rstrip('/')}/api/v1/statuses",
                        headers={"Authorization": f"Bearer {self.token}", "Idempotency-Key": key},
                        json={"status": text, "visibility": "public", "language": "en"},
                        timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("url") or data.get("uri") or ""


DEVTO_API = "https://dev.to/api/articles"
# Dev.to takes four tags at most.
DIGEST_TAGS = ["ai", "llm", "opensource", "free"]


@dataclass
class DevTo:
    """One article a month, not one per event: the whole list in the
    registry's own words plus what changed last month (see `build_digest`)."""
    api_key: str
    name: str = "devto"

    def publish(self, client: httpx.Client, title: str, body_markdown: str) -> str:
        r = client.post(DEVTO_API,
                        headers={"api-key": self.api_key, "Content-Type": "application/json"},
                        json={"article": {"title": title, "body_markdown": body_markdown,
                                          "published": True, "tags": DIGEST_TAGS,
                                          "series": "Free LLM radar"}},
                        timeout=TIMEOUT)
        r.raise_for_status()
        return r.json().get("url", "")


def devto_from_env(env: dict) -> DevTo | None:
    return DevTo(env["DEVTO_API_KEY"]) if env.get("DEVTO_API_KEY") else None


def digest_key(today) -> str:
    return f"digest|{today:%Y-%m}"


def _previous_month(today):
    first = today.replace(day=1)
    return (first - timedelta(days=1)).replace(day=1), first


def build_digest(entries: list[Entry], events: list[Event], today) -> tuple[str, str]:
    """Title and Markdown for the month: the state of the list, what changed
    last month, every live row with its page. Generated, like the README it
    summarises, so it never names an offer the list stopped backing."""
    active = [e for e in entries if not is_archived(e, today)]
    start, end = _previous_month(today)
    changed = [ev for ev in events if start <= ev.ts.date() < end]
    no_card = sum(1 for e in active if not e.card_required)
    title = (f"Free LLM APIs and coding agents, {today:%B %Y}: {len(active)} verified offers, "
             f"{no_card} without a card")
    out = [
        f"*Generated on {today.isoformat()} from [a registry]({REPO_URL}) that a live probe "
        f"re-verifies {probe_frequency()}. Every offer below is on the list today; the ones it "
        f"carries no more are in the archive, each with why it left. Each name links to the "
        f"row's own page with the vendor's words, the connection details and the evidence.*",
        "",
        f"**{len(active)} live offers · {no_card} ask for no card · one page each at "
        f"{providers_index_url()}**",
        "",
        "## Pick by what you need", "",
        "| I want… | Start with |", "|---|---|",
    ]
    by_name = {e.name: provider_page_url(e.id) for e in entries}
    def names(rows):
        return " · ".join(f"[{r['name']}]({by_name.get(r['name'], r['url'])})"
                          + ("".join(f" `{f}`" for f in r["families"]) if r.get("families") else "")
                          for r in rows)
    p = picks(entries, today)
    for label, key in (("Frontier-tier models on a $0 plan", "frontier"),
                       ("An API key that gets the most done for free", "apis"),
                       ("One key, many free models", "aggregators"),
                       ("No account at all", "keyless"),
                       ("A trial that asks for no card", "trials"),
                       ("Claude Code on a free lane", "claude_code")):
        if p.get(key):
            out.append(f"| **{label}** | {names(p[key])} |")
    out += ["", f"## What changed in {start:%B}", ""]
    if changed:
        for ev in changed:
            line = f"- `{ev.ts.date().isoformat()}` — {EVENT_WORDS[ev.event]}: **{ev.name}**"
            detail = event_detail(ev, entries)
            if detail:
                line += f" — {detail}"
            elif ev.models and ev.event is not EventType.REMOVED:
                line += " — " + ", ".join(ev.models)
            out.append(line)
    else:
        out.append("Nothing moved: every row that was live is still live, and none changed its models.")
    out += ["", "## Every live offer", ""]
    for cat_title, rows in sections(active):
        out += [f"### {cat_title}", "", "| Offer | Free models | Card | Verified |", "|---|---|---|---|"]
        for e in rows:
            fams = ", ".join(f"`{f}`" + _access_flag(e, f) for f in live_families(e)) or "—"
            if e.access:
                fams += f"; {access_words(e.access)}"
            out.append(f"| [{e.name}]({provider_page_url(e.id)}) | {fams} | "
                       f"{'yes' if e.card_required else 'no'} | {e.last_verified.isoformat()} |")
        out.append("")
    out += ["---", "",
            f"The list, the probes, the Atom feed and the generated configs (opencode, LiteLLM, "
            f"Claude Code) are at {REPO_URL}. Know a legal free tier that is missing? Open an issue "
            f"there — it will be probed like everything else.", ""]
    return title, "\n".join(out)


# The two credentials each channel needs, both or neither.
CREDENTIALS = {"bluesky": ("BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"),
               "mastodon": ("MASTODON_BASE_URL", "MASTODON_ACCESS_TOKEN")}


def channels_from_env(env: dict) -> list:
    """A channel exists when both halves of its credentials do; half a
    credential configures nothing (see half_configured)."""
    channels: list = []
    if all(env.get(name) for name in CREDENTIALS["bluesky"]):
        channels.append(Bluesky(env["BLUESKY_HANDLE"], env["BLUESKY_APP_PASSWORD"],
                                env.get("BLUESKY_PDS") or "https://bsky.social"))
    if all(env.get(name) for name in CREDENTIALS["mastodon"]):
        channels.append(Mastodon(env["MASTODON_BASE_URL"], env["MASTODON_ACCESS_TOKEN"]))
    return channels


def half_configured(env: dict) -> list[str]:
    """A line for each channel with one of its two credentials set, which posts
    nothing — said in the run's log, where a mistyped secret would otherwise
    read as a quiet week."""
    return [f"announce: {channel} posts nothing — {have} is set and {lack} is not"
            for channel, pair in CREDENTIALS.items()
            for have, lack in (pair, pair[::-1])
            if env.get(have) and not env.get(lack)]


def load_ledger(path: Path) -> set[tuple[str, str]]:
    """(event key, channel) pairs already posted. Missing file, nothing posted."""
    if not path.exists():
        return set()
    done: set[tuple[str, str]] = set()
    for number, line in jsonl_lines(path.read_text(encoding="utf-8")):
        try:
            row = json.loads(line)
            done.add((row["key"], row["channel"]))
        except Exception as exc:
            raise ValueError(f"{path}: line {number} is not an announcement record: {exc}") from exc
    return done


def append_ledger(path: Path, rows: list[dict]) -> None:
    """Append, never rewrite: a line already posted stays as it was, as in
    history.jsonl."""
    if not rows:
        return
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def select(events: list[Event], done: set[tuple[str, str]], channel: str, now: datetime,
           max_age_days: int = MAX_AGE_DAYS, cap: int = POSTS_PER_RUN) -> list[Event]:
    """What this channel still owes its readers: recent, unposted, oldest first."""
    horizon = now - timedelta(days=max_age_days)
    due = [ev for ev in events
           if ev.ts >= horizon and (event_key(ev), channel) not in done]
    due.sort(key=lambda ev: ev.ts)
    return due[:cap]


def run(history_path: Path, registry_path: Path, ledger_path: Path, env: dict,
        now: datetime | None = None, dry_run: bool = False,
        client: httpx.Client | None = None) -> list[dict]:
    """Post what is due on every configured channel; return the ledger rows written."""
    now = now or datetime.now(timezone.utc)
    channels, devto = channels_from_env(env), devto_from_env(env)
    for line in half_configured(env):
        print(line)
    if not channels and devto is None:
        print("announce: no channel configured (BLUESKY_HANDLE + BLUESKY_APP_PASSWORD, "
              "MASTODON_BASE_URL + MASTODON_ACCESS_TOKEN, DEVTO_API_KEY) — nothing to post")
        return []
    events = load_history(history_path)
    entries = load_registry(registry_path)
    entries_by_id = {e.id: e for e in entries}
    done = load_ledger(ledger_path)
    stamp = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    own = client is None
    client = client or httpx.Client(headers=UA)
    rows: list[dict] = []
    try:
        today = now.astimezone(timezone.utc).date()
        if devto is not None and (digest_key(today), devto.name) not in done:
            title, body = build_digest(entries, events, today)
            if dry_run:
                print(f"announce [devto] would publish: {title}\n{body[:600]}\n")
            else:
                try:
                    where = devto.publish(client, title, body)
                    rows.append({"key": digest_key(today), "channel": devto.name, "ts": stamp,
                                 "where": where})
                    print(f"announce [devto] published: {where}")
                except httpx.HTTPError as exc:
                    print(f"::warning::announce [devto] failed: {exc}")
        for channel in channels:
            for ev in select(events, done, channel.name, now):
                key, text = event_key(ev), compose(ev, entries_by_id)
                if dry_run:
                    print(f"announce [{channel.name}] would post:\n{text}\n")
                    continue
                try:
                    where = channel.post(client, text, key, now)
                except httpx.HTTPError as exc:
                    # Said, not hidden, and left for the next run: the ledger
                    # records only what was posted, so a failed line is retried
                    # for as long as it is recent enough to be worth saying.
                    print(f"::warning::announce [{channel.name}] failed for {ev.id}: {exc}")
                    continue
                row = {"key": key, "channel": channel.name, "ts": stamp, "where": where}
                rows.append(row)
                print(f"announce [{channel.name}] posted {ev.event.value} {ev.id}: {where}")
    finally:
        if own:
            client.close()
    append_ledger(ledger_path, rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Post the recent history events from the "
                                                 "project's own accounts.")
    parser.add_argument("--history", type=Path, default=Path("history.jsonl"))
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--ledger", type=Path, default=Path("announced.jsonl"))
    parser.add_argument("--dry-run", action="store_true",
                        help="compose and print every due post, send nothing, record nothing")
    args = parser.parse_args()
    rows = run(args.history, args.registry, args.ledger, dict(os.environ), dry_run=args.dry_run)
    print(f"announce: {len(rows)} post(s) recorded in {args.ledger}")
