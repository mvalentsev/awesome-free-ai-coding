"""Keep discovered provider/source links separate from completed vendor reviews."""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import yaml

from . import git
from .models import is_covered, site_of, valid_source_url

_ASSET = re.compile(r'\.(?:png|jpe?g|gif|webp|svg|ico|woff2?|ttf|css|js|mjs|mp[34]|zip|gz)$', re.I)
_COMPARISON = re.compile(r'(?:^|/)[^/]+-(?:alternatives?|competitors?)(?:/|$)', re.I)
_SOCIAL = {'x.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'youtu.be',
           'facebook.com', 'instagram.com', 'discord.com', 'discord.gg', 't.me',
           'telegram.org', 'bsky.app', 'reddit.com'}
LEAD_VERDICTS = ('canonical', 'task', 'irrelevant')


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and (href := dict(attrs).get('href')):
            self.links.append(href)


def answered_sites(repo: Path, sha: str) -> set[str]:
    """Use the committed decisions; expired verdicts do not answer new leads."""
    known = set()
    today = datetime.now(timezone.utc).date()
    for filename in ('registry.yaml', 'watchlist.yaml', 'blocklist.yaml', 'sources.yaml'):
        value = yaml.safe_load(git.show(repo, sha, filename) or '') or []
        if filename == 'registry.yaml':
            for row in value.get('entries', []) if isinstance(value, dict) else []:
                if row.get('delisted'):
                    continue
                urls = [row['url'], *row.get('source_urls', [])]
                if row.get('api'):
                    urls.append(row['api']['base_url'])
                known.update(site_of(u) for u in urls)
        elif filename == 'blocklist.yaml':
            known.update(r['domain'] for r in value)
        elif filename == 'watchlist.yaml':
            for row in value.get('watched', []) if isinstance(value, dict) else []:
                if (today - date.fromisoformat(str(row['checked_on']))).days <= 90:
                    known.update(row['domains'])
        else:
            for row in value.get('read', []) if isinstance(value, dict) else []:
                if (today - date.fromisoformat(str(row['checked_on']))).days <= 180:
                    # A directory verdict names a URL, not every repository
                    # published by its host or owner.
                    known.add(row['url'].rstrip('/'))
    return known


def collect_leads(bodies: dict[str, str], known: set[str]) -> list[dict]:
    """Capture unmatched links, including same-site competitor comparisons.

    These are review candidates, not assertions of a free offer or a guessed
    vendor domain. There is no recursive fetch or sign-up here.
    """
    leads = {}
    for source, body in sorted(bodies.items()):
        parser = _Links()
        parser.feed(body)
        links = [*parser.links, *re.findall(r'\[[^\]]+\]\((https?://[^\s)]+)\)', body)]
        links.extend(re.findall(r'(?m)^\s*\[[^\]]+\]:\s*<?(https?://[^\s<>]+)', body))
        if not parser.links:
            links.extend(re.findall(r'https?://[^\s<>"\x27`\\)\]]+', body))
        for href in links:
            try:
                parts = urlsplit(urljoin(source, href))
            except ValueError:
                continue
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))
            if not valid_source_url(url) or _ASSET.search(parts.path):
                continue
            comparison = bool(_COMPARISON.search(parts.path))
            if not comparison and (is_covered(url, {site_of(source)})
                    or is_covered(url, known) or url.rstrip('/') in known
                    or is_covered(url, _SOCIAL)):
                continue
            ident = hashlib.sha256(url.encode()).hexdigest()[:20]
            lead = leads.setdefault(ident, {'id': ident, 'url': url,
                'kind': 'comparison' if comparison else 'link', 'sources': []})
            if source not in lead['sources']:
                lead['sources'].append(source)
    return sorted(leads.values(), key=lambda v: v['url'])


def validate_dispositions(bundle, value: dict, *, imported: bool = False) -> None:
    inventory = bundle.load('sources', {}).get('lead_inventory', [])
    records = value.get('lead_dispositions', [])
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError('lead dispositions need structured records')
    if sorted(r.get('id', '') for r in records) != sorted(r['id'] for r in inventory):
        raise ValueError('lead dispositions must cover every captured provider/source lead')
    scope = bundle.load('scope')
    for record in records:
        if record.get('verdict') not in LEAD_VERDICTS:
            raise ValueError('lead disposition needs a canonical decision, persistent task or irrelevant finding')
        if not isinstance(record.get('finding'), str) or not record['finding'].strip():
            raise ValueError('lead disposition needs a concrete finding')
        evidence = record.get('evidence')
        if not isinstance(evidence, list) or not evidence or any(not isinstance(p, str) or not p for p in evidence):
            raise ValueError('lead disposition needs evidence')
        if imported and any(p not in bundle.files for p in evidence):
            raise ValueError('lead disposition evidence is not registered')
        if record['verdict'] == 'canonical':
            target = record.get('target', {})
            filename = target.get('file')
            if filename not in ('registry.yaml', 'watchlist.yaml', 'blocklist.yaml', 'sources.yaml'):
                raise ValueError('lead canonical disposition needs a curated decision file')
            current = yaml.safe_load(git.show(bundle.repo, scope['sha'], filename) or '') or []
            if isinstance(current, dict):
                current = current.get({'registry.yaml': 'entries', 'watchlist.yaml': 'watched', 'sources.yaml': 'read'}[filename], [])
            keys = {str(r.get('id', r.get('name', r.get('domain', r.get('url', ''))))) for r in current}
            if target.get('key') not in keys:
                raise ValueError('lead canonical decision does not exist at the reviewed commit')
        if record['verdict'] == 'task':
            task = record.get('task', {})
            filename = task.get('file', '')
            path = bundle.out / filename if imported else Path(filename)
            if not path.is_absolute():
                path = bundle.repo / path
            if imported and filename not in bundle.files:
                raise ValueError('lead task evidence is not registered')
            if not path.is_file():
                raise ValueError('lead disposition needs an existing persistent task register')
            import json
            tasks = json.loads(path.read_text()).get('tasks', [])
            matches = [t for t in tasks if t.get('id') == task.get('id')]
            states = {'open', 'scheduled', 'recurring', 'conditional', 'deferred', 'decision', 'idea'}
            if len(matches) != 1 or matches[0].get('status') not in states or not matches[0].get('next_action'):
                raise ValueError('lead disposition needs a retained unresolved task with a next action')
