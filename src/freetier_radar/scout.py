from __future__ import annotations

import argparse
import json
import os
import re
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
Use ONLY the evidence below (search hits, fetched pages, curated feed excerpts).
Propose an entry ONLY when the evidence explicitly supports its free offering,
and set source_urls to the evidence URLs you used. Official vendor pages only —
no reverse proxies, key-sharing or scraped gateways. The probe endpoint must be
a server-rendered page containing the keywords, or a public JSON models API.
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
    probe: {{type: page-keywords, endpoint: <official url>, keywords: ["free"]}}
Max 8. Empty list if the evidence shows nothing new.
EVIDENCE:
{evidence}
"""

GENERATIONS_PROMPT = SYSTEM_RULES + """
TASK: MODEL-GENERATIONS. These model families are currently listed: {families}
Mark families that have a clearly newer generation from the same vendor.
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
Superseded families: {supersede}

_Proposed by the web-evidence scout — review before merging. Weekly probes keep re-verifying after merge._
"""


class LLMClient:
    """Gemini first (free tier), OpenRouter free models as fallback."""

    def __init__(self, gemini_key: str | None, openrouter_key: str | None,
                 openrouter_model: str | None = None,
                 gemini_model: str = "gemini-2.5-flash",
                 http: httpx.Client | None = None):
        self._gemini_key = gemini_key
        self._or_key = openrouter_key
        self._or_model = openrouter_model
        self._gemini_model = gemini_model
        self._http = http or httpx.Client(timeout=httpx.Timeout(90.0, connect=15.0))

    def complete(self, prompt: str) -> str:
        errors = []
        for fn in (self._gemini, self._openrouter):
            try:
                return fn(prompt)
            except (RuntimeError, httpx.HTTPError, KeyError, IndexError) as exc:
                errors.append(str(exc))
        raise RuntimeError("all LLM backends failed: " + "; ".join(errors))

    def _gemini(self, prompt: str) -> str:
        if not self._gemini_key:
            raise RuntimeError("no GEMINI_API_KEY")
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self._gemini_model}:generateContent?key={self._gemini_key}")
        r = self._http.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _openrouter(self, prompt: str) -> str:
        if not self._or_key:
            raise RuntimeError("no OPENROUTER_API_KEY")
        if self._or_model is None:
            self._or_model = pick_openrouter_model(self._http)
        r = self._http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self._or_key}"},
            json={"model": self._or_model, "messages": [{"role": "user", "content": prompt}]},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def pick_openrouter_model(http: httpx.Client) -> str:
    """Pick a currently-listed :free model so the fallback never rots."""
    try:
        r = http.get("https://openrouter.ai/api/v1/models")
        r.raise_for_status()
        data = r.json().get("data", [])
        free = [str(m.get("id", "")) for m in data if isinstance(m, dict)
                and str(m.get("id", "")).endswith(":free")]
    except (httpx.HTTPError, json.JSONDecodeError):
        return FALLBACK_OPENROUTER_MODEL
    for hint in PREFERRED_MODEL_HINTS:
        for model_id in free:
            if hint in model_id:
                return model_id
    return free[0] if free else FALLBACK_OPENROUTER_MODEL


def extract_yaml_block(text: str) -> str:
    m = re.search(r"```(?:yaml)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def _parse(text: str) -> dict:
    data = yaml.safe_load(extract_yaml_block(text))
    return data if isinstance(data, dict) else {}


def probe_check_sync(entry: Entry, client: httpx.Client) -> str | None:
    """Synchronous single-shot version of the weekly probe for vetting proposals."""
    try:
        resp = client.get(entry.probe.endpoint, follow_redirects=True)
    except httpx.HTTPError as exc:
        return f"unreachable: {exc}"
    if resp.status_code >= 400:
        return f"HTTP {resp.status_code}"
    return check_content(resp, entry)


def apply_updates(entries: list[Entry], updates: list[dict]) -> list[str]:
    applied = []
    for i, e in enumerate(entries):
        upd = next((u for u in updates if u.get("id") == e.id), None)
        if not upd:
            continue
        data = e.model_dump(mode="json")
        for key in EDITABLE:
            if key in upd:
                data[key] = upd[key]
        entries[i] = Entry.model_validate(data)
        applied.append(e.id)
    return applied


def apply_new(entries: list[Entry], new_entries: list[dict], today: date,
              verifier: Callable[[Entry], str | None] | None = None,
              ) -> tuple[list[str], list[str]]:
    """Validate, dedupe (by id and domain) and probe-verify proposals.

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


def apply_supersede(entries: list[Entry], supersede: list[dict]) -> list[str]:
    done = []
    for s in supersede:
        for e in entries:
            for m in e.models:
                if m.family == s.get("family") and s.get("superseded_by"):
                    m.superseded_by = s["superseded_by"]
                    done.append(m.family)
    return done


def run_scout(llm, entries: list[Entry], failures: list[dict],
              page_fetcher: Callable[[list[str]], dict[str, str]], today: date,
              evidence: Evidence | None = None,
              verifier: Callable[[Entry], str | None] | None = None) -> dict:
    result = {"updates": [], "new": [], "rejected": [], "supersede": [],
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
        data = _parse(llm.complete(FIX_PROMPT.format(context=context)))
        result["updates"] = apply_updates(entries, data.get("updates") or [])

    if evidence is not None and not evidence.is_empty():
        data = _parse(llm.complete(DISCOVER_PROMPT.format(
            existing=", ".join(e.id for e in entries),
            domains=", ".join(sorted({domain_of(e.url) for e in entries})),
            evidence=format_evidence(evidence),
        )))
        result["new"], result["rejected"] = apply_new(
            entries, data.get("new_entries") or [], today, verifier)

    families = sorted({m.family for e in entries for m in e.models})
    if families:
        data = _parse(llm.complete(GENERATIONS_PROMPT.format(families=", ".join(families))))
        result["supersede"] = apply_supersede(entries, data.get("supersede") or [])

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures/failures.json"))
    parser.add_argument("--pr-body", type=Path, default=Path("scout-pr.md"))
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY")
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if not gemini_key and not or_key:
        print("no LLM keys configured, skipping scout")
        return

    entries = load_registry(args.registry)
    failures = json.loads(args.failures.read_text()) if args.failures.exists() else []
    llm = LLMClient(gemini_key, or_key, os.environ.get("SCOUT_OPENROUTER_MODEL"))

    known_domains = {domain_of(e.url) for e in entries}
    known_domains |= {domain_of(u) for e in entries for u in e.source_urls}
    evidence = gather_evidence(DISCOVERY_QUERIES, known_domains, os.environ)
    print(f"evidence: {len(evidence.hits)} hits, {len(evidence.pages)} pages, "
          f"providers: {', '.join(evidence.providers) or 'none'}")

    with httpx.Client(timeout=httpx.Timeout(20.0, connect=10.0),
                      headers={"User-Agent": "freetier-radar/0.2"}) as probe_client:
        result = run_scout(llm, entries, failures, fetch_page_texts, date.today(),
                           evidence=evidence,
                           verifier=lambda e: probe_check_sync(e, probe_client))

    save_registry(args.registry, entries)
    args.pr_body.write_text(PR_BODY_TEMPLATE.format(
        providers=", ".join(result["providers"]) or "none",
        updates=", ".join(result["updates"]) or "—",
        new=", ".join(result["new"]) or "—",
        rejected="; ".join(result["rejected"]) or "—",
        supersede=", ".join(result["supersede"]) or "—",
    ), encoding="utf-8")
    print(f"scout: {result}")
