import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / 'repo'
    root.mkdir()
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', os.devnull)
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    subprocess.run(['git', 'init', '-b', 'main', str(root)], check=True, capture_output=True)
    workflow = root / '.github/workflows/conformance.yml'
    workflow.parent.mkdir(parents=True)
    workflow.write_text(yaml.safe_dump({'on': {'push': {'branches': ['main'], 'paths': [
        'configs/litellm.yaml', 'configs/codex/*.config.toml',
        'src/freetier_radar/conformance.py', '.github/workflows/conformance.yml']}}}))
    (root / 'README.md').write_text('Initial\n')
    _commit(root)
    receipt = tmp_path / 'dispatch.json'
    gh = tmp_path / 'gh'
    gh.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                  'open(os.environ["DISPATCH_RECEIPT"], "w").write(json.dumps(sys.argv[1:]))\n'
                  'sys.exit(int(os.environ.get("DISPATCH_EXIT", "0")))\n')
    gh.chmod(0o755)
    monkeypatch.setenv('PATH', str(tmp_path) + os.pathsep + os.environ['PATH'])
    monkeypatch.setenv('DISPATCH_RECEIPT', str(receipt))
    return root, receipt


def _commit(root):
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Test',
                    '-c', 'user.email=test@example.invalid', 'commit', '-m', 'test'],
                   check=True, capture_output=True)
    return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()


def _change(root, path):
    before = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(target.read_text() + '\nchanged\n' if target.exists() else 'changed\n')
    return before, _commit(root)


@pytest.mark.parametrize('path', ['configs/litellm.yaml', 'configs/codex/provider.config.toml',
                                  'src/freetier_radar/conformance.py'])
def test_bot_push_dispatches_the_exact_changed_commit(repo, path):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    before, sha = _change(root, path)
    assert dispatch(root, before, sha)
    args = json.loads(receipt.read_text())
    assert args == ['workflow', 'run', 'conformance.yml', '--repo',
                    'mvalentsev/awesome-free-ai-coding', '--ref', 'main',
                    '-f', 'expected_sha=' + sha]


@pytest.mark.parametrize('path', ['README.md', 'configs/opencode.json', 'configs/codex/provider.txt'])
def test_unaffected_changes_do_not_dispatch(repo, path):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    before, sha = _change(root, path)
    assert not dispatch(root, before, sha)
    assert not receipt.exists()


def test_no_change_does_not_dispatch(repo):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    sha = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    assert not dispatch(root, sha, sha)
    assert not receipt.exists()


def test_filters_are_read_from_the_pushed_commit(repo):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    workflow = root / '.github/workflows/conformance.yml'
    data = yaml.safe_load(workflow.read_text())
    data['on']['push']['paths'].append('new-client.txt')
    workflow.write_text(yaml.safe_dump(data))
    _commit(root)
    before, sha = _change(root, 'new-client.txt')
    data['on']['push']['paths'] = ['README.md']
    workflow.write_text(yaml.safe_dump(data))
    assert dispatch(root, before, sha)
    assert receipt.exists()


@pytest.mark.parametrize('invalid', ['HEAD', '--help', 'a' * 39, 'a' * 41, 'z' * 40])
def test_dispatch_rejects_non_commit_arguments_before_calling_gh(repo, invalid):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    before, sha = _change(root, 'configs/litellm.yaml')
    with pytest.raises(ValueError):
        dispatch(root, invalid, sha)
    with pytest.raises(ValueError):
        dispatch(root, before, invalid)
    assert not receipt.exists()


def test_dispatch_rejects_a_different_checkout_and_reversed_range(repo):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    before, sha = _change(root, 'configs/litellm.yaml')
    with pytest.raises(ValueError):
        dispatch(root, sha, before)
    assert not receipt.exists()


def test_dispatch_failure_is_not_a_successful_publication_check(repo, monkeypatch):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    before, sha = _change(root, 'configs/litellm.yaml')
    monkeypatch.setenv('DISPATCH_EXIT', '1')
    with pytest.raises(subprocess.CalledProcessError):
        dispatch(root, before, sha)
    assert receipt.exists()


