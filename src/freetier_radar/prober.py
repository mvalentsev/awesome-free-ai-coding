from __future__ import annotations

import argparse
import asyncio
import html
import json
import re
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path

import httpx

from .models import (
    CHALLENGE_MARKERS, DEAD_MARKERS, NOTICE_HOLD_DAYS, Entry, Follow, ModelFamily, Probe, ProbeType,
    _id_squash, _squash, id_family, names_family, is_archived_for_good, lane_ids, load_registry,
    notice_holds, save_registry,
)

TIMEOUT = httpx.Timeout(20.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.2"}
ATTEMPTS = 3
BACKOFF_SECONDS = 2.0
CONCURRENCY = 8
PROVISIONAL_PROMOTE_DAYS = 14


class ProbeStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"  # page reachable but the free offer is no longer evidenced
    INCONCLUSIVE = "inconclusive"  # could not check: blocked, down, network error
    # Offer verified, but not the Models column: a family its page no longer
    # names, one its catalog no longer serves free beside one it does, or every
    # family superseded.
    STALE_MODELS = "stale-models"
    # Offer and families verified, but a published detail is not backed: the ids
    # against the catalog, the keyless or public-key lane, the Anthropic or Codex
    # route, a public key its page stopped printing, the data-use sentence or the
    # border.
    STALE_IDS = "stale-ids"


@dataclass
class ProbeResult:
    status: ProbeStatus
    detail: str = ""


async def probe_entry(client: httpx.AsyncClient, entry: Entry,
                      attempts: int = ATTEMPTS, backoff: float = BACKOFF_SECONDS,
                      today: date | None = None) -> ProbeResult:
    resp, stop = await _read(client, entry.probe.endpoint, attempts, backoff)
    if stop is not None:
        return stop
    if entry.probe.follow is not None:
        resp, stop = await _read_followed(client, entry, resp, attempts, backoff)
        if stop is not None:
            return stop
    # The vendor's own bytes, for the checks below that read its words back;
    # a catalog read with a free list is checked with the list's marks on it.
    page = resp
    if entry.probe.free_list is not None:
        resp, stop = await _read_free_list(client, entry, resp, attempts, backoff)
        if stop is not None:
            return stop
    detail = check_content(resp, entry)
    # A catalog that still serves one of the row's families free is a live
    # lane: the families it stopped serving are a Models-column note (the
    # words check_content wrote), not a failure. A lane serving none fails.
    column = ""
    if (detail is not None and entry.probe.type is ProbeType.API_MODELS
            and any(family_named(resp, entry, m.family) for m in entry.models)):
        column, detail = detail, None
    if detail is None:
        # A row published as keyless is only as live as a call without a
        # key, and one the vendor prints a key for as a call with that key:
        # its catalog answering says the models exist, not that anyone may
        # call them. A refusal is the offer itself, so it outranks every
        # note below; a note of its own waits for them.
        keyless = None
        if (entry.api and entry.api.key_kind in ("none", "public")
                and entry.api.model_ids):
            keyless = await keyless_lane_verdict(client, entry, attempts, backoff,
                                                 today or date.today())
            if keyless is not None and keyless.status is not ProbeStatus.STALE_IDS:
                return keyless
        # The offer is evidenced. Whether the Models column is, a catalog
        # answered above and a page answers here (see unevidenced_families). A
        # flagged column leads the verdict and the read goes on: every later
        # note follows it after " | ", where the fix prompt looks for the half
        # that is not the model's to repair (see for_a_human).
        unevidenced = unevidenced_families(resp, entry)
        if unevidenced:
            column = "listed families the page does not name: " + ", ".join(unevidenced)

        def verdict(status: ProbeStatus, note: str = "") -> ProbeResult:
            # The keyless or public-key lane's note rides with whatever else
            # the read found, after it.
            if keyless is not None:
                note = f"{note} | {keyless.detail}" if note else keyless.detail
            if column:
                return ProbeResult(ProbeStatus.STALE_MODELS,
                                   f"{column} | {note}" if note else column)
            return ProbeResult(status, note)

        # The row's ids, asked in both directions (see stale_ids): an api-models
        # probe asks the bytes it already has, a page-keywords row the catalog
        # it names in probe.catalog, fetched now. A catalog that does not
        # answer is a note, not a skip: the row stays verified by its page.
        if entry.probe.type is ProbeType.API_MODELS:
            catalog = resp
        elif entry.probe.catalog:
            catalog, failure = await _fetch_catalog(client, entry.probe.catalog, attempts, backoff)
            if catalog is None:
                return verdict(ProbeStatus.STALE_IDS,
                               f"api.model_ids could not be checked: catalog "
                               f"{entry.probe.catalog} {failure}")
        else:
            catalog = None
        if catalog is not None:
            stale = stale_ids(catalog, entry)
            if stale:
                return verdict(ProbeStatus.STALE_IDS, stale)
            gap = codex_endpoint_gap(catalog, entry)
            if gap:
                return verdict(ProbeStatus.STALE_IDS, gap)
        # The Anthropic-format route a row names for Claude Code, asked keyless:
        # the answer is only whether anything listens at that path.
        if entry.api and entry.api.anthropic_base_url:
            missing = await anthropic_route_missing(client, entry, attempts, backoff)
            if missing:
                return verdict(ProbeStatus.STALE_IDS, missing)
        # And the route a keyed row names for Codex CLI, asked the same way; a
        # row without an account was asked Codex's whole request above.
        if entry.api and entry.api.codex and entry.api.key_kind == "own":
            missing = await codex_route_missing(client, entry, attempts, backoff)
            if missing:
                return verdict(ProbeStatus.STALE_IDS, missing)
        # A key handed to everyone is the vendor's only while the vendor's
        # page prints it — see public_key_unprinted.
        if entry.api and entry.api.public_key:
            unprinted = await public_key_unprinted(client, entry, page, attempts, backoff)
            if unprinted:
                return verdict(ProbeStatus.STALE_IDS, unprinted)
        # The data-use sentence (see data_use_moved) and the border (see
        # border_moved) are both read, and both notes kept: one does not answer
        # the other.
        moved = []
        if entry.data_use is not None:
            moved.append(await data_use_moved(client, entry, page, attempts, backoff))
        if entry.border is not None:
            moved.append(await border_moved(client, entry, page, attempts, backoff))
        if any(moved):
            return verdict(ProbeStatus.STALE_IDS, " | ".join(m for m in moved if m))
        if keyless is not None:
            return verdict(keyless.status)
        return verdict(ProbeStatus.PASS)
    # Asked only once the content check has failed, since a live page can carry
    # a <noscript> asking for JavaScript beside the offer. A bot wall means the
    # vendor's page was not seen, not that the offer is gone.
    challenge = challenge_marker_hit(page.text)
    if challenge is not None:
        return ProbeResult(ProbeStatus.INCONCLUSIVE, f'bot challenge: page says "{challenge}"')
    # A failing catalog row still reports its dead ids: this response is the
    # catalog, so asking costs nothing, and a human is about to edit the row.
    # Page rows are repaired or archived whole — see
    # test_a_dead_offer_outranks_a_catalog_check.
    if entry.probe.type is ProbeType.API_MODELS:
        beside = stale_ids(resp, entry)
        if beside:
            detail = f"{detail} | {beside}"
    return ProbeResult(ProbeStatus.FAIL, detail)


async def _ask[A](send: Callable[[], Awaitable[A]], attempts: int, backoff: float,
                  status: Callable[[A], int] = lambda answer: answer.status_code,
                  again: Callable[[A, float], bool] | None = None) -> tuple[A | None, str]:
    """The first answer `send` gets that is the caller's to read, or None and
    why no try got one. Every call the probe makes is patient the same way: a
    network error and a 5xx are asked again after a pause of `backoff` times
    the tries already made, and so is an answer `again` finds worth the next
    pause (a keyless lane's momentary 429); anything else — a 2xx, a 401, a
    404 — is an answer."""
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            answer = await send()
        except httpx.HTTPError as exc:
            # httpx raises a read timeout with no message
            last = f"network error: {str(exc) or type(exc).__name__}"
            continue
        if status(answer) >= 500:
            last = f"HTTP {status(answer)}"
            continue
        if again is not None and i + 1 < attempts and again(answer, backoff * (i + 1)):
            continue
        return answer, ""
    return None, last


async def _read(client: httpx.AsyncClient, url: str, attempts: int, backoff: float,
                named: bool = False) -> tuple[httpx.Response | None, ProbeResult | None]:
    """The page at `url`, or the verdict that reading it already is: a 401, 403
    or 429 is a wall rather than an answer, a 5xx or a network error is asked
    again, and any other 4xx is the page gone. `named` puts the url in the
    verdict, for a page the probe reached through another one."""
    resp, last = await _ask(lambda: client.get(url, timeout=TIMEOUT, follow_redirects=True),
                            attempts, backoff)
    if resp is None:
        where = f"{url} " if named else ""
        return None, ProbeResult(ProbeStatus.INCONCLUSIVE,
                                 f"{where}unreachable after {attempts} attempts: {last}")
    said = f"{url} answered " if named else ""
    if resp.status_code in (401, 403, 429):
        return None, ProbeResult(ProbeStatus.INCONCLUSIVE, f"blocked: {said}HTTP {resp.status_code}")
    if resp.status_code >= 400:
        return None, ProbeResult(ProbeStatus.FAIL, f"page gone: {said}HTTP {resp.status_code}")
    return resp, None


def followed_url(index: object, follow: Follow) -> str | None:
    """The page a JSON index names at `follow.field`, with `follow.suffix` after
    it, or None where the index names no https URL there."""
    value = index
    for part in follow.field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    if not isinstance(value, str) or not value.startswith("https://"):
        return None
    return value.rstrip("/") + follow.suffix


def _index_names(resp: httpx.Response, follow: Follow) -> str | None:
    try:
        return followed_url(resp.json(), follow)
    except ValueError:
        return None


async def _read_followed(client: httpx.AsyncClient, entry: Entry, index: httpx.Response,
                         attempts: int, backoff: float
                         ) -> tuple[httpx.Response | None, ProbeResult | None]:
    """The page the index at the probe's endpoint names today — see Follow. An
    index that names none says where the docs are no more than a timeout does,
    so it is inconclusive; the page it names is read like any endpoint."""
    url = _index_names(index, entry.probe.follow)
    if url is None:
        return None, ProbeResult(ProbeStatus.INCONCLUSIVE,
                                 f"the index at {entry.probe.endpoint} names no page in "
                                 f"{entry.probe.follow.field}")
    return await _read(client, url, attempts, backoff, named=True)


async def _read_free_list(client: httpx.AsyncClient, entry: Entry, catalog: httpx.Response,
                          attempts: int, backoff: float
                          ) -> tuple[httpx.Response | None, ProbeResult | None]:
    """The catalog with the vendor's free marks on it — see join_free_list. A
    list that cannot be read leaves the offer unchecked rather than unmet:
    taken as a list that marks nothing, a bot wall or a changed search format
    would fail every family, and three runs of that archive a live row."""
    url = entry.probe.free_list
    listed, failure = await _fetch_page(client, url, attempts, backoff)
    if listed is not None:
        joined, failure = join_free_list(catalog, listed, entry.probe.lane)
        if joined is not None:
            return joined, None
    return None, ProbeResult(ProbeStatus.INCONCLUSIVE, f"free list {url} {failure}")


def join_free_list_sync(client: httpx.Client, entry: Entry, catalog: httpx.Response
                        ) -> tuple[httpx.Response | None, str]:
    """join_free_list for the scout's synchronous client: the catalog with the
    marks on it, or None and why the list could not be read."""
    url = entry.probe.free_list
    try:
        listed = client.get(url, follow_redirects=True)
    except httpx.HTTPError as exc:
        return None, f"free list {url} unreachable: {exc}"
    if listed.status_code != 200:
        return None, f"free list {url} answered HTTP {listed.status_code}"
    joined, failure = join_free_list(catalog, listed, entry.probe.lane)
    return (joined, "") if joined is not None else (None, f"free list {url} {failure}")


async def probe_page_url(client: httpx.AsyncClient, probe: Probe) -> str:
    """The url whose page a probe's keywords are read against: its endpoint, or
    the page a followed index names today, and the endpoint again where the
    index cannot be read — whatever reads it then says what it found."""
    if probe.follow is None:
        return probe.endpoint
    try:
        resp = await client.get(probe.endpoint, timeout=TIMEOUT, follow_redirects=True)
    except httpx.HTTPError:
        return probe.endpoint
    return _index_names(resp, probe.follow) or probe.endpoint


def probe_page_url_sync(client: httpx.Client, probe: Probe) -> str:
    """probe_page_url for the scout's synchronous client."""
    if probe.follow is None:
        return probe.endpoint
    try:
        resp = client.get(probe.endpoint, follow_redirects=True)
    except httpx.HTTPError:
        return probe.endpoint
    return _index_names(resp, probe.follow) or probe.endpoint


# Never completes: no key, one token, a model id no vendor has. The only
# answer it wants is the status line, and a route that exists says so before it
# reads the body — 401 without a key, 400 or 422 on the model, 429 on a rate
# limit — while a path nothing serves answers 404, 405 or 410.
ANTHROPIC_PROBE_BODY = {"model": "freetier-radar", "max_tokens": 1,
                        "messages": [{"role": "user", "content": "ping"}]}
ROUTE_GONE = (404, 405, 410)


async def anthropic_route_missing(client: httpx.AsyncClient, entry: Entry, attempts: int,
                                  backoff: float) -> str | None:
    """Why the Anthropic-format route a row publishes is not to be trusted, or
    None while it answers. Deliberately shallow — an auth wall's 401 is the
    same 401 a real route gives — because the field is set only where the
    vendor documents the route. A route that cannot be reached is a note, not a
    skip: the row stays verified by its page."""
    url = entry.api.anthropic_base_url.rstrip("/") + "/v1/messages"
    # A model the row publishes, not the placeholder: Fireworks checks the
    # model before the key and answers an unknown one 404, which reads here as
    # a route gone.
    body = ({**ANTHROPIC_PROBE_BODY, "model": entry.api.model_ids[0]}
            if entry.api.model_ids else ANTHROPIC_PROBE_BODY)
    resp, last = await _ask(lambda: client.post(url, json=body,
                                                headers={"anthropic-version": "2023-06-01"},
                                                timeout=TIMEOUT, follow_redirects=True),
                            attempts, backoff)
    if resp is None:
        return f"anthropic route could not be checked: POST {url} {last or 'did not answer'}"
    if resp.status_code in ROUTE_GONE:
        return f"anthropic route gone: POST {url} answered HTTP {resp.status_code}"
    return None


# The request Codex CLI sends a provider under this list's profiles (captured
# from Codex 0.157.1 with the profiles' settings on), cut to one tool and one
# message. Every field is one a lane could refuse — OVHcloud's /responses
# refused `include`, which Codex sends on every call and no setting removes —
# so none is left out, and it asks for the stream Codex reads.
CODEX_PROBE_TOOL = {
    "type": "function", "name": "exec_command", "strict": False,
    "description": "Runs a command in a PTY, returning output or a session ID for ongoing "
                   "interaction.",
    "parameters": {"type": "object", "additionalProperties": False, "required": ["cmd"],
                   "properties": {"cmd": {"type": "string",
                                          "description": "Shell command to execute."}}},
}
# The events that end a Responses stream: only the first ends a turn Codex can
# use.
CODEX_DONE = "response.completed"
CODEX_BROKEN = ("response.failed", "response.incomplete", "error")
# What a read of the stream stops at: "error" is left to the parse, being a
# word any text can hold.
CODEX_STREAM_ENDS = (CODEX_DONE, *CODEX_BROKEN[:2])
# How much of a stream is read before the turn counts as unfinished.
CODEX_READ_CAP = 256 * 1024


def codex_probe_body(model: str) -> dict:
    """The request, asking something no cache has answered before (see
    keyless_probe_body)."""
    conversation = str(uuid.uuid4())
    return {"model": model, "instructions": "You are a coding agent. Answer in one word.",
            "input": [{"type": "message", "role": "user", "content": [
                {"type": "input_text",
                 "text": f"Reply with the word pong. ({uuid.uuid4().hex[:12]})"}]}],
            "tools": [CODEX_PROBE_TOOL], "tool_choice": "auto", "parallel_tool_calls": True,
            "reasoning": {}, "store": False, "stream": True,
            "include": ["reasoning.encrypted_content"],
            "prompt_cache_key": conversation, "client_metadata": {"session_id": conversation}}


def _codex_events(text: str) -> list[str]:
    """The event types a Responses stream carries, in order: the `type` of each
    `data:` line's JSON, since Kilo's gateway sends no `event:` lines."""
    types = []
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        try:
            event = json.loads(line[5:].strip())
        except ValueError:
            continue
        if isinstance(event, dict) and isinstance(event.get("type"), str):
            types.append(event["type"])
    return types


def _codex_completed(answer: tuple[int, str] | str) -> bool:
    """Whether a turn ended the way Codex can use: a 2xx stream reaching
    response.completed with nothing broken before it. A whole JSON response to
    a request for a stream is not one — Codex reads events, not a body."""
    if isinstance(answer, str) or answer[0] >= 300:
        return False
    events = _codex_events(answer[1])
    return CODEX_DONE in events and not any(e in CODEX_BROKEN for e in events)


def _codex_said(answer: tuple[int, str] | str) -> str:
    if isinstance(answer, str):
        return answer
    status, text = answer
    events = _codex_events(text)
    if status < 300:
        return (f"HTTP {status}, a stream ending in {events[-1]}" if events
                else f"HTTP {status} without a Responses stream")
    said = _said(text)
    return f"HTTP {status}" + (f": {said}" if said else "")


async def _codex_call(client: httpx.AsyncClient, url: str, model: str, headers: dict,
                      attempts: int, backoff: float) -> tuple[int, str] | str:
    """One Codex turn's request and the stream it gets, read to its end or to
    CODEX_READ_CAP: (status, text), or why there was none. A 5xx (its stream
    left unread), a network error and a turn that breaks off are asked again.
    Codex CLI asks a broken turn again itself: parse_failed_response makes a
    failed turn's code Retryable unless it names the code, a failed turn with
    no error and an incomplete one become Stream errors, and it retries both
    (openai/codex codex-rs/codex-api/src/sse/responses_error.rs, responses.rs
    and protocol/src/error.rs, read 2026-09-30) — so one broken turn is not a
    lane that stopped taking the request."""
    async def turn() -> tuple[int, str]:
        async with client.stream("POST", url, json=codex_probe_body(model),
                                 headers={**headers, "Accept": "text/event-stream"},
                                 timeout=TIMEOUT, follow_redirects=True) as resp:
            text = ""
            if resp.status_code < 500:
                async for chunk in resp.aiter_text():
                    text += chunk
                    if len(text) > CODEX_READ_CAP or _codex_ended(text):
                        break
            return resp.status_code, text

    def broke_off(answer: tuple[int, str], _pause: float) -> bool:
        return answer[0] < 300 and any(e in CODEX_BROKEN for e in _codex_events(answer[1]))
    answer, last = await _ask(turn, attempts, backoff, status=lambda answer: answer[0],
                              again=broke_off)
    return answer if answer is not None else (last or "did not answer")


def _codex_ended(text: str) -> bool:
    """Whether a stream holds an event that ends it, its line arrived whole.
    The type comes first in the line and the line runs on for the whole
    response — Kilo's response.completed is about 8 KB — so a read that stops
    at the type's chunk keeps half a line no JSON parser reads, and a finished
    turn reads as one that stopped at its last whole event (one read in four
    on 2026-09-29)."""
    return any(at != -1 and "\n" in text[at:]
               for at in (text.find(end) for end in CODEX_STREAM_ENDS))


async def codex_route_missing(client: httpx.AsyncClient, entry: Entry, attempts: int,
                              backoff: float) -> str | None:
    """Why the Responses route a keyed row publishes for Codex CLI is not to be
    trusted, or None while it answers. Read the way anthropic_route_missing
    reads its route, and for its reasons: a keyless call cannot finish a keyed
    lane's turn, a 401 is the route saying it exists, a 404, 405 or 410 is a
    route that is gone, and one that cannot be reached is said so. A keyless
    row is asked the whole request instead (see _codex_drift)."""
    url = entry.api.codex.base_url + "/responses"
    answer = await _codex_call(client, url, entry.api.model_ids[0], {}, attempts, backoff)
    if isinstance(answer, str):
        return f"codex route could not be checked: POST {url} {answer}"
    if answer[0] in ROUTE_GONE:
        return f"codex route gone: POST {url} answered HTTP {answer[0]}"
    return None


# Where a catalog lists the paths it serves each model at: Routeway's
# `endpoints`, LLMTR's `supported_endpoints` (both read 2026-09-29).
CATALOG_ENDPOINT_FIELDS = ("endpoints", "supported_endpoints")


def codex_endpoint_gap(catalog: httpx.Response, entry: Entry) -> str:
    """Why the id a row's Codex profile names cannot take Codex's request by
    its own catalog's word, or "" while nothing says so.

    A vendor's Codex page speaks of its gateway; a catalog that lists the paths
    each model is served at speaks of the model, and it is the more specific
    word: on 2026-09-29 Routeway's page set Codex up on its API while its
    catalog served the row's first free id, muse-glimmer-30b:free, at
    /v1/chat/completions alone. The profile names the first id, and a free lane
    rotates, so the id is asked every run. A catalog that lists no paths for it
    says nothing either way."""
    if not (entry.api and entry.api.codex and entry.api.model_ids):
        return ""
    model = entry.api.model_ids[0]
    for row in _catalog_items(catalog, entry.probe.lane) or []:
        if _model_id(row) != model:
            continue
        for field in CATALOG_ENDPOINT_FIELDS:
            paths = row.get(field)
            if (isinstance(paths, list) and paths and all(isinstance(p, str) for p in paths)
                    and not any(p.rstrip("/").endswith("/responses") for p in paths)):
                return (f"codex profile names {model}, which the catalog serves at "
                        f"{', '.join(paths)} only — put an id it serves at /responses first "
                        "in api.model_ids, or take api.codex out")
        return ""
    return ""


# The smallest chat call there is. What it reads is the status line, whether
# the body is a completion and the model it names, never the message, and one
# token is all it costs the vendor.
KEYLESS_PROBE_BODY = {"max_tokens": 1, "messages": [{"role": "user", "content": "ping"}]}


def keyless_probe_body() -> dict:
    """KEYLESS_PROBE_BODY asking something no cache has answered before: behind
    a host that caches its answers (Pollinations' old host does), a lane whose
    backend had died would go on passing on a stored reply."""
    return {**KEYLESS_PROBE_BODY,
            "messages": [{"role": "user", "content": f"ping {uuid.uuid4().hex[:12]}"}]}
KEYLESS_REFUSED = (401, 403)
# The Authorization header LiteLLM puts on a call to a lane its config marks
# `api_key: none` — the one proxy this list writes a config for, and one that
# sends a bearer token on every call (see ApiInfo.refuses_bearer).
PROXY_BEARER = "Bearer none"
# How many of a keyless row's ids are tried before the run says none answered.
# The first is the README's curl; the next two tell a rate-limited first id from
# a rate-limited lane.
KEYLESS_IDS_TRIED = 3


async def _keyless_call(client: httpx.AsyncClient, url: str, model: str, headers: dict,
                        attempts: int, backoff: float,
                        patient_with_429: bool = False) -> httpx.Response | str:
    """One keyless completion for `model`: the response, or why there was none.
    A 5xx and a network error are retried, and so is a 2xx whose body carries
    a 5xx — OpenRouter's format sends the status line before the first token
    (see _completion), so an upstream's 503 arrives inside a 200; so is a 429
    when the caller is patient with one and the vendor names no longer wait
    than the pause before the next try; every other answer is final."""
    def again(resp: httpx.Response, pause: float) -> bool:
        if resp.status_code == 429:
            return patient_with_429 and _asks_to_wait_at_most(resp, pause)
        return resp.status_code < 300 and _carried_status(resp) >= 500
    resp, last = await _ask(lambda: client.post(url, json={"model": model, **keyless_probe_body()},
                                                headers=headers, timeout=TIMEOUT,
                                                follow_redirects=True),
                            attempts, backoff, again=again)
    return resp if resp is not None else (last or "did not answer")


def _carried_status(resp: httpx.Response) -> int:
    """The status an error in a body names — `error.code` where it is a number,
    as OpenRouter's format gives it — or 0 where the body names none."""
    try:
        error = resp.json().get("error")
    except (ValueError, AttributeError):
        return 0
    code = error.get("code") if isinstance(error, dict) else None
    return code if isinstance(code, int) else 0


def _completion(answer: httpx.Response | str) -> dict | None:
    """The chat completion a 2xx answer carries, or None where it carries none.

    A gateway can say no with a 200. OpenRouter's format, which Kilo's gateway
    answers in too, sends the status before the first token, so a failure
    arrives as an `error` field in the body or as a choice with
    `finish_reason: error`. The content is not read — one token is often
    reasoning with no content yet — only that a choice holds a message and no
    error."""
    if isinstance(answer, str) or answer.status_code >= 300:
        return None
    try:
        body = answer.json()
    except ValueError:
        return None
    if not isinstance(body, dict) or body.get("error"):
        return None
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return None
    choice = choices[0]
    if choice.get("finish_reason") == "error" or not isinstance(choice.get("message"), dict):
        return None
    return body


# The last segment of an id that names no model, only how one is picked:
# Kilo's kilo-auto/free and openrouter/free, BazaarLink's auto:free.
ROUTER_IDS = {"auto", "free"}


def _model_key(model_id: str) -> str:
    """The model an id names, as letters and digits: its last path segment,
    less a :variant tag and a -free or -latest that names no model of its own."""
    name = model_id.lower().rsplit("/", 1)[-1].split(":", 1)[0]
    return re.sub(r"[^a-z0-9]", "", re.sub(r"[-_.](free|latest)$", "", name))


def _answered_as(asked: str, completion: dict) -> str | None:
    """The model a completion names where it is not the one asked, else None.

    The two names are compared by `_model_key`, and one key running on into the
    other is the same model: vendors cut a served name short (LLM Tech answers
    nvidia/Qwen3.8-27B-NVFP4 as qwen38) and add a dated revision, but a size
    or a version that differs is another model. A router id names none, and a completion that names none is
    taken at its word."""
    served = completion.get("model")
    if not isinstance(served, str):
        return None
    want, got = _model_key(asked), _model_key(served)
    if want in ROUTER_IDS or want.startswith(got) or got.startswith(want):
        return None
    return served


def _asks_to_wait_at_most(resp: httpx.Response, seconds: float) -> bool:
    """Whether a 429's Retry-After, if it sends one, is over by `seconds` — the
    pause before the next try. A date, or anything else that is not a number of
    seconds, is read as a wait the run does not make."""
    value = resp.headers.get("retry-after")
    if value is None:
        return True
    try:
        return float(value) <= seconds
    except ValueError:
        return False


async def keyless_lane_verdict(client: httpx.AsyncClient, entry: Entry, attempts: int,
                               backoff: float, today: date) -> ProbeResult | None:
    """Whether a lane this list publishes as keyless still answers without a key,
    or None while its first id does.

    On a row that sets `api.auth: none` the field is the offer: the README's
    zero-signup curl and its "No account at all" answer are built from it, and
    a keyless /v1/models says only that the models exist, not that anyone may
    call them. So the first id in `api.model_ids` gets one completion, one
    token, no Authorization header, and a 2xx carrying a completion is the only
    answer that leaves nothing to say — a 200 without one is a non-answer like
    any other (see `_completion`), and a completion from a model the id does not
    name is a note (see `_answered_as`). A rate limit does not end the offer,
    but it does end the command, so any other answer sends the check on to the
    next id, up to KEYLESS_IDS_TRIED:

    - a later id answering is a note naming it, since the fix is to put it first;
    - every id answering 429 is a note that the lane is rate-limited from here;
    - with no id answering, a 401 or 403 on the first is the vendor asking for a
      key, which FAILs the row — unless the body is a bot wall, which is no
      answer at all. Any other 4xx is about the request rather than the lane
      (vLLM answers 404 for a model id that has rotated out), and it, like a
      lane that could not be reached, is a note beside a row that stays
      verified.

    When the first id answers, a keyless lane is asked the same call again with
    the bearer token LiteLLM sends (see `_bearer_drift`), and either kind is
    asked the request Codex CLI sends (see `_codex_drift`).

    A refusal the list has already owned up to is the one exception: where the
    row carries an `api.notice` that still holds, the maintainer has chosen to
    wait for the vendor's word with a warning on the page, so the refusal is a
    note naming the day the notice stops holding, and past that day it fails
    the row. The day a noticed lane answers again, the run says to take the
    notice down.

    A lane the vendor prints a key for is the same question asked with that
    key: the call carries `api.public_key` (LLM Tech's shared free trial key)
    as a bearer token, and a lane that refuses it — the no-account offer
    ending, or a key the vendor replaced, which only a person reading its page
    can copy — fails the same way."""
    url = entry.api.base_url.rstrip("/") + "/chat/completions"
    # A lane that wants an id per conversation (api.session_header) gets a fresh
    # one in every call, under this project's user agent, as the vendor asks any
    # client to.
    headers = ({entry.api.session_header: str(uuid.uuid4())}
               if entry.api.session_header else {})
    public = entry.api.public_key is not None
    if public:
        headers["Authorization"] = f"Bearer {entry.api.public_key}"
    lane = "public-key" if public else "keyless"
    first_is_read = ("readers are pointed at the first id in api.model_ids" if public
                     else "the README's curl uses the first id in api.model_ids")
    notice = entry.api.notice
    tried: list[tuple[str, httpx.Response | str]] = []
    for model in entry.api.model_ids[:KEYLESS_IDS_TRIED]:
        # LLM7 serves an anonymous caller one request a second, so an id asked
        # the instant the one before it answered is refused for the rate, not for
        # itself: the ids after the first wait the pause the probe takes between
        # tries.
        if tried:
            await asyncio.sleep(backoff)
        # The README's id is asked again after a 429 the way it would be after a
        # 5xx, or an upstream's passing 429 would name a different id to put
        # first on every run. A 429 on the ids after it is final: they only tell
        # a rate-limited first id from a rate-limited lane.
        answer = await _keyless_call(client, url, model, headers, attempts, backoff,
                                     patient_with_429=not tried)
        completion = _completion(answer)
        if completion is not None:
            take_down = (f"take down api.notice of {notice.since.isoformat()}, which tells readers "
                         "the lane does not work") if notice else ""
            served = _answered_as(model, completion)
            swapped = ([f"{lane} call to {model} answered as {served} — the id serves another model "
                        "than it names; read the catalog before the configs keep handing it out"]
                       if served else [])
            if not tried:
                notes = swapped + ([f"{lane} call to {model} answered HTTP {answer.status_code} — "
                                    + take_down] if take_down else [])
                if not public:
                    await asyncio.sleep(backoff)
                    drift = await _bearer_drift(client, entry, url, model, headers, backoff)
                    notes += [drift] if drift else []
                await asyncio.sleep(backoff)
                codex = await _codex_drift(client, entry, model, headers, attempts, backoff)
                notes += [codex] if codex else []
                if not notes:
                    return None
                return ProbeResult(ProbeStatus.STALE_IDS, " | ".join(notes))
            first, first_answer = tried[0]
            moved = (f"{lane} call to {first} answered {_keyless_said(first_answer)} while "
                     f"{model} answered HTTP {answer.status_code} — {first_is_read}, "
                     f"so put {model} first" + (f", and {take_down}" if take_down else ""))
            return ProbeResult(ProbeStatus.STALE_IDS, " | ".join([moved] + swapped))
        tried.append((model, answer))
    first, first_answer = tried[0]
    if isinstance(first_answer, str):
        return ProbeResult(ProbeStatus.STALE_IDS,
                           f"{lane} lane could not be checked: POST {url} {first_answer}")
    if first_answer.status_code in KEYLESS_REFUSED:
        challenge = challenge_marker_hit(first_answer.text)
        if challenge is not None:
            return ProbeResult(ProbeStatus.INCONCLUSIVE,
                               f'bot challenge on the {lane} call: page says "{challenge}"')
        refused = (f"{lane} lane refused: POST {url} "
                   f"{'with api.public_key' if public else 'with no key'} answered "
                   f"HTTP {first_answer.status_code}")
        if notice is None:
            return ProbeResult(ProbeStatus.FAIL, refused)
        ends = (notice.since + timedelta(days=NOTICE_HOLD_DAYS)).isoformat()
        if notice_holds(notice, today):
            return ProbeResult(ProbeStatus.STALE_IDS,
                               f"{refused} — api.notice of {notice.since.isoformat()} holds the "
                               f"row until {ends}")
        return ProbeResult(ProbeStatus.FAIL,
                           f"{refused} — api.notice of {notice.since.isoformat()} stopped holding "
                           f"on {ends}")
    if all(not isinstance(a, str) and a.status_code == 429 for _, a in tried):
        return ProbeResult(ProbeStatus.STALE_IDS,
                           f"{lane} lane rate-limited: " + ", ".join(m for m, _ in tried)
                           + " answered HTTP 429 — "
                           + ("a reader calling it with the key gets 429 too" if public
                              else "the README's curl on this row answers 429 too"))
    return ProbeResult(ProbeStatus.STALE_IDS,
                       f"{lane} call to {first} answered {_keyless_said(first_answer)}")


async def _codex_drift(client: httpx.AsyncClient, entry: Entry, model: str, headers: dict,
                       attempts: int, backoff: float) -> str | None:
    """Whether `api.codex` still says what a lane without an account does,
    asked on the id that has just answered a chat call: the request Codex CLI
    sends, at the Codex base + /responses — the lane's own base where the row
    names none — with the same headers. The whole turn is asked, not the
    route: a route can answer and refuse the request (see CODEX_PROBE_TOOL).

    An answer on a row without the field is a lane Codex could call directly,
    with a profile of its own, and a row with the field that stops taking the
    request hands readers a profile that fails the same way. Asked once where
    the field is not set, since a refusal there is the ordinary answer, and
    patiently where it is, since there a refusal is news. A lane that wants an
    id per conversation in its own header is not asked: no Codex profile could
    send it."""
    if entry.api.session_header:
        return None
    claimed = entry.api.codex is not None
    base = entry.api.codex.base_url if claimed else entry.api.base_url.rstrip("/")
    url = base + "/responses"
    lane = "public-key" if entry.api.public_key else "keyless"
    answer = await _codex_call(client, url, model, headers, attempts if claimed else 1, backoff)
    took = _codex_completed(answer)
    if took and not claimed:
        return (f"{lane} POST {url} took the request Codex CLI sends — set api.codex.base_url "
                f"to {base} and the row gets a Codex profile of its own")
    if claimed and not took:
        if isinstance(answer, str) or answer[0] == 429:
            return f"codex route could not be checked: POST {url} {_codex_said(answer)}"
        return (f"{lane} POST {url} no longer takes the request Codex CLI sends: it answered "
                f"{_codex_said(answer)}, and the row's Codex profile fails the same way")
    return None


async def _bearer_drift(client: httpx.AsyncClient, entry: Entry, url: str, model: str,
                        headers: dict, backoff: float) -> str | None:
    """Whether `api.refuses_bearer` still says what the lane does, asked once on
    the id that has just answered a bare call: the same call, carrying the bearer
    token LiteLLM would send. A refusal on a row without the field, or an answer
    on a row with it, is the note; anything else — a rate limit, an error, a bot
    wall — says nothing about the header either way. A bearer-only payment
    refusal needs a further fresh bare completion: a 402 alone could be the
    anonymous allowance running out between the two calls."""
    answer = await _keyless_call(client, url, model, {**headers, "Authorization": PROXY_BEARER},
                                 1, backoff)
    if isinstance(answer, str):
        return None
    said = f"keyless call to {model} with a bearer token answered HTTP {answer.status_code}"
    refused = answer.status_code in KEYLESS_REFUSED
    if (answer.status_code == 402 and not entry.api.refuses_bearer
            and challenge_marker_hit(answer.text) is None):
        control = await _keyless_call(client, url, model, headers, 1, backoff)
        refused = not isinstance(control, str) and _completion(control) is not None
    if (refused and not entry.api.refuses_bearer
            and challenge_marker_hit(answer.text) is None):
        return (f"{said} — LiteLLM sends one on every call, so set api.refuses_bearer: true to "
                "leave the lane out of its config")
    if _completion(answer) is not None and entry.api.refuses_bearer:
        return f"{said} — drop api.refuses_bearer, and the LiteLLM config takes the lane back"
    return None


async def public_key_unprinted(client: httpx.AsyncClient, entry: Entry, probed: httpx.Response,
                               attempts: int, backoff: float) -> str | None:
    """Why the key a row publishes as the vendor's own is not to be trusted as
    that, or None while the vendor's page still prints it.

    `api.public_key` is the vendor's to hand out only while the vendor's own
    page, `api.key_url`, prints it; otherwise it is a key someone passed around,
    which is key sharing and does not qualify. A key that still works after its
    page stopped printing it may be revoked any day or already replaced, and
    only a person reading the page can fix that, so it is a note beside a row
    its page keeps verified. Where the key's page is the page the probe reads
    it is read once.
    """
    url = entry.api.key_url
    page, failure = await _page_beside(client, url, entry, probed, attempts, backoff)
    if page is None:
        return f"api.public_key could not be checked against {url}: {failure}"
    if entry.api.public_key in page.text:
        return None
    return (f"api.public_key is no longer printed on {url} — read the page for the key it "
            "publishes now")


async def data_use_moved(client: httpx.AsyncClient, entry: Entry, probed: httpx.Response,
                         attempts: int, backoff: float) -> str | None:
    """Why the row's word on training no longer stands, or None while the
    vendor's page still says it.

    The README marks a vendor that may train on what a reader sends, and the
    row's page quotes the sentence the mark rests on. A vendor that rewrites
    that page changes what a reader pays for the free tier, so the sentence is
    read back every run, typography flattened the way freetier-quotes reads
    every quote. A page that cannot be read is said so rather than skipped."""
    from .quotes import page_texts, quote_found  # quotes reads pages through this module
    url = entry.data_use.url
    page, failure = await _page_beside(client, url, entry, probed, attempts, backoff)
    if page is None:
        return f"data_use could not be checked against {url}: {failure}"
    if quote_found(entry.data_use.quote, page_texts(page.text)):
        return None
    return (f"data_use quote is no longer on {url} — read what the vendor says now about "
            "training on what users send")


# How a border note ends: what the reviewer does about it.
BORDER_REREAD = "read the vendor's territory words again"


async def border_moved(client: httpx.AsyncClient, entry: Entry, probed: httpx.Response,
                       attempts: int, backoff: float) -> str | None:
    """Why the row's border no longer reads as it was recorded, or None while it
    does.

    The border rests on the vendor's own list or sentence — Google's region
    list, NVIDIA's list of the countries its phone step refuses, a clause in a
    SaaS agreement — and vendors move them, so it is read back every run the
    way it was read the day it was recorded: every recorded country still named
    on the page and no new one beside them, the quote still there, the codes a
    vendor publishes as data unchanged, the host still not answering from
    inside each country it leaves out. A change is a note beside a row that
    stays verified, never a failure: the offer is still there, and which
    countries it reaches is a reviewer's to reread."""
    from .quotes import page_texts, quote_found  # quotes reads pages through this module
    border = entry.border
    if border.read == "none":
        return None
    if border.read == "dns":
        return await _border_dns(client, entry, attempts, backoff)
    recorded = set(border.served if border.served is not None else border.left_out)
    names = border.read == "page" and bool(recorded)
    if not (border.quote or names or border.read == "codes"):
        # A vendor that names no country, in no sentence the row quotes:
        # there is nothing on its page to hold the border to.
        return None
    url = border.source
    page, failure = await _page_beside(client, url, entry, probed, attempts, backoff)
    if page is None:
        return f"border could not be checked against {url}: {failure}"
    if border.read == "codes":
        listed = _listed_codes(page.text)
        if listed is None:
            return f"border could not be checked against {url}: the answer is no list of codes"
        added, gone = sorted(listed - recorded), sorted(recorded - listed)
        if not added and not gone:
            return None
        said = [f"now lists {', '.join(added)}" if added else "",
                f"no longer lists {', '.join(gone)}" if gone else ""]
        return f"border: {url} {' and '.join(s for s in said if s)} — {BORDER_REREAD}"
    notes = []
    if border.quote and not quote_found(border.quote, page_texts(page.text)):
        notes.append("its quote is gone")
    if names:
        from .countries import codes_named, country_name
        rendered, raw = _country_texts(page.text)
        seen = codes_named(rendered)
        gone = sorted(recorded - seen - codes_named(raw))
        added = sorted(seen - recorded - set(border.also_named))
        if gone:
            notes.append("no longer names " + ", ".join(country_name(c) for c in gone))
        if added:
            notes.append("now also names " + ", ".join(country_name(c) for c in added))
    if not notes:
        return None
    return f"border: {url} — {'; '.join(notes)} — {BORDER_REREAD}"


def _country_texts(body: str) -> tuple[str, str]:
    """A page as country names are read off it: the rendered text and the raw
    body, markup out and entities decoded, capitals kept — "Chad" is a
    country and "chad" is not. A name only in the raw body (a framework's
    payload) still counts as on the page; only the rendered text can add one,
    so a country picker in a script is not a list growing."""
    def plain(text: str) -> str:
        return " ".join(html.unescape(TAG.sub(" ", text)).split())
    return plain(_rendered(body)), plain(body)


def _listed_codes(body: str) -> set[str] | None:
    """A vendor's list of country codes published as data — NVIDIA serves its
    as a JSON array under a .yaml name — or None when the answer is not one."""
    import yaml
    try:
        data = yaml.safe_load(body)
    except yaml.YAMLError:
        return None
    if isinstance(data, dict):
        lists = [v for v in data.values() if isinstance(v, list)]
        data = lists[0] if len(lists) == 1 else None
    if not isinstance(data, list) or not all(isinstance(c, str) for c in data):
        return None
    return {c.strip().upper() for c in data}


async def _border_dns(client: httpx.AsyncClient, entry: Entry, attempts: int,
                      backoff: float) -> str | None:
    """The host still answering 0.0.0.1, or nothing, from inside every country
    the border leaves out, asked of a public resolver on behalf of a subnet in
    each country (DNS_SUBNETS). A real address from one of them is the border
    lifting there."""
    from .countries import DNS_SUBNETS, country_name
    border = entry.border
    lifted, unread = [], []
    for code in border.left_out:
        url = f"{border.source}&edns_client_subnet={DNS_SUBNETS[code]}"
        answer, failure = await _fetch_page(client, url, attempts, backoff)
        if answer is None:
            unread.append(f"{country_name(code)} ({failure})")
            continue
        try:
            records = answer.json().get("Answer") or []
        except ValueError:
            unread.append(f"{country_name(code)} (no DNS answer in the reply)")
            continue
        addresses = sorted({r.get("data", "") for r in records if r.get("type") == 1} - {"0.0.0.1"})
        if addresses:
            lifted.append(f"{country_name(code)} ({', '.join(addresses)})")
    notes = []
    if lifted:
        notes.append(f"border: the host answers from {', '.join(lifted)} now — {BORDER_REREAD}")
    if unread:
        notes.append(f"border could not be checked from {', '.join(unread)}")
    return " | ".join(notes) or None


def _said(text: str) -> str:
    """The start of a body a note quotes, whitespace folded: enough to tell an
    error's words, short enough for one line of the report."""
    return " ".join(text.split())[:160]


def _keyless_said(answer: httpx.Response | str) -> str:
    """A non-answer as the run reports it; a 2xx here is one without a completion."""
    if isinstance(answer, str):
        return answer
    said = _said(answer.text)
    return (f"HTTP {answer.status_code}" + (" without a completion" if answer.status_code < 300 else "")
            + (f": {said}" if said else ""))


async def _fetch_page(client: httpx.AsyncClient, url: str, attempts: int,
                      backoff: float) -> tuple[httpx.Response | None, str]:
    """A second page a row's checks read, or why it could not be read, with the
    patience the probe gives its own endpoint: a 5xx or a network error is
    retried, and any other answer but a 200 is reported."""
    resp, last = await _ask(lambda: client.get(url, timeout=TIMEOUT, follow_redirects=True),
                            attempts, backoff)
    if resp is None:
        return None, f"unreachable after {attempts} attempts: {last}"
    if resp.status_code != 200:
        return None, f"answered HTTP {resp.status_code}"
    return resp, ""


async def _page_beside(client: httpx.AsyncClient, url: str, entry: Entry,
                       probed: httpx.Response, attempts: int,
                       backoff: float) -> tuple[httpx.Response | None, str]:
    """The page a check beside the probe reads at `url`: the page the probe
    has just read where `url` is that page — one read, not two — else
    `_fetch_page`'s, or why it could not be read."""
    if url == entry.probe.endpoint and entry.probe.follow is None:
        return probed, ""
    return await _fetch_page(client, url, attempts, backoff)


async def _fetch_catalog(client: httpx.AsyncClient, url: str, attempts: int,
                         backoff: float) -> tuple[httpx.Response | None, str]:
    """The catalog a page-keywords row names, or why it could not be read. The
    same patience as the page itself, and anything that is not a JSON list of
    models — a 401, a bot wall, an HTML shell — is reported rather than read as
    an empty catalog, which would call every id dead."""
    resp, failure = await _fetch_page(client, url, attempts, backoff)
    if resp is None:
        return None, failure
    items = _catalog_items(resp)
    if not items or not any(_model_id(m) for m in items):
        return None, "answered no model ids" if items is not None else "answered something other than JSON"
    return resp, ""


def check_content(resp: httpx.Response, entry: Entry) -> str | None:
    """None = content confirms the entry; string = what is missing.

    Works on both sync and async httpx responses, so the scout reuses it to
    vet newly proposed entries before accepting them.
    """
    if entry.probe.type is ProbeType.API_MODELS:
        return _check_api_models(resp, entry)
    return _check_page_keywords(resp, entry)


def _model_id(model: dict) -> str:
    """What you put in the request body. OpenAI-shaped catalogs call the field
    `id`; the new-api family of gateways (TokenRouter and its kin) calls the
    same string `model_name`.

    `model_id` is read before `model_name` because a catalog that publishes both
    means the second one as a title — AIHubMix ships `"model_id":
    "coding-glm-5.1-free"` next to `"model_name": "Coding GLM 5.1 (free)"`, and
    a family matched against the title misses every hyphen."""
    for key in ("id", "model_id", "model_name"):
        value = model.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _number(value: object) -> float | None:
    """A price the vendor actually published. Booleans are numbers in Python and
    would read as a free 0/paid 1, so they are not."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _price_row(value: object) -> float | None:
    """One side of the price, however the vendor writes the row down. Most spell
    it as the bare number; Routeway wraps it in the unit it is quoted in —
    `{"unit": "1M tokens", "price_per_million_t": 0}`. Which unit that is does
    not matter to the only question asked here: is the row still a zero."""
    if isinstance(value, dict):
        for key in ("price_per_million_t", "price_per_million", "price", "amount", "value"):
            price = _number(value.get(key))
            if price is not None:
                return price
        return None
    return _number(value)


def _tiered_price_of(tiers: list) -> list[float] | None:
    """Requesty publishes one price row per usage tier, as a list of
    `{prompt_tokens_threshold, input_price, output_price}` rather than a single
    pricing object. Every tier is read: a lane that costs nothing below a
    threshold and bills above it is a discount, not a free model."""
    prices = []
    for tier in tiers:
        if not isinstance(tier, dict):
            return None
        for key in ("input_price", "output_price"):
            price = _price_row(tier.get(key))
            if price is not None:
                prices.append(price)
            elif key in tier:
                return None
    return prices or None


def _price_of(model: dict) -> list[float] | None:
    """What one plain completion costs, as the vendor publishes it, or None when
    it publishes nothing we understand. OpenRouter and BazaarLink name the rows
    prompt/completion, Vercel input/output, Requesty ships a tier per row, and
    the new-api family publishes multipliers instead (see _multiplier_price_of).
    Of a pricing object only the token rows are read; a per-call charge is
    _charges_elsewhere's question."""
    pricing = model.get("pricing")
    if isinstance(pricing, list):
        return _tiered_price_of(pricing)
    if not isinstance(pricing, dict):
        return _multiplier_price_of(model)
    prices = []
    for key in ("prompt", "completion", "input", "output"):
        price = _price_row(pricing.get(key))
        if price is not None:
            prices.append(price)
        elif key in pricing:
            return None
    return prices or None


def _multiplier_price_of(model: dict) -> list[float] | None:
    """The new-api family publishes no pricing object. A row is billed either per
    request (`quota_type` 1, `model_price` in currency) or per token, where
    `model_ratio` multiplies a house unit and `completion_ratio` scales the
    output side of it. The unit cancels out for the only question asked here —
    is this row still a zero — so the multipliers are compared directly.

    `quota_type` is read loosely on purpose: a gateway that sends it as "1"
    would otherwise fall through to the token branch, where a per-request price
    sits next to a zero `model_ratio` and reads as free."""
    if _number(model.get("quota_type")) == 1:
        price = _number(model.get("model_price"))
        return [price] if price is not None else None
    ratio = _number(model.get("model_ratio"))
    if ratio is None:
        return None
    completion = _number(model.get("completion_ratio"))
    return [ratio, ratio * (completion if completion is not None else 1.0)]


def _is_withdrawn(model: dict) -> bool:
    """The vendor's own verdict that a row cannot be called right now: an
    `available` flag that is false — Routeway's catalog carries one, and a free
    list's retirement mark sets it (see join_free_list) — or a retirement date
    the row carries that has come (see _retired_on). A price can stay 0 while
    the lane goes away, so a price-only check would vouch for it forever.

    Read loosely, like `quota_type`: a gateway that stringifies the boolean would
    otherwise turn this into a check that can never fire. A missing or null field
    means the vendor said nothing, which is not a withdrawal.

    `outdated` is deliberately not read: Routeway sets it on models that are
    `available: true` and callable, and a model's age is is_model_stale's
    question.
    """
    if _retired_on(model) is not None:
        return True
    value = model.get("available", True)
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return value.strip().lower() in ("false", "no", "off", "0")
    return False


# Where a catalog dates the end of a row itself: Requesty's `retires`, a Unix
# time, and OpenRouter's and Kilo's `expiration_date`, a day.
RETIREMENT_FIELDS = ("retires", "expiration_date")


def _retired_on(model: dict) -> date | None:
    """The day a catalog row says it retired, once that day has come in UTC —
    or None.

    Requesty keeps a row in its catalog, still priced 0, after the day its
    `retires` names. A date still to come is notice, not a withdrawal: the id
    answers until then."""
    today = datetime.now(timezone.utc).date()
    for key in RETIREMENT_FIELDS:
        value = model.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and value > 0:
            day = datetime.fromtimestamp(value, timezone.utc).date()
        else:
            day = _utc_day(value)
        if day is not None and day <= today:
            return day
    return None


def _withdrawn_note(model: dict) -> str:
    """A withdrawn row as a run report names it: with the day it retired, where
    the catalog dates that itself."""
    retired = _retired_on(model)
    return f"{_model_id(model)} retired on {retired}" if retired else _model_id(model)


def _price_note(model: dict, listed: bool = False) -> str:
    """Why a row is not free, in words a person can check: on a row read with a
    free list the mark is the list's, and "the catalog" would send them to a
    document that marks nothing."""
    mid = _model_id(model) or "?"
    if _free_flag(model) is False:
        return (f"{mid} is not marked free on the free list" if listed
                else f"{mid} is marked not free by the catalog")
    prices = _price_of(model)
    if prices is None:
        return f"{mid} publishes no price"
    note = f"{mid} priced {'/'.join(f'{p:g}' for p in prices)}"
    pricing = model.get("pricing") if isinstance(model.get("pricing"), dict) else {}
    extra = [f"{k} {_price_row(v):g}" for k, v in pricing.items()
             if (k.lower() in _PER_CALL_KEYS or any(m in k.lower() for m in _PER_UNIT_MARKERS))
             and _price_row(v) not in (None, 0)]
    return note + (" plus " + ", ".join(extra) if extra else "")


def _catalog_items(resp: httpx.Response, lane: str | None = None) -> list[dict] | None:
    """Every model row of an OpenAI-shaped catalog, however the vendor wraps it,
    or None when the body is not JSON at all — the one case a caller has to tell
    apart from an empty catalog.

    Where the row names a `probe.lane`, the rows are that key's array and
    nothing else in the document: the other lanes list the same models on
    other terms, and a family found there is not a family found free.

    Otherwise the rows are the document itself, its OpenAI `data`, or — where
    there is no `data` — its `models`, the way Opper's keyless catalog answers
    (`{"models": [...]}`)."""
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return None
    return _rows(data, lane)


def _rows(data: object, lane: str | None) -> list[dict]:
    """The model rows of a parsed catalog, as _catalog_items finds them — the
    document's own objects, so a caller can mark them where they stand."""
    if lane is not None:
        rows = data.get(lane) if isinstance(data, dict) else None
        rows = rows if isinstance(rows, list) else []
    elif isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("data", data.get("models", []))
        rows = rows if isinstance(rows, list) else []
    else:
        rows = []
    return [m for m in rows if isinstance(m, dict)]


# The label NVIDIA files every free endpoint under in NGC's catalog search, and
# displays as "Free Endpoint" on the model's page at build.nvidia.com.
NGC_FREE_LABEL = "nim_type_preview"


def _free_endpoints(resp: httpx.Response) -> dict[str, dict] | str:
    """Every endpoint a free list marks free, keyed by `_id_squash` of
    publisher/name — or, where the document cannot be read as a free list, why.

    The one list read today is NGC's catalog search filtered to NVIDIA's free
    label, the data build.nvidia.com's model pages render from. An endpoint is
    named there without its publisher (`glm-5-3`), the publisher sits in a
    label of its own (`z-ai`) and the free mark is a label value. The catalog
    spells that model `z-ai/glm-5.3`, so the key is squashed the way an id is.

    The label is read on every endpoint rather than trusted to the query's
    filter: a query is a request, and a search that stopped honouring it would
    otherwise mark every endpoint it returned free. A document of another shape
    is reported rather than guessed at, and so is a list longer than the page
    read, since an endpoint on a page not read would be called not free.
    """
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return "answered something other than JSON"
    groups = data.get("results") if isinstance(data, dict) else None
    if not isinstance(groups, list):
        return "answered something other than an NGC catalog search"
    pages = data.get("resultPageTotal")
    if isinstance(pages, int) and pages > 1:
        return f"runs to {pages} pages and only the first was read"
    free: dict[str, dict] = {}
    for group in groups:
        resources = group.get("resources") if isinstance(group, dict) else None
        for endpoint in resources if isinstance(resources, list) else []:
            if not isinstance(endpoint, dict) or not isinstance(endpoint.get("name"), str):
                continue
            labels = {label.get("key"): label for label in endpoint.get("labels") or []
                      if isinstance(label, dict)}
            general = labels.get("general", {}).get("unresolvedValues")
            publishers = labels.get("publisher", {}).get("values")
            if (not isinstance(general, list) or NGC_FREE_LABEL not in general
                    or not isinstance(publishers, list) or not publishers):
                continue
            free[_id_squash(f"{publishers[0]}/{endpoint['name']}")] = endpoint
    return free


def free_list_marks(resp: httpx.Response) -> dict[str, str] | str:
    """The endpoints a free list marks free, keyed as `_free_endpoints` keys
    them, each with the date the vendor retires it or "" — or, where the
    document cannot be read as a free list, why. A retirement is a DEPRECATION
    attribute holding the last day the endpoint is supported, as the vendor
    writes it ("09/21/2026"); the model's page then reads "Free Endpoint:
    Deprecated"."""
    endpoints = _free_endpoints(resp)
    if isinstance(endpoints, str):
        return endpoints
    marks: dict[str, str] = {}
    for key, endpoint in endpoints.items():
        attributes = {a.get("key"): a.get("value") for a in endpoint.get("attributes") or []
                      if isinstance(a, dict)}
        retired = attributes.get("DEPRECATION")
        marks[key] = retired if isinstance(retired, str) else ""
    return marks


def free_list_dates(resp: httpx.Response, model_ids: list[str]) -> dict[str, date] | str:
    """The UTC day the vendor created the free endpoint of each of `model_ids`
    the list marks free — or, where the document cannot be read as a free list,
    why.

    NGC stamps every endpoint with the moment NVIDIA created it (`dateCreated`),
    and the list is NVIDIA's word on which endpoints are free, so the stamp on
    a marked endpoint is the day the free id began — the vendor's date the
    two-week bar counts from where it is earlier (see freetier_radar.bars). An
    endpoint with no readable stamp gives no date rather than a guess."""
    endpoints = _free_endpoints(resp)
    if isinstance(endpoints, str):
        return endpoints
    dates: dict[str, date] = {}
    for model_id in model_ids:
        endpoint = endpoints.get(_id_squash(model_id))
        day = _utc_day(endpoint.get("dateCreated")) if endpoint else None
        if day is not None:
            dates[model_id] = day
    return dates


def _utc_day(stamp: object) -> date | None:
    """The UTC day of an ISO 8601 moment, read as UTC where it names no zone."""
    if not isinstance(stamp, str):
        return None
    try:
        moment = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).date()


