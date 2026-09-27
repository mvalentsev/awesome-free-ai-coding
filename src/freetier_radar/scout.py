from __future__ import annotations

import argparse
import json
import os
import re
import time
import traceback
from functools import partial
from datetime import date
from pathlib import Path
from typing import Callable

import httpx
import yaml

from .discovery import Evidence, domain_of, fetch_page_texts, format_evidence, gather_evidence
from .models import (SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Entry, Source, Watched,
                     is_archived, is_blocked, is_covered, is_source_current,
                     is_watch_current, known_domains, load_blocklist, load_dismissed,
                     load_registry, load_sources, load_watchlist, save_registry, site_of,
                     probe_frequency, watch_match)
from .prober import (ProbeStatus, challenge_marker_hit, check_content, family_named,
                     for_a_human, join_free_list_sync, probe_page_url_sync,
                     unevidenced_families)

EDITABLE = {"offering", "limits", "card_required", "probe", "models"}

# How much of a watchlist reason to quote when a proposal is turned away. The PR
# body lists rejections on one line each; the full reason runs to a paragraph.
WATCH_REASON_IN_PR = 120

DISCOVERY_QUERIES = [
    "free tier LLM API for developers",
    "free LLM API no credit card",
    "AI coding agent free plan",
    "free frontier model API access",
    "new LLM inference provider free tier",
]

FALLBACK_OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"
PREFERRED_MODEL_HINTS = ("deepseek", "qwen", "gpt-oss", "glm", "llama")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Anonymous, keyless OpenAI-compatible endpoint (rate-limited) — last-resort
# backend so the scout keeps working with zero configured secrets.
OVH_BASE_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
OVH_PREFERRED_HINTS = ("gpt-oss", "qwen3")
RETRY_429_ATTEMPTS = 3
RETRY_429_SLEEP = 20.0

# Read timeout per backend call. The discovery prompt runs to ~20k tokens, and a
# reasoning model can spend minutes on it (the slowest measured answer took
# 202s); the run is twice a week, so waiting is cheap.
LLM_READ_TIMEOUT = 300.0

# Wall-clock ceiling for one backend call, which the read timeout is not — see
# `LLMClient._post`. It sits well above the slowest measured answer.
LLM_CALL_DEADLINE = 420.0

# Wall-clock budget for the whole scout run: four LLM phases over a five-backend
# chain could otherwise run for hours, and the scout is the optional half of the
# run, so a phase out of time is skipped. Overridable via SCOUT_DEADLINE_SECONDS.
SCOUT_DEADLINE_SECONDS = 1800.0

# The share of what is left of that budget the evidence phase may spend before
# the first LLM call (see `Deadline.share`). A working keyless run gathers its
# evidence in ~20s, so the cap only ever fires on a hang.
EVIDENCE_BUDGET_FRACTION = 0.25

# Listing a backend's models is a small GET and must not inherit the long read
# timeout meant for generation.
MODELS_LIST_TIMEOUT = 30.0

# What an OpenAI-compatible endpoint answers about a model it no longer serves:
# 400 (opencode Zen) or 404 (a stricter router). See `LLMClient._chat_any`.
BAD_MODEL_STATUS = (400, 404)

# How much of a refusal's body is read, and how much of the vendor's sentence
# reaches the log. A refusal is a short JSON error; the cap is for the backend
# that answers a status with a whole HTML page.
REFUSAL_BODY_LIMIT = 4096
REFUSAL_REASON_CHARS = 200

# Retirement sweep: one page per live entry, trimmed so the prompt stays small.
# A quote shorter than this is too weak to verify against a page.
RETIREMENT_PAGE_CHARS = 2500
MIN_QUOTE_CHARS = 25

# Only pages carrying one of these reach the LLM: every live page would cost tens
# of thousands of tokens for a question that is almost always "no", and could
# exceed a backend's context. The words are broad on purpose: a false positive
# costs a few hundred tokens, a miss costs a retirement.
RETIREMENT_SIGNALS = (
    "retir", "sunset", "discontinu", "deprecat", "shut down", "shutting down",
    "shutdown", "will end", "has ended", "end of life", "no longer available",
    "no longer be available", "no longer offer", "winding down", "last day",
)

SYSTEM_RULES = (
    "You update a registry of LEGAL free LLM coding resources. "
    "Output ONLY a yaml code block, no prose. Never invent URLs or limits: "
    "use only facts from the provided page texts. If unsure, output an empty list."
)

FIX_PROMPT = SYSTEM_RULES + """
TASK: FIX-FAILED probes. For each flagged entry, using its failure detail and
official page text below, propose corrected values (e.g. a working probe endpoint,
updated limits). Allowed keys per update: id (unchanged), offering, limits,
card_required, probe, models. An offering says what the offer is; on an entry of
free_part: models it names no model, since the models list does.
A "stale-models" failure means the probe passed and the offer is alive, but the
entry's model list is in doubt — every family listed for it was marked
superseded, the page no longer names a family the entry lists, or the catalog
no longer serves one of its families free while it still serves another. The
failure detail says which. Reply with a models list naming only families the
page text below names itself, and leave the probe alone.
A "missing families" detail, on that verdict or on a plain failure, names
families the entry lists and the evidence no longer backs. The list you reply
with replaces the old one whole: keep the families that still stand, drop the
one that went, and add the ones that replaced it where the page names them in
its place — a reply that only deletes turns a swapped generation into a model
the readers lose. Where the probe type is api-models the page text IS the
vendor's catalog, and a family counts only where the catalog still carries a
FREE id for it: an id matching the entry's free marker, and free by the
catalog's own flag or by a zero price where it publishes one. A family whose
only ids are metered is not a free model and fails the same probe next run.
A failure detail can carry more after " | " about api.model_ids or
client_lane.model_ids, free ids the catalog, its free list or its lane names, the
keyless lane, the Anthropic or Codex route, the public key, the data-use sentence or
the border — that half is addressed to a human and is not yours to repair: `api` and `client_lane` are not keys you may
write, and an exact id copied out of a catalog is not something to reproduce
from memory. Read it as evidence about which way the lane
moved, and answer only with the keys you are allowed.
A corrected page-keywords probe needs at least one keyword that dies with the
offer — a quota or price figure, a model id, or a sentence of four or more words
quoted verbatim from the page below — and it must be in what the page renders:
keywords are matched with script and style tags stripped out, so a string that
lives only in a state blob or an OpenAPI enum passes every run and proves
nothing. Words like "free", "hobby", "free quota" or "no credit card required"
are rejected for the same reason: they outlive the offer.
Output only the keys you are actually changing — never a null value, and skip an
entry entirely when you have nothing to correct for it.
Output format:
updates:
  - id: <existing id>
    <changed keys only>
FLAGGED ENTRIES, FAILURE DETAILS AND PAGE TEXTS:
{context}
"""

