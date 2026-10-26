"""Require an evidenced independent review of the exact push, kept private."""
from __future__ import annotations

import json
import re
import yaml
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import git

CRITERIA = ('existing_behavior', 'reuse', 'copy', 'user_path', 'regression', 'diff', 'eligibility')
ELIGIBILITY_FIELDS = ('plan', 'payment', 'regions', 'limits', 'deadline', 'conflicts')
ELIGIBILITY_MAX_AGE_DAYS = 1
CONFLICT_STATES = ('none', 'resolved', 'unresolved')
WITHDRAWAL_VERDICTS = ('ended', 'ineligible')
SIGNOFFS = '.remember/review-signoffs'


def changed_paths(repo: Path, base: str, sha: str) -> list[str]:
    result = git.run(repo, 'diff', '--name-only', '-z', base, sha)
    if result.returncode:
        raise ValueError('cannot read review diff')
    return sorted(filter(None, result.stdout.split('\0')))


def vendor_scope(repo: Path, base: str, sha: str) -> dict:
    """One fact-review scope for source collection and mandatory signoffs.

    Search records repeat canonical fields; modification dates and daily stamps
    are writer metadata. Neither alone changes vendor facts. Canonical registry,
    remaining index fields and substantive page content each establish scope.
    """
    from .page_dates import content_hash
    indexes, registries = [], []
    for ref in (base, sha):
        index = json.loads(git.show(repo, ref, 'index.json') or '{}')
        registry = yaml.safe_load(git.show(repo, ref, 'registry.yaml') or '') or {}
        indexes.append({e['id']: {k: v for k, v in e.items() if k != 'search'}
                        for e in index.get('entries', [])})
        registries.append({e['id']: e for e in registry.get('entries', [])})
    rows = set()
    for left, right in (indexes, registries):
        rows.update(row for row in left.keys() | right.keys() if left.get(row) != right.get(row))
    for path in changed_paths(repo, base, sha):
        if path.startswith('providers/') and path.endswith('.md'):
            old, new = (git.show(repo, ref, path) or '' for ref in (base, sha))
            if content_hash(old) != content_hash(new):
                rows.add(Path(path).stem)
    known = set().union(*(set(index) for index in indexes), *(set(registry) for registry in registries))
    rows &= known
    result = {}
    for row in sorted(rows):
        families = sorted({m['family'] for index in indexes for m in index.get(row, {}).get('models', [])})
        result[row] = families
    withdrawals = []
    for row in sorted(rows):
        old, new = (index.get(row, {}) for index in indexes)
        removed = {m['family'] for m in old.get('models', [])} - {m['family'] for m in new.get('models', [])}
        if old and (removed or (not old.get('archived') and new.get('archived'))):
            withdrawals.append(row)
    return {'rows': sorted(rows), 'eligibility': result, 'withdrawals': withdrawals}


def eligibility_scope(repo: Path, base: str, sha: str) -> dict[str, list[str]]:
    """Derive mandatory offer and model coverage independently of the signoff."""
    return vendor_scope(repo, base, sha)['eligibility']


