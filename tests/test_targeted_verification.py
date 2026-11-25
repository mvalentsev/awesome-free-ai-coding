import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml


@pytest.mark.parametrize('selection,expected', [('', []),
    ('novita experiential-labs', ['novita', 'experiential-labs']),
    ('novita\nexperiential-labs', ['novita', 'experiential-labs']),
    ('novita --registry elsewhere', None), ('novita;exit', None), ('   ', None)])
def test_workflow_passes_exact_provider_ids_as_arguments(tmp_path, selection, expected):
    workflow = yaml.safe_load(Path('.github/workflows/update.yml').read_text())
    steps = workflow['jobs']['update']['steps']
    scope = next(step for step in steps if step.get('name') == 'Resolve provider scope')
    assert scope['env']['PROBE_IDS'] == '${{ inputs.provider_ids }}'
    github_env = tmp_path / 'env'
    summary = tmp_path / 'summary'
    env = {**os.environ, 'PROBE_IDS': selection, 'GITHUB_ENV': str(github_env),
           'PROBE_DRY_RUN': 'false', 'GITHUB_STEP_SUMMARY': str(summary)}
    result = subprocess.run(['bash', '-e', '-c', scope['run']], cwd=tmp_path,
                            env=env, capture_output=True, text=True)
    if expected is None:
        assert result.returncode != 0
        assert not github_env.exists()
        return
    assert result.returncode == 0, result.stderr
    selector, value = github_env.read_text().strip().split('=', 1)
    env[selector] = value

    stub = tmp_path / 'uv'
    receipt = tmp_path / 'arguments.json'
    stub.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                    'with open(os.environ["ARG_RECEIPT"], "a") as receipt:\n'
                    '    print(json.dumps(sys.argv[1:]), file=receipt)\n'
                    'print(sys.argv[2])\n')
    stub.chmod(0o755)
    env.update(PATH=str(tmp_path) + os.pathsep + os.environ['PATH'], ARG_RECEIPT=str(receipt))
    names = ('Probe all entries', 'Report the models owed a family',
             'Read every quoted phrase back against its pages')
    scoped = [step for step in steps if step.get('name') in names]
    assert [step['name'] for step in scoped] == list(names)
    commit = next(i for i, step in enumerate(steps) if step.get('id') == 'commit')
    assert steps.index(scope) < steps.index(scoped[0]) < steps.index(scoped[-1]) < commit
    assert all('if' not in step for step in scoped)
    result = subprocess.run(['bash', '-e', '-c', '\n'.join(step['run'] for step in scoped)],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    ids_arg = ['--ids', *expected] if expected else []
    assert [json.loads(line) for line in receipt.read_text().splitlines()] == [
        ['run', 'freetier-probe', '--registry', 'registry.yaml', '--failures', 'failures', *ids_arg],
        ['run', 'freetier-bars', *ids_arg],
        ['run', 'freetier-quotes', '--report', *expected],
    ]
    assert summary.read_text().splitlines() == ['freetier-bars', 'freetier-quotes']


def test_targeted_workflow_does_not_start_unrelated_mutations_or_outreach():
    data = yaml.safe_load(Path('.github/workflows/update.yml').read_text())
    steps = data['jobs']['update']['steps']
    scout = next(step for step in steps if step.get('id') == 'scout')
    report_check = next(step for step in steps if step.get('id') == 'scout_checks')
    assert '!inputs.provider_ids' in scout['if']
    assert report_check['if'] == "steps.scout.outputs.changed == 'true'"
    for step in steps:
        name = step.get('name', '')
        if name == "Record the scout's changes and render every page":
            assert step['if'] == report_check['if']
        elif name == 'Open scout PR':
            assert step['if'] == "${{ !inputs.dry_run && steps.scout_checks.outcome == 'success' }}"
        elif (step not in (scout, report_check) and
              ('scout' in name.lower() or name in ('Announce what changed',
               'Re-read tier marks from the Artificial Analysis index'))):
            assert '!inputs.provider_ids' in str(step.get('if', '')), name


@pytest.mark.parametrize('outcome', ['success', 'failure', 'cancelled', 'skipped'])
def test_targeted_dry_run_cannot_hide_a_failed_probe(outcome, tmp_path):
    data = yaml.safe_load(Path('.github/workflows/update.yml').read_text())
    steps = data['jobs']['update']['steps']
    assert next(s for s in steps if s.get('name') == 'Probe all entries')['id'] == 'probe'
    step = next(s for s in steps if s.get('name') == 'Require selected providers to verify')
    assert 'always()' in step['if'] and 'inputs.provider_ids' in step['if']
    assert step['env']['PROBE_OUTCOME'] == '${{ steps.probe.outcome }}'
    result = subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path,
        env={**os.environ, 'PROBE_OUTCOME': outcome}, capture_output=True)
    assert (result.returncode == 0) is (outcome == 'success')
