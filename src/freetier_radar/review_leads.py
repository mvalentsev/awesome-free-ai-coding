"""Keep discovered provider/source links separate from completed vendor reviews."""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import yaml
from markdown_it import MarkdownIt

from . import git
from .models import (Source, Watched, is_covered, is_source_current, is_watch_current,
                     site_of, valid_source_url, utc_today)

_ASSET = re.compile(r'\.(?:png|jpe?g|gif|webp|svg|ico|woff2?|ttf|css|js|mjs|mp[34]|zip|gz)$', re.I)
_COMPARISON = re.compile(
    r'(?:^|/)(?:comparisons?|[^/]+-(?:alternatives?|competitors?)(?:-[^/]+)?|[^/]+-vs-[^/]+)(?:/|$)',
    re.I,
)
_COMPARISON_TEXT = re.compile(
    r'\balternatives?\s+to\s+\S|\b(?:comparisons?|alternatives?)\s+directory\b'
    r'|\ball\s+alternatives?\b|\b[\w.-]+\s+vs\.?\s+[\w.-]+\b', re.I,
)
_REVISION_COMPARE = re.compile(r'(?:^|/)compare/[^/]*\.{2,3}[^/]*(?:/|$)', re.I)
_NAVIGATION = re.compile(
    r'^(?:/[a-z]{2}(?:-[a-z]{2})?)?/(?:about|contact|privacy(?:-policy)?'
    r'|terms(?:-of-service|-and-conditions)?|cookies?|cookie-policy|pricing|plans'
    r'|login|logout|sign-?in|sign-?up|auth)/?$', re.I,
)
_DATA_SUFFIXES = {'.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.json', '.py', '.go', '.rs', '.css',
                  '.yaml', '.yml', '.toml', '.xml', '.csv'}
_HTML_TYPES = {'text/html', 'application/xhtml+xml'}
_MARKDOWN_TYPES = {'text/markdown', 'text/x-markdown', 'application/markdown'}
_SOCIAL = {'x.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'youtu.be',
           'facebook.com', 'instagram.com', 'discord.com', 'discord.gg', 't.me',
           'telegram.org', 'bsky.app', 'reddit.com'}
LEAD_VERDICTS = ('canonical', 'task', 'irrelevant')


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.labels = []
        self.current = None
        self.hidden = 0
        self.document = False
        self.preamble = True
        self.base_href = None

    def handle_decl(self, decl):
        if self.preamble and decl.lower().split()[:2] == ['doctype', 'html']:
            self.document = True

    def handle_starttag(self, tag, attrs):
        if self.preamble:
            self.document = self.document or tag in ('html', 'head', 'body')
            self.preamble = False
        attributes = dict(attrs)
        if tag == 'base' and self.base_href is None and attributes.get('href') is not None:
            self.base_href = attributes['href']
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag == 'a':
            self.current = None
        if tag == 'a' and (href := attributes.get('href')):
            self.links.append(href)
            self.labels.append([attributes.get('aria-label') or '', attributes.get('title') or ''])
            self.current = len(self.links)-1
        elif tag == 'img' and self.current is not None:
            self.labels[self.current].append(attributes.get('alt') or '')

    def handle_data(self, data):
        if data.strip('\ufeff \t\r\n'):
            self.preamble = False
        if self.current is not None and not self.hidden:
            self.labels[self.current].append(data)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden-1)
        if tag == 'a':
            self.current = None


def _markdown_links(body: str) -> list[tuple[str, str]]:
    def words(part):
        if part.children:
            return ' '.join(words(child) for child in part.children)
        return part.content if part.type in ('text', 'code_inline') else ''

    links = []
    html = _Links()
    for block in MarkdownIt('commonmark').parse(body):
        if block.type == 'html_block':
            html.feed(block.content)
        href, label = None, []
        for part in block.children or []:
            if part.type == 'html_inline':
                html.feed(part.content)
            elif part.type == 'link_open' and not html.hidden:
                href, label = part.attrGet('href'), [part.attrGet('title') or '']
            elif part.type == 'link_close':
                if href:
                    links.append((href, ' '.join(label)))
                href = None
            elif part.type in ('text', 'code_inline', 'image'):
                text = words(part)
                html.handle_data(text)
                if href and not html.hidden:
                    label.append(text)
    return [(href, ' '.join(html.labels[i])) for i, href in enumerate(html.links)] + links


def _links(body: str, *, source: str = '', content_type: str = '',
           base_url: str | None = None) -> list[tuple[str, str]]:
    mime = content_type.partition(';')[0].strip().lower()
    literal_only = ((bool(mime) and mime not in _HTML_TYPES | _MARKDOWN_TYPES | {'text/plain'})
                    or (mime in ('', 'text/plain')
                        and Path(urlsplit(source).path).suffix.lower() in _DATA_SUFFIXES))
    parser = _Links()
    if not literal_only:
        parser.feed(body)
    document = mime in _HTML_TYPES or (mime not in _MARKDOWN_TYPES and parser.document)
    links = ([(href, ' '.join(parser.labels[i])) for i, href in enumerate(parser.links)]
             if document and not literal_only else [])
    # Existing literal absolute-URL discovery remains available in source/code data.
    # Relative targets and names come from parsed Markdown links, not code or HTML literals.
    links.extend((href, '') for href in re.findall(r'\[[^\]]+\]\((https?://[^\s)]+)\)', body))
    links.extend((href, '') for href in re.findall(r'(?m)^\s*\[[^\]]+\]:\s*<?(https?://[^\s<>]+)', body))
    if not literal_only and not document:
        links.extend(_markdown_links(body))
    if not parser.links:
        links.extend((href, '') for href in re.findall(r'https?://[^\s<>"\x27`\\)\]]+', body))
    if not source:
        return links
    reference = source if base_url is None else base_url
    if document and parser.base_href is not None:
        try:
            reference = urljoin(reference, parser.base_href)
        except ValueError:
            reference = ''
    resolved = []
    safe_reference = valid_source_url(reference)
    for href, label in links:
        try:
            if not safe_reference and urlsplit(href).scheme.lower() != 'https':
                continue
            resolved.append((urljoin(reference, href), label))
        except ValueError:
            continue
    return resolved


