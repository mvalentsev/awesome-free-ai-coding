"""Every phrase a row puts in quotation marks, read back against the pages it cites.

A probe checks its keywords and nothing else. The prose around them —
`offering`, `limits`, `api.note` — is written by hand, much of it from research
that quoted the vendor, and nothing ever read it back. On 2026-09-16 an audit of
the seventeen provisional rows found quotes that were on none of the vendor's
pages: MegaNova's "Free, no credit card required" (its page says "Free
registration — no credit card required"), LLMTR's "Prompt ve yanıt içeriği
saklanmaz" (its privacy page promises something narrower), and a Freebuff data
policy quoted after the vendor had reversed it. Quotation marks say the words
are the vendor's, and this checks that claim.

For each row it reads the `source_urls` and the probe endpoint, keeps both the
rendered text and the raw body — a quote can live in JSON-LD or a framework
payload — and looks for every quote of three words or more in them, with the
typography flattened: entities, tags, markdown emphasis, curly quotes and
apostrophes, dashes and whitespace. A quote joined across an ellipsis is checked
fragment by fragment. What is not found is printed with its row and field, and
the fix is one of two things: the vendor's exact words, or a source URL that
carries them.
"""
from __future__ import annotations

import argparse
import asyncio
import html
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import httpx

from .models import Entry, is_archived, load_registry
from .prober import UA, _plain_spaces, _rendered

TIMEOUT = httpx.Timeout(30.0, connect=10.0)
CONCURRENCY = 8
MIN_WORDS = 3

_QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')
_ELLIPSIS = re.compile(r"\s*(?:…|\.\.\.)\s*")
_TAG = re.compile(r"<[^>]+>")
_SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+([,.;:!?)])")
_TYPOGRAPHY = str.maketrans({
    "“": '"', "”": '"', "„": '"', "’": "'", "‘": "'", "`": "'",
    "–": "-", "—": "-", "‑": "-", "−": "-",
    "*": " ", "_": " ",
})


@dataclass(frozen=True)
class Missing:
    entry_id: str
    field: str
    quote: str
    # Not on the pages that answered, while another of the row's sources did not
    # answer at all. Qodo's terms page refuses some reads with 403 and serves the
    # next, and a refused read made its quote look like a vendor rewording.
    unverified: bool = False


def flatten(text: str) -> str:
    """Text reduced to what a reader would copy: no markup, one kind of quote,
    apostrophe and dash, single spaces, no space a stripped tag left before
    punctuation, lower case."""
    text = html.unescape(text.replace('\\"', '"').replace("\\n", " "))
    text = _plain_spaces(text).translate(_TYPOGRAPHY)
    return _SPACE_BEFORE_PUNCTUATION.sub(r"\1", " ".join(text.split())).lower()


def quotes_in(text: str) -> list[str]:
    """The quoted phrases worth checking: three words or more. Shorter quotes are
    labels ("Free", "$0") that match anywhere and prove nothing. Quotation marks
    are for the vendor's published words; what an endpoint or a client answered
    — an error body, a status line — is written in backticks, which no page
    carries and this does not read."""
    found = []
    for match in _QUOTED.finditer(text or ""):
        quote = (match.group(1) or match.group(2)).strip()
        if len(quote.split()) >= MIN_WORDS:
            found.append(quote)
    return found


def row_quotes(entry: Entry) -> list[tuple[str, str]]:
    fields = [("offering", entry.offering), ("limits", entry.limits)]
    if entry.api and entry.api.note:
        fields.append(("api.note", entry.api.note))
    return [(field, quote) for field, text in fields for quote in quotes_in(text)]


def quote_found(quote: str, pages: list[str]) -> bool:
    """Whether every fragment of `quote` occurs in one of the flattened pages.
    Fragments of two words or fewer, left by an ellipsis, are skipped."""
    fragments = [flatten(f) for f in _ELLIPSIS.split(quote)]
    fragments = [f.strip(" ,;:.") for f in fragments if len(f.split()) > 2]
    if not fragments:
        return True
    return all(any(f in page for page in pages) for f in fragments)


def row_urls(entry: Entry) -> list[str]:
    urls = list(entry.source_urls) + [entry.probe.endpoint]
    if entry.probe.catalog:
        urls.append(entry.probe.catalog)
    return list(dict.fromkeys(urls))


async def fetch_pages(client: httpx.AsyncClient, urls: list[str]) -> tuple[list[str], list[str]]:
    """The flattened rendered text and raw body of every url that answered, and
    a line for each that did not — a quote is only as checked as its sources."""
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(url: str) -> tuple[str, list[str] | str]:
        async with sem:
            try:
                resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
            except httpx.HTTPError as exc:
                return url, f"{url}: {type(exc).__name__}"
        if resp.status_code >= 400:
            return url, f"{url}: HTTP {resp.status_code}"
        rendered = flatten(_TAG.sub(" ", _rendered(resp.text)))
        return url, [rendered, flatten(_TAG.sub(" ", resp.text))]

    pages: list[str] = []
    unread: list[str] = []
    for _, got in await asyncio.gather(*(one(u) for u in urls)):
        if isinstance(got, str):
            unread.append(got)
        else:
            pages.extend(got)
    return pages, unread


async def check_entries(entries: list[Entry], client: httpx.AsyncClient
                        ) -> tuple[list[Missing], dict[str, list[str]]]:
    missing: list[Missing] = []
    unread: dict[str, list[str]] = {}
    for entry in entries:
        # An archived row's pages are the ones that ended; its quotes are history.
        if entry.retired_on is not None or is_archived(entry, date.today()):
            continue
        quotes = row_quotes(entry)
        if not quotes:
            continue
        pages, failed = await fetch_pages(client, row_urls(entry))
        if failed:
            unread[entry.id] = failed
        for field, quote in quotes:
            if not quote_found(quote, pages):
                missing.append(Missing(entry.id, field, quote, unverified=bool(failed)))
    return missing, unread


async def _amain(registry: Path, ids: list[str]) -> int:
    entries = load_registry(registry)
    if ids:
        entries = [e for e in entries if e.id in ids]
    async with httpx.AsyncClient(headers=UA) as client:
        missing, unread = await check_entries(entries, client)
    for entry_id, lines in unread.items():
        for line in lines:
            print(f"  {entry_id}: source not read — {line}")
    for m in missing:
        if m.unverified:
            print(f"  {m.entry_id} {m.field}: unverified — not on the sources that answered, and "
                  f"{'; '.join(unread[m.entry_id])} — \"{m.quote}\"")
        else:
            print(f"  {m.entry_id} {m.field}: not on its sources — \"{m.quote}\"")
    checked = sum(len(row_quotes(e)) for e in entries
                  if e.retired_on is None and not is_archived(e, date.today()))
    confirmed = [m for m in missing if not m.unverified]
    unverified = len(missing) - len(confirmed)
    print(f"checked {checked} quotes in {len(entries)} rows — {len(confirmed)} not found on the rows' own sources"
          + (f", {unverified} unverified because a source did not answer" if unverified else ""))
    # A refused read is a reason to read again, not a quote to rewrite.
    return len(confirmed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("ids", nargs="*", help="only these rows")
    args = parser.parse_args()
    sys.exit(1 if asyncio.run(_amain(args.registry, args.ids)) else 0)
