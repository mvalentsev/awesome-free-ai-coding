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
    stub = tmp_path / 'uv'
    receipt = tmp_path / 'arguments.json'
    stub.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                    'open(os.environ["ARG_RECEIPT"], "w").write(json.dumps(sys.argv[1:]))\n')
    stub.chmod(0o755)
    for name in ('Probe all entries', 'Read every quoted phrase back against its pages'):
        step = next(step for step in steps if step.get('name') == name)
        assert step['env']['PROBE_IDS'] == '${{ inputs.provider_ids }}'
        receipt.unlink(missing_ok=True)
        result = subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path,
            env={**os.environ, 'PATH': str(tmp_path) + os.pathsep + os.environ['PATH'],
                 'ARG_RECEIPT': str(receipt), 'PROBE_IDS': selection,
                 'PROBE_DRY_RUN': 'false', 'GITHUB_STEP_SUMMARY': str(tmp_path / 'summary')},
            capture_output=True, text=True)
        if expected is None:
            assert result.returncode != 0
            assert not receipt.exists()
        else:
            assert result.returncode == 0, result.stderr
            args = json.loads(receipt.read_text())
            if name == 'Probe all entries':
                assert args == ['run', 'freetier-probe', '--registry', 'registry.yaml',
                                '--failures', 'failures', *(['--ids', *expected] if expected else [])]
            else:
                assert args == ['run', 'freetier-quotes', '--report', *expected]


def test_targeted_workflow_does_not_start_unrelated_mutations_or_outreach():
    data = yaml.safe_load(Path('.github/workflows/update.yml').read_text())
    steps = data['jobs']['update']['steps']
    for step in steps:
        name = step.get('name', '')
        if ('scout' in name.lower() or name in ('Announce what changed',
                'Re-read tier marks from the Artificial Analysis index')):
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
