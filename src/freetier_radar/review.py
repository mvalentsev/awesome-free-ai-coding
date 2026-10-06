"""Reusable private evidence for a review; vendor and independent judgments stay explicit."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from fnmatch import fnmatchcase
from pathlib import Path

import httpx
import yaml

from . import git
from .indexnow import index_at
from .layout import node_for
from .models import Entry
from .prober import TIMEOUT, UA, _ask, probe_page_url
from .quotes import page_texts, quote_found, row_quote_source, row_quotes, row_urls
from .render import PAGES_URL, REPO_URL

PUSH_BASE_FLAG = '--push-base'


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


class Bundle:
    """Raw evidence and phase results, kept outside tracked/published files."""

    def __init__(self, out: Path, repo: Path):
        self.out, self.repo = out.resolve(), repo.resolve()
        if self.out.is_file() or '.git' in self.out.parts:
            raise ValueError('evidence must be a private directory')
        if git.run(self.repo, 'rev-parse', '--git-dir').returncode == 0 and self.out.is_relative_to(self.repo):
            relative = self.out.relative_to(self.repo).as_posix()
            if relative == '.' or git.run(self.repo, 'check-ignore', '--no-index', '-q', relative + '/').returncode:
                raise ValueError('evidence inside the repository must be git-ignored')
        self.out.mkdir(parents=True, exist_ok=True)
        self.files = self.load('manifest', {}).get('files', {})

    def load(self, name: str, default=None):
        path = self.out / (name + '.json')
        expected = getattr(self, 'files', {}).get(name + '.json')
        if hasattr(self, 'files') and name != 'manifest' and path.exists() and not expected:
            raise ValueError('unregistered evidence: ' + name)
        if expected and path.exists() and digest(path.read_bytes()) != expected:
            raise ValueError('changed evidence: ' + name)
        return json.loads(path.read_text()) if path.exists() else default

    def write(self, name: str, body: bytes) -> str:
        path = (self.out / name).resolve()
        if not path.is_relative_to(self.out) or path == self.out:
            raise ValueError('evidence path escapes its directory')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        self.files[name] = digest(body)
        return name

    def save(self, name: str, value: dict) -> dict:
        self.write(name + '.json', (json.dumps(value, indent=2) + '\n').encode())
        (self.out / 'manifest.json').write_text(json.dumps({'files': self.files}, indent=2) + '\n')
        return value


def lock_bundle(bundle: Bundle):
    """Hold an OS lock until the CLI exits; interrupted runs leave no stale lock."""
    lock = (bundle.out / '.lock').open('a+b')
    try:
        if os.name == 'nt':
            import msvcrt
            lock.write(b'0')
            lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        lock.close()
        raise ValueError('another review phase is using this evidence directory') from exc
    return lock


def integrity(bundle: Bundle) -> list[str]:
    problems = []
    for name, expected in bundle.files.items():
        path = (bundle.out / name).resolve()
        if not path.is_relative_to(bundle.out) or not path.is_file() or digest(path.read_bytes()) != expected:
            problems.append('missing or changed evidence: ' + name)
    return problems


def revision(repo: Path, ref: str) -> str:
    result = git.run(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}')
    if result.returncode:
        raise ValueError('cannot resolve commit: ' + ref)
    return result.stdout.strip()


def blob(repo: Path, sha: str, path: str) -> bytes:
    result = subprocess.run(['git', '-C', str(repo), 'show', f'{sha}:{path}'], capture_output=True)
    if result.returncode:
        raise ValueError('cannot read committed file: ' + path)
    return result.stdout


def prepare(repo: Path, base: str, head: str, bundle: Bundle, verification_run: int | None = None,
            push_base: str | None = None) -> dict:
    if verification_run is not None and push_base is not None:
        raise ValueError('a verification run supplies its own push evidence')
    base, sha = revision(repo, base), revision(repo, head)
    push_base = revision(repo, push_base) if push_base is not None else base
    if any(git.run(repo, 'merge-base', '--is-ancestor', left, right).returncode
           for left, right in ((base, push_base), (push_base, sha))):
        raise ValueError('push base must be between the review base and head')
    previous = bundle.load('scope')
    if previous and (previous.get('base'), previous.get('sha'), previous.get('verification_run'),
                     previous.get('push_base', previous.get('base'))) != (base, sha, verification_run, push_base):
        raise ValueError('different commits require a new evidence directory')
    before, after = index_at(base, repo=repo), index_at(sha, repo=repo)
    if before is None or after is None:
        raise ValueError('both commits must contain a readable index.json')
    paths = git.run(repo, 'diff', '--name-only', '-z', base, sha).stdout.strip('\0').split('\0')
    paths = [p for p in paths if p]
    push_paths = [p for p in git.run(repo, 'diff', '--name-only', '-z', push_base, sha).stdout.strip('\0').split('\0') if p]
    result = git.run(repo, 'diff', '--binary', base, sha)
    if result.returncode:
        raise ValueError('cannot read the complete diff')
    bundle.write('diff.patch', result.stdout.encode())
    result = git.run(repo, 'diff', '--binary', push_base, sha)
    if result.returncode:
        raise ValueError('cannot read the push diff')
    bundle.write('push.diff.patch', result.stdout.encode())
    registries = {}
    for ref, label in ((base, 'before'), (sha, 'after')):
        for path in ('registry.yaml', 'index.json'):
            body = blob(repo, ref, path)
            bundle.write(label + '/' + path, body)
            if path == 'registry.yaml':
                registries[label] = yaml.safe_load(body)['entries']
    def changed(previous, current, field):
        old = {v[field]: v for v in previous}
        new = {v[field]: v for v in current}
        return sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
    def changed_pages(folder, key, field):
        return {v[field] for v in [*before.get(key, []), *after.get(key, [])]
                if f'{folder}/{v[field]}.md' in paths}
    rows = sorted(set(changed(before.get('entries', []), after.get('entries', []), 'id')) |
                  set(changed(registries['before'], registries['after'], 'id')) |
                  changed_pages('providers', 'entries', 'id'))
    families = sorted(set(changed(before.get('models', []), after.get('models', []), 'family')) |
                      changed_pages('models', 'models', 'family'))
    required = {'pages build and deployment'}
    for filename in ('ci.yml', 'indexnow.yml', 'conformance.yml'):
        content = git.show(repo, sha, '.github/workflows/' + filename)
        workflow = yaml.safe_load(content) if content else None
        if not workflow:
            continue
        triggers = workflow.get('on', workflow.get(True, {}))
        push = triggers.get('push') if isinstance(triggers, dict) else None
        if push is None:
            continue
        patterns = (push or {}).get('paths', [])
        if any(pattern.startswith('!') for pattern in patterns):
            raise ValueError('negative workflow paths need explicit review')
        if not patterns or any(fnmatchcase(path, pattern) for path in push_paths for pattern in patterns):
            required.add(workflow['name'])
    if verification_run is not None:
        run = json.loads(gh('run', 'view', str(verification_run), '--repo', REPO_URL.removeprefix('https://github.com/'),
                            '--json', 'databaseId,name,status,conclusion,headSha,url,attempt'))
        log = gh('run', 'view', str(verification_run), '--repo', REPO_URL.removeprefix('https://github.com/'),
                 '--attempt', str(run['attempt']), '--log')
        workflow = yaml.safe_load(blob(repo, sha, '.github/workflows/update.yml'))
        run = produced_run(repo, sha, run, log, workflow['name'])
        run['log'] = bundle.write(f"workflows/{run['databaseId']}-{run['attempt']}.log", log.encode())
        bundle.save('verification-run', run)
        for path in ('ci.yml', 'indexnow.yml'):
            required.discard(yaml.safe_load(blob(repo, sha, '.github/workflows/' + path))['name'])
        required.add(workflow['name'])
    scope = {'base': base, 'sha': sha, 'paths': paths, 'rows': rows,
             'push_base': push_base, 'push_paths': push_paths,
             'families': families,
             'workflows': sorted(required), 'verification_run': verification_run, 'prepared_at': now()}
    if previous and any(previous.get(key) != scope[key] for key in ('paths', 'rows', 'families', 'workflows')):
        raise ValueError('changed coverage requires a new evidence directory')
    return bundle.save('scope', scope)


async def fetch(client: httpx.AsyncClient, url: str, bundle: Bundle, *,
                expected: bytes | None = None, backoff: float = 2) -> dict:
    attempts = []
    prefix = 'http/' + digest(url.encode())[:20] + '-' + uuid.uuid4().hex[:8]
    async def send():
        try:
            response = await client.get(url, follow_redirects=True)
        except httpx.HTTPError as exc:
            attempts.append({'at': now(), 'error': str(exc) or type(exc).__name__})
            raise
        file = bundle.write(prefix + '-' + str(len(attempts)) + '.raw', response.content)
        attempts.append({'at': now(), 'status': response.status_code, 'file': file,
                         'sha256': digest(response.content),
                         'retry_after': response.headers.get('retry-after'),
                         'final_url': str(response.url)})
        return response
    response, error = await _ask(send, 3, backoff)
    passed = response is not None and response.status_code == 200
    if expected is not None:
        passed = passed and response.content == expected
    return {'url': url, 'passed': passed, 'attempts': attempts, 'error': error,
            'expected_sha256': digest(expected) if expected is not None else None}


def scoped(bundle: Bundle) -> dict:
    scope = bundle.load('scope')
    if not scope or scope.get('passed') is False or any(
            len(scope.get(key, '')) != 40 or any(c not in '0123456789abcdef' for c in scope[key])
            for key in ('sha', 'base')):
        raise ValueError('run prepare first')
    return scope


async def sources(bundle: Bundle, extra: list[str]) -> dict:
    scope = scoped(bundle)
    entries = [Entry.model_validate(e) for e in yaml.safe_load(blob(bundle.repo, scope['sha'], 'registry.yaml'))['entries']
               if e['id'] in scope['rows']]
    urls, by_row, followed = set(extra), {}, []
    async def capture(response):
        await response.aread()
        file = bundle.write('http/follow-' + uuid.uuid4().hex + '.raw', response.content)
        followed.append({'url': str(response.url), 'status': response.status_code, 'file': file,
                         'at': now(), 'retry_after': response.headers.get('retry-after')})
    async with httpx.AsyncClient(headers=UA, timeout=TIMEOUT) as client:
        client.event_hooks['response'] = [capture]
        for entry in entries:
            page = await probe_page_url(client, entry.probe) if entry.probe.follow else None
            selected = row_urls(entry, page)
            if entry.probe.free_list:
                selected.append(entry.probe.free_list)
            by_row[entry.id] = list(dict.fromkeys(selected))
            urls.update(selected)
        client.event_hooks['response'] = []
        if 'src/freetier_radar/intelligence-index.json' in scope['paths']:
            urls.add(json.loads(blob(bundle.repo, scope['sha'], 'src/freetier_radar/intelligence-index.json'))['source'])
        sem = asyncio.Semaphore(8)
        async def one(url):
            async with sem:
                return await fetch(client, url, bundle)
        checks = await asyncio.gather(*(one(u) for u in sorted(urls)))
    raw_bodies = {r['url']: (bundle.out / r['attempts'][-1]['file']).read_text(errors='replace')
                  for r in checks if r['passed']}
    bodies = {url: page_texts(body) for url, body in raw_bodies.items()}
    quotes, catalogs, quotas = [], [], []
    for entry in entries:
        pages = [p for u in by_row[entry.id] for p in bodies.get(u, [])]
        unread = any(u not in bodies for u in by_row[entry.id])
        for field, quote in row_quotes(entry):
            source = row_quote_source(entry, field)
            quotes.append({'row': entry.id, 'field': field, 'quote': quote,
                           'found': quote_found(quote, bodies.get(source, []) if source else pages),
                           'unverified': source not in bodies if source else unread})
        if entry.page_catalog:
            from .page_catalog import check_page_catalog
            body = raw_bodies.get(entry.page_catalog.source)
            notes = check_page_catalog(body, entry.page_catalog) if body is not None else ['source unreadable']
            catalogs.append({'row': entry.id, 'source': entry.page_catalog.source, 'notes': notes,
                             'passed': not notes})
        from .quotas import quota_changes
        for i, quota in enumerate(entry.quotas):
            body = raw_bodies.get(quota.source)
            notes = quota_changes(body, quota) if body is not None else ['source unreadable']
            quotas.append({'row': entry.id, 'field': f'quotas[{i}]', 'source': quota.source,
                           'notes': notes, 'passed': not notes})
    return bundle.save('sources', {'sha': scope['sha'], 'read_at': now(), 'by_row': by_row,
                                  'checks': checks, 'quotes': quotes, 'followed': followed,
                                  'page_catalogs': catalogs,
                                  'quotas': quotas,
                                  'passed': all(r['passed'] for r in checks) and all(q['found'] for q in quotes)
                                            and all(c['passed'] for c in catalogs)
                                            and all(q['passed'] for q in quotas),
                                  'judgment': 'Source reads, quote matching and configured page catalogs; vendor eligibility still needs review.'})


def produced_run(repo: Path, sha: str, run: dict, log: str, name: str) -> dict:
    """A scheduled run's trigger SHA differs from the verification commit it creates."""
    candidates = re.findall(r'\[main ([0-9a-f]{7,40})\] chore: verification', log)
    matched = any(revision(repo, candidate) == sha for candidate in candidates)
    ancestor = git.run(repo, 'merge-base', '--is-ancestor', run['headSha'], sha).returncode == 0
    if run['name'] != name or run['status'] != 'completed' or run['conclusion'] != 'success' or not matched or not ancestor:
        raise ValueError('verification run must succeed and its full log must identify the exact produced commit')
    return {**run, 'producedSha': sha}