def join_free_list(catalog: httpx.Response, free_list: httpx.Response,
                   lane: str | None = None) -> tuple[httpx.Response | None, str]:
    """The catalog as it would read if it carried the free list's marks itself,
    or None and why the list could not be read.

    A catalog that prices nothing leaves require_zero_price nothing to read, so
    the marks go where a flag would be: an id the list marks is `free`, one the
    list also dates for retirement is `available: false` as well — the vendor's
    word that the endpoint is going, said before the day it stops answering —
    and every other id is `free: false`, the ones the catalog keeps answering
    with no page at all among them. From there the family check, the dead ids
    and the unlisted ones read it as they read Kilo's isFree or Routeway's
    available. A catalog that is not JSON is handed back as it came, for the
    check that reads it to report."""
    marks = free_list_marks(free_list)
    if isinstance(marks, str):
        return None, marks
    try:
        data = catalog.json()
    except json.JSONDecodeError:
        return catalog, ""
    for model in _rows(data, lane):
        retired = marks.get(_id_squash(_model_id(model)))
        model["free"] = retired is not None
        if retired:
            model["available"] = False
    return httpx.Response(catalog.status_code, json=data, request=catalog.request), ""


def _empty_lane(resp: httpx.Response, lane: str) -> str:
    """Why a lane gave no rows. An empty array is the vendor's own word that
    nothing is on offer; a document without the key has changed shape, and
    the probe is what wants repairing. Opposite fixes, one failure each."""
    data = resp.json()
    if isinstance(data, dict) and isinstance(data.get(lane), list):
        return f"the {lane!r} lane lists no model ids"
    return f"response has no {lane!r} lane"


