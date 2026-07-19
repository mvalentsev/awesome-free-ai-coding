from __future__ import annotations

import argparse
import asyncio
import json
from datetime import date
from pathlib import Path

import httpx

from .models import Entry, ProbeType, load_registry, save_registry

TIMEOUT = httpx.Timeout(20.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.1 (+https://github.com/awesome-free-ai-coding)"}


async def probe_entry(client: httpx.AsyncClient, entry: Entry) -> str | None:
    """None = проба прошла, строка = описание проблемы."""
    try:
        resp = await client.get(entry.probe.endpoint, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        return f"http error: {exc}"
    if entry.probe.type is ProbeType.API_MODELS:
        return _check_api_models(resp, entry)
    return _check_page_keywords(resp, entry)


def _check_api_models(resp: httpx.Response, entry: Entry) -> str | None:
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return "response is not JSON"
    items = data.get("data", []) if isinstance(data, dict) else []
    ids = [str(m.get("id", "")).lower() for m in items if isinstance(m, dict)]
    if not ids:
        return "no model ids in response"
    marker = entry.probe.free_marker.lower()
    missing = [
        m.family for m in entry.models
        if not any(m.family.lower() in mid and (not marker or marker in mid) for mid in ids)
    ]
    return f"missing families: {', '.join(missing)}" if missing else None


def _check_page_keywords(resp: httpx.Response, entry: Entry) -> str | None:
    text = resp.text.lower()
    missing = [k for k in entry.probe.keywords if k.lower() not in text]
    return f"missing keywords: {', '.join(missing)}" if missing else None


def apply_results(entries: list[Entry], results: dict[str, str | None], today: date) -> list[Entry]:
    failed = []
    for e in entries:
        detail = results.get(e.id)
        if detail is None:
            e.last_verified = today
            e.probe_failures = 0
        else:
            e.probe_failures += 1
            failed.append(e)
    return failed


async def _amain(registry_path: Path, failures_dir: Path) -> None:
    entries = load_registry(registry_path)
    async with httpx.AsyncClient(headers=UA) as client:
        results = {e.id: await probe_entry(client, e) for e in entries}
    failed = apply_results(entries, results, date.today())
    save_registry(registry_path, entries)
    failures_dir.mkdir(parents=True, exist_ok=True)
    payload = [{"id": e.id, "detail": results[e.id]} for e in failed]
    (failures_dir / "failures.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"probed {len(entries)} entries, {len(failed)} failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures"))
    args = parser.parse_args()
    asyncio.run(_amain(args.registry, args.failures))