def validate_judgment(value: dict, scope: dict) -> None:
    if not isinstance(value, dict):
        raise ValueError('review must be a JSON object')
    if value.get('sha') != scope['sha'] or value.get('base') != scope['base']:
        raise ValueError('review must name the exact base and head')
    if value.get('paths') != sorted(scope['paths']):
        raise ValueError('review must cover every changed file')
    if value.get('decision') != 'approve':
        raise ValueError('review has unresolved changes')
    criteria = value.get('criteria', {})
    if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
        raise ValueError('review needs all criteria: ' + ', '.join(CRITERIA))
    for name, check in criteria.items():
        if not isinstance(check, dict) or check.get('verdict') not in ('pass', 'not-applicable'):
            raise ValueError(name + ': needs a verdict')
        if not isinstance(check.get('finding'), str) or not check['finding'].strip():
            raise ValueError(name + ': needs a concrete finding or non-applicability reason')
        evidence = check.get('evidence')
        if not isinstance(evidence, list) or not evidence or any(not isinstance(p, str) or not p for p in evidence):
            raise ValueError(name + ': needs evidence, including for non-applicability')
    required = scope.get('eligibility', {})
    records = value.get('model_eligibility', [])
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError('model eligibility needs structured records')
    if sorted(r.get('row', '') for r in records) != sorted(required):
        raise ValueError('offer eligibility must cover every affected row, including unnamed free offers')
    for record in records:
        row = record['row']
        if record.get('families') != required[row]:
            raise ValueError(row + ': eligibility must cover previous and resulting families')
        for field in ELIGIBILITY_FIELDS:
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(row + ': eligibility needs ' + field)
        if record.get('conflict_status') not in CONFLICT_STATES:
            raise ValueError(row + ': eligibility needs an explicit conflict_status')
        if record['conflict_status'] == 'resolved' and (
                not isinstance(record.get('resolution'), str) or not record['resolution'].strip()):
            raise ValueError(row + ': resolved conflicts need the superseding evidence and reasoning')
        if row in scope.get('withdrawals', []):
            if record['conflict_status'] == 'unresolved':
                raise ValueError(row + ': withdrawal cannot rely on unresolved free-access conflicts')
            modes = record.get('access_modes')
            if not isinstance(modes, list) or not modes:
                raise ValueError(row + ': withdrawal needs every advertised free access mode')
            names = []
            for mode in modes:
                if not isinstance(mode, dict) or not isinstance(mode.get('name'), str) or not mode['name'].strip():
                    raise ValueError(row + ': withdrawal needs named access modes')
                names.append(mode['name'])
                if mode.get('verdict') not in WITHDRAWAL_VERDICTS:
                    raise ValueError(row + ': withdrawal has an available or unresolved access mode')
                if not isinstance(mode.get('finding'), str) or not mode['finding'].strip():
                    raise ValueError(row + ': withdrawal access mode needs a concrete finding')
                sources = mode.get('sources')
                if not isinstance(sources, list) or not sources or any(s not in record.get('sources', []) for s in sources):
                    raise ValueError(row + ': withdrawal access modes need current reviewed sources')
            if len(names) != len(set(names)):
                raise ValueError(row + ': withdrawal access modes must be distinct')
        for field in ('sources', 'evidence'):
            if not isinstance(record.get(field), list) or not record[field] or any(
                    not isinstance(v, str) or not v for v in record[field]):
                raise ValueError(row + ': eligibility needs ' + field)
        try:
            checked = datetime.fromisoformat(record['checked_at'])
            if checked.tzinfo is None:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise ValueError(row + ': eligibility needs a timestamp with timezone') from None


def fresh_eligibility(records: list[dict]) -> None:
    current = datetime.now(timezone.utc)
    for record in records:
        checked = datetime.fromisoformat(record['checked_at'])
        if checked < current - timedelta(days=ELIGIBILITY_MAX_AGE_DAYS) or checked > current + timedelta(minutes=5):
            raise ValueError(record['row'] + ': eligibility evidence is stale or future-dated')


def current_eligibility_sources(bundle, records: list[dict]) -> None:
    sources = bundle.load('sources', {})
    read = {r['url']: r for r in sources.get('checks', []) if r.get('passed') is True}
    current = datetime.now(timezone.utc)
    for record in records:
        for url in record['sources']:
            source = read.get(url)
            if source is None:
                raise ValueError(record['row'] + ': eligibility needs successful current source reads')
            try:
                checked = datetime.fromisoformat(source['attempts'][-1]['at'])
                if checked.tzinfo is None or checked < current - timedelta(days=ELIGIBILITY_MAX_AGE_DAYS) or checked > current + timedelta(minutes=5):
                    raise ValueError()
            except (KeyError, IndexError, TypeError, ValueError):
                raise ValueError(record['row'] + ': eligibility source receipt is missing, stale or future-dated') from None