def _check_api_models(resp: httpx.Response, entry: Entry) -> str | None:
    items = _catalog_items(resp, entry.probe.lane)
    if items is None:
        return "response is not JSON"
    if not any(_model_id(m) for m in items):
        if entry.probe.lane is not None:
            return _empty_lane(resp, entry.probe.lane)
        return "no model ids in response"
    missing, withdrawn, priced = [], [], []
    families = [f.family for f in entry.models]
    for family in entry.models:
        # An id vouches for the most specific family it names: coding-glm-5.2-free
        # is glm-5.2's, and must not keep glm-5 alive after glm-5's own id left.
        matches = [
            m for m in items
            if id_family(families, _model_id(m)) == family.family
            and entry.probe.carries_marker(_model_id(m))
        ]
        if not matches:
            missing.append(family.family)
            continue
        # A row the vendor marks uncallable is not a free lane whatever its price
        # says, so it is dropped before the price is read below — otherwise a
        # withdrawn zero would go on vouching for a family whose only callable
        # row has started billing.
        live = [m for m in matches if not _is_withdrawn(m)]
        if not live:
            withdrawn.append(", ".join(_withdrawn_note(m) or family.family for m in matches[:3]))
            continue
        # Presence in the catalog is not the offer: an aggregator can leave a
        # free model's id where it was and start charging for it. Where the
        # vendor publishes prices, the zero is the offer.
        if entry.probe.require_zero_price and not any(_is_free(m) for m in live):
            priced.append(", ".join(_price_note(m, entry.probe.free_list is not None)
                                    for m in live[:3]))
    problems = []
    if missing:
        problems.append(f"missing families: {', '.join(missing)}")
    if withdrawn:
        problems.append(f"marked unavailable: {'; '.join(withdrawn)}")
    if priced:
        problems.append(f"no longer free: {'; '.join(priced)}")
    return " | ".join(problems) if problems else None