def answered_sites(repo: Path, sha: str) -> set[str]:
    """Keep exact source/product decisions and operator-wide blocks separate."""
    known = set()
    today = utc_today()
    for filename in ('registry.yaml', 'watchlist.yaml', 'blocklist.yaml', 'sources.yaml'):
        value = yaml.safe_load(git.show(repo, sha, filename) or '') or []
        if filename == 'registry.yaml':
            for row in value.get('entries', []) if isinstance(value, dict) else []:
                if row.get('delisted'):
                    continue
                urls = [row['url'], *row.get('source_urls', [])]
                if row.get('api'):
                    urls.append(row['api']['base_url'])
                known.update(urls)
        elif filename == 'blocklist.yaml':
            known.update(r['domain'] for r in value)
        elif filename == 'watchlist.yaml':
            for record in (value.get('watched') if isinstance(value, dict) else value) or []:
                row = Watched.model_validate(record)
                if is_watch_current(row, today):
                    # A dated offer decision does not answer every product
                    # or directory sharing the vendor's host.
                    known.update('https://' + domain for domain in row.domains)
        else:
            for record in (value.get('read') if isinstance(value, dict) else value) or []:
                row = Source.model_validate(record)
                if is_source_current(row, today):
                    # A directory verdict names a URL, not every repository
                    # published by its host or owner.
                    known.add(row.url.rstrip('/'))
    return known


def _url_key(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower().removeprefix('www.'),
                      parts.path.rstrip('/'), parts.query, ''))


def collect_leads(bodies: dict[str, str], known: set[str], *,
                  content_types: dict[str, str] | None = None,
                  base_urls: dict[str, str] | None = None) -> list[dict]:
    """Capture unmatched links, including same-site competitor comparisons.

    These are review candidates, not assertions of a free offer or a guessed
    vendor domain. There is no recursive fetch or sign-up here.
    """
    exact = {_url_key(url) for url in known if valid_source_url(url)}
    operators = {site for site in known if '://' not in site}
    leads = {}
    for source, body in sorted(bodies.items()):
        if not valid_source_url(source):
            continue
        reference = (base_urls or {}).get(source, source)
        self_keys = {_url_key(source)}
        publisher = ''
        if valid_source_url(reference):
            self_keys.add(_url_key(reference))
            publisher = site_of(reference)
        for href, label in _links(body, source=source, content_type=(content_types or {}).get(source, ''),
                                  base_url=reference):
            try:
                parts = urlsplit(urljoin(source, href))
            except ValueError:
                continue
            # RFC 3986 section 3.4, checked 2026-11-05: query data can identify a resource.
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ''))
            if not valid_source_url(url) or _ASSET.search(parts.path):
                continue
            comparison = not _REVISION_COMPARE.search(parts.path) and bool(
                _COMPARISON.search(parts.path) or _COMPARISON_TEXT.search(' '.join(label.split())))
            own_navigation = not parts.query and publisher and is_covered(url, {publisher}) and (
                not parts.path.strip('/') or _NAVIGATION.fullmatch(parts.path)
                or _REVISION_COMPARE.search(parts.path))
            key = _url_key(url)
            if not comparison and (key in exact or key in self_keys
                    or own_navigation or is_covered(url, operators) or is_covered(url, _SOCIAL)):
                continue
            ident = hashlib.sha256(url.encode()).hexdigest()[:20]
            lead = leads.setdefault(ident, {'id': ident, 'url': url,
                'kind': 'comparison' if comparison else 'link', 'sources': []})
            if comparison:
                lead['kind'] = 'comparison'
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
    registers, decisions = {}, {}
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
            if filename not in decisions:
                current = yaml.safe_load(git.show(bundle.repo, scope['sha'], filename) or '') or []
                if isinstance(current, dict):
                    current = current.get({'registry.yaml': 'entries', 'watchlist.yaml': 'watched', 'sources.yaml': 'read'}[filename], [])
                decisions[filename] = {str(r.get('id', r.get('name', r.get('domain', r.get('url', ''))))) for r in current}
            if target.get('key') not in decisions[filename]:
                raise ValueError('lead canonical decision does not exist at the reviewed commit')
        if record['verdict'] == 'task':
            task = record.get('task', {})
            filename = task.get('file', '')
            path = bundle.out / filename if imported else Path(filename)
            if not path.is_absolute():
                path = bundle.repo / path
            if imported and filename not in bundle.files:
                raise ValueError('lead task evidence is not registered')
            if path not in registers:
                if not path.is_file():
                    raise ValueError('lead disposition needs an existing persistent task register')
                import json
                registers[path] = json.loads(path.read_text()).get('tasks', [])
            tasks = registers[path]
            matches = [t for t in tasks if t.get('id') == task.get('id')]
            states = {'open', 'scheduled', 'recurring', 'conditional', 'deferred', 'decision', 'idea'}
            if len(matches) != 1 or matches[0].get('status') not in states or not matches[0].get('next_action'):
                raise ValueError('lead disposition needs a retained unresolved task with a next action')
