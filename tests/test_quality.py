import subprocess
import json
from datetime import datetime, timedelta, timezone

import pytest

from freetier_radar.gate import pre_push
from freetier_radar.quality import CRITERIA, accept_judgment
from freetier_radar.review import Bundle


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def proposal(tmp_path):
    git(tmp_path, 'init', '-q', '-b', 'main')
    git(tmp_path, 'config', 'user.name', 'test')
    git(tmp_path, 'config', 'user.email', 'test@example.com')
    (tmp_path / '.gitignore').write_text('.remember/\n')
    (tmp_path / '.githooks').mkdir()
    (tmp_path / '.githooks/pre-push').write_text('exec freetier-gate pre-push\n')
    (tmp_path / 'README.md').write_text('before\n')
    git(tmp_path, 'add', '.')
    git(tmp_path, 'commit', '-qm', 'chore: baseline')
    git(tmp_path, 'commit', '--allow-empty', '-qm', 'chore: reviewed baseline')
    base = git(tmp_path, 'rev-parse', 'HEAD')
    (tmp_path / 'README.md').write_text('after\n')
    git(tmp_path, 'add', '.')
    git(tmp_path, 'commit', '-qm', 'docs: proposal')
    return base, git(tmp_path, 'rev-parse', 'HEAD')


def push(repo, base, head):
    return pre_push(repo, [f'HEAD {head} refs/heads/main {base}'], steps=[])


def test_normal_push_rejects_a_commit_with_no_independent_review(tmp_path):
    base, head = proposal(tmp_path)
    assert any('independent review' in p for p in push(tmp_path, base, head))


def signoff(repo, base, head):
    bundle = Bundle(repo / '.remember/evidence', repo)
    bundle.save('scope', {'base': base, 'sha': head, 'push_base': base, 'paths': ['README.md']})
    evidence = repo / '.remember/finding.txt'
    evidence.write_text('Before/after and peer review findings.\n')
    value = {'base': base, 'sha': head, 'paths': ['README.md'], 'decision': 'approve',
             'criteria': {name: {'verdict': 'pass', 'finding': 'Reviewed ' + name,
                                 'evidence': [str(evidence)]} for name in CRITERIA}}
    return bundle, value


def test_complete_evidenced_review_allows_the_exact_push(tmp_path):
    base, head = proposal(tmp_path)
    bundle, value = signoff(tmp_path, base, head)
    accept_judgment(bundle, value)
    assert push(tmp_path, base, head) == []
    # Importing freezes the evidence used; changing the original does not rewrite history.
    (tmp_path / '.remember/finding.txt').write_text('later notes')
    assert push(tmp_path, base, head) == []


@pytest.mark.parametrize('defect', ['missing', 'partial-families', 'missing-conflicts',
                                  'stale', 'unread-source', 'stale-source', 'future', None])
def test_eligibility_signoff_requires_current_conditions_for_every_changed_family(tmp_path, defect):
    base, head = proposal(tmp_path)
    (tmp_path / 'index.json').write_text(json.dumps({'entries': [{
        'id': 'vendor', 'models': [{'family': 'alpha'}, {'family': 'beta'}]}]}))
    git(tmp_path, 'add', 'index.json')
    git(tmp_path, 'commit', '-qm', 'fix: fixture model claims')
    head = git(tmp_path, 'rev-parse', 'HEAD')
    bundle, value = signoff(tmp_path, base, head)
    scope = bundle.load('scope')
    scope['paths'] = value['paths'] = ['README.md', 'index.json']
    scope['eligibility'] = {'vendor': ['alpha', 'beta']}
    bundle.save('scope', scope)
    source = 'https://vendor.example/plans'
    bundle.save('sources', {'checks': [{'url': source, 'passed': True,
                            'attempts': [{'at': datetime.now(timezone.utc).isoformat()}]}]})
    evidence = str(tmp_path / '.remember/finding.txt')
    record = {'row': 'vendor', 'families': ['alpha', 'beta'],
              'plan': 'Free', 'payment': 'No payment', 'regions': 'US only',
              'limits': 'One hour per day', 'deadline': 'No published end date',
              'conflicts': 'Compared live Free and Starter tables; no conflict',
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'sources': [source], 'evidence': [evidence]}
    value['model_eligibility'] = [record]
    if defect == 'missing':
        value.pop('model_eligibility')
    elif defect == 'partial-families':
        record['families'] = ['alpha']
    elif defect == 'missing-conflicts':
        record.pop('conflicts')
    elif defect == 'unread-source':
        bundle.save('sources', {'checks': [{'url': source, 'passed': False}]})
    elif defect == 'stale-source':
        bundle.save('sources', {'checks': [{'url': source, 'passed': True,
            'attempts': [{'at': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()}]}]})
    elif defect:
        offset = timedelta(days=-2) if defect == 'stale' else timedelta(days=1)
        record['checked_at'] = (datetime.now(timezone.utc) + offset).isoformat()
    if defect:
        with pytest.raises(ValueError):
            accept_judgment(bundle, value)
        assert push(tmp_path, base, head)
    else:
        accept_judgment(bundle, value)
        assert push(tmp_path, base, head) == []


@pytest.mark.parametrize('defect', ['checkboxes', 'partial-diff', 'wrong-head', 'empty-finding',
                                   'missing-proof', 'unresolved'])
def test_a_form_without_actual_review_cannot_create_a_signoff(tmp_path, defect):
    base, head = proposal(tmp_path)
    bundle, value = signoff(tmp_path, base, head)
    if defect == 'checkboxes':
        value['criteria'] = {name: True for name in CRITERIA}
    elif defect == 'partial-diff':
        value['paths'] = []
    elif defect == 'wrong-head':
        value['sha'] = base
    elif defect == 'empty-finding':
        value['criteria']['reuse']['finding'] = ' '
    elif defect == 'missing-proof':
        value['criteria']['copy']['evidence'] = []
    else:
        value['decision'] = 'revise'
    with pytest.raises(ValueError):
        accept_judgment(bundle, value)
    assert push(tmp_path, base, head)


@pytest.mark.parametrize('defect', ['changed-evidence', 'missing-evidence', 'changed-judgment', 'stale-head', 'stale-base',
                                   'removed-hook'])
def test_push_rechecks_evidence_and_commit_binding(tmp_path, defect):
    base, head = proposal(tmp_path)
    bundle, value = signoff(tmp_path, base, head)
    accept_judgment(bundle, value)
    artifact = bundle.out / 'judgment/reuse/0-finding.txt'
    if defect == 'changed-evidence':
        artifact.write_text('changed')
    elif defect == 'missing-evidence':
        artifact.unlink()
    elif defect == 'changed-judgment':
        value = bundle.load('judgment')
        value['criteria']['reuse']['finding'] = 'Changed review'
        bundle.save('judgment', value)
    elif defect == 'stale-base':
        base = git(tmp_path, 'rev-parse', f'{base}^')
    else:
        if defect == 'removed-hook':
            (tmp_path / '.githooks/pre-push').unlink()
        else:
            (tmp_path / 'README.md').write_text('another change\n')
        git(tmp_path, 'add', '.')
        git(tmp_path, 'commit', '-qm', 'docs: another proposal')
        head = git(tmp_path, 'rev-parse', 'HEAD')
    assert any('independent review' in p for p in push(tmp_path, base, head))