_FREE_FLAGS = ("isFree", "is_free", "free")


def _free_flag(model: dict) -> bool | None:
    """The vendor's own word on whether a row is free, where it gives one. Kilo
    marks every row isFree and prices Google's Lyria previews at 0 with the
    flag false; Kenari puts `free` inside `pricing` beside the metered rate
    the same model costs without its :free suffix. Where the catalog says
    whether a row is free, that is the answer, and the prices are read only
    where it does not. A boolean only: a string or a number under one of these
    keys is not a verdict."""
    for holder in (model, model.get("pricing")):
        if isinstance(holder, dict):
            for key in _FREE_FLAGS:
                value = holder.get(key)
                if isinstance(value, bool):
                    return value
    return None


# Price rows that bill every ordinary call of the model, whatever it is priced
# per token: a flat charge per request (EmpirioLabs prices gemma-3-27b per
# message) or a charge per unit of the model's own medium (Vercel prices
# spacexai/grok-stt per second of audio), both beside 0 per token.
_PER_CALL_KEYS = ("request", "per_request", "request_price", "price_per_request")
_PER_UNIT_MARKERS = ("per_second", "per_minute", "duration", "per_hour")


def _charges_elsewhere(model: dict) -> bool:
    """A non-zero price on the row that every ordinary call pays. Cache, image
    and web-search rows are not read: they price an optional input, and a free
    text lane is still free without it. The list is deliberately narrow — a
    stricter reading fails the offer check, and three failed probes archive a
    live row, so an unknown add-on key must not be able to do that."""
    pricing = model.get("pricing")
    if not isinstance(pricing, dict):
        return False
    for key, value in pricing.items():
        lowered = key.lower()
        if lowered in _PER_CALL_KEYS or any(m in lowered for m in _PER_UNIT_MARKERS):
            price = _price_row(value)
            if price is not None and price != 0:
                return True
    return False


