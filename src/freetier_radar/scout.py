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
# The curated-file loaders live in models.py; re-exported here because this is
# where callers and tests have always reached for them.
from .models import (WATCH_RECHECK_DAYS, Entry, Watched, is_archived, is_blocked,
                     is_watch_current, known_domains, load_blocklist, load_dismissed,
                     load_registry, load_watchlist, save_registry, watch_match)
from .prober import challenge_marker_hit, check_content

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

# Read timeout per backend call. The discovery prompt runs to ~78k characters
# (~20k tokens) on a real evidence set, and a reasoning model can spend minutes
# on it: measured 2026-08-03, minimax-m3 answered in 88s, gpt-oss:120b in 33s,
# deepseek-v4-flash-free peaked at 202s, and nemotron-3-ultra — the scout's
# primary model until that day — did not answer within 600s at all. Under the
# old 90s it timed out on every scheduled run, silently, until the chain
# started logging failures. The run is twice a week, so waiting is cheap and
# the ceiling sits well above the slowest backend we would actually use.
LLM_READ_TIMEOUT = 300.0

# Wall-clock ceiling for one backend call, which the read timeout above is not:
# httpx restarts its clock on every byte received, so a backend that trickles
# output holds the call open indefinitely. That is not theory — on 2026-08-03
# OpenRouter streamed for ~9 minutes inside a 90-second timeout and then handed
# over a truncated body. The ceiling sits above the slowest measured answer
# (202s) with room to spare, and turns a trickle into a failure the chain can
# step over.
LLM_CALL_DEADLINE = 420.0

# Wall-clock budget for the whole scout run. Four LLM phases over a five-backend
# chain can multiply into hours of a job nobody is watching, and the scout is
# the optional half of the run: a phase that has run out of time is worth
# skipping, never worth hanging for. Overridable via SCOUT_DEADLINE_SECONDS.
SCOUT_DEADLINE_SECONDS = 1800.0

# The share of that budget the evidence phase may spend before the first LLM call.
# Measured 2026-08-14 on a keyless run: two searchers 4.8s, ten page fetches 13.4s,
# five curated feeds 1.2s — 19.5s all told. The ceiling is 22x that on the default
# budget, so it can only ever fire on a hang, not on a slow-but-working run. Left
# uncapped the same phase can hold the line for ~1100s of its own accord, and it
# is spending the LLM phases' time to do it.
EVIDENCE_BUDGET_FRACTION = 0.25

# Listing a backend's models is a small GET and must not inherit the long read
# timeout meant for generation.
MODELS_LIST_TIMEOUT = 30.0

# Retirement sweep: one page per live entry, trimmed so the prompt stays small.
# A quote shorter than this is too weak to verify against a page.
RETIREMENT_PAGE_CHARS = 2500
MIN_QUOTE_CHARS = 25

