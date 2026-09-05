from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
import respx

from freetier_radar.announce import (
    MAX_AGE_DAYS, POST_LIMIT, POSTS_PER_RUN, Bluesky, Mastodon, channels_from_env, compose,
    event_key, link_facets, load_ledger, run, select,
)
from freetier_radar.history import Event, EventType, append_history
from freetier_radar.models import Entry, save_registry

TODAY = date(2026, 9, 6)
NOW = datetime(2026, 9, 6, 5, 30, tzinfo=timezone.utc)
PAGE = "https://mvalentsev.github.io/awesome-free-ai-coding/providers/"


def entry(**kw) -> Entry:
    d = {"id": "x", "name": "X", "category": "api-free-tier", "url": "https://x.ai",
         "offering": "Free inference on open models, no card",
         "first_seen": date(2026, 9, 1), "last_verified": TODAY,
         "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["x-mini-2"]}}
    return Entry.model_validate({**d, **kw})


def event(kind: EventType, ts: datetime = NOW, **kw) -> Event:
    d = {"ts": ts, "event": kind, "id": "x", "name": "X", "url": "https://x.ai"}
    return Event.model_validate({**d, **kw})


def test_every_kind_of_event_composes_a_post_that_fits_and_links_the_row():
    """The post is the history line in a reader's feed: what happened, to whom,
    and one link to the page that carries the evidence. Bluesky's 300 is the
    tightest limit of the channels, so it is the limit for all of them."""
    by_id = {"x": entry()}
    for kind, words in ((EventType.ADDED, "New on the free-LLM radar"),
                        (EventType.ARCHIVED, "Archived"),
                        (EventType.RESTORED, "Back"),
                        (EventType.MODELS, "free models changed")):
        text = compose(event(kind, detail="3 failed probes", models=["a", "b"]), by_id)
        assert words in text and "X" in text and PAGE + "x/" in text, (kind, text)
        assert len(text) <= POST_LIMIT
    # a row that was deleted has no page any more; the list itself is the link
    gone = compose(event(EventType.REMOVED, id="gone", name="Gone"), by_id)
    assert "Delisted" in gone and "github.com/mvalentsev/awesome-free-ai-coding" in gone


def test_a_long_offer_is_cut_at_a_word_and_the_link_always_survives():
    by_id = {"x": entry(offering="word " * 120)}
    text = compose(event(EventType.ADDED), by_id)
    assert len(text) <= POST_LIMIT
    assert text.endswith(PAGE + "x/")
    assert "…" in text and "wor…" not in text


def test_link_facets_use_utf8_byte_offsets():
    """Bluesky addresses rich text by byte, not by character; a dash before the
    URL is three bytes, and an offset counted in characters would point the
    facet one character short and leave the link dead."""
    text = "New — https://example.org/p/ · done"
    facets = link_facets(text)
    assert len(facets) == 1
    start, end = facets[0]["index"]["byteStart"], facets[0]["index"]["byteEnd"]
    assert text.encode("utf-8")[start:end].decode() == "https://example.org/p/"
    assert facets[0]["features"][0]["uri"] == "https://example.org/p/"


def test_select_takes_the_recent_unannounced_events_oldest_first_and_capped():
    """Enabling a channel a month after the list started must not replay the
    whole history into a new account's feed: only the last MAX_AGE_DAYS count,
    at most POSTS_PER_RUN a run, in the order they happened."""
    old = event(EventType.ADDED, ts=NOW - timedelta(days=MAX_AGE_DAYS + 1), id="old")
    recent = [event(EventType.ADDED, ts=NOW - timedelta(hours=h), id=f"r{h}")
              for h in range(POSTS_PER_RUN + 3)]
    done = {(event_key(recent[-1]), "bluesky")}
    chosen = select([old, *recent], done, "bluesky", NOW)
    assert old not in chosen
    assert recent[-1] not in chosen  # already announced on this channel
    assert len(chosen) == POSTS_PER_RUN
    assert chosen == sorted(chosen, key=lambda ev: ev.ts)
    # the same event is still due on a channel that has not posted it
    assert recent[-1] in select([old, *recent], done, "mastodon", NOW)


def test_no_channel_configured_means_no_post_and_no_ledger(tmp_path: Path):
    reg, hist, ledger = tmp_path / "registry.yaml", tmp_path / "history.jsonl", tmp_path / "announced.jsonl"
    save_registry(reg, [entry()])
    append_history(hist, [event(EventType.ADDED)])
    assert channels_from_env({}) == []
    posted = run(hist, reg, ledger, env={}, now=NOW)
    assert posted == [] and not ledger.exists()


@respx.mock
def test_bluesky_and_mastodon_post_each_event_once_and_the_ledger_remembers(tmp_path: Path):
    reg, hist, ledger = tmp_path / "registry.yaml", tmp_path / "history.jsonl", tmp_path / "announced.jsonl"
    save_registry(reg, [entry(), entry(id="y", name="Y")])
    append_history(hist, [event(EventType.ADDED), event(EventType.ARCHIVED, id="y", name="Y",
                                                         detail="3 failed probes")])
    session = respx.post("https://bsky.social/xrpc/com.atproto.server.createSession").mock(
        return_value=httpx.Response(200, json={"accessJwt": "jwt", "did": "did:plc:abc"}))
    record = respx.post("https://bsky.social/xrpc/com.atproto.repo.createRecord").mock(
        return_value=httpx.Response(200, json={"uri": "at://did:plc:abc/app.bsky.feed.post/1", "cid": "c"}))
    toot = respx.post("https://fosstodon.org/api/v1/statuses").mock(
        return_value=httpx.Response(200, json={"id": "1", "url": "https://fosstodon.org/@radar/1"}))
    env = {"BLUESKY_HANDLE": "radar.bsky.social", "BLUESKY_APP_PASSWORD": "pw",
           "MASTODON_BASE_URL": "https://fosstodon.org/", "MASTODON_ACCESS_TOKEN": "tok"}
    posted = run(hist, reg, ledger, env=env, now=NOW)
    assert len(posted) == 4 and session.call_count == 1 and record.call_count == 2 and toot.call_count == 2
    # the record is what Bluesky needs: repo, collection, a typed record with byte facets
    import json
    body = json.loads(record.calls[0].request.content)
    assert body["repo"] == "did:plc:abc" and body["collection"] == "app.bsky.feed.post"
    assert body["record"]["$type"] == "app.bsky.feed.post" and body["record"]["facets"][0]["index"]["byteStart"] > 0
    assert record.calls[0].request.headers["Authorization"] == "Bearer jwt"
    # Mastodon gets the idempotency key of the event, so a retried run cannot double-post
    assert toot.calls[0].request.headers["Idempotency-Key"] == event_key(event(EventType.ADDED))
    assert toot.calls[0].request.headers["Authorization"] == "Bearer tok"
    assert len(load_ledger(ledger)) == 4
    # a second run has nothing left to say
    assert run(hist, reg, ledger, env=env, now=NOW) == []


@respx.mock
def test_a_channel_that_fails_is_retried_next_run_and_does_not_stop_the_other(tmp_path: Path):
    reg, hist, ledger = tmp_path / "registry.yaml", tmp_path / "history.jsonl", tmp_path / "announced.jsonl"
    save_registry(reg, [entry()])
    append_history(hist, [event(EventType.ADDED)])
    respx.post("https://bsky.social/xrpc/com.atproto.server.createSession").mock(
        return_value=httpx.Response(500))
    toot = respx.post("https://fosstodon.org/api/v1/statuses").mock(
        return_value=httpx.Response(200, json={"id": "1", "url": "https://fosstodon.org/@radar/1"}))
    env = {"BLUESKY_HANDLE": "radar.bsky.social", "BLUESKY_APP_PASSWORD": "pw",
           "MASTODON_BASE_URL": "https://fosstodon.org", "MASTODON_ACCESS_TOKEN": "tok"}
    posted = run(hist, reg, ledger, env=env, now=NOW)
    assert [p["channel"] for p in posted] == ["mastodon"] and toot.call_count == 1
    assert load_ledger(ledger) == {(event_key(event(EventType.ADDED)), "mastodon")}


@respx.mock
def test_a_dry_run_posts_nothing_and_records_nothing(tmp_path: Path, capsys):
    reg, hist, ledger = tmp_path / "registry.yaml", tmp_path / "history.jsonl", tmp_path / "announced.jsonl"
    save_registry(reg, [entry()])
    append_history(hist, [event(EventType.ADDED)])
    route = respx.post(url__regex=r".*").mock(return_value=httpx.Response(200, json={}))
    env = {"MASTODON_BASE_URL": "https://fosstodon.org", "MASTODON_ACCESS_TOKEN": "tok"}
    posted = run(hist, reg, ledger, env=env, now=NOW, dry_run=True)
    assert posted == [] and not route.called and not ledger.exists()
    assert "New on the free-LLM radar: X" in capsys.readouterr().out


def test_channels_need_both_halves_of_their_credentials():
    assert [c.name for c in channels_from_env({"BLUESKY_HANDLE": "h", "BLUESKY_APP_PASSWORD": "p"})] == ["bluesky"]
    assert channels_from_env({"BLUESKY_HANDLE": "h"}) == []
    assert [c.name for c in channels_from_env({"MASTODON_BASE_URL": "https://m.example", "MASTODON_ACCESS_TOKEN": "t"})] == ["mastodon"]
    assert isinstance(channels_from_env({"BLUESKY_HANDLE": "h", "BLUESKY_APP_PASSWORD": "p"})[0], Bluesky)
    assert isinstance(channels_from_env({"MASTODON_BASE_URL": "https://m.example", "MASTODON_ACCESS_TOKEN": "t"})[0], Mastodon)
