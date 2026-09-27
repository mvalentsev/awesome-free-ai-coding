"""Every phrase a row puts in quotation marks, read back against the pages it cites.

A probe checks its keywords and nothing else. The prose around them —
`offering`, `limits`, `api.note` — is written by hand, and quotation marks say
its words are the vendor's; this checks that claim. For each live row it reads
the row's pages (see `row_urls`), keeps both the rendered text and the raw body
— a quote can live in JSON-LD or a framework payload — and looks for every
quote of three words or more in them, with the typography flattened (see
`flatten`). A quote joined across an ellipsis is checked fragment by fragment.
What is not found is printed with its row and field, and the fix is one of two
things: the vendor's exact words, or a source URL that carries them.
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
from .prober import CONCURRENCY, TAG, UA, _plain_spaces, _rendered, probe_page_url

TIMEOUT = httpx.Timeout(30.0, connect=10.0)
MIN_WORDS = 3

_QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')
_ELLIPSIS = re.compile(r"\s*(?:…|\.\.\.)\s*")
_MARKDOWN_LINK = re.compile(r"\[([^\]\n]*)\]\([^)\s]*\)")
# Han and kana make up the words of a Chinese or Japanese sentence, and CJK
# punctuation and full-width forms sit between them. Neither script puts a space
# between words, so a space beside any of them is what a stripped tag left.
_HAN_OR_KANA = "぀-ヿ㐀-䶿一-鿿豈-﫿"
_CJK = _HAN_OR_KANA + "、-〿＀-￯"
_CJK_WORD_CHAR = re.compile(f"[{_HAN_OR_KANA}]")
_SPACE_BESIDE_CJK = re.compile(f"\\s+(?=[{_CJK}])|(?<=[{_CJK}])\\s+")
_JSON_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")
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
    # answer at all: a refused read (Qodo's terms page refuses some with 403) is
    # not a vendor rewording.
    unverified: bool = False


def flatten(text: str) -> str:
    """Text reduced to what a reader would copy: no markup, a markdown link read
    as its text, one kind of quote, apostrophe and dash, single spaces, no space
    a stripped tag left before punctuation or beside a Chinese or Japanese
    character — a sentence there has none, and a link inside it leaves one —
    lower case."""
    text = text.replace('\\"', '"').replace("\\n", " ")
    # Page data escapes the way JSON does: Freebuff's JSON-LD FAQ carries
    # "Smart & Fast" as `Smart \u0026 Fast`.
    text = html.unescape(_JSON_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), text))
    text = _plain_spaces(_MARKDOWN_LINK.sub(r"\1", text)).translate(_TYPOGRAPHY)
    text = _SPACE_BEFORE_PUNCTUATION.sub(r"\1", " ".join(text.split()))
    return _SPACE_BESIDE_CJK.sub("", text).lower()


def page_texts(body: str) -> list[str]:
    """What a quote is looked for in on one page: the rendered text and the raw
    body, both flattened — a quote can live in JSON-LD or a framework payload."""
    return [flatten(TAG.sub(" ", _rendered(body))), flatten(TAG.sub(" ", body))]


def words(text: str) -> float:
    """How many words a phrase holds. Chinese and Japanese put no space between
    words, so `str.split()` would count a whole sentence of them as one; there,
    two characters count as a word, about what one runs to."""
    return len(_CJK_WORD_CHAR.sub(" ", text).split()) + len(_CJK_WORD_CHAR.findall(text)) / 2


def quotes_in(text: str) -> list[str]:
    """The quoted phrases worth checking: three words or more. Shorter quotes are
    labels ("Free", "$0") that match anywhere and prove nothing. Quotation marks
    are for the vendor's published words; what an endpoint or a client answered
    — an error body, a status line — is written in backticks, which no page
    carries and this does not read."""
    found = []
    for match in _QUOTED.finditer(text or ""):
        quote = (match.group(1) or match.group(2)).strip()
        if words(quote) >= MIN_WORDS:
            found.append(quote)
    return found


def row_quotes(entry: Entry) -> list[tuple[str, str]]:
    fields = [("offering", entry.offering), ("limits", entry.limits)]
    if entry.api and entry.api.note:
        fields.append(("api.note", entry.api.note))
    found = [(field, quote) for field, text in fields for quote in quotes_in(text)]
    # Quoted by construction, whatever its length: the page prints it in quotes.
    if entry.data_use:
        found.append(("data_use.quote", entry.data_use.quote))
    return found


def quote_found(quote: str, pages: list[str]) -> bool:
    """Whether every fragment of `quote` occurs in one of the flattened pages.
    Fragments of two words or fewer, left by an ellipsis, are skipped."""
    fragments = [flatten(f) for f in _ELLIPSIS.split(quote)]
    fragments = [f.strip(" ,;:.") for f in fragments if words(f) > 2]
    if not fragments:
        return True
    return all(any(f in page for page in pages) for f in fragments)


def row_urls(entry: Entry, page: str | None = None) -> list[str]:
    """The row's sources, its probe's page — `page` where the probe follows an
    index to it, the endpoint otherwise — its catalog, and the page its word on
    training is quoted from."""
    urls = list(entry.source_urls) + [page or entry.probe.endpoint]
    if entry.probe.catalog:
        urls.append(entry.probe.catalog)
    if entry.data_use:
        urls.append(entry.data_use.url)
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
        return url, page_texts(resp.text)

    pages: list[str] = []
    unread: list[str] = []
    for _, got in await asyncio.gather(*(one(u) for u in urls)):
        if isinstance(got, str):
            unread.append(got)
        else:
            pages.extend(got)
    return pages, unread


def live_rows(entries: list[Entry], today: date) -> list[Entry]:
    """The rows whose quotes are read: an archived row's pages are the ones that
    ended, and its quotes are history. A shutdown still to come archives
    nothing yet."""
    return [e for e in entries if not is_archived(e, today)]


async def check_entries(entries: list[Entry], client: httpx.AsyncClient,
                        today: date | None = None
                        ) -> tuple[list[Missing], dict[str, list[str]]]:
    missing: list[Missing] = []
    unread: dict[str, list[str]] = {}
    for entry in live_rows(entries, today or date.today()):
        quotes = row_quotes(entry)
        if not quotes:
            continue
        page = await probe_page_url(client, entry.probe) if entry.probe.follow else None
        pages, failed = await fetch_pages(client, row_urls(entry, page))
        if failed:
            unread[entry.id] = failed
        for field, quote in quotes:
            if not quote_found(quote, pages):
                missing.append(Missing(entry.id, field, quote, unverified=bool(failed)))
    return missing, unread


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def summary(missing: list[Missing], quotes: int, rows: int) -> str:
    """The line a pass ends on: how much it read and what it did not find."""
    confirmed = sum(not m.unverified for m in missing)
    unverified = len(missing) - confirmed
    return (f"checked {_count(quotes, 'quote')} in {_count(rows, 'row')} — {confirmed} not found on "
            f"the rows' own sources"
            + (f", {unverified} unverified because a source did not answer" if unverified else ""))


def markdown(missing: list[Missing], unread: dict[str, list[str]], quotes: int, rows: int) -> str:
    """The pass as the scheduled run prints it in its summary, beside the models
    owed a family: each quote gone from its row's pages, each one no page that
    answered carries while another did not answer, each source that did not
    answer — a list of rows to read again, not a verdict on any of them."""
    lines = ["## Quotes no longer on their pages", ""]
    gone = [m for m in missing if not m.unverified]
    unsure = [m for m in missing if m.unverified]
    if not missing and not unread:
        lines += ["Every quoted phrase is on its row's own pages.", ""]
    if gone:
        lines += ["**Not on its sources** — read the vendor's page again, then quote its words as "
                  "they stand or point `source_urls` at the page that has them:", ""]
        lines += [f'- {m.entry_id} {m.field}: "{m.quote}"' for m in gone]
        lines.append("")
    if unsure:
        lines += ["**Unverified** — not on the sources that answered, while another did not:", ""]
        lines += [f'- {m.entry_id} {m.field}: "{m.quote}"' for m in unsure]
        lines.append("")
    if unread:
        lines += ["**Sources not read:**", ""]
        lines += [f"- {entry_id}: {line}" for entry_id, failed in unread.items() for line in failed]
        lines.append("")
    lines.append(summary(missing, quotes, rows))
    return "\n".join(lines) + "\n"


async def _amain(registry: Path, ids: list[str], report: bool = False) -> int:
    entries = load_registry(registry)
    if ids:
        entries = [e for e in entries if e.id in ids]
    today = date.today()
    async with httpx.AsyncClient(headers=UA) as client:
        missing, unread = await check_entries(entries, client, today)
    read = live_rows(entries, today)
    quotes = sum(len(row_quotes(e)) for e in read)
    if report:
        # A report, not a check: the run that prints it carries on to commit
        # what it verified, and the rows it names are read again by a person.
        print(markdown(missing, unread, quotes, len(read)), end="")
        return 0
    for entry_id, lines in unread.items():
        for line in lines:
            print(f"  {entry_id}: source not read — {line}")
    for m in missing:
        if m.unverified:
            print(f"  {m.entry_id} {m.field}: unverified — not on the sources that answered, and "
                  f"{'; '.join(unread[m.entry_id])} — \"{m.quote}\"")
        else:
            print(f"  {m.entry_id} {m.field}: not on its sources — \"{m.quote}\"")
    print(summary(missing, quotes, len(read)))
    # A refused read is a reason to read again, not a quote to rewrite.
    return sum(not m.unverified for m in missing)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=Path("registry.yaml"))
    parser.add_argument("ids", nargs="*", help="only these rows")
    parser.add_argument("--report", action="store_true",
                        help="print the pass as markdown for a run summary, and exit 0")
    args = parser.parse_args()
    sys.exit(1 if asyncio.run(_amain(args.registry, args.ids, args.report)) else 0)