def accept_judgment(bundle, value: dict) -> dict:
    from .review import digest, integrity, now, scoped
    scope = scoped(bundle)
    facts = vendor_scope(bundle.repo, scope['base'], scope['sha'])
    if scope.get('eligibility', {}) != facts['eligibility'] or scope.get('withdrawals', []) != facts['withdrawals']:
        raise ValueError('eligibility scope does not match the committed facts')
    validate_judgment(value, scope)
    if sorted(scope['paths']) != changed_paths(bundle.repo, scope['base'], scope['sha']):
        raise ValueError('scope no longer matches the complete diff')
    if integrity(bundle):
        raise ValueError('review evidence is missing or changed')
    fresh_eligibility(value.get('model_eligibility', []))
    current_eligibility_sources(bundle, value.get('model_eligibility', []))
    # Import evidence rather than leave references to mutable external files.
    criteria = {}
    for name, check in value['criteria'].items():
        paths = []
        for index, source in enumerate(check['evidence']):
            path = Path(source)
            if not path.is_file():
                raise ValueError(name + ': evidence does not exist: ' + source)
            paths.append(bundle.write(f'judgment/{name}/{index}-{path.name}', path.read_bytes()))
        criteria[name] = {**check, 'evidence': paths}
    records = []
    for record in value.get('model_eligibility', []):
        paths = []
        for index, source in enumerate(record['evidence']):
            path = Path(source)
            if not path.is_file():
                raise ValueError(record['row'] + ': eligibility evidence does not exist: ' + source)
            paths.append(bundle.write(f"judgment/eligibility-{record['row']}/{index}-{path.name}", path.read_bytes()))
        records.append({**record, 'evidence': paths})
    result = bundle.save('judgment', {**value, 'criteria': criteria, 'model_eligibility': records,
                                    'passed': True, 'at': now()})
    receipt = bundle.repo / SIGNOFFS / (scope['sha'] + '.json')
    if git.run(bundle.repo, 'check-ignore', '--no-index', '-q', str(receipt)).returncode:
        raise ValueError('review signoffs must be git-ignored')
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({'bundle': str(bundle.out),
                                  'judgment_sha256': digest((bundle.out / 'judgment.json').read_bytes())}) + '\n')
    return result


def check_judgment(bundle, scope: dict) -> None:
    value = bundle.load('judgment')
    if not value or value.get('passed') is not True:
        raise ValueError('independent review is missing or failed')
    validate_judgment(value, scope)
    for check in [*value['criteria'].values(), *value.get('model_eligibility', [])]:
        if any(path not in bundle.files for path in check['evidence']):
            raise ValueError('review evidence is not registered')


def review_problems(repo: Path, base: str, sha: str) -> list[str]:
    # Existing hooks also protect a proposal that removes the hook itself.
    if not any('freetier-gate pre-push' in (git.show(repo, ref, '.githooks/pre-push') or '')
               for ref in (base, sha)) or base == sha:
        return []
    from .review import Bundle, digest, integrity
    try:
        receipt = json.loads((repo / SIGNOFFS / (sha + '.json')).read_text())
        bundle = Bundle(Path(receipt['bundle']), repo)
        scope, judgment = bundle.load('scope'), bundle.load('judgment')
        if not scope or not judgment or scope.get('sha') != sha or scope.get('push_base', scope['base']) != base:
            raise ValueError('review covers a different push')
        check_judgment(bundle, scope)
        facts = vendor_scope(repo, scope['base'], sha)
        if scope.get('eligibility', {}) != facts['eligibility'] or scope.get('withdrawals', []) != facts['withdrawals']:
            raise ValueError('eligibility scope does not match the committed facts')
        fresh_eligibility(judgment.get('model_eligibility', []))
        current_eligibility_sources(bundle, judgment.get('model_eligibility', []))
        if sorted(scope['paths']) != changed_paths(repo, scope['base'], sha):
            raise ValueError('review does not cover the complete diff')
        if digest((bundle.out / 'judgment.json').read_bytes()) != receipt['judgment_sha256']:
            raise ValueError('review signoff changed')
        if integrity(bundle):
            raise ValueError('review evidence is missing or changed')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f'independent review required for {sha[:7]}: {exc}. '
                'Use freetier-review judgment after reviewing the complete diff.']
    return []