# Only pages carrying one of these reach the LLM. Feeding all 30 live pages in
# cost ~20k tokens for a question that is almost always "no" — and a prompt that
# large can exceed a backend's context, failing the whole scout run over an
# optional sweep. The words are deliberately broad: false positives cost a few
# hundred tokens, a miss costs a retirement.
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
card_required, probe, models.
A "stale-models" failure means the probe passed and the offer is alive, but every
family listed for it was marked superseded: reply with a models list naming the
families the free tier serves today, and leave the probe alone.
A corrected page-keywords probe needs at least one keyword that dies with the
offer — a quota or price figure, a model id or JSON field, or a sentence of four
or more words quoted verbatim from the page below. Words like "free", "hobby",
"free quota" or "no credit card required" are rejected: they outlive the offer.
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
  - an id: the free model's id or a JSON field of the vendor's own API —
    "mistral-medium", "advanced_model_request_limit", '"name":"free"';
  - a sentence of four or more words quoted verbatim from the page and specific
    to this offer — "free models through kilo gateway".
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
    offering: ...
    limits: ...
    models:                # ONLY models actually usable for free on the free tier/plan,
                           # never the vendor's paid catalog; omit when the evidence is silent
      - {{family: <substring of the vendor's API model ids>, tier: frontier | strong, released: 'YYYY-MM'}}
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
Backend chain: {backend}

Updated entries: {updates}
New entries (probe-verified): {new}
Rejected candidates: {rejected}
Retirements announced by the vendor: {retired}
Phases skipped (out of wall-clock budget): {skipped}

Generation bumps suggested — **not applied**, edit registry.yaml yourself if a
free tier really moved on: {supersede}
Already dismissed in dismissed.yaml, not proposed again: {suppressed}

Watchlist verdicts due for a re-check (older than {recheck_days} days, and no
longer suppressing anything): {stale_watch}

_Proposed by the web-evidence scout — review before merging. Weekly probes keep re-verifying after merge._
"""


class DeadlineExceeded(RuntimeError):
    """A backend held the call open past the run's wall-clock budget."""


class Deadline:
    """The run's remaining wall-clock time, shared by every phase and every call.

    Deliberately one budget rather than a per-phase allowance: the phases are
    ordered by value — fixes first, then discovery, then the optional sweeps —
    so a slow first phase should eat into the last one, not into the job.
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

        Taken from what is left rather than from the original allowance, so it
        can never outlive the run it belongs to. The exception to the one-budget
        rule above: the phases ordered by value are the LLM ones, and a phase
        that merely feeds them is not entitled to starve them.
        """
        return Deadline(self.remaining() * fraction, self._clock)


class LLMClient:
    """Ordered backend chain, first success wins:

    1. custom OpenAI-compatible endpoint (SCOUT_BASE_URL / SCOUT_MODEL /
       optional SCOUT_API_KEY) — point it at NVIDIA NIM, Groq, Cerebras, ...
    2. a second endpoint of the same kind (SCOUT_FALLBACK_BASE_URL /
       SCOUT_FALLBACK_MODEL / SCOUT_FALLBACK_API_KEY). Two configured free
       providers beat one: on 2026-08-03 the primary timed out and the run
       landed on OpenRouter, which answered a truncated body and killed it.
    3. Gemini API                 (GEMINI_API_KEY)
    4. OpenRouter :free models    (OPENROUTER_API_KEY, model picked live)
    5. anonymous OVH AI Endpoints (no key at all)
    """

    def __init__(self, gemini_key: str | None = None, openrouter_key: str | None = None,
                 openrouter_model: str | None = None,
                 gemini_model: str = "gemini-2.5-flash",
                 custom_base_url: str | None = None, custom_model: str | None = None,
                 custom_key: str | None = None,
                 fallback_base_url: str | None = None, fallback_model: str | None = None,
                 fallback_key: str | None = None,
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
        # it has a url and a model, so a half-configured spare stays out.
        self._customs = [
            (name, url.rstrip("/"), model, key)
            for name, url, model, key in (
                ("custom", custom_base_url, custom_model, custom_key),
                ("custom-fallback", fallback_base_url, fallback_model, fallback_key),
            )
            if url and model
        ]
        self._ovh_model: str | None = None
        self.answered_by: str | None = None
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
            (name, partial(self._chat, url, model, key))
            for name, url, model, key in self._customs
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
            # Forcing exists to exercise a backend that never gets its turn —
            # the spare endpoint answered in a local test and has not run in CI
            # once, because the primary has never failed on a scheduled run.
            # Falling through to another backend would defeat that, so an
            # unconfigured name is an error, not a silent chain run.
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
                # Which backend actually answered is otherwise only visible as
                # an absence — the run that quietly fell through to OpenRouter
                # for weeks looked exactly like a healthy one in the log.
                print(f"scout backend {name} answered in {self._clock() - started:.0f}s")
                self.answered_by = name
                return text
            # Deliberately broad: the only thing this loop can usefully do with a
            # misbehaving backend is move to the next one. A narrow tuple let a
            # JSONDecodeError out on 2026-08-03 — OpenRouter answered HTTP 200
            # with a truncated body, and the scout died mid-chain with three
            # untried backends behind it.
            except Exception as exc:
                print(f"scout backend {name} failed: {type(exc).__name__}: {exc}")
                errors.append(f"{name}: {type(exc).__name__}: {exc}")
        raise RuntimeError("all LLM backends failed: " + "; ".join(errors))

    def describe(self) -> str:
        """One line for the PR body: what the chain was, and who answered."""
        chain = " → ".join(n for n, _ in self._backends())
        head = f"forced {self._force} (configured: {chain})" if self._force else chain
        return f"{head} — answered by {self.answered_by or 'nothing'}"

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

        httpx's timeout is per read, not per call, so it cannot answer "has this
        backend had long enough?" — it only ever asks "has it been silent for
        too long?". A backend answering HTTP 200 and then trickling bytes passes
        that test forever: OpenRouter streamed for ~9 minutes inside a 90-second
        timeout on 2026-08-03 and delivered a truncated body at the end of it.
        Reading in chunks and checking the wall clock makes that an ordinary
        backend failure, which the chain already knows how to step over. The
        read timeout stays on top for the opposite failure — a backend that
        says nothing at all — capped by the same budget.
        """
        budget = self._budget()
        end = self._clock() + budget
        timeout = httpx.Timeout(min(LLM_READ_TIMEOUT, budget), connect=15.0)
        with self._http.stream("POST", url, headers=headers, json=payload,
                               timeout=timeout) as r:
            if r.status_code == 429:
                return r.status_code, b""
            r.raise_for_status()
            chunks = []
            for chunk in r.iter_bytes():
                chunks.append(chunk)
                if self._clock() > end:
                    raise DeadlineExceeded(
                        f"{url} was still streaming after {budget:.0f}s")
        return r.status_code, b"".join(chunks)

    def _chat(self, base_url: str, model: str, key: str | None, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        for attempt in range(RETRY_429_ATTEMPTS):
            status, body = self._post(
                f"{base_url}/chat/completions", headers,
                {"model": model, "messages": [{"role": "user", "content": prompt}]},
            )
            if status != 429:
                return json.loads(body)["choices"][0]["message"]["content"]
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
            self._or_model = pick_openrouter_model(self._http)
        return self._chat(OPENROUTER_BASE_URL, self._or_model, self._or_key, prompt)

    def _ovh(self, prompt: str) -> str:
        if self._ovh_model is None:
            self._ovh_model = pick_ovh_model(self._http)
        return self._chat(OVH_BASE_URL, self._ovh_model, None, prompt)


def _list_model_ids(http: httpx.Client, base_url: str) -> list[str]:
    r = http.get(f"{base_url}/models", timeout=MODELS_LIST_TIMEOUT)
    r.raise_for_status()
    return [str(m.get("id", "")) for m in r.json().get("data", []) if isinstance(m, dict)]


def pick_openrouter_model(http: httpx.Client) -> str:
    """Pick a currently-listed :free model so the fallback never rots."""
    try:
        ids = _list_model_ids(http, OPENROUTER_BASE_URL)
    except (httpx.HTTPError, json.JSONDecodeError):
        return FALLBACK_OPENROUTER_MODEL
    free = [i for i in ids if i.endswith(":free")]
    for hint in PREFERRED_MODEL_HINTS:
        for model_id in free:
            if hint in model_id:
                return model_id
    return free[0] if free else FALLBACK_OPENROUTER_MODEL


def pick_ovh_model(http: httpx.Client) -> str:
    """Pick a live model on the anonymous OVH endpoint (errors fail the backend over)."""
    ids = _list_model_ids(http, OVH_BASE_URL)
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


def format_watchlist(watchlist: list[Watched], today: date) -> str:
    """The current verdicts, for the discovery prompt.

    Expired ones are left out deliberately: telling the model a service has no
    free tier on the strength of a verdict this file itself no longer trusts is
    how a watchlist quietly becomes a blocklist. `reopen_if` goes in because the
    useful instruction is not "never propose this" but "propose it when THIS
    changed" — the model is reading fresh evidence the verdict never saw.
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
    """Synchronous single-shot version of the weekly probe for vetting proposals."""
    try:
        resp = client.get(entry.probe.endpoint, follow_redirects=True)
    except httpx.HTTPError as exc:
        return f"unreachable: {exc}"
    if resp.status_code >= 400:
        return f"HTTP {resp.status_code}"
    problem = check_content(resp, entry)
    if problem is None:
        return None
    # Name the bot wall in the rejection reason. "missing keywords" reads as a
    # bad proposal; "bot challenge" tells the reviewer the endpoint answers a
    # wall to everything that is not a browser — cto.new's lesson, in the PR body.
    challenge = challenge_marker_hit(resp.text)
    return f'bot challenge: page says "{challenge}"' if challenge else problem


def apply_updates(entries: list[Entry], updates: list[dict]) -> tuple[list[str], list[str]]:
    """Apply the LLM's corrections to flagged entries.

    Returns (applied ids, rejected "id: reason" strings). One bad update must
    not sink the run: by the time the scout speaks, the verification commit is
    already pushed, and a failed run cannot be rerun (it checks out the old SHA
    and its push is refused as non-fast-forward). Two ways the model gets an
    update wrong, both seen live: a null where the prompt told it to leave a
    key alone (`probe: null` for the retired github-models entry, run
    30798513182, 2026-08-03) and a corrected value that does not validate."""
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
        try:
            entries[i] = Entry.model_validate({**e.model_dump(mode="json"), **changed})
        except Exception as exc:
            print(f"update for {e.id} rejected: {exc}")
            rejected.append(f"{e.id}: invalid update ({type(exc).__name__})")
            continue
        applied.append(e.id)
    return applied, rejected


def apply_new(entries: list[Entry], new_entries: list[dict], today: date,
              verifier: Callable[[Entry], str | None] | None = None,
              blocklist: dict[str, str] | None = None,
              watchlist: list[Watched] | None = None,
              ) -> tuple[list[str], list[str]]:
    """Validate, dedupe (by id and domain), blocklist- and watchlist-filter, and
    probe-verify proposals.

    Returns (added ids, rejected "id: reason" strings). With no verifier the
    probe check is skipped (tests, offline runs).

    The watchlist filter is checked after the blocklist and before the probe: a
    service with no free tier usually still serves a page, so its proposal would
    burn a live probe on a question a human already answered. An expired verdict
    filters nothing on purpose — that is what makes it a watchlist."""
    existing_ids = {e.id for e in entries}
    existing_domains = {domain_of(e.url) for e in entries}
    added, rejected = [], []
    for raw in new_entries:
        if not isinstance(raw, dict):
            continue
        rid = raw.get("id", "<missing id>")
        if rid in existing_ids:
            continue
        try:
            e = Entry.model_validate({**raw, "first_seen": today, "last_verified": today,
                                      "provisional": True, "probe_failures": 0})
        except Exception as exc:
            rejected.append(f"{rid}: invalid ({type(exc).__name__})")
            continue
        if blocklist and is_blocked(domain_of(e.url), blocklist):
            rejected.append(f"{e.id}: blocklisted domain")
            continue
        if domain_of(e.url) in existing_domains:
            rejected.append(f"{e.id}: domain already covered")
            continue
        watched = watch_match(domain_of(e.url), watchlist or [], today)
        if watched is not None:
            # Truncated by length rather than at the first full stop: the reasons
            # are full of hostnames and prices, so splitting on "." cuts
            # "api.llm7.io" in half and reads as a typo in the PR body.
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
        existing_domains.add(domain_of(e.url))
        added.append(e.id)
    return added, rejected


def supersede_proposals(entries: list[Entry], supersede: list[dict],
                        dismissed: set[tuple[str, str, str]] | None = None,
                        ) -> tuple[list[str], list[str]]:
    """Describe generation bumps for a human to accept — never write them.

    The scout used to apply these straight to the registry, and three times
    running it buried a free family behind a paid one: z.ai's glm-4.7-flash was
    marked superseded by glm-5.2 while that entry's own limits say the GLM-5.x
    flagships are not free. The mark decides what the README lists as free, but
    the model proposing it sees only a list of family names — no entry, no
    limits, no page. So it cannot answer the question that matters, which is
    not "what is newer" but "what does this free tier serve today".

    Returns (proposed, suppressed). Only bumps that would change something are
    reported, and a bump listed in dismissed.yaml is reported as suppressed
    rather than silently dropped — a filter nobody can see is a filter nobody
    can correct."""
    dismissed = dismissed or set()
    proposed, suppressed = [], []
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
                    else:
                        proposed.append(line)
    return proposed, suppressed


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _has_retirement_signal(text: str) -> bool:
    lowered = text.lower()
    return any(s in lowered for s in RETIREMENT_SIGNALS)


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
              deadline: Deadline | None = None) -> dict:
    result = {"updates": [], "new": [], "rejected": [], "supersede": [], "suppressed": [],
              "retired": [], "skipped": [],
              # Verdicts that have aged out of suppressing anything. Reported so
              # the question reaches a human on a schedule instead of only when
              # someone happens to re-read the file.
              "stale_watch": [f"{w.name} (checked {w.checked_on.isoformat()})"
                              for w in (watchlist or []) if not is_watch_current(w, today)],
              "providers": evidence.providers if evidence else []}

    def within_budget(phase: str) -> bool:
        """Phases run in descending order of value, so the one that finds the
        budget spent is always the cheapest one left to lose."""
        if deadline is not None and deadline.expired():
            print(f"{phase} skipped: the run's wall-clock budget is spent")
            result["skipped"].append(phase)
            return False
        return True

    if failures and within_budget("fixes"):
        flagged = {f["id"]: f for f in failures}
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
        result["updates"], rejected = apply_updates(entries, data.get("updates") or [])
        result["rejected"] += rejected

    if evidence is not None and not evidence.is_empty() and within_budget("discovery"):
        # Discovery carries the longest prompt of the run, so it is the phase
        # most likely to exhaust a backend. Losing it must not also throw away
        # the fixes the previous phase already made.
        try:
            data = _ask(llm, DISCOVER_PROMPT.format(
                existing=", ".join(e.id for e in entries),
                domains=", ".join(sorted({domain_of(e.url) for e in entries})),
                blocked=", ".join(sorted(blocklist)) if blocklist else "none",
                watched=format_watchlist(watchlist or [], today),
                evidence=format_evidence(evidence),
            ))
            result["new"], rejected = apply_new(
                entries, data.get("new_entries") or [], today, verifier, blocklist, watchlist)
            result["rejected"] += rejected
        except RuntimeError as exc:
            print(f"discovery skipped: {exc}")

    # Sweep every live entry for a shutdown announcement. Without this the scout
    # only ever looks at an entry after its probe fails, i.e. on the day the free
    # tier dies — a retirement announced weeks ahead goes unnoticed until then.
    live = [e for e in entries if e.retired_on is None and e.source_urls]
    if live and within_budget("retirement sweep"):
        pages = page_fetcher([e.source_urls[0] for e in live])
        candidates = [e for e in live if _has_retirement_signal(pages.get(e.source_urls[0], ""))]
        context = "\n\n".join(
            f"ENTRY {e.id} ({e.name}) — offering: {e.offering}\n"
            f"PAGE {e.source_urls[0]}:\n{pages.get(e.source_urls[0], '')[:RETIREMENT_PAGE_CHARS]}"
            for e in candidates
        )
        print(f"retirement sweep: {len(candidates)}/{len(live)} pages carry a signal")
        if context:
            # An optional sweep must never sink the run that finds new entries.
            try:
                data = _ask(llm, RETIREMENT_PROMPT.format(context=context))
                result["retired"] = apply_retirements(entries, data.get("retire") or [], pages)
            except RuntimeError as exc:
                print(f"retirement sweep skipped: {exc}")

    # Archived entries are excluded: their families belong to a product that is
    # gone, so any bump proposed for them is noise a reviewer can only ignore.
    # GitHub Models kept drawing "gpt-4.1 → gpt-5.6" months after GitHub shut
    # the product down.
    families = sorted({m.family for e in entries if not is_archived(e, today) for m in e.models})
    if families and within_budget("generation check"):
        # Pure suggestions for the PR body — the cheapest thing in the run to
        # lose, and it runs last, so it must never discard what came before it.
        try:
            data = _ask(llm, GENERATIONS_PROMPT.format(families=", ".join(families)))
            result["supersede"], result["suppressed"] = supersede_proposals(
                entries, data.get("supersede") or [], dismissed)
        except RuntimeError as exc:
            print(f"generation check skipped: {exc}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures/failures.json"))
    parser.add_argument("--blocklist", type=Path, default=Path("blocklist.yaml"))
    parser.add_argument("--dismissed", type=Path, default=Path("dismissed.yaml"))
    parser.add_argument("--watchlist", type=Path, default=Path("watchlist.yaml"))
    parser.add_argument("--pr-body", type=Path, default=Path("scout-pr.md"))
    parser.add_argument(
        "--dry-run", action="store_true",
        help="run every phase but leave registry.yaml untouched — how the "
             "fallback backend gets exercised without a PR to close afterwards")
    args = parser.parse_args()

    # This repository's own files load here, outside the catch-all below, and are
    # meant to raise. The catch-all exists for what the scout cannot control — a
    # backend down, a model answering HTML — and swallowing a config error into
    # it makes a broken repo look like a quiet run: on 2026-08-14 a colon in a
    # blocklist reason made yaml.safe_load throw, the scout aborted before its
    # first LLM call, and the workflow still reported success.
    entries = load_registry(args.registry)
    blocklist = load_blocklist(args.blocklist)
    dismissed = load_dismissed(args.dismissed)
    watchlist = load_watchlist(args.watchlist)
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
        deadline=deadline,
        force=os.environ.get("SCOUT_FORCE_BACKEND"),
    )

    evidence = gather_evidence(DISCOVERY_QUERIES, known_domains(entries), os.environ,
                               time_left=deadline.share(EVIDENCE_BUDGET_FRACTION).remaining)
    print(f"evidence: {len(evidence.hits)} hits, {len(evidence.pages)} pages, "
          f"providers: {', '.join(evidence.providers) or 'none'}")

    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=10.0),
                          headers={"User-Agent": "freetier-radar/0.2"}) as probe_client:
            # Bound here rather than inside run_scout, which knows the fetcher
            # only as a callable: the retirement sweep asks for one page per live
            # entry — 39 of them today, each at its own 30s read timeout — inside
            # a phase that checks the budget once, before any of them.
            result = run_scout(llm, entries, failures,
                               partial(fetch_page_texts, time_left=deadline.remaining),
                               date.today(),
                               evidence=evidence,
                               verifier=lambda e: probe_check_sync(e, probe_client),
                               blocklist=blocklist,
                               dismissed=dismissed,
                               watchlist=watchlist,
                               deadline=deadline)
    except Exception as exc:
        # Last line of defence, and deliberately catch-all. The scout is the
        # optional half of the run: by the time it speaks, the verification
        # commit is already pushed, and a failed job cannot be rerun (it checks
        # out the old SHA and its push is refused as non-fast-forward). So
        # nothing the scout can hit — every backend down, a backend answering
        # HTML, a proposal that will not validate — is worth failing the
        # workflow for. Leave the registry untouched, say so in the PR body,
        # and let the traceback stand in the log.
        traceback.print_exc()
        print(f"scout aborted: {exc}")
        args.pr_body.write_text(f"## Scout proposals\n\nScout aborted: {exc}\n", encoding="utf-8")
        return

    if args.dry_run:
        print("dry run: registry left untouched")
    else:
        save_registry(args.registry, entries)
    args.pr_body.write_text(PR_BODY_TEMPLATE.format(
        providers=", ".join(result["providers"]) or "none",
        backend=llm.describe(),
        updates=", ".join(result["updates"]) or "—",
        new=", ".join(result["new"]) or "—",
        rejected="; ".join(result["rejected"]) or "—",
        supersede=", ".join(result["supersede"]) or "—",
        suppressed=", ".join(result["suppressed"]) or "—",
        stale_watch=", ".join(result["stale_watch"]) or "—",
        recheck_days=WATCH_RECHECK_DAYS,
        retired=", ".join(result["retired"]) or "—",
        skipped=", ".join(result["skipped"]) or "—",
    ), encoding="utf-8")
    print(f"scout: {result}")
