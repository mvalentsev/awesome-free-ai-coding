"""Recover anonymous public HTML after a confirmed browser challenge."""
from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import json
import os
import re
import socket
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import curl_cffi
import httpx
from curl_cffi.requests.exceptions import RequestException
from curl_cffi.curl import CURL_WRITEFUNC_ERROR

from .models import CHALLENGE_MARKERS

RECOVERY_SECONDS = 20
RECOVERY_REDIRECTS = 5
RECOVERY_BYTES = 8 * 1024 * 1024
# curl_cffi 0.16.3's Chrome profile recovered both original vendor pages in
# Actions on 2026-10-12. Source: curl-cffi.readthedocs.io/en/stable/impersonate/.
# This is HTTP browser impersonation, without a JavaScript runtime.
PROFILE = "chrome"
_evidence: ContextVar[Path | None] = ContextVar("page_read_evidence", default=None)


@contextmanager
def page_evidence(directory: Path):
    """Keep public wall/recovery receipts outside tracked repository files."""
    token = _evidence.set(directory)
    try:
        yield
    finally:
        _evidence.reset(token)


def public_page_url(url: str) -> bool:
    """A page URL, excluding credentials, API routes and private destinations."""
    try:
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        if (parsed.scheme != "https" or parsed.username or parsed.password or parsed.query
                or parsed.port not in (None, 443) or "." not in host
                or host.endswith((".local", ".localhost", ".internal"))
                or host.startswith("api.") or "/v1/" in parsed.path
                or "/api/" in parsed.path or parsed.path.rstrip("/").endswith(("/models", "/catalog"))):
            return False
        try:
            ipaddress.ip_address(host)
        except ValueError:
            return True
        return False
    except ValueError:
        return False


def _addresses(host: str) -> list[str]:
    addresses = sorted({result[4][0] for result in socket.getaddrinfo(
        host, 443, type=socket.SOCK_STREAM)})
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
        raise ValueError("page hostname does not resolve exclusively to public addresses")
    return addresses


def browser_challenge(response: httpx.Response) -> bool:
    if "html" not in response.headers.get("content-type", "").lower():
        return False
    raw = response.text.lower()
    if response.status_code == 403:
        return any(marker in raw for marker in CHALLENGE_MARKERS)
    # A normal rendered page can contain a noscript notice or discuss bot
    # checks. On HTTP 200 require the challenge title or its actual machinery.
    title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S)
    return (title is not None and any(m in title.group(1) for m in CHALLENGE_MARKERS)
            or any(m in raw for m in ("cf-browser-verification", "window._cf_chl_opt", "vercel security checkpoint")))


