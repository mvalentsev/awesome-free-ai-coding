"""Tell the project's own accounts what the history just recorded.

The list already keeps an append-only log of everything it publishes and an
Atom feed of the same; this is the last step that makes them travel — a post
per event from accounts the project owns, labelled as a bot, on networks whose
API is meant for one. Nothing here goes near a community's front page: Hacker
News forbids automated submissions and Reddit treats them as spam, and a repo
that tried would spend its reputation to gain a ban. Those two are a person's
job. This file's job is the slow, honest half: every arrival, archival and
model change, said once, with the page that carries the evidence.

Three rules keep it from being noise. It posts only what a channel has not
seen (an append-only ledger keyed by event and channel, so a retried run
cannot double-post and a channel that failed is simply retried next time).
It posts only recent events, at most a few per run, oldest first — enabling a
channel a month in must not replay the whole history into a fresh account.
And it posts nothing at all until the credentials exist: with no channel
configured it says so and exits 0, which is what the workflow expects of it.
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

from .history import Event, EventType, load_history
from .models import Entry, is_archived, live_families, load_registry
from .render import CATEGORY_TITLES, PAGES_URL, REPO_URL, picks, provider_page_url

__all__ = ["MAX_AGE_DAYS", "POSTS_PER_RUN", "POST_LIMIT", "Bluesky", "Mastodon", "DevTo",
           "channels_from_env", "devto_from_env", "compose", "event_key", "link_facets",
           "load_ledger", "append_ledger", "select", "build_digest", "digest_key", "run", "main"]

# Older than this and an event is news to nobody: a channel switched on late
# starts from the last two runs, not from the first line of the log.
MAX_AGE_DAYS = 14
# Per channel, per run. A cron that found five things to say in one morning
# has said enough; the rest keep until the next run.
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


def _cut(text: str, room: int) -> str:
    """Cut at a word, mark the cut. `room` is what the fixed parts left over."""
    text = " ".join(text.split())
    if len(text) <= room:
        return text
    if room <= 1:
        return "…"
    cut = text.rfind(" ", 0, room - 1)
    return text[:cut if cut > 0 else room - 1].rstrip(" ,;:.—-") + "…"


def compose(ev: Event, entries_by_id: dict[str, Entry], limit: int = POST_LIMIT) -> str:
    """The post: what happened, to whom, in the row's words, and one link.

    The link is the row's own page — the evidence, the limits, the history —
    and for a row deleted from the registry, which has no page any more, the
    list itself. The link is never cut: the body is what gives way.
    """
    e = entries_by_id.get(ev.id)
    link = provider_page_url(ev.id) if e is not None else REPO_URL
    if ev.event is EventType.ADDED:
        lead, body, tail = (f"New on the free-LLM radar: {ev.name}",
                            e.offering if e is not None else ev.detail,
                            "Verified by a live probe")
    elif ev.event is EventType.ARCHIVED:
        lead, body, tail = (f"Archived: {ev.name}", ev.detail,
                            "The list drops what stops verifying")
    elif ev.event is EventType.RESTORED:
        lead, body, tail = (f"Back: {ev.name}", ev.detail or "passing its probe again",
                            "Restored to the list")
    elif ev.event is EventType.REMOVED:
        lead, body, tail = f"Delisted: {ev.name}", ev.detail, "Removed from the list by hand"
    else:
        lead = f"{ev.name}: free models changed"
        body = ev.detail
        tail = ("Now: " + ", ".join(ev.models)) if ev.models else "The row keeps no free model"
    fixed = f"{lead} — .\n{tail} → {link}"
    room = limit - len(fixed)
    text_body = _cut(body, room) if body and room > 1 else ""
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
        # The idempotency key is the event's own: Mastodon keeps it for hours,
        # so a run retried inside that window cannot post the same line twice.
        r = client.post(f"{self.base_url.rstrip('/')}/api/v1/statuses",
                        headers={"Authorization": f"Bearer {self.token}", "Idempotency-Key": key},
                        json={"status": text, "visibility": "public", "language": "en"},
                        timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("url") or data.get("uri") or ""


DEVTO_API = "https://dev.to/api/articles"
# Dev.to takes four tags at most; these are the ones its readers follow.
DIGEST_TAGS = ["ai", "llm", "opensource", "free"]
PAGE_LABELS_PLAIN: dict[EventType, str] = {
    EventType.ADDED: "Added", EventType.ARCHIVED: "Archived", EventType.RESTORED: "Restored",
    EventType.REMOVED: "Delisted", EventType.MODELS: "Free models changed",
}


@dataclass
class DevTo:
    """One article a month, not one per event: Dev.to is read as a blog, and a
    blog that posts a line every time a model rotates is one nobody follows.
    The article is the whole list in the registry's own words plus what changed
    last month, which is what a search for "free llm api <month> <year>" wants."""
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
        f"re-verifies twice a week. Every offer below passed its probe; the ones that stopped "
        f"passing are in the archive, not here. Each name links to the row's own page with the "
        f"vendor's words, the connection details and the evidence.*",
        "",
        f"**{len(active)} live offers · {no_card} ask for no card · one page each at "
        f"{PAGES_URL}/providers/**",
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
            line = f"- `{ev.ts.date().isoformat()}` — {PAGE_LABELS_PLAIN[ev.event]}: **{ev.name}**"
            if ev.detail:
                line += f" — {ev.detail}"
            elif ev.models:
                line += " — " + ", ".join(ev.models)
            out.append(line)
    else:
        out.append("Nothing moved: every row that was live is still live, and none changed its models.")
    out += ["", "## Every live offer", ""]
    for cat, cat_title in CATEGORY_TITLES.items():
        rows = sorted((e for e in active if e.category is cat), key=lambda e: (e.rank, e.name.lower()))
        if not rows:
            continue
        out += [f"### {cat_title}", "", "| Offer | Free models | Card | Verified |", "|---|---|---|---|"]
        for e in rows:
            fams = ", ".join(f"`{f}`" for f in live_families(e)) or "—"
            out.append(f"| [{e.name}]({provider_page_url(e.id)}) | {fams} | "
                       f"{'yes' if e.card_required else 'no'} | {e.last_verified.isoformat()} |")
        out.append("")
    out += ["---", "",
            f"The list, the probes, the Atom feed and the generated configs (opencode, LiteLLM, "
            f"Claude Code) are at {REPO_URL}. Know a legal free tier that is missing? Open an issue "
            f"there — it will be probed like everything else.", ""]
    return title, "\n".join(out)


def channels_from_env(env: dict) -> list:
    """A channel exists when both halves of its credentials do; half a
    credential is a typo, and a typo must not read as "nothing configured"
    for one channel while the other posts."""
    channels: list = []
    if env.get("BLUESKY_HANDLE") and env.get("BLUESKY_APP_PASSWORD"):
        channels.append(Bluesky(env["BLUESKY_HANDLE"], env["BLUESKY_APP_PASSWORD"],
                                env.get("BLUESKY_PDS") or "https://bsky.social"))
    if env.get("MASTODON_BASE_URL") and env.get("MASTODON_ACCESS_TOKEN"):
        channels.append(Mastodon(env["MASTODON_BASE_URL"], env["MASTODON_ACCESS_TOKEN"]))
    return channels


def load_ledger(path: Path) -> set[tuple[str, str]]:
    """(event key, channel) pairs already posted. Missing file, nothing posted."""
    if not path.exists():
        return set()
    done: set[tuple[str, str]] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            done.add((row["key"], row["channel"]))
        except Exception as exc:
            raise ValueError(f"{path}: line {number} is not an announcement record: {exc}") from exc
    return done


def append_ledger(path: Path, rows: list[dict]) -> None:
    """Append, never rewrite — the same rule as history.jsonl, for the same reason."""
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
