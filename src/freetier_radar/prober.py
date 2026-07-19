from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path

import httpx

from .models import Entry, ProbeType, load_registry, save_registry

TIMEOUT = httpx.Timeout(20.0, connect=10.0)
UA = {"User-Agent": "freetier-radar/0.2"}
ATTEMPTS = 3
BACKOFF_SECONDS = 2.0
CONCURRENCY = 8


class ProbeStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"  # page reachable but the free offer is no longer evidenced
    INCONCLUSIVE = "inconclusive"  # could not check: blocked, down, network error


@dataclass
class ProbeResult:
    status: ProbeStatus
    detail: str = ""


async def probe_entry(client: httpx.AsyncClient, entry: Entry,
                      attempts: int = ATTEMPTS, backoff: float = BACKOFF_SECONDS) -> ProbeResult:
    last = ""
    for i in range(attempts):
        if i:
            await asyncio.sleep(backoff * i)
        try:
            resp = await client.get(entry.probe.endpoint, timeout=TIMEOUT, follow_redirects=True)
        except httpx.HTTPError as exc:
            last = f"network error: {exc}"
            continue
        if resp.status_code in (401, 403, 429):
            return ProbeResult(ProbeStatus.INCONCLUSIVE, f"blocked: HTTP {resp.status_code}")
        if resp.status_code >= 500:
            last = f"HTTP {resp.status_code}"
            continue
        if resp.status_code >= 400:
            return ProbeResult(ProbeStatus.FAIL, f"page gone: HTTP {resp.status_code}")
        detail = check_content(resp, entry)
        if detail is None:
            return ProbeResult(ProbeStatus.PASS)
        return ProbeResult(ProbeStatus.FAIL, detail)
    return ProbeResult(ProbeStatus.INCONCLUSIVE, f"unreachable after {attempts} attempts: {last}")


def check_content(resp: httpx.Response, entry: Entry) -> str | None:
    """None = content confirms the entry; string = what is missing.

    Works on both sync and async httpx responses, so the scout reuses it to
    vet newly proposed entries before accepting them.
    """
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


def apply_results(entries: list[Entry], results: dict[str, ProbeResult], today: date) -> list[Entry]:
    """PASS verifies and resets failures; FAIL increments them; INCONCLUSIVE
    touches nothing — the staleness rule archives entries that stay unverifiable.
    Returns entries needing scout attention (FAIL and INCONCLUSIVE)."""
    needs_attention = []
    for e in entries:
        result = results.get(e.id)
        if result is None:
            continue
        if result.status is ProbeStatus.PASS:
            e.last_verified = today
            e.probe_failures = 0
        else:
            if result.status is ProbeStatus.FAIL:
                e.probe_failures += 1
            needs_attention.append(e)
    return needs_attention


async def _amain(registry_path: Path, failures_dir: Path) -> None:
    entries = load_registry(registry_path)
    sem = asyncio.Semaphore(CONCURRENCY)

    async def bounded(entry: Entry) -> ProbeResult:
        async with sem:
            return await probe_entry(client, entry)

    async with httpx.AsyncClient(headers=UA) as client:
        outcomes = await asyncio.gather(*(bounded(e) for e in entries))
    results = {e.id: r for e, r in zip(entries, outcomes)}
    flagged = apply_results(entries, results, date.today())
    save_registry(registry_path, entries)
    failures_dir.mkdir(parents=True, exist_ok=True)
    payload = [
        {"id": e.id, "status": results[e.id].status.value, "detail": results[e.id].detail}
        for e in flagged
    ]
    (failures_dir / "failures.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"probed {len(entries)} entries, {len(flagged)} need attention")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("--failures", type=Path, default=Path("failures"))
    args = parser.parse_args()
    asyncio.run(_amain(args.registry, args.failures))
