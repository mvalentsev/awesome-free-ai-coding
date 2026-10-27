"""Collect current sources for dated human reviews of retained archived offers."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import time
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from .models import Entry, is_archived_for_good, is_blocked, load_blocklist, load_registry, site_of
from .page_reader import RECOVERY_BYTES, RECOVERY_REDIRECTS
from .prober import (CONCURRENCY, TIMEOUT, UA, check_content, followed_url,
                     join_free_list, page_response_ok)
from .quotes import row_urls
from .review import Bundle
from .source_urls import valid_source_url

ARCHIVE_RECHECK_DAYS = 7
ARCHIVE_REVIEW_SECONDS = 120


def due_entries(entries: list[Entry], blocklist: dict[str, str], today: date,
                *, all_archived: bool = False) -> list[Entry]:
    """Verification never restores these rows; a current manual judgment can."""
    return [e for e in entries if is_archived_for_good(e, today)
            and not e.duplicate_of and not is_blocked(site_of(e.url), blocklist)
            and (all_archived or e.archive_review is None
                 or (today - e.archive_review.checked_on).days >= ARCHIVE_RECHECK_DAYS)]


async def collect(entries: list[Entry], blocklist: dict[str, str], today: date,
                  bundle: Bundle, *, all_archived: bool = False,
                  client: httpx.AsyncClient | None = None) -> dict:
    selected = due_entries(entries, blocklist, today, all_archived=all_archived)
    deadline = time.monotonic() + ARCHIVE_REVIEW_SECONDS
    semaphore = asyncio.Semaphore(CONCURRENCY)
    sources, bodies = {}, {}

    async def guard(request):
        if (not valid_source_url(str(request.url))
                or is_blocked(site_of(str(request.url)), blocklist)):
            raise httpx.RequestError('archive source is excluded', request=request)

    async def one(url):
        async with semaphore:
            record = {'url': url, 'at': datetime.now(timezone.utc).isoformat(), 'readable': False}
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                record['error'] = 'archive source budget exhausted'
                return record
            async def read():
                # Ordinary HTTP only. A wall remains unavailable evidence. The
                # request hook checks every redirect before sending it.
                async with http.stream('GET', url, follow_redirects=True) as response:
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        if len(body) + len(chunk) > RECOVERY_BYTES:
                            raise ValueError('archive source exceeds body limit')
                        body.extend(chunk)
                    name = 'http/' + hashlib.sha256(url.encode()).hexdigest()[:24] + '.raw'
                    record.update(status=response.status_code, final_url=str(response.url),
                                  retry_after=response.headers.get('retry-after'),
                                  file=bundle.write(name, bytes(body)))
                    headers = {key: value for key, value in response.headers.items()
                               if key.lower() not in ('content-encoding', 'content-length')}
                    saved = httpx.Response(response.status_code, content=bytes(body),
                                           headers=headers, request=response.request)
                    record['readable'] = page_response_ok(saved)
                    if record['readable']:
                        bodies[url] = saved
            try:
                await asyncio.wait_for(read(), timeout=remaining)
            except (httpx.HTTPError, asyncio.TimeoutError, ValueError) as exc:
                record['error'] = str(exc) or type(exc).__name__
            return record

    async def run():
        urls = {url for e in selected for url in row_urls(e)}
        urls.update(e.probe.free_list for e in selected if e.probe.free_list)
        for record in await asyncio.gather(*(one(url) for url in sorted(urls))):
            sources[record['url']] = record
        followed = {}
        for e in selected:
            response = bodies.get(e.probe.endpoint)
            if response is not None and e.probe.follow:
                try:
                    target = followed_url(response.json(), e.probe.follow)
                except ValueError:
                    target = None
                followed[e.id] = target
        for record in await asyncio.gather(*(one(url) for url in sorted(
                {url for url in followed.values() if url and url not in sources}))):
            sources[record['url']] = record
        rows = []
        for e in selected:
            urls = row_urls(e)
            endpoint = followed.get(e.id, e.probe.endpoint)
            if e.probe.follow and not endpoint:
                notes = ['current probe index names no readable source']
            else:
                response = bodies.get(endpoint)
                notes = []
                if response is not None and e.probe.free_list:
                    listed = bodies.get(e.probe.free_list)
                    if listed is None:
                        response = None
                    else:
                        response, failure = join_free_list(response, listed, e.probe.lane)
                        if failure:
                            notes.append(failure)
                if response is None:
                    notes.append('last-offer probe source is unavailable')
                elif finding := check_content(response, e):
                    notes.append(finding)
            if endpoint and endpoint not in urls:
                urls.append(endpoint)
            if e.probe.free_list and e.probe.free_list not in urls:
                urls.append(e.probe.free_list)
            rows.append({'id': e.id, 'reviewed_on': str(e.archive_review.checked_on) if e.archive_review else None,
                         'reason': e.delisted.reason if e.delisted else 'vendor-announced retirement',
                         'sources': urls, 'historical_probe_findings': notes,
                         'needs_manual_review': True})
        return bundle.save('archive-review', {
            'at': datetime.now(timezone.utc).isoformat(), 'date': today.isoformat(),
            'recheck_days': ARCHIVE_RECHECK_DAYS, 'rows': rows, 'sources': list(sources.values()),
            'scope': 'Current source receipts and last-offer checks for manual review of every advertised free mode. '
                     'A matching old probe, a changed page or an unavailable source does not establish current eligibility. '
                     'No registry, verification field or review date is written.'})

    if client is None:
        async with httpx.AsyncClient(headers=UA, timeout=TIMEOUT,
                                     max_redirects=RECOVERY_REDIRECTS,
                                     event_hooks={'request': [guard]}) as http:
            return await run()
    http = client
    http.event_hooks['request'].append(guard)
    try:
        return await run()
    finally:
        http.event_hooks['request'].remove(guard)


def markdown(result: dict) -> str:
    lines = ['## Archived offers due for review', '']
    if not result['rows']:
        return '\n'.join(lines + ['No archived offer is due for a manual review.', ''])
    lines += ['Review all current free modes before keeping or changing each archive decision. '
              'Source receipts are in the archive-review artifact; fetching them does not renew the review date.', '']
    by_url = {s['url']: s for s in result['sources']}
    for row in result['rows']:
        unread = sum(not by_url.get(url, {}).get('readable') for url in row['sources'])
        finding = '; '.join(row['historical_probe_findings']) or 'last-offer probe still matches'
        lines.append(f"- {row['id']}: {finding}; {unread}/{len(row['sources'])} sources unavailable; manual review required")
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=Path('registry.yaml'))
    parser.add_argument('--blocklist', type=Path, default=Path('blocklist.yaml'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--all', action='store_true', help='read every eligible archived offer regardless of its review date')
    args = parser.parse_args()
    bundle = Bundle(args.out, Path.cwd())
    result = asyncio.run(collect(load_registry(args.registry), load_blocklist(args.blocklist),
                                 date.today(), bundle, all_archived=args.all))
    print(markdown(result), end='')


if __name__ == '__main__':
    main()