def latest_runs(runs: list[dict], sha: str) -> dict[str, dict]:
    chosen = {}
    for run in runs:
        if run.get('headSha') != sha and run.get('producedSha') != sha:
            continue
        name = run['name']
        rank = (run.get('databaseId', 0), run.get('attempt', 0))
        if name not in chosen or rank > (chosen[name].get('databaseId', 0), chosen[name].get('attempt', 0)):
            chosen[name] = run
    return chosen


def workflow_state(runs: list[dict], sha: str, required: set[str]) -> str:
    chosen = latest_runs(runs, sha)
    if any(r['status'] == 'completed' and r['conclusion'] not in ('success', '')
           for name, r in chosen.items() if name in required):
        return 'failed'
    if not required.issubset(chosen) or any(chosen[n]['status'] != 'completed' for n in required):
        return 'waiting'
    return 'passed' if all(chosen[n]['conclusion'] == 'success' for n in required) else 'failed'


def gh(*args: str) -> str:
    result = subprocess.run(['gh', *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('gh failed: ' + result.stderr.strip())
    return result.stdout


def wait_workflows(bundle: Bundle, every: float = 15, timeout: float = 900) -> dict:
    scope = scoped(bundle)
    deadline, previous = time.monotonic() + timeout, None
    required = set(scope['workflows'])
    while True:
        runs = json.loads(gh('run', 'list', '--repo', REPO_URL.removeprefix('https://github.com/'),
                             '--commit', scope['sha'], '--limit', '100', '--json',
                             'databaseId,name,status,conclusion,headSha,url,attempt'))
        if scope.get('verification_run'):
            origin = bundle.load('verification-run')
            current = json.loads(gh('run', 'view', str(scope['verification_run']), '--repo',
                                    REPO_URL.removeprefix('https://github.com/'), '--json',
                                    'databaseId,name,status,conclusion,headSha,url,attempt'))
            if current['attempt'] != origin['attempt'] or current['status'] != 'completed' or current['conclusion'] != 'success':
                raise ValueError('verification run changed; prepare its new attempt in a fresh evidence directory')
            runs.append(origin)
        chosen = latest_runs(runs, scope['sha'])
        state = workflow_state(runs, scope['sha'], required)
        progress = {n: (chosen[n]['status'], chosen[n]['conclusion']) if n in chosen else ('missing', '')
                    for n in sorted(required)}
        if progress != previous:
            print(json.dumps({'phase': 'workflows', 'state': state, 'runs': progress}), flush=True)
            previous = progress
        if state != 'waiting' or time.monotonic() >= deadline:
            break
        time.sleep(every)
    selected = [chosen[n] for n in sorted(required) if n in chosen]
    for run in selected:
        if run['status'] == 'completed':
            filename = f"workflows/{run['databaseId']}-{run['attempt']}.log"
            run['log'] = filename
            if filename in bundle.files and not integrity(bundle):
                continue
            bundle.write(filename,
                         gh('run', 'view', str(run['databaseId']), '--repo',
                            REPO_URL.removeprefix('https://github.com/'), '--attempt', str(run['attempt']), '--log').encode())
    bundle.write('open-prs.json', gh('pr', 'list', '--repo', REPO_URL.removeprefix('https://github.com/'),
                                    '--state', 'open', '--json', 'number,title,author,headRefOid,url').encode())
    return bundle.save('workflows', {'sha': scope['sha'], 'required': sorted(required), 'runs': selected,
                                     'passed': state == 'passed', 'state': state})


async def publication(bundle: Bundle) -> dict:
    scope = scoped(bundle)
    workflows = bundle.load('workflows', {})
    if workflows.get('passed') is not True or workflows.get('sha') != scope['sha'] or workflow_state(
            workflows.get('runs', []), scope['sha'], set(scope['workflows'])) != 'passed':
        raise ValueError('publication needs successful workflows for the exact commit')
    public = [p for p in scope['paths'] if Path(p).name == 'README.md' or
              ((node := node_for(p)) and node.published)]
    static = ['index.html', 'index.json', 'llms.txt', 'registry.yaml', 'history.jsonl',
              'configs/opencode.json', 'configs/litellm.yaml', 'configs/free-llm.env.example', 'feed.xml']
    static += [p for p in scope['paths'] if p.startswith(('assets/', 'configs/')) and p not in static
               and (node := node_for(p)) and node.published]
    previous = bundle.load('publication', {})
    cached = {r['url']: r for r in previous.get('checks', []) if r.get('kind') == 'source'}
    raw = REPO_URL.replace('github.com', 'raw.githubusercontent.com') + '/' + scope['sha'] + '/'
    async with httpx.AsyncClient(headers=UA, timeout=TIMEOUT) as client:
        sem = asyncio.Semaphore(8)
        async def one(kind, path):
            expected = blob(bundle.repo, scope['sha'], path)
            url = (raw if kind == 'source' else PAGES_URL + '/') + path
            old = cached.get(url)
            if kind == 'source' and old and old['passed'] and old['attempts']:
                file = bundle.out / old['attempts'][-1]['file']
                if file.is_file() and file.read_bytes() == expected:
                    return old
            async with sem:
                result = await fetch(client, url, bundle, expected=expected)
            return {**result, 'kind': kind, 'path': path}
        checks = await asyncio.gather(*(one('source', p) for p in public),
                                      *(one('served', p) for p in dict.fromkeys(static)))
        browser = bundle.load('browser-execution', {})
        if browser.get('sha') == scope['sha']:
            for image in {r['image_url']: r['image_path'] for r in browser.get('records', [])
                          if r.get('image_url')}.items():
                url, path = image
                result = await fetch(client, url, bundle, expected=blob(bundle.repo, scope['sha'], path))
                checks.append({**result, 'kind': 'github-image', 'path': path})
    return bundle.save('publication', {'sha': scope['sha'], 'checks': checks,
                                      'passed': all(r['passed'] for r in checks), 'checked_at': now()})


def client_result(client: str, code: int, events: list[dict], marker: str) -> dict:
    if client == 'opencode':
        parts = [e.get('part', {}) for e in events]
        tools = [p for p in parts if p.get('type') == 'tool' and p.get('state', {}).get('status') == 'completed']
        outputs = [p.get('state', {}).get('output', '') for p in tools]
        answers = [p.get('text', '') for p in parts if p.get('type') == 'text']
        completed = any(p.get('type') == 'step-finish' and p.get('reason') == 'stop' for p in parts)
    else:
        items = [e.get('item', {}) for e in events if e.get('type') == 'item.completed']
        tools = [p for p in items if p.get('type') == 'command_execution' and p.get('exit_code') == 0]
        outputs = [p.get('aggregated_output', '') for p in tools]
        answers = [p.get('text', '') for p in items if p.get('type') == 'agent_message']
        completed = any(e.get('type') == 'turn.completed' for e in events)
    matched = bool(answers) and marker in answers[-1]
    error = any(e.get('type') in ('error', 'turn.failed') for e in events)
    read = any(marker in output for output in outputs)
    return {'passed': code == 0 and completed and read and matched and not error, 'exit': code,
            'completed_turn': completed, 'fresh_marker_in_tool_output': read,
            'completed_tools': len(tools), 'fresh_marker_in_answer': matched, 'error_event': error}


def live_client(bundle: Bundle, client: str, binary: str, provider: str, model: str) -> dict:
    scope = scoped(bundle)
    rows = yaml.safe_load(blob(bundle.repo, scope['sha'], 'registry.yaml'))['entries']
    entry = next((Entry.model_validate(e) for e in rows if e['id'] == provider), None)
    if entry is None or not entry.api or model not in entry.api.model_ids:
        raise ValueError('provider and model must be a committed public API lane')
    if entry.api.auth != 'none':
        raise ValueError('isolated live-client currently supports keyless lanes only')
    work = bundle.out / ('client/' + client + '-' + uuid.uuid4().hex)
    home, project = work / 'home', work / 'project'
    home.mkdir(parents=True)
    project.mkdir()
    marker = 'review-' + uuid.uuid4().hex
    (project / 'audit-marker.txt').write_text(marker + '\n')
    env = {'PATH': os.environ['PATH'], 'HOME': str(home), 'LANG': 'C.UTF-8'}
    prompt = 'Read audit-marker.txt using a tool or shell command, then reply with exactly its contents. Do not edit files or inspect any other paths.'
    if client == 'opencode':
        config = work / 'opencode.json'; config.write_bytes(blob(bundle.repo, scope['sha'], 'configs/opencode.json'))
        env.update(OPENCODE_CONFIG=str(config), XDG_CONFIG_HOME=str(home / 'config'),
                   XDG_DATA_HOME=str(home / 'data'), XDG_CACHE_HOME=str(home / 'cache'))
        argv = [binary, 'run', '--pure', '--format', 'json', '-m', provider + '/' + model, prompt]
    else:
        config = home / '.codex'; config.mkdir()
        (config / (provider + '.config.toml')).write_bytes(blob(bundle.repo, scope['sha'], 'configs/codex/' + provider + '.config.toml'))
        env['CODEX_HOME'] = str(config)
        argv = [binary, 'exec', '--json', '-p', provider, '-m', model, '--sandbox', 'read-only', '--skip-git-repo-check', prompt]
    try:
        done = subprocess.run(argv, cwd=project, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=120)
        code, stdout, stderr = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = -1, exc.stdout or b'', (exc.stderr or b'') + b'\n120-second timeout'
    prefix = 'client/' + work.name + '/'
    bundle.write(prefix + 'stdout.jsonl', stdout)
    bundle.write(prefix + 'stderr.log', stderr)
    events = []
    for line in stdout.decode(errors='replace').splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    result = client_result(client, code, events, marker)
    phase = 'client-' + work.name
    return bundle.save(phase, {**result, 'sha': scope['sha'], 'provider': provider, 'phase': phase,
                                          'model': model, 'at': now(), 'evidence': prefix})


def report(bundle: Bundle) -> dict:
    required = ('scope', 'sources', 'workflows', 'publication', 'browser')
    names = [*required, *(p.stem for p in bundle.out.glob('client-*.json'))]
    phases = {name: bundle.load(name) for name in names if (bundle.out / (name + '.json')).exists()}
    missing = [p for p in required if p not in phases]
    sha = phases.get('scope', {}).get('sha')
    failed = [p for p, value in phases.items() if (p != 'scope' and value.get('passed') is not True) or
              (value.get('sha') != sha) or (p == 'scope' and value.get('passed') is False)]
    problems = integrity(bundle)
    browser = bundle.load('browser-execution', {})
    images = {(r['image_url'], r['image_path']) for r in browser.get('records', []) if r.get('image_url')}
    verified = {(r['url'], r['path']) for r in phases.get('publication', {}).get('checks', [])
                if r.get('kind') == 'github-image' and r.get('passed') is True}
    if images - verified:
        problems.append('loaded GitHub images need publication byte checks')
    return bundle.save('report', {'sha': sha, 'complete': not missing and not failed and not problems,
                                  'missing': missing, 'failed': failed, 'integrity_problems': problems,
                                  'human_review_required': True,
                                  'meaning': 'Evidence phases only; independent review and vendor judgments are not automated.',
                                  'phases': {p: {'passed': v.get('passed'), 'file': p + '.json'} for p, v in phases.items()}})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True, help='private, git-ignored evidence directory')
    sub = parser.add_subparsers(dest='phase', required=True)
    prepare_parser = sub.add_parser('prepare'); prepare_parser.add_argument('--base', required=True)
    prepare_parser.add_argument('--head', default='HEAD')
    prepare_parser.add_argument(PUSH_BASE_FLAG, help='commit immediately before the final human push; defaults to --base')
    prepare_parser.add_argument('--verification-run', type=int, help='successful update run that produced this bot commit')
    source_parser = sub.add_parser('sources'); source_parser.add_argument('--url', action='append', default=[])
    publish_parser = sub.add_parser('publication'); publish_parser.add_argument('--every', type=float, default=15)
    publish_parser.add_argument('--timeout', type=float, default=900)
    browser_parser = sub.add_parser('browser'); browser_parser.add_argument('--result', type=Path)
    client_parser = sub.add_parser('client'); client_parser.add_argument('--client', choices=('opencode', 'codex'), required=True)
    client_parser.add_argument('--binary', required=True); client_parser.add_argument('--provider', required=True)
    client_parser.add_argument('--model', required=True)
    sub.add_parser('report')
    args = parser.parse_args()
    bundle = None
    lock = None
    try:
        bundle = Bundle(args.out, args.root)
        lock = lock_bundle(bundle)
        bundle.files = bundle.load('manifest', {}).get('files', {})
        if args.phase == 'prepare':
            result = prepare(args.root, args.base, args.head, bundle, args.verification_run, args.push_base)
        elif args.phase == 'sources':
            result = asyncio.run(sources(bundle, args.url))
        elif args.phase == 'publication':
            if args.every < 1 or args.timeout < 0:
                raise ValueError('poll interval must be at least one second; timeout cannot be negative')
            result = wait_workflows(bundle, args.every, args.timeout)
            if result['passed']:
                result = asyncio.run(publication(bundle))
            else:
                result = bundle.save('publication', {'sha': result['sha'], 'passed': False,
                                                     'error': 'required workflows did not pass'})
        elif args.phase == 'client':
            result = live_client(bundle, args.client, str(Path(args.binary).resolve()), args.provider, args.model)
        elif args.phase == 'browser':
            from .review_browser import accept_browser, browser_script
            scope = scoped(bundle)
            if args.result:
                result = accept_browser(bundle, json.loads(args.result.read_text()), bundle.load('browser-plan'))
            else:
                result = {'sha': scope['sha'], 'script': bundle.write('browser.js', browser_script(bundle).encode())}
                bundle.save('browser-script', result)
        else:
            result = report(bundle)
        artifact = {'prepare': 'scope', 'browser': 'browser' if getattr(args, 'result', None) else 'browser-script'}.get(args.phase, args.phase)
        artifact = result.get('phase', artifact)
        print(json.dumps({'phase': args.phase, 'sha': result.get('sha'),
                          'passed': result.get('passed'), 'complete': result.get('complete'),
                          'evidence': str(bundle.out / (artifact + '.json'))}), flush=True)
        sys.exit(1 if result.get('passed') is False or result.get('complete') is False else 0)
    except (ValueError, RuntimeError, OSError, httpx.HTTPError) as exc:
        if bundle is not None and lock is not None:
            phase = {'prepare': 'scope', 'client': 'client-error-' + uuid.uuid4().hex}.get(args.phase, args.phase)
            scope = json.loads((bundle.out / 'scope.json').read_text()) if (bundle.out / 'scope.json').exists() else {}
            bundle.save(phase, {'phase': args.phase, 'sha': scope.get('sha'), 'passed': False,
                               'at': now(), 'error': str(exc)})
        parser.exit(1, 'review: ' + str(exc) + '\n')
    finally:
        if lock is not None:
            lock.close()