def _is_free(model: dict) -> bool:
    """Free by the catalog's own account: its flag where it has one, else every
    price it publishes for the row at zero."""
    flag = _free_flag(model)
    if flag is not None:
        return flag
    prices = _price_of(model)
    return prices is not None and all(p == 0 for p in prices) and not _charges_elsewhere(model)


def challenge_marker_hit(text: str) -> str | None:
    """The wording of a bot wall standing where the vendor's page should be."""
    lowered = text.lower()
    for marker in CHALLENGE_MARKERS:
        if marker in lowered:
            return marker
    return None


def dead_marker_hit(text: str) -> str | None:
    """The phrase a vendor uses to announce the offer is over, if the page has one."""
    for marker in DEAD_MARKERS:
        if _as_read(marker) in text:
            return marker
    return None


_SPACE_LOOKALIKES = str.maketrans(dict.fromkeys(
    "\u00a0\u202f\u2009\u2007\u2060", " "))


def _plain_spaces(text: str) -> str:
    """Text with plain spaces for the typographic ones a CMS puts between words
    a designer did not want broken across lines. They are invisible in a
    browser and in a copy-paste, so a keyword quoted off such a page would
    otherwise never occur in the bytes."""
    return text.translate(_SPACE_LOOKALIKES)


def _as_read(text: str) -> str:
    """Text the way a reader meets it and a keyword is quoted from it: entities
    read as their characters, plain spaces, every run of whitespace one space,
    case folded. HTML renders `&#39;` as an apostrophe and a line break in the
    page's source as a space, so a sentence a template escapes or wraps reads
    whole in a browser and in a copy-paste; freetier-quotes reads it the same
    way."""
    return " ".join(_plain_spaces(html.unescape(text)).split()).lower()