DISCOVER_PROMPT = SYSTEM_RULES + """
TASK: DISCOVER-NEW legal free coding tools / free-tier LLM APIs / no-card trials.
Existing ids (do not repeat): {existing}
Domains already covered (do not repeat): {domains}
Blocklisted domains (never propose): {blocked}
Checked recently and found to have no reachable free tier — propose one of these
ONLY if the evidence below shows the specific change named after "reopen if":
{watched}
Use ONLY the evidence below (search hits, fetched pages, curated feed excerpts).
Propose an entry ONLY when the evidence explicitly supports its free offering,
and set source_urls to the evidence URLs you used. Official vendor pages only —
no reverse proxies, key-sharing or scraped gateways. Every entry must be
directly usable by a developer in coding tools: either an HTTP API endpoint
(OpenAI-compatible or similar) that plugs into coding agents (opencode, Claude
Code, Codex CLI), or a coding agent/IDE/CLI itself with free included model
usage or credits. Browser-only SDKs, consumer-only apps, and BYOK-only tools
without any bundled free model usage do not qualify. The probe
endpoint must be a server-rendered page containing the keywords, or a public
JSON models API. Prefer the JSON models API whenever the vendor exposes one
without a key. At least one keyword must anchor on something that disappears
together with the offer, in one of these three shapes:
  - a figure: a quota, a price or a grant — "$0.10, subject to change",
    "anonymous users get one request every 15 seconds";
  - an id: the free model's id as the page prints it — "mistral-medium",
    "qwen/qwen3.8-27b";
  - a sentence of four or more words quoted verbatim from the page and specific
    to this offer — "free models through kilo gateway".
Keywords are matched against what the page renders, with its script and style
tags removed (JSON-LD excepted). A string that occurs only inside a state blob,
an OpenAPI enum, a response sample or an i18n bundle goes on matching long after
the offer it names is gone, so it anchors nothing and the proposal fails
verification.
Anything else is rejected outright, including "free", "hobby", "free quota",
"monthly credits", "no signup" and "no credit card required": those sit on a
vendor page for months after the free tier is withdrawn, so a probe built out of
them verifies nothing but that the page still loads. Copy keywords verbatim from
the evidence — a keyword that is not literally on the page fails immediately.
On a gateway that publishes per-model prices, also set require_zero_price: true,
so that an id kept in the catalog after it starts costing money fails the probe.
Output format:
new_entries:
  - id: <slug>
    name: ...
    category: agent-cli | api-free-tier | trial | aggregator
    url: <official site>
    source_urls: [...]
    card_required: false
    offering: ...          # what the offer is — the product, how it is reached, what it
                           #   asks; with free_part: models it names no model: models does
    limits: ...
    free_part: models | sum | unnamed
                           # models: the vendor names the models its free part serves — a
                           #   free lane, a zero price, a free quota per model, a free tier or
                           #   trial that names them, caps counted alike on every model;
                           # sum: only an amount spent across the catalog — a signup credit,
                           #   a grant of tokens every model draws on, an allowance at each
                           #   model's own price — so no model is free by itself;
                           # unnamed: the vendor does not say which models the free part reaches
    models:                # ONLY with free_part: models, and ONLY models actually usable for
                           # free on the free tier/plan, never the vendor's paid catalog; omit
                           # when the evidence is silent
      - {{family: <substring of the vendor's API model ids, the most specific one>}}
                           # no tier: tiers are measured on Artificial Analysis, never proposed
    probe: {{type: page-keywords, endpoint: <official url>,
             keywords: ["<free model id / quota figure / price row>", "free"]}}
           # or, when a keyless models API exists:
           {{type: api-models, endpoint: <https://.../v1/models>, free_marker: '',
             require_zero_price: true}}   # true whenever the API publishes prices
Max 8. Empty list if the evidence shows nothing new.
EVIDENCE:
{evidence}
"""

RETIREMENT_PROMPT = SYSTEM_RULES + """
TASK: FIND-RETIREMENTS. Below are live entries and the current text of their
official pages. Report an entry ONLY when its own page announces that the free
offering is ending or has already ended, and gives a date. A price change, a
paid plan, a deprecated model or a retired unrelated product is NOT a
retirement. Copy the announcing sentence verbatim from the page text — an
entry whose quote is not on the page is discarded.
Output format:
retire:
  - id: <existing id>
    retired_on: YYYY-MM-DD   # the day the free offering stops
    quote: <verbatim sentence from the page text below>
Empty list if no page announces one.
ENTRIES AND PAGE TEXTS:
{context}
"""

GENERATIONS_PROMPT = SYSTEM_RULES + """
TASK: MODEL-GENERATIONS. These model families are currently listed: {families}
Mark families that have a clearly newer generation from the same vendor.
A newer generation must be a DIFFERENT family: never mark a family as
superseded by a model or variant of that same family (e.g. nemotron is
not superseded by nemotron-3-ultra). When unsure, do not mark.
Output format:
supersede:
  - family: <old family>
    superseded_by: <newer family>
Empty list if nothing is clearly superseded.
"""

PR_BODY_TEMPLATE = """## Scout proposals

Discovery sources used: {providers}
Curated feeds that need a look: {feed_warnings}
Backend chain: {backend}
Pinned scout models this registry does not list under that base url: {unlisted_pins}

Updated entries: {updates}
New entries (probe-verified): {new}
Rejected candidates: {rejected}
Flagged by the probe and still unfixed — these need a human: {unfixed}
Retirements announced by the vendor: {retired}
Phases skipped (out of wall-clock budget): {skipped}
Phases that asked and got nothing — every backend in the chain failed: {llm_outages}

Generation bumps suggested — **not applied**, edit registry.yaml yourself if a
free tier really moved on: {supersede}
Already dismissed in dismissed.yaml, not proposed again: {suppressed}
Ruled out by the scout itself — a model of the same family, a family the row
already lists, one the row's own probe page or catalog does not name, or a bump
that would hide a family the row still serves: {supersede_filtered}

Watchlist verdicts due for a re-check (older than {recheck_days} days, and no
longer suppressing anything): {stale_watch}

Lists declined as feeds and due for a re-read (older than {source_days} days):
{stale_sources}

_Proposed by the web-evidence scout — review before merging. After the merge the probes re-verify it {schedule}._
"""


class DeadlineExceeded(RuntimeError):
    """A backend held the call open past the run's wall-clock budget."""