def _eligible(response: httpx.Response, client: httpx.Client | httpx.AsyncClient) -> bool:
    if (any(os.environ.get(k) for k in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"))
            or response.status_code not in (200, 403) or response.headers.get("retry-after")
            or client.auth is not None
            or "html" not in response.headers.get("content-type", "").lower()):
        return False
    credentials = ("authorization", "cookie", "x-api-key", "x-goog-api-key")
    # An ordinary redirect can strip query credentials or an Authorization
    # header. Inspect the original chain before starting an anonymous retry.
    for hop in [*response.history, response]:
        if (not public_page_url(str(hop.request.url)) or not public_page_url(str(hop.url))
                or any(h in hop.request.headers or h in client.headers for h in credentials)):
            return False
    return browser_challenge(response)


def _receipt(response: httpx.Response, backend: str) -> dict:
    return {"backend": backend, "at": datetime.now(timezone.utc).isoformat(),
            "status": response.status_code, "final_url": str(response.url),
            "content_type": response.headers.get("content-type"),
            "retry_after": response.headers.get("retry-after"),
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "body": response.content}


def _save(url: str, attempts: list[dict]) -> None:
    directory = _evidence.get()
    if directory is None:
        return
    directory.mkdir(parents=True, exist_ok=True)
    stem = uuid.uuid4().hex
    records = []
    for i, attempt in enumerate(attempts):
        record = {k: v for k, v in attempt.items() if k != "body"}
        if "body" in attempt:
            filename = f"{stem}-{i}.raw"
            (directory / filename).write_bytes(attempt["body"])
            record["file"] = filename
        records.append(record)
    (directory / f"{stem}.json").write_text(json.dumps(
        {"url": url, "attempts": records}, indent=2) + "\n")


def _profile_read(url: str, deadline: float, attempts: list[dict]) -> httpx.Response:
    """One fresh anonymous profile request per hop, with guarded redirects."""
    for hop in range(RECOVERY_REDIRECTS + 1):
        if not public_page_url(url):
            raise ValueError("recovery destination is not an anonymous public page")
        host = urlsplit(url).hostname
        addresses = _addresses(host)
        left = deadline - time.monotonic()
        if left <= 0:
            raise TimeoutError("page recovery budget exhausted")
        # Pin the checked addresses so a DNS change cannot turn this into a
        # private-network fetch. Never copy the original client's headers/auth.
        resolved = ",".join(f"[{a}]" if ":" in a else a for a in addresses)
        chunks, received = [], 0
        def receive(chunk: bytes) -> int:
            nonlocal received
            received += len(chunk)
            if received > RECOVERY_BYTES or time.monotonic() >= deadline:
                return CURL_WRITEFUNC_ERROR
            chunks.append(chunk)
            return len(chunk)
        answer = curl_cffi.get(url, impersonate=PROFILE, timeout=left,
            content_callback=receive,
            allow_redirects=False, headers={"Cache-Control": "no-cache"},
            curl_options={curl_cffi.CurlOpt.RESOLVE: [f"{host}:443:{resolved}".encode()],
                          curl_cffi.CurlOpt.MAXFILESIZE_LARGE: RECOVERY_BYTES})
        if httpx.URL(answer.url).copy_with(fragment=None) != httpx.URL(url).copy_with(fragment=None):
            raise ValueError("profile transport changed the requested source")
        content = b"".join(chunks) if chunks else answer.content
        if len(content) > RECOVERY_BYTES:
            raise ValueError("recovered page exceeds the body limit")
        # curl has already decoded the body. Preserve its wire encoding as
        # metadata, without asking httpx to decompress the HTML a second time.
        headers = {k: v for k, v in answer.headers.items()
                   if k.lower() not in ("content-encoding", "content-length")}
        response = httpx.Response(answer.status_code, content=content,
            headers=headers, request=httpx.Request("GET", answer.url))
        receipt = _receipt(response, "curl_cffi")
        receipt["wire_content_encoding"] = answer.headers.get("content-encoding")
        attempts.append(receipt)
        if response.status_code not in (301, 302, 303, 307, 308):
            return response
        location = response.headers.get("location")
        if not location or hop == RECOVERY_REDIRECTS:
            raise ValueError("recovery redirect was not completed")
        url = urljoin(url, location)
    raise ValueError("recovery redirect limit exceeded")


def recover_page_sync(client: httpx.Client | httpx.AsyncClient, response: httpx.Response,
                      *, time_left: float | None = None) -> httpx.Response:
    """Keep the direct answer unless a fresh anonymous HTML read succeeds.

    Callers opt in for page reads only. A reachable page missing a claim, an
    authentication refusal, a rate limit, or a gone page never starts recovery.
    """
    if not _eligible(response, client) or (time_left is not None and time_left <= 0):
        return response
    attempts = [_receipt(response, "httpx")]
    seconds = min(RECOVERY_SECONDS, time_left) if time_left is not None else RECOVERY_SECONDS
    result = response
    try:
        recovered = _profile_read(str(response.url), time.monotonic() + seconds, attempts)
        if (recovered.is_success and "html" in recovered.headers.get("content-type", "").lower()
                and not browser_challenge(recovered)):
            result = recovered
    except (RequestException, OSError, ValueError, TimeoutError) as exc:
        attempts.append({"backend": "curl_cffi", "at": datetime.now(timezone.utc).isoformat(),
                         "error": str(exc) or type(exc).__name__})
    for attempt in attempts[1:]:
        attempt.update(version=curl_cffi.__version__, profile=PROFILE)
    result.extensions["page_read_attempts"] = attempts
    _save(str(response.request.url), attempts)
    return result


async def recover_page(client: httpx.AsyncClient, response: httpx.Response) -> httpx.Response:
    if not _eligible(response, client):
        return response
    try:
        return await asyncio.wait_for(asyncio.to_thread(recover_page_sync, client, response),
                                      timeout=RECOVERY_SECONDS)
    except TimeoutError:
        return response