# A tag, taken out where a page is read as the text a reader sees.
TAG = re.compile(r"<[^>]+>")
_SCRIPT_OR_STYLE = re.compile(
    r"<script\b([^>]*)>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>", re.S | re.I)
_COMMENT = re.compile(r"<!--.*?-->", re.S)


def _rendered(text: str) -> str:
    """The page with its machinery taken out: framework state blobs, OpenAPI
    enums, response samples, i18n bundles — everything a vendor ships to the
    browser that a reader never sees.

    An anchor keyword is a promise that the string dies with the offer, and a
    script tag is where a string outlives it: an id in an OpenAPI enum or a
    response sample goes on matching after the vendor's table dropped the model.

    JSON-LD is kept. It sits in a script tag like the rest, but structured data
    is the vendor answering a question — Freebuff prints most of its FAQ answers
    only there — so stripping script tags by their name alone would take a real
    page's only evidence with it.

    Comments go too, and leave nothing behind: React writes an empty one on each
    side of a value it prints into a sentence, which a reader reads straight
    through ("with <!-- -->500<!-- --> credits a month", Experiential Labs,
    2026-09-29). They go after the scripts, so a script that carries the
    characters "<!--" cannot take the text that follows it along.
    """
    def cut(match: re.Match[str]) -> str:
        attrs = (match.group(1) or "").lower()
        return match.group(0) if "ld+json" in attrs else " "
    return _COMMENT.sub("", _SCRIPT_OR_STYLE.sub(cut, text))


