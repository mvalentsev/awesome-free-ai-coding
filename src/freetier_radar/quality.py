"""Require an evidenced independent review of the exact push, kept private."""
from __future__ import annotations

import json
from pathlib import Path

from . import git

CRITERIA = ('existing_behavior', 'reuse', 'copy', 'user_path', 'regression', 'diff')
SIGNOFFS = '.remember/review-signoffs'


def changed_paths(repo: Path, base: str, sha: str) -> list[str]:
    result = git.run(repo, 'diff', '--name-only', '-z', base, sha)
    if result.returncode:
        raise ValueError('cannot read review diff')
    return sorted(filter(None, result.stdout.split('\0')))


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
        raise ValueError('review needs all six criteria: ' + ', '.join(CRITERIA))
    for name, check in criteria.items():
        if not isinstance(check, dict) or check.get('verdict') not in ('pass', 'not-applicable'):
            raise ValueError(name + ': needs a verdict')
        if not isinstance(check.get('finding'), str) or not check['finding'].strip():
            raise ValueError(name + ': needs a concrete finding or non-applicability reason')
        evidence = check.get('evidence')
        if not isinstance(evidence, list) or not evidence or any(not isinstance(p, str) or not p for p in evidence):
            raise ValueError(name + ': needs evidence, including for non-applicability')


def accept_judgment(bundle, value: dict) -> dict:
    from .review import digest, integrity, now, scoped
    scope = scoped(bundle)
    validate_judgment(value, scope)
    if sorted(scope['paths']) != changed_paths(bundle.repo, scope['base'], scope['sha']):
        raise ValueError('scope no longer matches the complete diff')
    if integrity(bundle):
        raise ValueError('review evidence is missing or changed')
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
    result = bundle.save('judgment', {**value, 'criteria': criteria, 'passed': True, 'at': now()})
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
    for check in value['criteria'].values():
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
