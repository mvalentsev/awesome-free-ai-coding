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

from .models import Entry, load_registry, save_registry

EDITABLE = {"offering", "limits", "card_required", "probe", "models"}

DISCOVERY_QUERIES = [
    "free tier LLM API coding 2026",
    "AI coding agent free plan no credit card",
    "new free LLM endpoint frontier model",
]

SYSTEM_RULES = (
    "You update a registry of LEGAL free LLM coding resources. "
    "Output ONLY a yaml code block, no prose. Never invent URLs or limits: "
    "use only facts from the provided page texts. If unsure, output an empty list."
)

FIX_PROMPT = SYSTEM_RULES + """
TASK: FIX-FAILED probes. For each failed entry, using its official page text below,
propose corrected values. Allowed keys per update: id (unchanged), offering, limits,
card_required, probe, models.
Output format:
updates:
  - id: <existing id>
    <changed keys only>
FAILED ENTRIES AND PAGE TEXTS:
{context}
"""

DISCOVER_PROMPT = SYSTEM_RULES + """
TASK: DISCOVER-NEW legal free coding tools / free-tier LLM APIs / no-card trials.
Existing ids (do not repeat): {existing}
Focus areas: {queries}
Output format:
new_entries:
  - id: <slug>
    name: ...
    category: agent-cli | api-free-tier | trial | aggregator
    url: ...
    source_urls: [...]
    card_required: false
    offering: ...
    limits: ...
    probe: {{type: page-keywords, endpoint: <official url>, keywords: ["free"]}}
Only include entries you have page evidence for. Max 5.
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

Updated entries: {updates}
New entries: {new}
Superseded families: {supersede}

_Proposed by LLM scout — review before merging. Probes will re-verify after merge._
"""


class LLMClient:
    def __init__(self, gemini_key: str | None, openrouter_key: str | None,
                 openrouter_model: str = "deepseek/deepseek-chat-v3-0324:free",
                 http: httpx.Client | None = None):
        self._gemini_key = gemini_key
        self._or_key = openrouter_key
        self._or_model = openrouter_model
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
               f"gemini-2.5-flash:generateContent?key={self._gemini_key}")
        r = self._http.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _openrouter(self, prompt: str) -> str:
        if not self._or_key:
            raise RuntimeError("no OPENROUTER_API_KEY")
        r = self._http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self._or_key}"},
            json={"model": self._or_model, "messages": [{"role": "user", "content": prompt}]},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def extract_yaml_block(text: str) -> str:
    m = re.search(r"```(?:yaml)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def _parse(text: str) -> dict:
    data = yaml.safe_load(extract_yaml_block(text))
    return data if isinstance(data, dict) else {}


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


def apply_new(entries: list[Entry], new_entries: list[dict], today: date) -> list[str]:
    existing = {e.id for e in entries}
    added = []
    for raw in new_entries:
        if not isinstance(raw, dict) or raw.get("id") in existing:
            continue
        try:
            e = Entry.model_validate({**raw, "first_seen": today, "last_verified": today,
                                      "provisional": True, "probe_failures": 0})
        except Exception:
            continue
        entries.append(e)
        existing.add(e.id)
        added.append(e.id)
    return added


def apply_supersede(entries: list[Entry], supersede: list[dict]) -> list[str]:
    done = []
    for s in supersede:
        for e in entries:
            for m in e.models:
                if m.family == s.get("family") and s.get("superseded_by"):
                    m.superseded_by = s["superseded_by"]
                    done.append(m.family)
    return done


def fetch_pages(urls: list[str]) -> dict[str, str]:
    out = {}
    with httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0), follow_redirects=True) as client:
        for u in urls:
            try:
                r = client.get(u)
                text = re.sub(r"<[^>]+>", " ", r.text)
                out[u] = re.sub(r"\s+", " ", text)[:4000]
            except httpx.HTTPError:
                out[u] = ""
    return out


def run_scout(llm, entries: list[Entry], failures: list[dict],
              page_fetcher: Callable[[list[str]], dict[str, str]], today: date) -> dict:
    result = {"updates": [], "new": [], "supersede": []}

    if failures:
        failed_ids = {f["id"] for f in failures}
        ctx_entries = [e for e in entries if e.id in failed_ids]
        urls = [u for e in ctx_entries for u in e.source_urls]
        pages = page_fetcher(urls)
        context = "\n\n".join(
            f"ENTRY:\n{yaml.safe_dump(e.model_dump(mode='json', exclude_none=True), sort_keys=False)}"
            + "\n".join(f"PAGE {u}:\n{pages.get(u, '')}" for u in e.source_urls)
            for e in ctx_entries
        )
        data = _parse(llm.complete(FIX_PROMPT.format(context=context)))
        result["updates"] = apply_updates(entries, data.get("updates") or [])

    data = _parse(llm.complete(DISCOVER_PROMPT.format(
        existing=", ".join(e.id for e in entries), queries="; ".join(DISCOVERY_QUERIES))))
    result["new"] = apply_new(entries, data.get("new_entries") or [], today)

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
    llm = LLMClient(gemini_key, or_key, os.environ.get("SCOUT_OPENROUTER_MODEL",
                                                       "deepseek/deepseek-chat-v3-0324:free"))
    result = run_scout(llm, entries, failures, fetch_pages, date.today())
    save_registry(args.registry, entries)
    args.pr_body.write_text(PR_BODY_TEMPLATE.format(**result), encoding="utf-8")
    print(f"scout: {result}")