def _check_page_keywords(resp: httpx.Response, entry: Entry) -> str | None:
    rendered = _as_read(_rendered(resp.text))
    # An explicit withdrawal outranks the keywords: vendors leave the free tier
    # described on the page and add the bad news next to it. Read against the
    # rendered page for the same reason the keywords are: the sentence that
    # announces the end is one a reader is meant to see.
    dead = dead_marker_hit(rendered)
    if dead is not None:
        return f'offer withdrawn: page says "{dead}"'
    absent = [k for k in entry.probe.keywords if _as_read(k) not in rendered]
    whole = (_as_read(resp.text)
             if absent or entry.probe.machinery_keywords else "")
    # Which half of the response lacked a keyword is what a runner-only failure
    # turns on, and no copy of the page survives the run: a keyword the bytes
    # still carry means the stripping ate it and the row wants
    # machinery_keywords; one absent from the bytes means the origin served
    # something else.
    missing = [k if _as_read(k) not in whole else f"{k} (in the page's machinery only)"
               for k in absent]
    if entry.probe.machinery_keywords:
        missing += [k for k in entry.probe.machinery_keywords if _as_read(k) not in whole]
    if not missing:
        return None
    # And the size: a page that answers 200 with a shell or a variant is a
    # different size, the only trace of it left in the log.
    return f"missing keywords: {', '.join(missing)} — {len(resp.text):,} bytes read"


def unevidenced_families(resp: httpx.Response, entry: Entry) -> list[str]:
    """Families the README publishes that the probed page does not even name.

    What `_check_api_models` asks of a catalog, asked of a page: the keywords
    anchor the offer, and this asks whether the models listed beside it are
    still there. Deliberately weak. It reads the raw body, not the rendered
    text the keywords are held to, so a name the vendor serves only inside its
    page data counts; whether the page names the model as free is the stronger
    question, and the one an anchor keyword answers. A family also counts where
    its parts are named close together (see _named_in_parts).

    It never fails an entry: three failures archive a row, and a marketing page
    that drops a model name in a restyle must not bury a live service. The
    verdict is STALE_MODELS — the offer is alive, the Models column is not
    trustworthy — which the scout's FIX_PROMPT repairs; a catalog row is held
    to the same line (see probe_entry).
    """
    if entry.probe.type is not ProbeType.PAGE_KEYWORDS:
        return []
    squashed, text = _squash(resp.text), resp.text.lower()
    return [m.family for m in entry.models
            if not names_family(m.family, squashed, _squash) and not _named_in_parts(m.family, text)]


def family_named(resp: httpx.Response, entry: Entry, family: str) -> bool | None:
    """Whether what a row's probe reads names `family` the way the row's own
    families are held to: named on the page, or served free in the catalog lane.
    None when the response cannot answer — not JSON, or no rows to look in.

    The probe asks it of a catalog row whose content check failed (see
    probe_entry), and the scout of a generation bump before a human reads it: a
    newer generation this vendor does not serve cannot supersede one it does."""
    asked = entry.model_copy(update={"models": [ModelFamily(family=family)]})
    if entry.probe.type is ProbeType.API_MODELS:
        items = _catalog_items(resp, entry.probe.lane)
        if items is None or not any(_model_id(m) for m in items):
            return None
        return _check_api_models(resp, asked) is None
    return not unevidenced_families(resp, asked)


def dead_model_ids(resp: httpx.Response, entry: Entry) -> list[str]:
    """Ids in `api.model_ids` that the catalog no longer answers for: not in it,
    retired by its own date, marked unavailable, or — where the row reads
    prices — no longer free.

    No family or keyword check reads this field, and it fills the generated
    configs a reader pastes into a client. It is never asked of a page: a name
    missing from prose is not a withdrawal, and here the consequence would be a
    deletion from a config file. A page row that names a keyless catalog in
    `probe.catalog` is asked of that catalog instead. A lane served only inside
    the vendor's own client keeps its ids in `client_lane`, and is asked the
    same question of the lane its probe reads.

    The match is exact, because the id is what goes in the request body: a
    re-versioned id names the same model and is another string. A missing id is reported with any catalog id it may have
    become (see _successor_hint), since a re-versioned id wants a rename.

    It never fails an entry and never repairs one: a free lane rotating its ids
    is this list doing its job, and the repair is an exact string copied from a
    catalog, which the scout leaves to a human (see for_a_human).
    """
    lane = lane_ids(entry)
    if lane is None:
        return []
    catalog: dict[str, dict] = {}
    for model in _catalog_items(resp, entry.probe.lane) or []:
        mid = _model_id(model)
        if mid:
            catalog.setdefault(mid, model)
    dead = []
    for wanted in lane.model_ids:
        model = catalog.get(wanted)
        if model is None:
            dead.append(f"{wanted} is not in the catalog{_successor_hint(wanted, catalog)}")
        elif _retired_on(model) is not None:
            dead.append(f"{wanted} retired on {_retired_on(model)} by the catalog's own date")
        elif _is_withdrawn(model):
            dead.append(f"{wanted} is marked unavailable")
        elif entry.probe.require_zero_price and not _is_free(model):
            dead.append(_price_note(model, entry.probe.free_list is not None))
    return dead


def unlisted_free_ids(resp: httpx.Response, entry: Entry) -> list[str]:
    """Ids the catalog serves free that `api.model_ids` does not carry — the
    other direction of dead_model_ids, and the one that sees a lane grow.

    The lane is the row's own definition of it, not a bare zero. An id is in
    it when it carries `probe.free_marker` where the row sets one, is free by
    the catalog's own account (see _is_free), and is not marked unavailable —
    the tests the offer check and dead_model_ids already apply. The marker
    matters: OpenRouter and Kilo both price Google's Lyria music previews at 0
    with no :free suffix. The check is asked only where prices are read, since
    on a catalog that publishes none every id would be free, or where the
    vendor lists its free lane under a key of its own (`probe.lane`): that lane
    is the vendor's whole account of what is free, so its ids count without a
    price unless the row reads prices too.

    Ids in `api.ignored_ids` are left out: a zero somebody has read and left
    unlisted, with the reason in `api.note`, that would otherwise print on
    every run.

    Like dead_model_ids it never fails a row and is never handed to the
    scout: whether to add an id, or record it as ignored, is a judgement about
    what the row is for.
    """
    lane = lane_ids(entry)
    if (entry.probe.type is not ProbeType.API_MODELS or lane is None
            or not (entry.probe.require_zero_price or entry.probe.lane)):
        return []
    known = set(lane.model_ids) | set(lane.ignored_ids)
    unlisted = set()
    for model in _catalog_items(resp, entry.probe.lane) or []:
        mid = _model_id(model)
        if (mid and mid not in known and entry.probe.carries_marker(mid)
                and (_is_free(model) or not entry.probe.require_zero_price)
                and not _is_withdrawn(model)):
            unlisted.add(mid)
    return sorted(unlisted)


