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
from .models import Entry, load_registry
from .render import REPO_URL, provider_page_url

__all__ = ["MAX_AGE_DAYS", "POSTS_PER_RUN", "POST_LIMIT", "Bluesky", "Mastodon",
           "channels_from_env", "compose", "event_key", "link_facets", "load_ledger",
           "append_ledger", "select", "run", "main"]

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
    channels = channels_from_env(env)
    if not channels:
        print("announce: no channel configured (BLUESKY_HANDLE + BLUESKY_APP_PASSWORD, "
              "MASTODON_BASE_URL + MASTODON_ACCESS_TOKEN) — nothing to post")
        return []
    events = load_history(history_path)
    entries_by_id = {e.id: e for e in load_registry(registry_path)}
    done = load_ledger(ledger_path)
    own = client is None
    client = client or httpx.Client(headers=UA)
    rows: list[dict] = []
    try:
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
                row = {"key": key, "channel": channel.name,
                       "ts": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                       "where": where}
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
