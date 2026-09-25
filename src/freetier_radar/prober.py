from __future__ import annotations

import argparse
import asyncio
import json
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path

import httpx

from .models import (
    CHALLENGE_MARKERS, DEAD_MARKERS, NOTICE_HOLD_DAYS, Entry, Follow, ModelFamily, Probe, ProbeType,
    _id_squash, _squash, family_names, is_archived_for_good, lane_ids, load_registry,
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
    STALE_MODELS = "stale-models"  # offer verified, but not the Models column: a family its page no longer names, one its catalog no longer serves free beside one it does, or every family superseded
    STALE_IDS = "stale-ids"  # offer and families verified, but a published connection detail is not backed: api.model_ids against the catalog, the Anthropic route, or a public key its page stopped printing


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
    # lane, and the families it stopped serving are the Models column's
    # problem, not the offer's. Until 2026-09-24 one model leaving failed the
    # whole row, three runs of that archive it, and so a rotating lane's column
    # was kept short: OpenRouter's named two families for a month while its
    # catalog served a dozen more free. The column verdict is the same words
    # check_content wrote, flagged the way a page row's missing family is; a
    # lane that serves none of them still fails.
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
        if (entry.api and (entry.api.auth == "none" or entry.api.public_key)
                and entry.api.model_ids):
            keyless = await keyless_lane_verdict(client, entry, attempts, backoff,
                                                 today or date.today())
            if keyless is not None and keyless.status is not ProbeStatus.STALE_IDS:
                return keyless
        # The offer is evidenced. Whether the models the README hangs off it
        # still are is a second question: a catalog answered it above, a page
        # is asked here — see unevidenced_families. A flagged column is the
        # verdict, but it no longer ends the read: until 2026-09-21 it returned
        # here, and every question below went unasked on the rows most likely
        # to need them. Regolo dropped Llama 3.3 from its price table and its
        # catalog at once; the run flagged the family, the scout dropped it,
        # and the id stayed in the configs because the catalog was never read.
        # So the column's note leads, and whatever the rest of the read finds
        # follows it after " | ", where the fix prompt already looks for the
        # half that is not the model's to repair.
        unevidenced = unevidenced_families(resp, entry)
        if unevidenced:
            column = "listed families the page does not name: " + ", ".join(unevidenced)

        def verdict(status: ProbeStatus, note: str = "") -> ProbeResult:
            if column:
                return ProbeResult(ProbeStatus.STALE_MODELS,
                                   f"{column} | {note}" if note else column)
            return ProbeResult(status, note)

        # A third question, and the last field here that nothing read back
        # — asked in both directions, since a config that hands out a dead
        # id and a config that misses a live one are the same list being
        # out of date. An api-models probe asks it of the bytes it already
        # has; a page-keywords row asks it of the catalog it names, if any,
        # fetched now. A catalog that does not answer is said so, not
        # skipped: the row stays verified by its page, and the line in the
        # pull request is the whole difference between a check that ran
        # and one that quietly did not.
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
                if keyless is not None:
                    stale = f"{stale} | {keyless.detail}"
                return verdict(ProbeStatus.STALE_IDS, stale)
        # The last published connection detail, and the only one a GET
        # cannot see: the Anthropic-format route a row names for Claude
        # Code. Asked keyless, so the answer is never a message — it is
        # whether anything is listening at that path.
        if entry.api and entry.api.anthropic_base_url:
            missing = await anthropic_route_missing(client, entry, attempts, backoff)
            if missing:
                return verdict(ProbeStatus.STALE_IDS, missing)
        # A key handed to everyone is the vendor's only while the vendor's
        # page prints it — see public_key_unprinted.
        if entry.api and entry.api.public_key:
            unprinted = await public_key_unprinted(client, entry, page, attempts, backoff)
            if unprinted:
                if keyless is not None:
                    unprinted = f"{unprinted} | {keyless.detail}"
                return verdict(ProbeStatus.STALE_IDS, unprinted)
        # The row's word on what the vendor does with what a reader sends rests
        # on one sentence on one page — see data_use_moved.
        if entry.data_use is not None:
            moved = await data_use_moved(client, entry, page, attempts, backoff)
            if moved:
                if keyless is not None:
                    moved = f"{moved} | {keyless.detail}"
                return verdict(ProbeStatus.STALE_IDS, moved)
        if keyless is not None:
            return verdict(keyless.status, keyless.detail)
        return verdict(ProbeStatus.PASS)
    # Only asked once the content check has already failed. Plenty of live
    # pages carry a <noscript> asking for JavaScript while serving the offer
    # perfectly well above it — on those the keywords match and this never
    # runs. It is when they do NOT match that the wording matters: a bot wall
    # means we did not see the vendor's page, not that the offer is gone.
    challenge = challenge_marker_hit(page.text)
    if challenge is not None:
        return ProbeResult(ProbeStatus.INCONCLUSIVE, f'bot challenge: page says "{challenge}"')
    # A failing api-models row is where a dead id hides best, and until
    # 2026-09-08 this return was the reason: the id check lives above, on
    # the path a passing row takes. On 2026-09-07 LLMTR failed because
    # minimax/minimax-m3-free had left its catalog and only the metered
    # minimax/minimax-m3 answered for the family — and the same read had
    # taken three ids out of `api.model_ids`, which the report never said.
    # The scout dropped the family, the pull request read as a whole
    # repair, and all three ids stayed in the generated configs.
    #
    # The catalog that failed the family is this same response, so asking
    # costs nothing and the answer belongs beside the failure: one lane
    # moved, and a human is about to edit that row. Deliberately not asked
    # of a page row — see test_a_dead_offer_outranks_a_catalog_check. There
    # the failure IS the offer, the catalog is a second fetch, and the row
    # is repaired or archived whole rather than field by field.
    if entry.probe.type is ProbeType.API_MODELS:
        beside = stale_ids(resp, entry)
        if beside:
            detail = f"{detail} | {beside}"
    return ProbeResult(ProbeStatus.FAIL, detail)


async def _read(client: httpx.AsyncClient, url: str, attempts: int, backoff: float,
                named: bool = False) -> tuple[httpx.Response | None, ProbeResult | None]:
    """The page at `url`, or the verdict that reading it already is: a 401, 403
    or 429 is a wall rather than an answer, a 5xx or a network error is asked
    again, and any other 4xx is the page gone. `named` puts the url in the
    verdict, for a page the probe reached through another one."""
    said = f"{url} answered " if named else ""
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        except httpx.HTTPError as exc:
            last = f"network error: {exc}"
            continue
        if resp.status_code in (401, 403, 429):
            return None, ProbeResult(ProbeStatus.INCONCLUSIVE, f"blocked: {said}HTTP {resp.status_code}")
        if resp.status_code >= 500:
            last = f"HTTP {resp.status_code}"
            continue
        if resp.status_code >= 400:
            return None, ProbeResult(ProbeStatus.FAIL, f"page gone: {said}HTTP {resp.status_code}")
        return resp, None
    where = f"{url} " if named else ""
    return None, ProbeResult(ProbeStatus.INCONCLUSIVE,
                             f"{where}unreachable after {attempts} attempts: {last}")


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
ANTHROPIC_GONE = (404, 405, 410)


async def anthropic_route_missing(client: httpx.AsyncClient, entry: Entry, attempts: int,
                                  backoff: float) -> str | None:
    """Why the Anthropic-format route a row publishes is not to be trusted, or
    None while it answers. Set beside `api.anthropic_base_url` only where the
    vendor documents the route; this check is the twice-weekly half, and it is
    deliberately shallow — a 401 from an auth wall is the same 401 a real route
    gives — because the deep half already happened when the field was set.
    A route that cannot be reached is said so rather than skipped, like a
    catalog that stops answering: the row stays verified by its page, and the
    line in the pull request is the difference between a check that ran and
    one that quietly did not."""
    url = entry.api.anthropic_base_url.rstrip("/") + "/v1/messages"
    # A model the row publishes, not a placeholder: Fireworks checks the model
    # before the key and answered a made-up one with 404 "Model not found" on
    # 2026-09-17 — the status this check reads as a route that is gone — and a
    # model it serves with 401. Every other route answered both the same way.
    body = ({**ANTHROPIC_PROBE_BODY, "model": entry.api.model_ids[0]}
            if entry.api.model_ids else ANTHROPIC_PROBE_BODY)
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            resp = await client.post(url, json=body,
                                     headers={"anthropic-version": "2023-06-01"},
                                     timeout=TIMEOUT, follow_redirects=True)
        except httpx.HTTPError as exc:
            last = f"network error: {exc}"
            continue
        if resp.status_code >= 500:
            last = f"HTTP {resp.status_code}"
            continue
        if resp.status_code in ANTHROPIC_GONE:
            return f"anthropic route gone: POST {url} answered HTTP {resp.status_code}"
        return None
    return f"anthropic route could not be checked: POST {url} {last or 'did not answer'}"


# The smallest chat call there is. What it reads is the status line, whether
# the body is a completion and the model it names, never the message, and one
# token is all it costs the vendor.
KEYLESS_PROBE_BODY = {"max_tokens": 1, "messages": [{"role": "user", "content": "ping"}]}
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
    A 5xx and a network error are retried; so is a 429 when the caller is
    patient with one and the vendor names no longer wait than the pause before
    the next try; every other answer is final."""
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            resp = await client.post(url, json={"model": model, **KEYLESS_PROBE_BODY},
                                     headers=headers, timeout=TIMEOUT, follow_redirects=True)
        except httpx.HTTPError as exc:
            last = f"network error: {exc}"
            continue
        if resp.status_code >= 500:
            last = f"HTTP {resp.status_code}"
            continue
        if (resp.status_code == 429 and patient_with_429 and i + 1 < attempts
                and _asks_to_wait_at_most(resp, backoff * (i + 1))):
            continue
        return resp
    return last or "did not answer"


def _completion(answer: httpx.Response | str) -> dict | None:
    """The chat completion a 2xx answer carries, or None where it carries none.

    A 2xx was the whole test until 2026-09-21, and a gateway can say no with
    one. OpenRouter's docs say why, and Kilo's gateway answers in OpenRouter's
    format: the 200 goes out before the first token, so "the status stays 200
    even when every provider fails — the last error reaches you in the
    response body", and a provider error after that is the choice's, as
    `finish_reason: error` beside whatever message came first — "Check the
    body for an error field even on a 200". freellmapi's ElectronHub adapter
    throws out a proxy-error banner served as HTTP 200, and mnfst's verifier
    counts a 200 without choices[] as unknown. The content is not read — one
    token, often reasoning with no content yet — only that a choice holds a
    message and no error."""
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

    freellmapi's key tests caught gateways answering an id with a model it
    does not name — every Lucidity open/* route as synth-2.5-preview, eleven
    Septor -free aliases as minimax-m2.5-free (2026-09-18), Sail's legacy
    GLM-5.2 id as GLM-5.3. What a vendor calls the model it serves is compared
    by key, and one key running on into the other is the same model: vendors
    cut a served name short (LLM Tech answers nvidia/Qwen3.8-27B-NVFP4 as
    qwen38) and add a dated revision (Router9's deepseek-v4-flash as -0731),
    but a size or a version that differs is another model. A router id names
    none, and a completion that names none is taken at its word."""
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

    `api.auth: none` is not a connection detail like the rest of the api block;
    on a row that sets it, it is the offer. OVHcloud is listed for its anonymous
    lane, and the README's zero-signup curl and its "No account at all" answer
    are both built from that one field. Until 2026-09-14 nothing called it: the
    probe read the keyless /v1/models, which says the models exist and not that
    anyone may call them, so a vendor closing its anonymous lane would have left
    the first command on the page answering 401 behind a green run.

    So the first id in `api.model_ids` gets one completion, one token, no
    Authorization header, and a 2xx carrying a completion is the only answer
    that leaves nothing to say — a 200 without one is a non-answer like any
    other (see `_completion`), and a completion from a model the id does not
    name is a note (see `_answered_as`). A 429 used to count as an answer too
    — an anonymous lane is rate-limited instead of keyed — and that is how the
    README's first command sat on opencode's big-pickle while it answered 429
    FreeUsageLimitError to every call, from here and from readers, and
    ling-3.0-flash-fin-free beside it answered 200 three times out of three
    (2026-09-16). A rate limit does not end the offer, but it does end the
    command, so any other answer sends the check on to the next id, up to
    KEYLESS_IDS_TRIED:

    - a later id answering is a note naming it, since the fix is to put it first;
    - every id answering 429 is a note that the lane is rate-limited from here;
    - with no id answering, a 401 or 403 on the first is the vendor asking for a
      key, which FAILs the row, and three runs of it archive the row and take the
      command off the page — unless the body is a bot wall, which is no answer at
      all. Any other 4xx is about the request rather than the lane: vLLM answers
      404 for a model id that has rotated out, and uncloseai serves one id at a
      time. That, and a lane that could not be reached, is a note beside a row
      that stays verified, the way a dead id or a missing Anthropic route is.

    A refusal the list has already owned up to is the one exception. Where the
    row carries an `api.notice` that still holds, the maintainer has chosen to
    wait for the vendor's word with a warning on the page — opencode Zen refused
    every client but OpenCode from 2026-09-17 and said nothing — and three runs
    of FAIL would overrule that choice by calendar in ten days. So the refusal is
    a note naming the notice and the day it stops holding, and past that day it
    fails the row as before. The day a noticed lane answers again the notice is
    the stale sentence on the page, and the run says to take it down.

    A lane the vendor prints a key for is the same question asked with that
    key. LLM Tech's quickstart hands everyone "a shared free trial key", so the
    row needs no account, and `api.public_key` is to it what the missing key is
    to a keyless row: the call carries it as a bearer token, and a lane that
    refuses it is the no-account offer ending — or a key the vendor replaced,
    which only a person reading its page can copy — so it fails the same way."""
    url = entry.api.base_url.rstrip("/") + "/chat/completions"
    # A lane that wants an id per conversation (opencode Zen's x-opencode-session)
    # answers a call without one with 400, so the call carries a fresh id of its own
    # under this project's user agent, as the vendor asks any client to.
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
        # 5xx: on 2026-09-17 kilo-auto/free answered 429 from its upstream to the
        # runner and 200 elsewhere within the hour, LLM7's first id the reverse,
        # and each run named a different id to put first. The ids after it only
        # tell a rate-limited first id from a rate-limited lane, and are asked once.
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


async def _bearer_drift(client: httpx.AsyncClient, entry: Entry, url: str, model: str,
                        headers: dict, backoff: float) -> str | None:
    """Whether `api.refuses_bearer` still says what the lane does, asked once on
    the id that has just answered a bare call: the same call, carrying the bearer
    token LiteLLM would send. A refusal on a row without the field, or an answer
    on a row with it, is the note; anything else — a rate limit, an error, a bot
    wall — says nothing about the header either way."""
    answer = await _keyless_call(client, url, model, {**headers, "Authorization": PROXY_BEARER},
                                 1, backoff)
    if isinstance(answer, str):
        return None
    said = f"keyless call to {model} with a bearer token answered HTTP {answer.status_code}"
    if (answer.status_code in KEYLESS_REFUSED and not entry.api.refuses_bearer
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

    `api.public_key` is the vendor's to hand out only as long as the vendor's
    own page prints it: that page, `api.key_url`, is the whole difference
    between a key the vendor gives everyone — LLM Tech's shared trial key — and
    a key someone passed around, which is key sharing and does not qualify. A
    key that still works after its page stopped printing it is one the vendor
    may revoke any day or has already replaced, and either way the fix is a
    person reading the page, so it is a note beside a row its page keeps
    verified. Where the key's page is the page the probe reads it is read once.
    """
    url = entry.api.key_url
    if url == entry.probe.endpoint and entry.probe.follow is None:
        page = probed
    else:
        page, failure = await _fetch_page(client, url, attempts, backoff)
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

    The README marks a vendor that may train on what a reader sends with one
    glyph, and the row's page quotes the sentence it rests on: "Content used to
    improve our products" in the Gemini API's free column, a data policy's "we
    never train on your prompts". A vendor that rewrites that page changes what
    a reader pays for the free tier, so the sentence is read back every run,
    typography flattened the way freetier-quotes reads every quote. A page that
    cannot be read is said so rather than skipped."""
    from .quotes import page_texts, quote_found  # quotes reads pages through this module
    url = entry.data_use.url
    if url == entry.probe.endpoint and entry.probe.follow is None:
        page = probed
    else:
        page, failure = await _fetch_page(client, url, attempts, backoff)
        if page is None:
            return f"data_use could not be checked against {url}: {failure}"
    if quote_found(entry.data_use.quote, page_texts(page.text)):
        return None
    return (f"data_use quote is no longer on {url} — read what the vendor says now about "
            "training on what users send")


def _keyless_said(answer: httpx.Response | str) -> str:
    """A non-answer as the run reports it; a 2xx here is one without a completion."""
    if isinstance(answer, str):
        return answer
    said = " ".join(answer.text.split())[:160]
    return (f"HTTP {answer.status_code}" + (" without a completion" if answer.status_code < 300 else "")
            + (f": {said}" if said else ""))


async def _fetch_page(client: httpx.AsyncClient, url: str, attempts: int,
                      backoff: float) -> tuple[httpx.Response | None, str]:
    """A second page a row's checks read, or why it could not be read, with the
    patience the probe gives its own endpoint: a 5xx or a network error is
    retried, and any other answer but a 200 is reported."""
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        except httpx.HTTPError as exc:
            last = f"network error: {exc}"
            continue
        if resp.status_code >= 500:
            last = f"answered HTTP {resp.status_code}"
            continue
        if resp.status_code != 200:
            return None, f"answered HTTP {resp.status_code}"
        return resp, ""
    return None, f"unreachable after {attempts} attempts: {last}"


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
    pricing object.

    Every tier is read, because the question is whether the row is a zero all
    the way up. A lane that costs nothing below a threshold and bills above it
    is a discount, not a free model, and taking only the first row — the
    cheapest one, since the list is ordered by threshold — would file it as
    free."""
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
    prompt/completion, Vercel input/output, Requesty ships a tier per row; cache,
    image and request rows are ignored — a free lane is defined by the price of
    ordinary tokens."""
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
    """The vendor's own verdict that a row cannot be called right now.

    Of the catalogs probed here only Routeway publishes one — `available`, on all
    239 of its rows, false on exactly one, and that one a zero-priced `:free` id.
    That is the whole hole: the price stays 0 while the lane goes away, so a
    price-only check vouches for it forever.

    Read loosely, like `quota_type`: a gateway that stringifies the boolean would
    otherwise turn this into a check that can never fire. A missing or null field
    means the vendor said nothing, which is not a withdrawal.

    `outdated` is deliberately not read. The same catalog sets it on eight models
    that are `available: true` and callable — a model's age is is_model_stale's
    question, and answering it here would fail live entries over it.
    """
    value = model.get("available", True)
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return value.strip().lower() in ("false", "no", "off", "0")
    return False


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
    there is no `data` — its `models`: Opper's keyless catalog answers
    `{"models": [...]}`, and read as `data` alone it was an empty catalog."""
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
    attribute holding the last day the endpoint is supported:
    deepseek-v4-flash-0731 carried "09/21/2026" while its page read "Free
    Endpoint: Deprecated"."""
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

    The two-week bar before a free id joins the Models column counts from the
    read that found it or from the vendor's own date for the free id, the
    earlier. NGC stamps every endpoint with the moment NVIDIA created it, and
    the list is NVIDIA's word on which endpoints are free, so the stamp on a
    marked endpoint is the day the free id began: z-ai/glm-5.3's reads
    "2026-09-15T19:47:58.961Z", and the row listed the id on 2026-09-22. An
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
    marker = entry.probe.free_marker.lower()
    missing, withdrawn, priced = [], [], []
    for family in entry.models:
        matches = [
            m for m in items
            if family_names(family.family, _model_id(m))
            and (not marker or marker in _model_id(m).lower())
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
            withdrawn.append(", ".join(_model_id(m) or family.family for m in matches[:3]))
            continue
        # Presence in the catalog is not the offer: an aggregator can leave a
        # free model's id exactly where it was and start charging for it, and a
        # substring check would keep passing forever. Where the vendor publishes
        # prices, the zero is the offer.
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
    flag false; Kenari puts `free` inside `pricing` and prints the metered
    rate beside it, because a :free call "is billed Rp 0" and the price rows
    are what the same model costs without the suffix. Where the catalog says
    in so many words whether a row is free, that is the answer, and the prices
    are read only where it does not. A boolean only: a string or a number
    under one of these keys is not a verdict."""
    for holder in (model, model.get("pricing")):
        if isinstance(holder, dict):
            for key in _FREE_FLAGS:
                value = holder.get(key)
                if isinstance(value, bool):
                    return value
    return None


# Price rows that bill every ordinary call of the model, whatever it is priced
# per token: a flat charge per request, or a charge per unit of the model's
# own medium. Vercel prices spacexai/grok-stt at 0 per token and 0.000028 per
# second of audio; EmpirioLabs prices gemma-3-27b at 0 per token and $0.004
# per message. Reading the token rows alone called both free.
_PER_CALL_KEYS = ("request", "per_request", "request_price", "price_per_request")
_PER_UNIT_MARKERS = ("per_second", "per_minute", "duration", "per_hour")


def _charges_elsewhere(model: dict) -> bool:
    """A non-zero price on the row that every ordinary call pays. Cache, image
    and web-search rows stay ignored, as they always were: they price an
    optional input, and a free text lane is still free without it. The list
    is deliberately narrow — a stricter reading fails the offer check, and
    three failed probes archive a live row, so an unknown add-on key must not
    be able to do that. Measured 2026-09-02 across the eight live rows whose
    prices are read: no listed id carries a non-zero price outside the token
    rows, so nothing live turns on this."""
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


def dead_marker_hit(text: str, probe: Probe) -> str | None:
    """The phrase a vendor uses to announce the offer is over, if the page has one."""
    for marker in (*DEAD_MARKERS, *probe.dead_markers):
        if _as_read(marker) in text:
            return marker
    return None


_SPACE_LOOKALIKES = str.maketrans(dict.fromkeys(
    "\u00a0\u202f\u2009\u2007\u2060", " "))


def _plain_spaces(text: str) -> str:
    """The typographic spaces a CMS puts between words a designer did not want
    broken across lines. They are invisible in a browser and in a copy-paste, so
    a keyword quoted off the page — "100 million free tokens" on Inception Labs'
    own page — simply never occurs in the bytes, and the probe reports a
    withdrawn offer over a non-breaking space."""
    return text.translate(_SPACE_LOOKALIKES)


def _as_read(text: str) -> str:
    """Text the way a reader meets it and a keyword is quoted from it: plain
    spaces, every run of whitespace one space, case folded. HTML renders a line
    break in the page's source as a space, so a sentence a template wraps at
    eighty columns reads whole in a browser and in a copy-paste — and LLM Tech's
    quickstart, serving "2M tokens" and "per day per address" on two source
    lines, failed a keyword quoted straight off the page on 2026-09-18, while
    freetier-quotes, which already read whitespace this way, found the quote."""
    return " ".join(_plain_spaces(text).split()).lower()


_SCRIPT_OR_STYLE = re.compile(
    r"<script\b([^>]*)>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>", re.S | re.I)


def _rendered(text: str) -> str:
    """The page with its machinery taken out: framework state blobs, OpenAPI
    enums, response samples, i18n bundles — everything a vendor ships to the
    browser that a reader never sees.

    An anchor keyword is a promise that the string dies with the offer, and a
    script tag is exactly where a string does not. Groq's Free Plan Limits table
    lost llama-3.3-70b-versatile and llama-3.1-8b-instant somewhere between
    2026-08-14 and 2026-09-08, and the id this list anchored on went on matching
    ten times over, in an OpenAPI enum and a set of response samples; the probe
    passed every run while the README published a model the vendor had stopped
    giving away. The same shape had already been found twice by hand — Groq's
    llama-4 and Mistral's i18n bundle, both fixed in the registry because
    nothing here could tell them apart from the page.

    JSON-LD is kept. It sits in a script tag like the rest, but structured data
    is the vendor answering a question — Freebuff's whole offer is a JSON-LD FAQ
    block and nothing else — so stripping script tags by their name alone would
    take a real page's only evidence with it.
    """
    def cut(match: re.Match[str]) -> str:
        attrs = (match.group(1) or "").lower()
        return match.group(0) if "ld+json" in attrs else " "
    return _SCRIPT_OR_STYLE.sub(cut, text)


def _check_page_keywords(resp: httpx.Response, entry: Entry) -> str | None:
    rendered = _as_read(_rendered(resp.text))
    # An explicit withdrawal outranks the keywords: vendors leave the free tier
    # described on the page and add the bad news next to it. Read against the
    # rendered page for the same reason the keywords are: the sentence that
    # announces the end is one a reader is meant to see.
    dead = dead_marker_hit(rendered, entry.probe)
    if dead is not None:
        return f'offer withdrawn: page says "{dead}"'
    absent = [k for k in entry.probe.keywords if _as_read(k) not in rendered]
    whole = (_as_read(resp.text)
             if absent or entry.probe.machinery_keywords else "")
    # Which half of the response was missing it is the question a runner-only
    # failure turns on, and the one nothing can answer afterwards: no copy of
    # the page survives the run. A keyword the bytes still carry means our own
    # stripping ate it and the row wants machinery_keywords; a keyword absent
    # from the bytes means the origin served something else, which is what trae
    # did on 2026-09-10 while passing from every other address.
    missing = [k if _as_read(k) not in whole else f"{k} (in the page's machinery only)"
               for k in absent]
    if entry.probe.machinery_keywords:
        missing += [k for k in entry.probe.machinery_keywords if _as_read(k) not in whole]
    if not missing:
        return None
    # And the size, because a page that answers 200 with a shell or a variant is
    # a different size, and that is the only trace of it left in the log.
    return f"missing keywords: {', '.join(missing)} — {len(resp.text):,} bytes read"


def unevidenced_families(resp: httpx.Response, entry: Entry) -> list[str]:
    """Families the README publishes that the probed page does not even name.

    `_check_api_models` demands every listed family back from the catalog, and on
    that half of the registry a model that quietly leaves is flagged by the run.
    A page-keywords probe had no equivalent: its keywords anchor the OFFER, and
    nothing ever asked whether the models listed beside that offer are still
    there. Measured 2026-08-14 across every live page-keywords entry, a third of
    the published families appeared nowhere in the page their probe reads.

    Deliberately weak, in two ways that are both the point:

    It reads the same bytes the keywords do, so a name the vendor serves inside
    its page data counts. Whether the page names the model AS FREE is the
    stronger question, and the one an anchor keyword answers — novita's id sat
    next to a price for weeks before anyone noticed, and no presence check would
    have caught that.

    That weakness was measured the other way round on 2026-08-14, by byte
    location rather than presence: of the 32 live page-keywords entries, four
    match only in bytes a reader never sees, and every one of the four is
    deliberate — trae's `"name":"free"`, cursor's `"name":"hobby","price":"0"`,
    z.ai's ids glued to their price cells, and Upstage's own section heading
    inside a client-rendered payload. What the same pass did catch is the shape
    this docstring cannot: a family evidenced by an OpenAPI enum the page embeds
    (Groq's llama-4, absent from the Free Plan Limits table beside it) and one
    evidenced by an i18n bundle linking a 2025 blog post (Mistral). Both were
    fixed in the registry rather than here, because from this function the two
    cases are the same bytes.

    And it never fails an entry. Three failures archive a row, so a marketing
    page that drops a model name in a restyle would bury a live service inside a
    week. Since 2026-09-24 a catalog row is held to the same line, a family
    leaving a lane that still serves another one free being a flag and not a
    failure (see probe_entry). STALE_MODELS is what "the offer is alive, the
    Models column is not trustworthy" already means here, and it is what the
    scout's FIX_PROMPT already knows how to repair.
    """
    if entry.probe.type is not ProbeType.PAGE_KEYWORDS:
        return []
    squashed, text = _squash(resp.text), resp.text.lower()
    return [m.family for m in entry.models
            if _squash(m.family) not in squashed and not _named_in_parts(m.family, text)]


def family_named(resp: httpx.Response, entry: Entry, family: str) -> bool | None:
    """Whether what a row's probe reads names `family` the way the row's own
    families are held to: named on the page, or served free in the catalog lane.
    None when the response cannot answer — not JSON, or no rows to look in.

    What a generation bump is measured against before a human reads it: a newer
    generation this vendor does not serve cannot supersede one it does. On
    2026-09-14 the scout pointed Groq, Hetzner, OVH, LLMTR and FreeInference at
    qwen3.7-flash, which none of their pages or catalogs names."""
    asked = entry.model_copy(update={"models": [ModelFamily(family=family)]})
    if entry.probe.type is ProbeType.API_MODELS:
        items = _catalog_items(resp, entry.probe.lane)
        if items is None or not any(_model_id(m) for m in items):
            return None
        return _check_api_models(resp, asked) is None
    return not unevidenced_families(resp, asked)


def dead_model_ids(resp: httpx.Response, entry: Entry) -> list[str]:
    """Ids in `api.model_ids` that the catalog no longer answers for.

    This is the last curated field here that nothing ever read back. It is not
    the Models column, so neither `_check_api_models` nor `unevidenced_families`
    looks at it, and it is not on any page, so no keyword anchors it — yet it is
    the field that fills `configs/litellm.yaml`, `configs/opencode.json` and
    `configs/free-llm.env.example`, which is what a reader actually pastes into
    a client. Three scout pull requests running dropped a family from `models[]`
    and left its id here — bazaarlink in #10, opencode and vercel-ai-gateway in
    #11, openrouter-free in #12 — and each time the configs went on handing out
    an id that 404s until somebody happened to look. Measured 2026-08-28 across
    the ten live api-models entries: 7 of their 72 ids were already dead, spread
    over two rows whose probes were passing that morning.

    It is never asked of a page, for the reason `unevidenced_families` is
    deliberately weak: a page-keywords probe reads prose, and a name missing
    from prose is not a withdrawal. Here the consequence would be worse — a
    deletion from a config file rather than a flag on a column. A page row
    that names a keyless catalog in `probe.catalog` is asked of that catalog
    instead: on 2026-09-02 four of the twelve page rows carrying ids had one
    (Ollama, opencode Zen, SambaNova, Regolo), 18 of their 37 ids between them.
    Inception is deliberately not among them — mercury-edit-2 answers
    /v1/edit/completions and is absent from /v1/models by design, and a check
    that cannot tell that apart would call it dead on every run. A lane served
    only inside the vendor's own client keeps its ids in `client_lane`, and is
    asked the same question of the lane its probe reads.

    The match is exact, because `api.model_ids` holds what goes in the request
    body. `deepseek-ai/deepseek-v4-flash` and its live successor
    `deepseek-ai/deepseek-v4-flash-0731` are one model and two ids, and only the
    second one answers; a substring test would call the row healthy forever.
    That is also why a missing id is reported with any catalog id that extends
    it: NVIDIA re-versioned that row rather than dropping it, so the repair is a
    rename, and the two cases are indistinguishable without the hint.

    It never fails an entry and never repairs one. A free lane rotating its ids
    is this list doing its job — kilo-code's own note says so — so archiving a
    row over it would be the mistake `unevidenced_families` exists to avoid.
    And the repair is an exact string copied from a catalog, which is the last
    thing to let an LLM guess at: the scout is told to leave these rows for a
    human rather than sent off to fix them.
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
        elif _is_withdrawn(model):
            dead.append(f"{wanted} is marked unavailable")
        elif entry.probe.require_zero_price and not _is_free(model):
            dead.append(_price_note(model, entry.probe.free_list is not None))
    return dead


def unlisted_free_ids(resp: httpx.Response, entry: Entry) -> list[str]:
    """Ids the catalog prices at zero that `api.model_ids` does not carry.

    The other direction of dead_model_ids, and the one that stayed invisible
    after it was written: a check that reads only the ids the registry already
    has cannot see a lane grow. Measured 2026-09-02 across the eight live
    api-models rows whose prices the probe reads, eleven zero-priced ids sat
    unlisted on four rows whose probes were passing — Vercel 5, Routeway 3,
    Requesty 2, TokenRouter 1 — and the six Kilo had added that week had been
    found by hand. Each is a model a reader could have been calling.

    The lane is the row's own definition of it, not a bare zero. An id is in
    it when it carries `probe.free_marker` where the row sets one, is priced 0
    on ordinary tokens, and is not marked unavailable — the three tests the
    offer check and dead_model_ids already apply. The marker matters:
    OpenRouter and Kilo both price Google's Lyria music previews at 0 with no
    :free suffix, and Kilo marks them isFree: false; TokenRouter's
    stealth/ox-alpha is a zero-priced preview outside its lane. The check is
    asked only where prices are read, because on a catalog that publishes
    none — NVIDIA NIM, OVHcloud — every id would be free and the report would
    be the catalog.

    Ids in `api.ignored_ids` are left out: a zero somebody has read and left
    unlisted, with the reason in `api.note` — AIHubMix's two image generators,
    and a row whose own description says it was removed from the platform.
    Without the list those would print on every run, and a report that always
    prints is a report nobody reads.

    A lane the vendor lists under a key of its own (`probe.lane`) is asked
    too, prices or none: Cline's free lane is the vendor's whole account of
    what is free, so every id in it is in the lane, and ids in the paid lanes
    beside it are not.

    Like dead_model_ids it never fails a row and is never handed to the
    scout: an id to add is an exact string copied out of a catalog, and
    whether to add it — or to record it as ignored — is a judgement about what
    the row is for.
    """
    lane = lane_ids(entry)
    if (entry.probe.type is not ProbeType.API_MODELS or lane is None
            or not (entry.probe.require_zero_price or entry.probe.lane)):
        return []
    marker = entry.probe.free_marker.lower()
    known = set(lane.model_ids) | set(lane.ignored_ids)
    unlisted = set()
    for model in _catalog_items(resp, entry.probe.lane) or []:
        mid = _model_id(model)
        if (mid and mid not in known and (not marker or marker in mid.lower())
                and (_is_free(model) or not entry.probe.require_zero_price)
                and not _is_withdrawn(model)):
            unlisted.add(mid)
    return sorted(unlisted)


def _stale_ids_detail(dead: list[str], unlisted: list[str], entry: Entry) -> str:
    """One line for a human with both directions on it. A rename that changed
    the words of an id — the case _successor_hint cannot see — is a dead id on
    one side and an unlisted one on the other, and they belong together. On a
    row read with a free list the unlisted ids are the ones the list marks, and
    the line says so: that catalog prices nothing to be zero. The line names
    the list the ids belong in, `api` or `client_lane`, and a client lane has
    no ignored ids: it writes no config to keep an id out of."""
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


# How every note about a row's connection details opens — its ids against the
# catalog, its keyless or public-key lane, its Anthropic route, the page that
# prints its public key — and about its word on training, which only a person
# re-reading the vendor's data page can restate. Each follows a family verdict
# after " | ".
_FOR_A_HUMAN = ("api.model_ids ", "client_lane.model_ids ", "zero-priced ids in the catalog ",
                "ids the free list ", "ids in the ",
                "api.public_key ", "keyless ", "public-key ", "anthropic route ", "data_use ")


def for_a_human(detail: str) -> str:
    """The part of a verdict's detail the fix prompt tells the model to leave
    alone, or "" where there is none: whatever follows the family verdict once
    a note about the connection details begins. A row the scout repaired can
    still carry it to the pull request — on 2026-09-21 aihubmix's eight dead
    ids left with the family half the model did answer for."""
    parts = detail.split(" | ")
    for i, part in enumerate(parts):
        if part.startswith(_FOR_A_HUMAN):
            return " | ".join(parts[i:])
    return ""


def stale_ids(catalog: httpx.Response, entry: Entry) -> str:
    """What the catalog says about this row's published ids, in both
    directions, or "" while they are all backed.

    The verdict a passing row gets and the sentence a failing one carries
    beside its own failure are the same question asked of the same bytes, so
    they are the same call: whether the row is being verified or repaired says
    nothing about whether `api.model_ids` is still true.
    """
    dead = dead_model_ids(catalog, entry)
    unlisted = unlisted_free_ids(catalog, entry)
    return _stale_ids_detail(dead, unlisted, entry) if dead or unlisted else ""


def _successor_hint(wanted: str, catalog: dict[str, dict]) -> str:
    """The catalog ids a missing one may have turned into, when a vendor
    re-versioned or renamed the row instead of withdrawing it. A withdrawal and
    a rename want opposite edits, and they are indistinguishable without this.

    Two shapes count and nothing else. An id that *extends* the missing one:
    NVIDIA re-dated `deepseek-ai/deepseek-v4-flash` as
    `deepseek-ai/deepseek-v4-flash-0731`. And an id built from exactly the same
    words in a different order: on 2026-09-02 `nvidia/nemotron-3-nano-30b-a3b`
    left that same catalog while `nvidia/nemotron-nano-3-30b-a3b` sat in it,
    which no prefix test can see because the vendor moved the version into the
    middle of the name. Both stay honest in the case that matters — Routeway's
    `llama-3.1-8b-instruct:free` left its free lane while the metered
    `llama-3.1-8b-instruct` went on being served, and calling that twin the
    successor is exactly the confusion `require_zero_price` was added to stop.
    It neither extends the missing id nor carries the same words."""
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
    """Antigravity enumerates its free agent models as "Claude Sonnet & Opus
    4.6": two models sharing one version number, and neither of them a substring
    of the page. A warning that fires on entries that are correct is a warning
    that gets ignored, so a family also counts as named when its parts appear in
    order and close together.

    Each part must start where a name starts. Without that, the version half of
    a family name matches inside a *different* version and the check vouches for
    a model nobody offers: kiro.dev/pricing, which serves Sonnet 4.5 free and
    sells 4.6, named opus-5 for this function through the "5" in "Opus 4.5",
    and glm-5 through a "GLM" in a country-support FAQ and a "5" in the minified
    markup after it. Anchoring on the left is enough — anchoring on the right
    too would unname minimax-2.1, which that same page writes at the end of a
    sentence as "MiniMax 2.1.". Measured against every live page-keywords entry
    on 2026-08-14: no family this repository publishes changes verdict.

    The letter in front of a version number is the vendor's, and it moves. On
    2026-08-20 the same Kiro page restyled the free-tier footnote it had written
    as "DeepSeek v3.2 and MiniMax 2.1." into "DeepSeek 3.2, and MiniMax M2.1" —
    same two models, same sentence, same free tier, and both families unnamed
    for this function. That is not a Models column going stale, it is a caption
    being retyped, and it reached a scout PR proposing to delete two models the
    vendor still hands out for free. So a version part is matched through
    _version_pattern, which lets that prefix letter differ on either side.
    Measured the same way on 2026-08-20, across all 18 live page-keywords
    entries that publish a family: kiro is the only verdict that moves, and it
    moves to none.
    """
    parts = [p for p in re.split(r"[\s_-]+", family.lower()) if p]
    if len(parts) < 2:
        return False
    spread = r"[^\n]{0,%d}?" % NAME_SPREAD
    anchored = (r"(?<![\w.])" + (_version_pattern(p) or re.escape(p)) for p in parts)
    return re.search(spread.join(anchored), text) is not None


# A generation number the vendor may or may not put a letter in front of:
# "v3.2", "3.2" and "M2.1" are one part each, and the letter is the vendor's.
# The dot is required. A bare number carries no letter here, because a hashed
# "h5" in minified markup would then name glm-5 for any page that says GLM
# nearby — the exact failure the left anchor in _named_in_parts exists to stop,
# walked back in through the number.
DOTTED_VERSION = re.compile(r"[a-z]?(\d+(?:\.\d+)+)")


def _version_pattern(part: str) -> str | None:
    """How a dotted version part may be spelled, or None for any other part.

    Three vendors write one generation three ways — "v3.2", "3.2", "M2.1" — and
    the registry has to write it once, so the prefix letter is optional on both
    sides. Nothing else about the part is relaxed: "2.1" still has to start
    where a name starts, and still has to sit within NAME_SPREAD of the part
    before it.
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
    passing entries whose model families are all superseded, and passing entries
    flagged for their Models column or their `api.model_ids`."""
    needs_attention = []
    for e in entries:
        result = results.get(e.id)
        if result is None:
            continue
        # The vendor's own shutdown date has passed, or a reviewer took the row
        # off: the entry is archived for good and its endpoint is meant to be
        # dead. Re-verifying it would keep moving last_verified forward on a
        # service that is gone, and flagging it sends the scout off to "fix" the
        # probe — which is how GitHub Models' HTTP 410 crashed the 2026-08-03 run.
        if is_archived_for_good(e, today):
            continue
        # STALE_MODELS and STALE_IDS are passes with a note: the probe reached
        # the page and the offer was evidenced there, so the liveness
        # bookkeeping is the same one a PASS gets. Letting last_verified freeze
        # instead would archive the row by staleness in ARCHIVE_AFTER_DAYS over
        # a question about its Models column or its config ids — which is the
        # opposite of what either flag is for.
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
    chained past: on 2026-09-02 a new row went into a commit with a keyword
    its page did not carry, because the dry run printed the failure and
    exited 0 and the `&&` after it never noticed. Flags that verify a row —
    stale-ids, stale-models — are not counted; neither is INCONCLUSIVE, which
    is the row's problem to report and not the run's."""
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
    # failures.json never leaves the runner, so the count alone was the whole
    # public account of a probe that fails from CI and passes from a laptop —
    # the one class of failure that cannot be reproduced locally.
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