class Deadline:
    """The run's remaining wall-clock time, shared by every phase and every call.

    One budget rather than a per-phase allowance: the phases run in order of
    value — fixes, then discovery, then the optional sweeps — so a slow first
    phase eats into the last one, not into the job.
    """

    def __init__(self, seconds: float, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._end = clock() + seconds

    def remaining(self) -> float:
        return self._end - self._clock()

    def expired(self) -> bool:
        return self.remaining() <= 0

    def share(self, fraction: float) -> "Deadline":
        """A sub-budget for a phase that must not be able to spend the run.

        Taken from what is left, so it can never outlive the run. The exception
        to the one-budget rule: the phases ordered by value are the LLM ones,
        and a phase that only feeds them, like evidence gathering, must not be
        able to starve them.
        """
        return Deadline(self.remaining() * fraction, self._clock)


def _model_candidates(pinned: str | None, published: list[str]) -> list[str]:
    """The pinned model first, then the ids the registry publishes for that
    endpoint, deduplicated with the order kept. A pin is a deliberate choice and
    outranks the list; the list is what the pin falls back to once the vendor
    retires it."""
    return list(dict.fromkeys(m for m in ([pinned] if pinned else []) + list(published) if m))


def published_model_ids(entries: list[Entry]) -> dict[str, list[str]]:
    """Every API base url this registry publishes, mapped to the model ids it
    lists under it. Retired and delisted rows are left out: their ids are
    precisely the ones a vendor stopped serving, or that stopped being free."""
    pools: dict[str, list[str]] = {}
    for entry in entries:
        if (entry.retired_on is not None or entry.delisted is not None
                or entry.api is None or not entry.api.base_url):
            continue
        pools.setdefault(entry.api.base_url.rstrip("/"), []).extend(entry.api.model_ids)
    return pools


class NoCompletion(RuntimeError):
    """An HTTP 200 whose body carries no choices — a gateway reporting an
    upstream failure inside a success status, the way Kilo's does for an
    overloaded model. The message is the vendor's own sentence."""


def refusal_reason(body: bytes) -> str:
    """What a refused call's body says, on one line: the `error.message` of an
    OpenAI-style error, a bare `error` or `message` string, or the text itself.
    An HTML page says nothing a log line can use, so it reads as no reason."""
    text = body.decode("utf-8", "replace").strip()
    if not text or text.startswith("<"):
        return ""
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    message: object = text
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            message = error["message"]
        elif isinstance(error, str):
            message = error
        elif isinstance(data.get("message"), str):
            message = data["message"]
    return " ".join(str(message).split())[:REFUSAL_REASON_CHARS]


class LLMClient:
    """Ordered backend chain, first success wins:

    1. custom OpenAI-compatible endpoint (SCOUT_BASE_URL / SCOUT_MODEL /
       optional SCOUT_API_KEY) — point it at NVIDIA NIM, Groq, Cerebras, ...
    2. a second endpoint of the same kind (SCOUT_FALLBACK_BASE_URL /
       SCOUT_FALLBACK_MODEL / SCOUT_FALLBACK_API_KEY)
    3. Gemini API                 (GEMINI_API_KEY)
    4. OpenRouter :free models    (OPENROUTER_API_KEY, model picked live)
    5. anonymous OVH AI Endpoints (no key at all)

    A custom backend's model is a repository variable, outside the registry and
    outside review, so it can name an id the vendor has retired or stopped
    serving free. `models_by_base_url` hands each custom backend the model_ids
    of the registry rows that publish its base url: the configured model is
    tried first, as a pin, and the ids the registry certifies as free stand
    behind it.
    """

    def __init__(self, gemini_key: str | None = None, openrouter_key: str | None = None,
                 openrouter_model: str | None = None,
                 # Google keeps the 2.5 models for keys that already used them;
                 # its changelog: "For any new projects, use our latest models:
                 # 3.5 Flash-Lite or 3.8 Flash".
                 gemini_model: str = "gemini-3.8-flash",
                 custom_base_url: str | None = None, custom_model: str | None = None,
                 custom_key: str | None = None,
                 fallback_base_url: str | None = None, fallback_model: str | None = None,
                 fallback_key: str | None = None,
                 models_by_base_url: dict[str, list[str]] | None = None,
                 http: httpx.Client | None = None,
                 deadline: Deadline | None = None,
                 call_deadline: float = LLM_CALL_DEADLINE,
                 force: str | None = None,
                 clock: Callable[[], float] = time.monotonic):
        self._gemini_key = gemini_key
        self._or_key = openrouter_key
        self._or_model = openrouter_model
        self._gemini_model = gemini_model
        # Both are plain OpenAI-compatible endpoints; an entry is used only when
        # it has a url and at least one model to try, so a half-configured spare
        # stays out.
        pools = models_by_base_url or {}
        self.unlisted_pins: list[str] = []
        self._customs: list[tuple[str, str, list[str], str | None]] = []
        for name, url, model, key in (
            ("custom", custom_base_url, custom_model, custom_key),
            ("custom-fallback", fallback_base_url, fallback_model, fallback_key),
        ):
            if not url:
                continue
            base = url.rstrip("/")
            published = pools.get(base, [])
            candidates = _model_candidates(model, published)
            if candidates:
                self._customs.append((name, base, candidates, key))
            # A pin the registry does not list for its endpoint goes to the PR
            # body: either the variable or the row's ids are wrong, and only a
            # human can tell which. An endpoint the registry does not describe
            # at all claims nothing.
            if model and published and model not in published:
                self.unlisted_pins.append(f"{name}: {model} on {base}")
        # (base url, model) pairs the endpoint has disowned during this run.
        self._dead_models: set[tuple[str, str]] = set()
        self._ovh_model: str | None = None
        self.answered_by: str | None = None
        self.answered_model: str | None = None
        self._deadline = deadline
        self._call_deadline = call_deadline
        self._clock = clock
        # "auto" is what the workflow sends when nobody picked a backend, so the
        # dispatch input needs no conditional around it.
        forced = (force or "").strip().lower()
        self._force = None if forced in ("", "auto") else forced
        self._http = http or httpx.Client(
            timeout=httpx.Timeout(LLM_READ_TIMEOUT, connect=15.0))

    def _backends(self) -> list[tuple[str, Callable[[str], str]]]:
        backends: list[tuple[str, Callable[[str], str]]] = [
            (name, partial(self._chat_any, url, candidates, key))
            for name, url, candidates, key in self._customs
        ]
        if self._gemini_key:
            backends.append(("gemini", self._gemini))
        if self._or_key:
            backends.append(("openrouter", self._openrouter))
        backends.append(("ovh-anonymous", self._ovh))
        return backends

    def complete(self, prompt: str) -> str:
        backends = self._backends()
        if self._force is not None:
            # Forcing exercises a backend that never gets its turn in the chain;
            # falling through to another would defeat that, so an unconfigured
            # name is an error, not a silent chain run.
            backends = [b for b in backends if b[0] == self._force]
            if not backends:
                raise RuntimeError(
                    f"forced backend {self._force!r} is not configured; available: "
                    + ", ".join(n for n, _ in self._backends()))
        errors = []
        for name, fn in backends:
            started = self._clock()
            try:
                text = fn(prompt)
                if not isinstance(text, str) or not text.strip():
                    raise RuntimeError("empty completion")
                # Name the backend and the model that answered: a run that fell
                # through the chain otherwise reads like a healthy one.
                model = f" ({self.answered_model})" if self.answered_model else ""
                print(f"scout backend {name}{model} answered in {self._clock() - started:.0f}s")
                self.answered_by = name
                return text
            # Broad on purpose: whatever a backend does wrong — a truncated
            # body, invalid JSON — all this loop can do is move to the next one.
            except Exception as exc:
                print(f"scout backend {name} failed: {type(exc).__name__}: {exc}")
                errors.append(f"{name}: {type(exc).__name__}: {exc}")
        raise RuntimeError("all LLM backends failed: " + "; ".join(errors))

    def describe(self) -> str:
        """One line for the PR body: what the chain was, and who answered."""
        chain = " → ".join(n for n, _ in self._backends())
        head = f"forced {self._force} (configured: {chain})" if self._force else chain
        answered = self.answered_by or "nothing"
        if self.answered_by and self.answered_model:
            answered += f" ({self.answered_model})"
        return f"{head} — answered by {answered}"

    def _budget(self) -> float:
        """Seconds this call may take: its own ceiling, or whatever is left of
        the run — whichever is shorter."""
        budget = self._call_deadline
        if self._deadline is not None:
            budget = min(budget, self._deadline.remaining())
        if budget <= 0:
            raise DeadlineExceeded("no wall-clock budget left for this run")
        return budget

    def _post(self, url: str, headers: dict[str, str], payload: dict) -> tuple[int, bytes]:
        """POST and read the body against the clock, returning (status, body).

        httpx's timeout is per read, not per call, so a backend that answers
        HTTP 200 and then trickles bytes never trips it. Reading in chunks
        against the wall clock makes that an ordinary backend failure the chain
        steps over. The read timeout, capped by the same budget, still catches
        a backend that says nothing at all.
        """
        budget = self._budget()
        end = self._clock() + budget
        timeout = httpx.Timeout(min(LLM_READ_TIMEOUT, budget), connect=15.0)
        with self._http.stream("POST", url, headers=headers, json=payload,
                               timeout=timeout) as r:
            if r.status_code == 429:
                return r.status_code, b""
            if r.is_error:
                raise self._refusal(r, end)
            chunks = []
            for chunk in r.iter_bytes():
                chunks.append(chunk)
                if self._clock() > end:
                    raise DeadlineExceeded(
                        f"{url} was still streaming after {budget:.0f}s")
        return r.status_code, b"".join(chunks)

    def _refusal(self, r: httpx.Response, end: float) -> httpx.HTTPStatusError:
        """The error for a refused call, carrying the start of the vendor's body.

        A streamed response has none of its body read yet, and the body is where
        the vendor says why. Read against the same clock as a success, and
        capped, since a refusal can be a whole HTML page. The message leaves the
        url out: Gemini's carries the key."""
        body = b""
        for chunk in r.iter_bytes():
            body += chunk
            if len(body) >= REFUSAL_BODY_LIMIT or self._clock() > end:
                break
        reason = refusal_reason(body)
        kept = httpx.Response(r.status_code, content=body[:REFUSAL_BODY_LIMIT],
                              request=r.request)
        return httpx.HTTPStatusError(
            f"HTTP {r.status_code}" + (f": {reason}" if reason else ""),
            request=r.request, response=kept)

    def _chat_any(self, base_url: str, candidates: list[str], key: str | None,
                  prompt: str) -> str:
        """Try this endpoint's models in turn, dropping the ones it disowns.

        A vendor can retire a model id while the endpoint and the key stay good,
        so a BAD_MODEL_STATUS answer costs a candidate, not the backend. So does
        an HTTP 200 with no choices in it, a gateway's way of saying the
        upstream behind one model failed. Every other answer — 401, the 402 of a
        spent wallet, 429, 5xx, a trickle — is the backend's own problem and
        goes to the chain above.
        """
        rejected = []
        for model in candidates:
            # Remembered for the whole run: four phases against one endpoint
            # would otherwise pay for the same retired id four times over.
            if (base_url, model) in self._dead_models:
                continue
            try:
                return self._chat(base_url, model, key, prompt)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in BAD_MODEL_STATUS:
                    raise
                self._dead_models.add((base_url, model))
                reason = refusal_reason(exc.response.content)
                rejected.append(f"{model} ({exc.response.status_code}"
                                + (f": {reason})" if reason else ")"))
            except NoCompletion as exc:
                # A gateway's upstream failing for one model says nothing about
                # the others behind it, and it may recover by the next phase,
                # so the candidate is skipped for this call rather than for the
                # run.
                rejected.append(f"{model} (no completion: {exc})")
        raise RuntimeError(
            "no model this endpoint still serves"
            + (f": {', '.join(rejected)}" if rejected else ""))

    def _chat(self, base_url: str, model: str, key: str | None, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        for attempt in range(RETRY_429_ATTEMPTS):
            status, body = self._post(
                f"{base_url}/chat/completions", headers,
                {"model": model, "messages": [{"role": "user", "content": prompt}]},
            )
            if status != 429:
                data = json.loads(body)
                choices = data.get("choices") if isinstance(data, dict) else None
                if not choices:
                    raise NoCompletion(refusal_reason(body) or "an answer without choices")
                self.answered_model = model
                return choices[0]["message"]["content"]
            if attempt + 1 < RETRY_429_ATTEMPTS:
                time.sleep(RETRY_429_SLEEP)
        raise RuntimeError("rate-limited on every attempt")

    def _gemini(self, prompt: str) -> str:
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self._gemini_model}:generateContent?key={self._gemini_key}")
        _, body = self._post(url, {}, {"contents": [{"parts": [{"text": prompt}]}]})
        return json.loads(body)["candidates"][0]["content"]["parts"][0]["text"]

    def _openrouter(self, prompt: str) -> str:
        if self._or_model is None:
            self._or_model = pick_openrouter_model(self._http, self._list_timeout())
        return self._chat(OPENROUTER_BASE_URL, self._or_model, self._or_key, prompt)

    def _ovh(self, prompt: str) -> str:
        if self._ovh_model is None:
            self._ovh_model = pick_ovh_model(self._http, self._list_timeout())
        return self._chat(OVH_BASE_URL, self._ovh_model, None, prompt)

    def _list_timeout(self) -> float:
        """The catalog read a backend picks its model from is held to the run's
        budget like the call itself: a spent budget reads no catalog."""
        return min(MODELS_LIST_TIMEOUT, self._budget())


def _list_model_ids(http: httpx.Client, base_url: str,
                    timeout: float = MODELS_LIST_TIMEOUT) -> list[str]:
    r = http.get(f"{base_url}/models", timeout=timeout)
    r.raise_for_status()
    return [str(m.get("id", "")) for m in r.json().get("data", []) if isinstance(m, dict)]


def pick_openrouter_model(http: httpx.Client, timeout: float = MODELS_LIST_TIMEOUT) -> str:
    """Pick a currently-listed :free model so the fallback never rots."""
    try:
        ids = _list_model_ids(http, OPENROUTER_BASE_URL, timeout)
    except (httpx.HTTPError, json.JSONDecodeError):
        return FALLBACK_OPENROUTER_MODEL
    free = [i for i in ids if i.endswith(":free")]
    for hint in PREFERRED_MODEL_HINTS:
        for model_id in free:
            if hint in model_id:
                return model_id
    return free[0] if free else FALLBACK_OPENROUTER_MODEL


def pick_ovh_model(http: httpx.Client, timeout: float = MODELS_LIST_TIMEOUT) -> str:
    """Pick a live model on the anonymous OVH endpoint (errors fail the backend over)."""
    ids = _list_model_ids(http, OVH_BASE_URL, timeout)
    for hint in OVH_PREFERRED_HINTS:
        for model_id in ids:
            if hint in model_id.lower():
                return model_id
    if not ids:
        raise RuntimeError("no models listed on OVH endpoint")
    return ids[0]


def extract_yaml_block(text: str) -> str:
    m = re.search(r"```(?:yaml)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def _parse(text: str) -> dict:
    data = yaml.safe_load(extract_yaml_block(text))
    return data if isinstance(data, dict) else {}


def _ask(llm, prompt: str, attempts: int = 2) -> dict:
    """LLM replies are untrusted YAML: retry a malformed one, then degrade to {}."""
    for attempt in range(attempts):
        try:
            return _parse(llm.complete(prompt))
        except yaml.YAMLError as exc:
            print(f"unparseable LLM reply (attempt {attempt + 1}/{attempts}): {exc}")
    return {}


def answered_domains(watchlist: list[Watched], blocklist: dict[str, str], today: date) -> set[str]:
    """Domains the curated files have already answered for, which the models.dev
    digest leaves out: the watchlist's current verdicts and the whole blocklist.
    An expired verdict answers nothing, as in `format_watchlist`, so its
    domains are not in the set and their zero-cost rows reach the digest again."""
    watched = {d.lower() for w in watchlist if is_watch_current(w, today) for d in w.domains}
    return watched | {b.lower() for b in blocklist}


def format_watchlist(watchlist: list[Watched], today: date) -> str:
    """The current verdicts, for the discovery prompt.

    Expired ones are left out: a verdict the file no longer trusts must not keep
    a service out, or the watchlist becomes a blocklist. `reopen_if` goes in,
    since the instruction is "propose it when this changed" and the model is
    reading evidence the verdict never saw.
    """
    current = [w for w in watchlist if is_watch_current(w, today)]
    if not current:
        return "none"
    return "\n".join(
        f"- {w.name} ({', '.join(w.domains)}), checked {w.checked_on.isoformat()}: "
        f"{w.reason.strip()}"
        + (f" — reopen if: {w.reopen_if.strip()}" if w.reopen_if else "")
        for w in current
    )


def probe_check_sync(entry: Entry, client: httpx.Client) -> str | None:
    """The run's probe, synchronous and single-shot, for vetting a proposal or a
    corrected row: None when the entry passes, else why it fails."""
    try:
        resp = client.get(probe_page_url_sync(client, entry.probe), follow_redirects=True)
    except httpx.HTTPError as exc:
        return f"unreachable: {exc}"
    if resp.status_code >= 400:
        return f"HTTP {resp.status_code}"
    if entry.probe.free_list is not None:
        resp, failure = join_free_list_sync(client, entry, resp)
        if resp is None:
            return failure
    problem = check_content(resp, entry)
    if problem is None:
        # The run only flags a live row for this (see `unevidenced_families`); a
        # proposal or a correction has nothing live to protect and is refused.
        unevidenced = unevidenced_families(resp, entry)
        return ("listed families the page does not name: " + ", ".join(unevidenced)
                if unevidenced else None)
    # Name a bot wall in the rejection: "missing keywords" reads as a bad
    # proposal, while "bot challenge" tells the reviewer the endpoint walls off
    # everything that is not a browser.
    challenge = challenge_marker_hit(resp.text)
    return f'bot challenge: page says "{challenge}"' if challenge else problem


def _measured_marks(models: object, entries: list[Entry]) -> object:
    """A proposal's models with the tiers the registry measured, and no others.

    A tier is read from Artificial Analysis by freetier-tiers, never taken on a
    model's word, so whatever tier or aa_model a proposal writes is dropped, and
    a family the registry has already measured gets the registry's marks back —
    which also keeps one tier per family in the pull request. Anything that is
    not a list of mappings is passed through for validation to refuse."""
    if not isinstance(models, list):
        return models
    marks = {m.family: (m.tier, m.aa_model) for e in entries for m in e.models if m.aa_model}
    out = []
    for m in models:
        if not isinstance(m, dict):
            out.append(m)
            continue
        m = {k: v for k, v in m.items() if k not in ("tier", "aa_model")}
        if m.get("family") in marks:
            tier, aa_model = marks[m["family"]]
            m.update(tier=tier.value if tier else None, aa_model=aa_model)
        out.append(m)
    return out


def apply_updates(entries: list[Entry], updates: list[dict],
                  verifier: Callable[[Entry], str | None] | None = None,
                  named: Callable[[Entry, str], bool | None] | None = None,
                  ) -> tuple[list[str], list[str]]:
    """Apply the LLM's corrections to flagged entries.

    Returns (applied ids, rejected "id: reason" strings). One bad update must
    not sink the run (see `main`): an update that does not validate is
    rejected, and one that does is run through `verifier`, the check a proposal
    passes — a fix that leaves the row failing is refused, the row keeps its
    values, and the reason goes to the PR.

    A shorter Models column always passes, so the verifier cannot see a reply
    that drops too much. A family the reply drops is kept wherever `named` —
    the row's own probe, read the way the run reads it — still finds it, unless
    a reviewer has marked it superseded, and the PR says which. On a page row
    that is presence on the page, as on every run, so a family the page now
    names only as paid is kept for the reviewer to judge."""
    applied, rejected = [], []
    for i, e in enumerate(entries):
        upd = next((u for u in updates if isinstance(u, dict) and u.get("id") == e.id), None)
        if not upd:
            continue
        # A null means "unchanged", never "erase this field": the model writes
        # one whenever it has nothing to change for a key the prompt named.
        changed = {k: upd[k] for k in EDITABLE if upd.get(k) is not None}
        if not changed:
            continue
        if "models" in changed:
            changed["models"] = _measured_marks(changed["models"], entries)
        try:
            fixed = Entry.model_validate({**e.model_dump(mode="json"), **changed})
        except Exception as exc:
            print(f"update for {e.id} rejected: {exc}")
            rejected.append(f"{e.id}: invalid update to {', '.join(sorted(changed))}"
                            f" — {_why(exc)}")
            continue
        kept = []
        if "models" in changed and named is not None:
            left = {m.family for m in fixed.models}
            kept = [m for m in e.models if m.family not in left and not m.superseded_by
                    and named(fixed, m.family) is True]
            if kept:
                fixed = fixed.model_copy(update={"models": [*fixed.models, *kept]})
        problem = verifier(fixed) if verifier is not None else None
        if problem:
            print(f"update for {e.id} rejected: {problem}")
            rejected.append(f"{e.id}: update to {', '.join(sorted(changed))}"
                            f" still fails the probe — {problem}")
            continue
        entries[i] = fixed
        applied.append(e.id)
        if kept:
            rejected.append(f"{e.id}: the update dropped {', '.join(m.family for m in kept)}, "
                            "which the row's own probe still names — kept")
    return applied, rejected


def _why(exc: Exception) -> str:
    """The rejection in one line, for the PR body rather than the run log: a
    reviewer reads the PR, and nobody reads the log of a run that succeeded.
    A validation error gives its first three errors as `loc: msg`, anything else
    its first line."""
    errors = getattr(exc, "errors", None)
    if not callable(errors):
        return str(exc).splitlines()[0]
    return "; ".join(f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}"
                     for err in errors()[:3]) or str(exc).splitlines()[0]


def apply_new(entries: list[Entry], new_entries: list[dict], today: date,
              verifier: Callable[[Entry], str | None] | None = None,
              blocklist: dict[str, str] | None = None,
              watchlist: list[Watched] | None = None,
              ) -> tuple[list[str], list[str]]:
    """Validate, dedupe (by id and by every site the registry reaches a row at —
    see `is_covered`), blocklist- and watchlist-filter, and probe-verify proposals.

    Returns (added ids, rejected "id: reason" strings). With no verifier the
    probe check is skipped (tests, offline runs).

    The watchlist filter is checked after the blocklist and before the probe: a
    service with no free tier usually still serves a page, so its proposal would
    burn a live probe on a question a human already answered. An expired verdict
    filters nothing (see `format_watchlist`)."""
    existing_ids = {e.id for e in entries}
    # An id is a published page for good. A proposal under an archived row's id
    # is a vendor coming back: it is reported, for a reviewer to restore that
    # row, rather than dropped as a duplicate.
    archived_ids = {e.id for e in entries if is_archived(e, today)}
    existing_sites = known_domains(entries)
    added, rejected = [], []
    for raw in new_entries:
        if not isinstance(raw, dict):
            continue
        rid = raw.get("id", "<missing id>")
        if rid in archived_ids:
            rejected.append(f"{rid}: an archived row holds this id — if the offer is back, "
                            "restore that row instead of adding a second one")
            continue
        if rid in existing_ids:
            continue
        if "models" in raw:
            raw = {**raw, "models": _measured_marks(raw["models"], entries)}
        try:
            e = Entry.model_validate({**raw, "first_seen": today, "last_verified": today,
                                      "provisional": True, "probe_failures": 0})
        except Exception as exc:
            rejected.append(f"{rid}: invalid — {_why(exc)}")
            continue
        if blocklist and is_blocked(domain_of(e.url), blocklist):
            rejected.append(f"{e.id}: blocklisted domain")
            continue
        if is_covered(e.url, existing_sites):
            rejected.append(f"{e.id}: domain already covered")
            continue
        watched = watch_match(domain_of(e.url), watchlist or [], today)
        if watched is not None:
            # Cut by length rather than at the first full stop: the reasons are
            # full of hostnames and prices, which a split on "." cuts in half.
            reason = " ".join(watched.reason.split())
            if len(reason) > WATCH_REASON_IN_PR:
                reason = reason[:WATCH_REASON_IN_PR].rsplit(" ", 1)[0] + "…"
            rejected.append(
                f"{e.id}: on the watchlist since {watched.checked_on.isoformat()} — {reason}")
            continue
        if verifier is not None:
            problem = verifier(e)
            if problem is not None:
                rejected.append(f"{e.id}: probe failed ({problem})")
                continue
        entries.append(e)
        existing_ids.add(e.id)
        existing_sites |= known_domains([e])
        added.append(e.id)
    return added, rejected


def supersede_proposals(entries: list[Entry], supersede: list[dict],
                        dismissed: set[tuple[str, str, str]] | None = None,
                        named: Callable[[Entry, str], bool | None] | None = None,
                        ) -> tuple[list[str], list[str], list[str]]:
    """Describe generation bumps for a human to accept — never write them.

    A superseded mark decides what the README lists as free, while the model
    proposing it sees only family names — no entry, no limits, no page — so it
    cannot tell what the free tier serves today.

    Returns (proposed, suppressed, filtered). Only bumps that would change
    something are reported, and a bump listed in dismissed.yaml is reported as
    suppressed rather than dropped, so the filter stays visible. `filtered` is
    what the scout rules out itself: a target of the same family, a target the
    row already lists, a target `named` says the row's own probe page or
    catalog lane does not name, and a family `named` still finds there, which a
    mark would hide while the vendor serves it. What is left is the old family
    gone from the row's evidence and the new one in it. `named` answering None
    means the page could not be read, and the bump goes through."""
    dismissed = dismissed or set()
    proposed, suppressed, filtered = [], [], []
    for s in supersede:
        family, target = s.get("family"), s.get("superseded_by")
        if not family or not target:
            continue
        for e in entries:
            for m in e.models:
                if m.family == family and m.superseded_by != target:
                    line = f"{e.id}: {family} → {target}"
                    if (e.id, family, target) in dismissed:
                        suppressed.append(line)
                    elif target.startswith(family + "-"):
                        filtered.append(f"{line} (a model of the same family)")
                    elif any(other.family == target for other in e.models):
                        filtered.append(f"{line} (the row already lists it)")
                    elif named is not None and named(e, target) is False:
                        filtered.append(f"{line} (not named where the row's probe reads)")
                    elif named is not None and named(e, family) is True:
                        filtered.append(f"{line} (the row's probe still names {family} too)")
                    else:
                        proposed.append(line)
    return proposed, suppressed, filtered


def named_by_row(client: httpx.Client, time_left: Callable[[], float] | None = None,
                 ) -> Callable[[Entry, str], bool | None]:
    """`family_named` against each row's own probe endpoint, read once a row
    however often it is asked. None — nothing known — when the endpoint cannot
    be read or the run's budget is spent, so an unchecked bump still reaches a
    human."""
    responses: dict[str, httpx.Response | None] = {}

    def named(entry: Entry, family: str) -> bool | None:
        if entry.id not in responses:
            if time_left is not None and time_left() <= 0:
                return None
            try:
                resp = client.get(probe_page_url_sync(client, entry.probe), follow_redirects=True)
            except httpx.HTTPError:
                resp = None
            if resp is not None and resp.status_code < 400 and entry.probe.free_list is not None:
                resp, _ = join_free_list_sync(client, entry, resp)
            responses[entry.id] = resp if resp is not None and resp.status_code < 400 else None
        resp = responses[entry.id]
        return None if resp is None else family_named(resp, entry, family)

    return named


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _has_retirement_signal(text: str) -> bool:
    lowered = text.lower()
    return any(s in lowered for s in RETIREMENT_SIGNALS)


def _retirement_excerpt(text: str) -> str:
    """The RETIREMENT_PAGE_CHARS the model is shown, cut around the first
    signal rather than from the top of the page: the signal is searched in
    every character the fetcher keeps, and the model must copy the announcing
    sentence verbatim from what it is shown."""
    lowered = text.lower()
    hits = [i for i in (lowered.find(s) for s in RETIREMENT_SIGNALS) if i != -1]
    start = max(0, min(hits, default=0) - RETIREMENT_PAGE_CHARS // 4)
    return text[start:start + RETIREMENT_PAGE_CHARS]


def apply_retirements(entries: list[Entry], retire: list[dict],
                      pages: dict[str, str]) -> list[str]:
    """Set retired_on from a vendor's own shutdown announcement.

    The quote has to appear verbatim in the page text we fetched — a retirement
    date is the one field that archives a live entry outright, so a paraphrased
    or invented announcement must not be able to set it."""
    applied = []
    by_id = {e.id: e for e in entries}
    for r in retire:
        if not isinstance(r, dict):
            continue
        entry = by_id.get(r.get("id"))
        quote = _flatten(str(r.get("quote", "")))
        if entry is None or entry.retired_on is not None or len(quote) < MIN_QUOTE_CHARS:
            continue
        if quote not in _flatten(" ".join(pages.get(u, "") for u in entry.source_urls)):
            continue
        try:
            when = date.fromisoformat(str(r.get("retired_on", "")))
        except ValueError:
            continue
        entry.retired_on = when
        applied.append(f"{entry.id} ({when.isoformat()})")
    return applied


def run_scout(llm, entries: list[Entry], failures: list[dict],
              page_fetcher: Callable[[list[str]], dict[str, str]], today: date,
              evidence: Evidence | None = None,
              verifier: Callable[[Entry], str | None] | None = None,
              blocklist: dict[str, str] | None = None,
              dismissed: set[tuple[str, str, str]] | None = None,
              watchlist: list[Watched] | None = None,
              sources: list[Source] | None = None,
              deadline: Deadline | None = None,
              named: Callable[[Entry, str], bool | None] | None = None) -> dict:
    result = {"updates": [], "new": [], "rejected": [], "supersede": [], "suppressed": [],
              "supersede_filtered": [],
              "retired": [], "skipped": [],
              # Phases on which every backend failed — see lost_to_backends.
              "llm_outages": [],
              # Filled in below, from what the fixes phase did not repair.
              "unfixed": [],
              # Verdicts that have aged out of suppressing anything, so the
              # question reaches a human on a schedule.
              "stale_watch": [f"{w.name} (checked {w.checked_on.isoformat()})"
                              for w in (watchlist or []) if not is_watch_current(w, today)],
              # The same for sources.yaml, whose lists the scout never reads:
              # the PR body is the one recurring channel to a human.
              "stale_sources": [f"{s.name} (read {s.checked_on.isoformat()})"
                                for s in (sources or []) if not is_source_current(s, today)],
              "providers": evidence.providers if evidence else []}

    def within_budget(phase: str) -> bool:
        """Phases run in descending order of value, so the one that finds the
        budget spent is always the cheapest one left to lose."""
        if deadline is not None and deadline.expired():
            print(f"{phase} skipped: the run's wall-clock budget is spent")
            result["skipped"].append(phase)
            return False
        return True

    def lost_to_backends(phase: str, exc: Exception) -> None:
        """A phase that had budget, asked, and came back empty-handed because
        the whole chain was down. Reported apart from `skipped`, which never
        asked at all, so a run whose chain was down does not read as one that
        found nothing."""
        print(f"{phase} skipped: {exc}")
        result["llm_outages"].append(phase)

    # A stale-ids row is not sent to the model. It needs an exact id copied out
    # of a vendor catalog into or out of `api.model_ids` (or `api.ignored_ids`),
    # `api` is not a key the prompt may write, and every key it may write is
    # still correct on that row. It reaches the PR through `unfixed` below.
    fixable = {f["id"]: f for f in failures
               if f.get("status") != ProbeStatus.STALE_IDS.value}
    if fixable and within_budget("fixes"):
        flagged = fixable
        ctx_entries = [e for e in entries if e.id in flagged]
        urls = [u for e in ctx_entries for u in e.source_urls]
        pages = page_fetcher(urls)
        context = "\n\n".join(
            f"ENTRY:\n{yaml.safe_dump(e.model_dump(mode='json', exclude_none=True), sort_keys=False)}"
            + f"FAILURE: {flagged[e.id].get('status', 'fail')} — {flagged[e.id].get('detail', '')}\n"
            + "\n".join(f"PAGE {u}:\n{pages.get(u, '')}" for u in e.source_urls)
            for e in ctx_entries
        )
        data = _ask(llm, FIX_PROMPT.format(context=context))
        result["updates"], rejected = apply_updates(entries, data.get("updates") or [], verifier,
                                                    named)
        result["rejected"] += rejected

    # Everything the probe flagged that the run did not repair goes into the PR
    # with its verdict: the fixes phase can be skipped, the model can decline,
    # and its answer can be rejected, and the row would otherwise appear nowhere
    # a reviewer looks. A repaired row keeps the half of its detail addressed to
    # a human (`for_a_human`), which no answer of the model can have repaired.
    repaired = set(result["updates"])
    for f in failures:
        detail = f.get("detail", "")
        if f["id"] not in repaired:
            result["unfixed"].append(f"{f['id']}: {f.get('status', 'fail')} — {detail}".strip(" —"))
        elif rest := for_a_human(detail):
            result["unfixed"].append(f"{f['id']}: {rest}")

    if evidence is not None and not evidence.is_empty() and within_budget("discovery"):
        # Discovery carries the longest prompt of the run, so it is the phase
        # most likely to exhaust a backend. Losing it must not also throw away
        # the fixes the previous phase already made.
        try:
            data = _ask(llm, DISCOVER_PROMPT.format(
                existing=", ".join(e.id for e in entries),
                domains=", ".join(sorted({site_of(e.url) for e in entries})),
                blocked=", ".join(sorted(blocklist)) if blocklist else "none",
                watched=format_watchlist(watchlist or [], today),
                evidence=format_evidence(evidence),
            ))
            result["new"], rejected = apply_new(
                entries, data.get("new_entries") or [], today, verifier, blocklist, watchlist)
            result["rejected"] += rejected
        except RuntimeError as exc:
            lost_to_backends("discovery", exc)

    # Sweep every live entry for a shutdown announcement, which the probe would
    # otherwise only notice on the day the free tier dies.
    live = [e for e in entries if e.retired_on is None and e.delisted is None and e.source_urls]
    if live and within_budget("retirement sweep"):
        pages = page_fetcher([e.source_urls[0] for e in live])
        candidates = [e for e in live if _has_retirement_signal(pages.get(e.source_urls[0], ""))]
        context = "\n\n".join(
            f"ENTRY {e.id} ({e.name}) — offering: {e.offering}\n"
            f"PAGE {e.source_urls[0]}:\n{_retirement_excerpt(pages.get(e.source_urls[0], ''))}"
            for e in candidates
        )
        # Named, so a count of 1 does not mean re-fetching every page to find it.
        flagged = f" ({', '.join(e.id for e in candidates)})" if candidates else ""
        print(f"retirement sweep: {len(candidates)}/{len(live)} pages carry a signal{flagged}")
        if context:
            # An optional sweep must never sink the run that finds new entries.
            try:
                data = _ask(llm, RETIREMENT_PROMPT.format(context=context))
                result["retired"] = apply_retirements(entries, data.get("retire") or [], pages)
            except RuntimeError as exc:
                lost_to_backends("retirement sweep", exc)

    # Archived entries are left out of both halves — the families asked about
    # and the rows a bump is matched against: a bump for a product that is gone
    # is noise, and one matched against an archived row would read its page.
    current = [e for e in entries if not is_archived(e, today)]
    families = sorted({m.family for e in current for m in e.models})
    if families and within_budget("generation check"):
        # Pure suggestions for the PR body — the cheapest thing in the run to
        # lose, and it runs last, so it must never discard what came before it.
        try:
            data = _ask(llm, GENERATIONS_PROMPT.format(families=", ".join(families)))
            result["supersede"], result["suppressed"], result["supersede_filtered"] = \
                supersede_proposals(current, data.get("supersede") or [], dismissed, named)
        except RuntimeError as exc:
            lost_to_backends("generation check", exc)

    return result


def _write_status(path: Path, outages: list[str], aborted: str | None,
                  feed_warnings: list[str] | None = None) -> None:
    """The one machine-readable line the workflow reads once everything else is
    written and pushed.

    The scout exits 0 whatever happens (see `main`), so the job's colour is
    decided by a last step reading this file, after the pull request exists — a
    notification, not an invitation to rerun. Feed warnings ride along as
    annotations and never turn the run red: a list that went quiet costs leads,
    not the run (`_read_feed` in discovery)."""
    path.write_text(json.dumps({"llm_outages": outages, "aborted": aborted,
                                "feed_warnings": feed_warnings or []}),
                    encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures/failures.json"))
    parser.add_argument("--blocklist", type=Path, default=Path("blocklist.yaml"))
    parser.add_argument("--dismissed", type=Path, default=Path("dismissed.yaml"))
    parser.add_argument("--watchlist", type=Path, default=Path("watchlist.yaml"))
    parser.add_argument("--sources", type=Path, default=Path("sources.yaml"))
    parser.add_argument("--pr-body", type=Path, default=Path("scout-pr.md"))
    parser.add_argument(
        "--status", type=Path, default=Path("scout-status.json"),
        help="where to record whether the run's LLM work actually happened — "
             "the workflow's last step reads this and decides the job's colour")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="run every phase but leave registry.yaml untouched — how the "
             "fallback backend gets exercised without a PR to close afterwards")
    args = parser.parse_args()

    # This repository's own files load here, outside the catch-all below, and are
    # meant to raise: the catch-all is for what the scout cannot control, and a
    # config error swallowed into it would make a broken repo look like a quiet
    # run.
    entries = load_registry(args.registry)
    blocklist = load_blocklist(args.blocklist)
    dismissed = load_dismissed(args.dismissed)
    watchlist = load_watchlist(args.watchlist)
    sources = load_sources(args.sources)
    failures = json.loads(args.failures.read_text()) if args.failures.exists() else []
    deadline = Deadline(float(os.environ.get("SCOUT_DEADLINE_SECONDS")
                              or SCOUT_DEADLINE_SECONDS))
    llm = LLMClient(
        gemini_key=os.environ.get("GEMINI_API_KEY"),
        openrouter_key=os.environ.get("OPENROUTER_API_KEY"),
        openrouter_model=os.environ.get("SCOUT_OPENROUTER_MODEL"),
        custom_base_url=os.environ.get("SCOUT_BASE_URL"),
        custom_model=os.environ.get("SCOUT_MODEL"),
        custom_key=os.environ.get("SCOUT_API_KEY"),
        fallback_base_url=os.environ.get("SCOUT_FALLBACK_BASE_URL"),
        fallback_model=os.environ.get("SCOUT_FALLBACK_MODEL"),
        fallback_key=os.environ.get("SCOUT_FALLBACK_API_KEY"),
        models_by_base_url=published_model_ids(entries),
        deadline=deadline,
        force=os.environ.get("SCOUT_FORCE_BACKEND"),
    )

    evidence = gather_evidence(DISCOVERY_QUERIES, known_domains(entries), os.environ,
                               time_left=deadline.share(EVIDENCE_BUDGET_FRACTION).remaining,
                               answered_domains=answered_domains(watchlist, blocklist, date.today()))
    print(f"evidence: {len(evidence.hits)} hits, {len(evidence.pages)} pages, "
          f"providers: {evidence.describe_providers() or 'none'}")
    for warning in evidence.feed_warnings:
        print(f"feed warning: {warning}")

    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=10.0),
                          headers={"User-Agent": "freetier-radar/0.2"}) as probe_client:
            # Bound here rather than inside run_scout, which knows the fetcher
            # only as a callable: the retirement sweep asks for one page per live
            # entry, each at its own 30s read timeout, inside a phase that checks
            # the budget once, before any of them.
            result = run_scout(llm, entries, failures,
                               partial(fetch_page_texts, time_left=deadline.remaining),
                               date.today(),
                               evidence=evidence,
                               verifier=lambda e: probe_check_sync(e, probe_client),
                               blocklist=blocklist,
                               dismissed=dismissed,
                               watchlist=watchlist,
                               sources=sources,
                               deadline=deadline,
                               named=named_by_row(probe_client, time_left=deadline.remaining))
    except Exception as exc:
        # Catch-all on purpose. The scout is the optional half of the run: by
        # the time it speaks, the verification commit is already pushed, and a
        # failed job cannot be rerun (it checks out the old SHA and its push is
        # refused as non-fast-forward). So an abort leaves the registry
        # untouched, says so in the PR body and the status file, keeps the
        # traceback in the log and exits 0; the workflow's last step turns the
        # run red once the pull request and the summary have landed.
        traceback.print_exc()
        print(f"scout aborted: {exc}")
        args.pr_body.write_text(f"## Scout proposals\n\nScout aborted: {exc}\n", encoding="utf-8")
        _write_status(args.status, [], aborted=str(exc), feed_warnings=evidence.feed_warnings)
        return

    if args.dry_run:
        print("dry run: registry left untouched")
    else:
        # history.jsonl is not written here: the render the workflow runs on
        # the scout's changes records them, on the pull request's branch.
        save_registry(args.registry, entries)
    args.pr_body.write_text(PR_BODY_TEMPLATE.format(
        providers=evidence.describe_providers() or "none",
        feed_warnings="; ".join(evidence.feed_warnings) or "—",
        backend=llm.describe(),
        unlisted_pins="; ".join(llm.unlisted_pins) or "—",
        updates=", ".join(result["updates"]) or "—",
        new=", ".join(result["new"]) or "—",
        rejected="; ".join(result["rejected"]) or "—",
        unfixed="; ".join(result["unfixed"]) or "—",
        supersede=", ".join(result["supersede"]) or "—",
        suppressed=", ".join(result["suppressed"]) or "—",
        supersede_filtered=", ".join(result["supersede_filtered"]) or "—",
        stale_watch=", ".join(result["stale_watch"]) or "—",
        recheck_days=WATCH_RECHECK_DAYS,
        schedule=probe_frequency(),
        stale_sources=", ".join(result["stale_sources"]) or "—",
        source_days=SOURCE_RECHECK_DAYS,
        retired=", ".join(result["retired"]) or "—",
        skipped=", ".join(result["skipped"]) or "—",
        llm_outages=", ".join(result["llm_outages"]) or "—",
    ), encoding="utf-8")
    _write_status(args.status, result["llm_outages"], aborted=None,
                  feed_warnings=evidence.feed_warnings)
    print(f"scout: {result}")