def _stale_ids_detail(dead: list[str], unlisted: list[str], entry: Entry) -> str:
    """One line for a human with both directions on it: a rename that changed
    the words of an id — the case _successor_hint cannot see — is a dead id on
    one side and an unlisted one on the other. On a row read with a free list
    the unlisted ids are the ones the list marks, and the line says so, since
    that catalog prices nothing. The line names the list the ids belong in,
    `api` or `client_lane`; a client lane has no ignored ids, as it writes no
    config to keep an id out of."""
    field = lane_ids(entry).field
    parts = []
    if dead:
        parts.append(f"{field}.model_ids the catalog no longer answers for: " + "; ".join(dead))
    if unlisted:
        if entry.probe.free_list is not None:
            found = "ids the free list marks free"
        elif entry.probe.require_zero_price:
            found = "zero-priced ids in the catalog"
        else:
            found = f"ids in the {entry.probe.lane!r} lane"
        todo = ("add them, or record them in api.ignored_ids" if field == "api"
                else "add them, and keep any that names no model in client_lane.no_family_ids")
        parts.append(f"{found} that {field}.model_ids does not list ({todo}): "
                     + ", ".join(unlisted))
    return " | ".join(parts)


# How a note for a human opens: the ids against the catalog, the keyless or
# public-key lane, the Anthropic and Codex routes, the page that prints the
# public key, the data-use sentence and the border — each only a person
# re-reading the vendor's page can restate. Each follows a family verdict
# after " | ".
_FOR_A_HUMAN = ("api.model_ids ", "client_lane.model_ids ", "zero-priced ids in the catalog ",
                "ids the free list ", "ids in the ",
                "api.public_key ", "keyless ", "public-key ", "anthropic route ", "codex route ",
                "data_use ", "border: ", "border could ")


def for_a_human(detail: str) -> str:
    """The part of a verdict's detail the fix prompt tells the model to leave
    alone, or "" where there is none: whatever follows the family verdict once
    a note for a human begins (see _FOR_A_HUMAN). A row the scout repaired
    still carries it to the pull request."""
    parts = detail.split(" | ")
    for i, part in enumerate(parts):
        if part.startswith(_FOR_A_HUMAN):
            return " | ".join(parts[i:])
    return ""


def stale_ids(catalog: httpx.Response, entry: Entry) -> str:
    """What the catalog says about this row's published ids, in both
    directions, or "" while they are all backed. A passing row gets it as its
    verdict and a failing api-models row beside its failure: whether a row is
    being verified or repaired says nothing about whether its ids are true.
    """
    dead = dead_model_ids(catalog, entry)
    unlisted = unlisted_free_ids(catalog, entry)
    return _stale_ids_detail(dead, unlisted, entry) if dead or unlisted else ""


def _successor_hint(wanted: str, catalog: dict[str, dict]) -> str:
    """The catalog ids a missing one may have turned into, when a vendor
    re-versioned or renamed the row instead of withdrawing it: a withdrawal and
    a rename want opposite edits.

    Two shapes count and nothing else: an id that extends the missing one
    (`deepseek-ai/deepseek-v4-flash` as `deepseek-ai/deepseek-v4-flash-0731`),
    and one built from exactly the same words in another order
    (`nvidia/nemotron-3-nano-30b-a3b` as `nvidia/nemotron-nano-3-30b-a3b`). The
    metered twin of a free id (`llama-3.1-8b-instruct` beside
    `llama-3.1-8b-instruct:free`) is neither, so it is never offered as the
    successor."""
    words = _id_words(wanted)
    heirs = sorted(mid for mid in catalog
                   if mid != wanted and (mid.startswith(wanted) or _id_words(mid) == words))
    return f" (catalog carries {', '.join(heirs[:2])})" if heirs else ""


def _id_words(model_id: str) -> tuple[str, ...]:
    """A model id as the sorted bag of words a vendor built it from — the unit
    that survives a rename which only reorders them."""
    return tuple(sorted(w for w in re.split(r"[^a-z0-9]+", model_id.lower()) if w))


# How far apart the parts of a family name may sit and still be one name. Wide
# enough for the words a vendor folds in ("Claude Sonnet & Opus 4.6" spends 24),
# narrow enough that a price list mentioning claude in one row and 4.6 in
# another does not vouch for a model nobody offers.
NAME_SPREAD = 48


def _named_in_parts(family: str, text: str) -> bool:
    """Whether a family's parts appear in order and within NAME_SPREAD of each
    other, for a page that names models that way — Antigravity's "Claude Sonnet
    & Opus 4.6" is two models sharing one version, neither a substring of the
    page.

    Each part must start where a name starts, or the version half of a family
    matches inside a different version and vouches for a model nobody offers:
    "Opus 4.5" would name opus-5. Only the left edge is anchored, since a name
    can end a sentence ("MiniMax 2.1."). A dotted version part is matched
    through _version_pattern, because the letter in front of a version number
    is the vendor's and moves: "MiniMax 2.1" and "MiniMax M2.1" are one model.
    """
    parts = [p for p in re.split(r"[\s_-]+", family.lower()) if p]
    if len(parts) < 2:
        return False
    spread = r"[^\n]{0,%d}?" % NAME_SPREAD
    anchored = (r"(?<![\w.])" + (_version_pattern(p) or re.escape(p)) for p in parts)
    return re.search(spread.join(anchored), text) is not None


# A generation number the vendor may or may not put a letter in front of:
# "v3.2", "3.2" and "M2.1" are one part each, and the letter is the vendor's.
# The dot is required: a bare number with a letter allowed in front would let
# a hashed "h5" in minified markup name glm-5 on any page that says GLM nearby.
DOTTED_VERSION = re.compile(r"[a-z]?(\d+(?:\.\d+)+)")


def _version_pattern(part: str) -> str | None:
    """How a dotted version part may be spelled (see DOTTED_VERSION), or None
    for any other part. Only the prefix letter is relaxed, on both sides: "2.1"
    still has to start where a name starts and sit within NAME_SPREAD of the
    part before it.
    """
    match = DOTTED_VERSION.fullmatch(part)
    return None if match is None else r"[a-z]?" + re.escape(match.group(1))


def is_model_stale(entry: Entry) -> bool:
    """Every listed family bumped to a newer generation. The entry is alive —
    a supersede mark never archives — but the README has no free model left to
    name for it, so the families need refreshing."""
    return bool(entry.models) and all(m.superseded_by for m in entry.models)


def apply_results(entries: list[Entry], results: dict[str, ProbeResult],
                  today: date) -> list[tuple[Entry, ProbeResult]]:
    """PASS verifies and resets failures; FAIL increments them; INCONCLUSIVE
    touches nothing — the staleness rule archives entries that stay unverifiable.
    A provisional entry that keeps passing probes for PROVISIONAL_PROMOTE_DAYS
    after first_seen is promoted to a regular entry. An entry past its
    vendor-announced retirement date, or delisted by a reviewer, is left alone
    entirely.
    Returns (entry, result) pairs needing scout attention: FAIL, INCONCLUSIVE,
    passing entries whose model families are all superseded, and passes flagged
    STALE_MODELS or STALE_IDS."""
    needs_attention = []
    for e in entries:
        result = results.get(e.id)
        if result is None:
            continue
        # The vendor's own shutdown date has passed, or a reviewer took the row
        # off: the entry is archived for good and its endpoint is meant to be
        # dead. Re-verifying it would keep moving last_verified forward on a
        # service that is gone, and flagging it would send the scout off to
        # "fix" the probe.
        if is_archived_for_good(e, today):
            continue
        # STALE_MODELS and STALE_IDS are passes with a note: the offer was
        # evidenced, so the liveness bookkeeping is a PASS's. A frozen
        # last_verified would archive the row by staleness in ARCHIVE_AFTER_DAYS
        # over a note.
        if result.status in (ProbeStatus.PASS, ProbeStatus.STALE_MODELS, ProbeStatus.STALE_IDS):
            e.last_verified = today
            e.probe_failures = 0
            if e.provisional and (today - e.first_seen).days >= PROVISIONAL_PROMOTE_DAYS:
                e.provisional = False
            if result.status is not ProbeStatus.PASS:
                needs_attention.append((e, result))
            elif is_model_stale(e):
                needs_attention.append((e, ProbeResult(
                    ProbeStatus.STALE_MODELS,
                    "every listed family is marked superseded — refresh models to the "
                    "generation the free tier actually serves")))
        else:
            if result.status is ProbeStatus.FAIL:
                e.probe_failures += 1
            needs_attention.append((e, result))
    return needs_attention


async def _amain(registry_path: Path, failures_dir: Path, dry_run: bool = False) -> int:
    """Returns the number of rows that FAILED, so a dry run can refuse to be
    chained past with `&&`. Flags that verify a row — stale-ids, stale-models —
    are not counted; neither is INCONCLUSIVE, which is the row's problem to
    report and not the run's."""
    entries = load_registry(registry_path)
    sem = asyncio.Semaphore(CONCURRENCY)

    # One date for the whole run: a notice's hold is read against it by the probe
    # and the verification it earns is stamped with it, and a run that crosses
    # midnight must not do the two on different days.
    today = date.today()

    async def bounded(entry: Entry) -> ProbeResult:
        async with sem:
            return await probe_entry(client, entry, today=today)

    # A row archived for good is not even asked: no answer could bring it back,
    # a retired endpoint is meant to be dead, and a delisted row can point at a
    # service the blocklist says never to fetch.
    probed = [e for e in entries if not is_archived_for_good(e, today)]
    async with httpx.AsyncClient(headers=UA) as client:
        outcomes = await asyncio.gather(*(bounded(e) for e in probed))
    results = {e.id: r for e, r in zip(probed, outcomes)}
    flagged = apply_results(entries, results, today)
    if dry_run:
        # Verification dates are earned in CI, where the probes run from a known
        # address. A local check is for reading, not for recording.
        print("dry run: registry left untouched")
    else:
        # history.jsonl is not written here: the render that follows records
        # what this run changed, together with any change committed since.
        save_registry(registry_path, entries)
    failures_dir.mkdir(parents=True, exist_ok=True)
    payload = [
        {"id": e.id, "status": r.status.value, "detail": r.detail}
        for e, r in flagged
    ]
    (failures_dir / "failures.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"probed {len(probed)} entries, {len(flagged)} need attention")
    # failures.json never leaves the runner, so each flagged row is printed: a
    # probe that fails from CI and passes from a laptop cannot be reproduced
    # locally.
    for row in payload:
        print(f"  {row['id']}: {row['status']} — {row['detail'] or 'no detail'}")
    return sum(1 for _, r in flagged if r.status is ProbeStatus.FAIL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures"))
    parser.add_argument("--dry-run", action="store_true",
                        help="probe everything and report, but write no verification dates")
    args = parser.parse_args()
    failed = asyncio.run(_amain(args.registry, args.failures, args.dry_run))
    # A real run hands its failures to the scout and must exit 0 for the
    # workflow to reach it; a dry run is read by a person, and a person
    # chaining it in a shell wants the chain to stop here.
    if args.dry_run and failed:
        raise SystemExit(1)
