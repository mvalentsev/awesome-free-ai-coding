from __future__ import annotations

import argparse
import json
import os
import re
import time
import traceback
from datetime import date
from pathlib import Path
from typing import Callable

import httpx
import yaml

from .discovery import Evidence, domain_of, fetch_page_texts, format_evidence, gather_evidence
from .models import Entry, load_registry, save_registry
from .prober import check_content

EDITABLE = {"offering", "limits", "card_required", "probe", "models"}

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
without a key. Keywords must anchor on something that disappears together with
the offer — the free model's id, its quota figure, or its price row. Generic
words are rejected: "free", "pricing" and "no credit card required" sit on a
vendor page for months after the free tier is withdrawn, so a probe built out
of them verifies nothing but that the page still loads.
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
           {{type: api-models, endpoint: <https://.../v1/models>, free_marker: ''}}
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

Updated entries: {updates}
New entries (probe-verified): {new}
Rejected candidates: {rejected}
Retirements announced by the vendor: {retired}

Generation bumps suggested — **not applied**, edit registry.yaml yourself if a
free tier really moved on: {supersede}

_Proposed by the web-evidence scout — review before merging. Weekly probes keep re-verifying after merge._
"""


class LLMClient:
    """Ordered backend chain, first success wins:

    1. custom OpenAI-compatible endpoint (SCOUT_BASE_URL / SCOUT_MODEL /
       optional SCOUT_API_KEY) — point it at NVIDIA NIM, Groq, Cerebras, ...
    2. Gemini API                 (GEMINI_API_KEY)
    3. OpenRouter :free models    (OPENROUTER_API_KEY, model picked live)
    4. anonymous OVH AI Endpoints (no key at all)
    """

    def __init__(self, gemini_key: str | None = None, openrouter_key: str | None = None,
                 openrouter_model: str | None = None,
                 gemini_model: str = "gemini-2.5-flash",
                 custom_base_url: str | None = None, custom_model: str | None = None,
                 custom_key: str | None = None,
                 http: httpx.Client | None = None):
        self._gemini_key = gemini_key
        self._or_key = openrouter_key
        self._or_model = openrouter_model
        self._gemini_model = gemini_model
        self._custom_base_url = custom_base_url.rstrip("/") if custom_base_url else None
        self._custom_model = custom_model
        self._custom_key = custom_key
        self._ovh_model: str | None = None
        self._http = http or httpx.Client(timeout=httpx.Timeout(90.0, connect=15.0))

    def complete(self, prompt: str) -> str:
        backends = []
        if self._custom_base_url and self._custom_model:
            backends.append(("custom", self._custom))
        if self._gemini_key:
            backends.append(("gemini", self._gemini))
        if self._or_key:
            backends.append(("openrouter", self._openrouter))
        backends.append(("ovh-anonymous", self._ovh))
        errors = []
        for name, fn in backends:
            try:
                text = fn(prompt)
                if not isinstance(text, str) or not text.strip():
                    raise RuntimeError("empty completion")
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

    def _chat(self, base_url: str, model: str, key: str | None, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        for attempt in range(RETRY_429_ATTEMPTS):
            r = self._http.post(
                f"{base_url}/chat/completions", headers=headers,
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            )
            if r.status_code == 429 and attempt + 1 < RETRY_429_ATTEMPTS:
                time.sleep(RETRY_429_SLEEP)
                continue
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        raise RuntimeError("rate-limited on every attempt")

    def _custom(self, prompt: str) -> str:
        return self._chat(self._custom_base_url, self._custom_model, self._custom_key, prompt)

    def _gemini(self, prompt: str) -> str:
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self._gemini_model}:generateContent?key={self._gemini_key}")
        r = self._http.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _openrouter(self, prompt: str) -> str:
        if self._or_model is None:
            self._or_model = pick_openrouter_model(self._http)
        return self._chat(OPENROUTER_BASE_URL, self._or_model, self._or_key, prompt)

    def _ovh(self, prompt: str) -> str:
        if self._ovh_model is None:
            self._ovh_model = pick_ovh_model(self._http)
        return self._chat(OVH_BASE_URL, self._ovh_model, None, prompt)


def _list_model_ids(http: httpx.Client, base_url: str) -> list[str]:
    r = http.get(f"{base_url}/models")
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


def load_blocklist(path: Path) -> dict[str, str]:
    """domain -> reason; missing file means an empty blocklist."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return {str(d["domain"]).lower(): str(d.get("reason", ""))
            for d in data if isinstance(d, dict) and d.get("domain")}


def is_blocked(domain: str, blocklist: dict[str, str]) -> bool:
    return any(domain == b or domain.endswith("." + b) for b in blocklist)


def probe_check_sync(entry: Entry, client: httpx.Client) -> str | None:
    """Synchronous single-shot version of the weekly probe for vetting proposals."""
    try:
        resp = client.get(entry.probe.endpoint, follow_redirects=True)
    except httpx.HTTPError as exc:
        return f"unreachable: {exc}"
    if resp.status_code >= 400:
        return f"HTTP {resp.status_code}"
    return check_content(resp, entry)


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
              ) -> tuple[list[str], list[str]]:
    """Validate, dedupe (by id and domain), blocklist-filter and probe-verify
    proposals.

    Returns (added ids, rejected "id: reason" strings). With no verifier the
    probe check is skipped (tests, offline runs)."""
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