def test_negative_workflow_filters_require_review_before_dispatch(repo):
    from freetier_radar.conformance import dispatch
    root, receipt = repo
    workflow = root / '.github/workflows/conformance.yml'
    data = yaml.safe_load(workflow.read_text())
    data['on']['push']['paths'].append('!configs/private/**')
    workflow.write_text(yaml.safe_dump(data))
    before = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    sha = _commit(root)
    with pytest.raises(ValueError, match='positive workflow path filters'):
        dispatch(root, before, sha)
    assert not receipt.exists()


@pytest.mark.parametrize('workflow,job,condition', [
    ('update', 'update', "!inputs.dry_run && steps.commit.outputs.pushed == 'true'"),
    ('expire', 'expire', "steps.publish.outputs.changed == 'true'"),
])
def test_both_bot_writers_use_the_shared_dispatch_after_a_push(workflow, job, condition):
    data = yaml.safe_load((ROOT / f'.github/workflows/{workflow}.yml').read_text())
    step = next(s for s in data['jobs'][job]['steps']
                if 'freetier-conformance dispatch' in s.get('run', ''))
    assert condition in step['if']
    assert step['env']['GH_TOKEN'] == '${{ github.token }}'
    assert data['permissions']['actions'] == 'write'
    assert not step.get('continue-on-error')


@pytest.mark.parametrize('workflow,job', [('update', 'update'), ('expire', 'expire')])
def test_bot_workflow_shell_passes_the_actual_commit_range(repo, tmp_path, workflow, job):
    root, receipt = repo
    before, sha = _change(root, 'configs/litellm.yaml')
    uv = tmp_path / 'uv'
    uv.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                  'open(os.environ["DISPATCH_RECEIPT"], "w").write(json.dumps(sys.argv[1:]))\n')
    uv.chmod(0o755)
    data = yaml.safe_load((ROOT / f'.github/workflows/{workflow}.yml').read_text())
    step = next(s for s in data['jobs'][job]['steps']
                if 'freetier-conformance dispatch' in s.get('run', ''))
    subprocess.run(['bash', '-e', '-c', step['run']], cwd=root, env=os.environ, check=True)
    assert json.loads(receipt.read_text()) == ['run', 'freetier-conformance', 'dispatch',
                                               '--before', before, '--sha', sha]


def test_documented_bot_dispatch_cannot_survive_a_removed_workflow_permission(tmp_path):
    from freetier_radar.claims import CLAIMS, check_claims
    root = tmp_path / 'claims'
    (root / '.github/workflows').mkdir(parents=True)
    (root / 'CONTRIBUTING.md').write_text((ROOT / 'CONTRIBUTING.md').read_text())
    for name in ['update', 'expire', 'conformance']:
        path = Path('.github/workflows') / (name + '.yml')
        (root / path).write_text((ROOT / path).read_text())
    claim = next(c for c in CLAIMS if 'writers explicitly dispatch' in c.pattern)
    assert not check_claims(root, [claim], scheduled=())
    path = root / '.github/workflows/expire.yml'
    path.write_text(path.read_text().replace('actions: write', 'actions: read'))
    assert check_claims(root, [claim], scheduled=())


@pytest.mark.parametrize('expected,actual,valid', [
    ('', 'a' * 40, True), ('a' * 40, 'a' * 40, True),
    ('a' * 40, 'b' * 40, False), ('HEAD', 'a' * 40, False),
    ('a' * 39, 'a' * 39, False), ('x; exit 0', 'a' * 40, False),
])
def test_dispatched_workflow_rejects_a_different_commit(expected, actual, valid, tmp_path):
    data = yaml.safe_load((ROOT / '.github/workflows/conformance.yml').read_text())
    triggers = data.get('on', data.get(True))
    assert 'expected_sha' in triggers['workflow_dispatch']['inputs']
    step = next(s for s in data['jobs']['conformance']['steps']
                if s.get('name') == 'Require the requested commit')
    assert step['env'] == {'EXPECTED_SHA': '${{ inputs.expected_sha }}',
                           'ACTUAL_SHA': '${{ github.sha }}'}
    result = subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path,
                            env={**os.environ, 'EXPECTED_SHA': expected, 'ACTUAL_SHA': actual},
                            capture_output=True, text=True)
    assert (result.returncode == 0) is valid