def supersede_proposals(entries: list[Entry], supersede: list[dict]) -> list[str]:
    """Describe generation bumps for a human to accept — never write them.

    The scout used to apply these straight to the registry, and three times
    running it buried a free family behind a paid one: z.ai's glm-4.7-flash was
    marked superseded by glm-5.2 while that entry's own limits say the GLM-5.x
    flagships are not free. The mark decides what the README lists as free, but
    the model proposing it sees only a list of family names — no entry, no
    limits, no page. So it cannot answer the question that matters, which is
    not "what is newer" but "what does this free tier serve today".

    Only bumps that would change something are reported."""
    out = []
    for s in supersede:
        family, target = s.get("family"), s.get("superseded_by")
        if not family or not target:
            continue
        for e in entries:
            for m in e.models:
                if m.family == family and m.superseded_by != target:
                    out.append(f"{e.id}: {family} → {target}")
    return out


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
              blocklist: dict[str, str] | None = None) -> dict:
    result = {"updates": [], "new": [], "rejected": [], "supersede": [], "retired": [],
              "providers": evidence.providers if evidence else []}

    if failures:
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

    if evidence is not None and not evidence.is_empty():
        # Discovery carries the longest prompt of the run, so it is the phase
        # most likely to exhaust a backend. Losing it must not also throw away
        # the fixes the previous phase already made.
        try:
            data = _ask(llm, DISCOVER_PROMPT.format(
                existing=", ".join(e.id for e in entries),
                domains=", ".join(sorted({domain_of(e.url) for e in entries})),
                blocked=", ".join(sorted(blocklist)) if blocklist else "none",
                evidence=format_evidence(evidence),
            ))
            result["new"], rejected = apply_new(
                entries, data.get("new_entries") or [], today, verifier, blocklist)
            result["rejected"] += rejected
        except RuntimeError as exc:
            print(f"discovery skipped: {exc}")

    # Sweep every live entry for a shutdown announcement. Without this the scout
    # only ever looks at an entry after its probe fails, i.e. on the day the free
    # tier dies — a retirement announced weeks ahead goes unnoticed until then.
    live = [e for e in entries if e.retired_on is None and e.source_urls]
    if live:
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

    families = sorted({m.family for e in entries for m in e.models})
    if families:
        # Pure suggestions for the PR body — the cheapest thing in the run to
        # lose, and it runs last, so it must never discard what came before it.
        try:
            data = _ask(llm, GENERATIONS_PROMPT.format(families=", ".join(families)))
            result["supersede"] = supersede_proposals(entries, data.get("supersede") or [])
        except RuntimeError as exc:
            print(f"generation check skipped: {exc}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures/failures.json"))
    parser.add_argument("--blocklist", type=Path, default=Path("blocklist.yaml"))
    parser.add_argument("--pr-body", type=Path, default=Path("scout-pr.md"))
    args = parser.parse_args()

    entries = load_registry(args.registry)
    failures = json.loads(args.failures.read_text()) if args.failures.exists() else []
    llm = LLMClient(
        gemini_key=os.environ.get("GEMINI_API_KEY"),
        openrouter_key=os.environ.get("OPENROUTER_API_KEY"),
        openrouter_model=os.environ.get("SCOUT_OPENROUTER_MODEL"),
        custom_base_url=os.environ.get("SCOUT_BASE_URL"),
        custom_model=os.environ.get("SCOUT_MODEL"),
        custom_key=os.environ.get("SCOUT_API_KEY"),
    )

    known_domains = {domain_of(e.url) for e in entries}
    known_domains |= {domain_of(u) for e in entries for u in e.source_urls}
    evidence = gather_evidence(DISCOVERY_QUERIES, known_domains, os.environ)
    print(f"evidence: {len(evidence.hits)} hits, {len(evidence.pages)} pages, "
          f"providers: {', '.join(evidence.providers) or 'none'}")

    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=10.0),
                          headers={"User-Agent": "freetier-radar/0.2"}) as probe_client:
            result = run_scout(llm, entries, failures, fetch_page_texts, date.today(),
                               evidence=evidence,
                               verifier=lambda e: probe_check_sync(e, probe_client),
                               blocklist=load_blocklist(args.blocklist))
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

    save_registry(args.registry, entries)
    args.pr_body.write_text(PR_BODY_TEMPLATE.format(
        providers=", ".join(result["providers"]) or "none",
        updates=", ".join(result["updates"]) or "—",
        new=", ".join(result["new"]) or "—",
        rejected="; ".join(result["rejected"]) or "—",
        supersede=", ".join(result["supersede"]) or "—",
        retired=", ".join(result["retired"]) or "—",
    ), encoding="utf-8")
    print(f"scout: {result}")
