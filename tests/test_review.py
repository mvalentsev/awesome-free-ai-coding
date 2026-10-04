"""Review evidence must refer to the requested tree, retain failures and stay private."""
import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest
import respx

from freetier_radar import review


def repo_at(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    env = {**os.environ, 'GIT_AUTHOR_NAME': 'a reviewer', 'GIT_AUTHOR_EMAIL': 't@example.com',
           'GIT_COMMITTER_NAME': 'a reviewer', 'GIT_COMMITTER_EMAIL': 't@example.com'}
    subprocess.run(['git', 'init', '-q', str(repo)], check=True, env=env)
    (repo / '.gitignore').write_text('.evidence/\n')
    before = {'entries': [{'id': 'vendor', 'models': [{'family': 'alpha', 'tier': 'strong'}]}],
              'models': [{'family': 'alpha', 'tier': 'strong', 'page': 'https://site.example/models/alpha/'}]}
    for index in (before, {**before, 'entries': [{'id': 'vendor', 'models': [
            {'family': 'alpha', 'tier': 'strong'}, {'family': 'beta', 'tier': 'strong'}]}],
            'models': [*before['models'], {'family': 'beta', 'tier': 'strong',
                                         'page': 'https://site.example/models/beta/'}]}):
        (repo / 'index.json').write_text(json.dumps(index))
        (repo / 'registry.yaml').write_text('entries: []\n')
        subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True, env=env)
        subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'chore: fixture'], check=True, env=env)
    return repo


def test_scope_resolves_refs_and_retains_whole_diff_without_reading_the_worktree(tmp_path):
    repo = repo_at(tmp_path)
    (repo / 'index.json').write_text('corrupt uncommitted text')
    bundle = review.Bundle(repo / '.evidence', repo)
    scope = review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    assert len(scope['sha']) == 40
    assert scope['rows'] == ['vendor']
    assert scope['families'] == ['beta']
    assert 'corrupt uncommitted' not in (bundle.out / 'diff.patch').read_text()
    assert json.loads((bundle.out / 'scope.json').read_text())['sha'] == scope['sha']


def test_evidence_cannot_overwrite_a_tracked_file_or_a_publishable_directory(tmp_path):
    repo = repo_at(tmp_path)
    for path in (repo, repo / 'public-evidence', repo / 'index.json', repo / '.git' / 'notes'):
        with pytest.raises(ValueError):
            review.Bundle(path, repo)
    review.Bundle(repo / '.evidence', repo)


def test_manifest_detects_changed_and_missing_raw_evidence(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    bundle.write('body.raw', b'original')
    bundle.save('phase', {'passed': True})
    assert review.integrity(bundle) == []
    (bundle.out / 'body.raw').write_bytes(b'changed')
    assert any('body.raw' in x for x in review.integrity(bundle))
    (bundle.out / 'body.raw').unlink()
    assert any('body.raw' in x for x in review.integrity(bundle))


@pytest.mark.parametrize('runs, want', [
    ([], 'waiting'),
    ([{'name': 'ci', 'headSha': 'wrong', 'status': 'completed', 'conclusion': 'success'}], 'waiting'),
    ([{'name': 'ci', 'headSha': 'a' * 40, 'status': 'completed', 'conclusion': 'failure'}], 'failed'),
    ([{'name': 'ci', 'headSha': 'a' * 40, 'status': 'completed', 'conclusion': 'success'}], 'passed'),
])
def test_workflows_cannot_pass_on_a_missing_wrong_or_failed_run(runs, want):
    assert review.workflow_state(runs, 'a' * 40, {'ci'}) == want


def test_workflow_rerun_uses_the_newest_attempt_and_not_an_older_green_run():
    old = {'databaseId': 1, 'name': 'ci', 'headSha': 'a' * 40,
           'status': 'completed', 'conclusion': 'success'}
    new = {**old, 'databaseId': 2, 'status': 'in_progress', 'conclusion': ''}
    assert review.workflow_state([old, new], 'a' * 40, {'ci'}) == 'waiting'


@respx.mock
async def test_publication_retries_network_failures_but_preserves_a_wrong_body(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    respx.get('https://site.example/index.json').mock(side_effect=[
        httpx.Response(503), httpx.Response(200, content=b'old tree')])
    async with httpx.AsyncClient() as client:
        result = await review.fetch(client, 'https://site.example/index.json', bundle,
                                    expected=b'new tree', backoff=0)
    assert result['passed'] is False
    assert [a['status'] for a in result['attempts']] == [503, 200]
    assert (bundle.out / result['attempts'][-1]['file']).read_bytes() == b'old tree'


@respx.mock
async def test_publication_checks_excluded_readmes_on_github_and_served_assets_on_pages(tmp_path, monkeypatch):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    sha = 'a' * 40
    paths = ['README.md', 'assets/README.md', 'configs/README.md',
             'assets/model-name.js', 'configs/codex/litellm.config.toml']
    bundle.save('scope', {'base': 'b' * 40, 'sha': sha, 'paths': paths,
                          'workflows': ['pages build and deployment']})
    bundle.save('workflows', {'sha': sha, 'passed': True, 'runs': [{
        'name': 'pages build and deployment', 'headSha': sha,
        'status': 'completed', 'conclusion': 'success'}]})
    monkeypatch.setattr(review, 'PAGES_URL', 'https://site.example')
    monkeypatch.setattr(review, 'REPO_URL', 'https://github.com/example/repo')
    monkeypatch.setattr(review, 'blob', lambda repo, ref, path: path.encode())
    raw = f'https://raw.githubusercontent.com/example/repo/{sha}/'
    respx.route(url__startswith=raw).mock(
        side_effect=lambda request: httpx.Response(200, content=str(request.url).removeprefix(raw).encode()))
    def served(request):
        path = str(request.url).removeprefix('https://site.example/')
        return httpx.Response(404 if path.endswith('README.md') else 200, content=path.encode())
    respx.route(url__startswith='https://site.example/').mock(side_effect=served)
    result = await review.publication(bundle)
    assert result['passed'], [c for c in result['checks'] if not c['passed']]
    checked = {(c['kind'], c['path']) for c in result['checks']}
    for path in paths[:3]:
        assert ('source', path) in checked
        assert ('served', path) not in checked
    for path in paths[3:]:
        assert ('source', path) in checked
        assert ('served', path) in checked


@respx.mock
async def test_rate_limited_source_is_not_retried_or_treated_as_a_changed_quote(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    respx.get('https://vendor.example/catalog').respond(429, headers={'Retry-After': '120'})
    async with httpx.AsyncClient() as client:
        result = await review.fetch(client, 'https://vendor.example/catalog', bundle, backoff=0)
    assert result['passed'] is False
    assert len(result['attempts']) == 1
    assert result['attempts'][0]['retry_after'] == '120'


def test_client_success_requires_the_fresh_answer_a_tool_and_no_error():
    good = [{'type': 'tool_use', 'part': {'type': 'tool', 'state': {'status': 'completed', 'output': 'fresh-marker'}}},
            {'type': 'text', 'part': {'type': 'text', 'text': 'fresh-marker'}},
            {'type': 'step_finish', 'part': {'type': 'step-finish', 'reason': 'stop'}}]
    assert review.client_result('opencode', 0, good, 'fresh-marker')['passed']
    for code, events in ((1, good), (0, good[:1]), (0, good[1:]), (0, good[:2]),
                         (0, good + [{'type': 'error'}])):
        assert not review.client_result('opencode', code, events, 'fresh-marker')['passed']
    assert not review.client_result('opencode', 0, good, 'different-marker')['passed']


def test_report_keeps_missing_phases_and_failed_live_calls_visible(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    bundle.save('scope', {'sha': 'a' * 40})
    bundle.save('client-opencode', {'passed': False, 'status': 429})
    result = review.report(bundle)
    assert not result['complete']
    assert 'publication' in result['missing']
    assert 'client-opencode' in result['failed']
    assert result['human_review_required']


def test_browser_plan_covers_changed_families_and_import_rejects_partial_or_wrong_runs(tmp_path):
    repo = repo_at(tmp_path)
    bundle = review.Bundle(repo / '.evidence', repo)
    review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    from freetier_radar.review_browser import browser_plan, accept_browser
    plan = browser_plan(bundle)
    assert [m['family'] for m in plan['models']] == ['beta']
    assert plan['widths'] == [1440, 375, 320]
    assert plan['schemes'] == ['light', 'dark']
    result = {'sha': plan['sha'], 'passed': True, 'records': [], 'pageErrors': []}
    assert not accept_browser(bundle, result, plan)['passed']
    result['records'] = [{'id': id} for id in plan['cases']]
    assert accept_browser(bundle, result, plan)['passed']
    result['sha'] = 'wrong'
    assert not accept_browser(bundle, result, plan)['passed']
    result['sha'] = plan['sha']
    result['records'].append(result['records'][0])
    assert not accept_browser(bundle, result, plan)['passed']


def test_report_rejects_present_but_unproven_phases(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    bundle.save('scope', {'sha': 'a' * 40})
    for phase in ('sources', 'workflows', 'publication', 'browser'):
        bundle.save(phase, {'sha': 'a' * 40})
    assert not review.report(bundle)['complete']


def test_browser_import_rejects_a_complete_stale_plan(tmp_path):
    repo = repo_at(tmp_path)
    bundle = review.Bundle(repo / '.evidence', repo)
    review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    from freetier_radar.review_browser import browser_plan, accept_browser
    plan = {**browser_plan(bundle), 'sha': 'b' * 40}
    result = {'sha': plan['sha'], 'passed': True,
              'records': [{'id': case} for case in plan['cases']]}
    assert not accept_browser(bundle, result, plan)['passed']


def test_client_requires_a_completed_turn_and_actual_marker_in_tool_output():
    events = [{'type': 'item.completed', 'item': {'type': 'command_execution',
              'exit_code': 0, 'aggregated_output': 'marker'}},
              {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'marker'}}]
    assert not review.client_result('codex', 0, events, 'marker')['passed']
    assert review.client_result('codex', 0, events + [{'type': 'turn.completed'}], 'marker')['passed']
    events[0]['item']['aggregated_output'] = 'something else'
    assert not review.client_result('codex', 0, events + [{'type': 'turn.completed'}], 'marker')['passed']


@respx.mock
async def test_network_errors_are_retained_before_a_successful_retry(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    respx.get('https://site.example/').mock(side_effect=[httpx.ConnectError('offline'),
                                                     httpx.Response(200, content=b'ok')])
    async with httpx.AsyncClient() as client:
        result = await review.fetch(client, 'https://site.example/', bundle, backoff=0)
    assert result['passed']
    assert len(result['attempts']) == 2
    assert result['attempts'][0]['error']


def test_real_prepare_cli_links_to_the_artifact_it_created(tmp_path):
    import sys
    repo = repo_at(tmp_path)
    out = repo / '.evidence'
    run = subprocess.run([sys.executable, '-c', 'from freetier_radar.review import main; main()',
                          '--root', str(repo), '--out', str(out), 'prepare', '--base', 'HEAD~1'],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    summary = json.loads(run.stdout)
    assert Path(summary['evidence']).is_file()
    assert summary['sha'] == json.loads((out / 'scope.json').read_text())['sha']


def test_bundle_lock_rejects_parallel_writers_and_releases_after_close(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    first = review.lock_bundle(bundle)
    try:
        with pytest.raises(ValueError, match='another review phase'):
            review.lock_bundle(bundle)
    finally:
        first.close()
    second = review.lock_bundle(bundle)
    second.close()


def test_existing_unregistered_phase_cannot_be_used_as_evidence(tmp_path):
    bundle = review.Bundle(tmp_path / 'evidence', tmp_path)
    (bundle.out / 'sources.json').write_text('{"passed": true}')
    with pytest.raises(ValueError, match='unregistered evidence'):
        bundle.load('sources')


def test_failed_cli_replaces_an_older_green_phase_with_a_persisted_error(tmp_path):
    import sys
    repo = repo_at(tmp_path)
    bundle = review.Bundle(repo / '.evidence', repo)
    scope = review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    bundle.save('browser', {'sha': scope['sha'], 'passed': True})
    result_file = tmp_path / 'result.json'
    result_file.write_text('{}')
    run = subprocess.run([sys.executable, '-c', 'from freetier_radar.review import main; main()',
                          '--root', str(repo), '--out', str(bundle.out), 'browser', '--result', str(result_file)],
                         capture_output=True, text=True)
    assert run.returncode == 1
    saved = review.Bundle(bundle.out, repo).load('browser')
    assert saved['passed'] is False
    assert 'generate the browser plan first' in saved['error']


def test_prepare_cannot_reuse_green_evidence_for_a_wider_scope_at_the_same_head(tmp_path):
    repo = repo_at(tmp_path)
    bundle = review.Bundle(repo / '.evidence', repo)
    review.prepare(repo, 'HEAD', 'HEAD', bundle)
    with pytest.raises(ValueError, match='different commits'):
        review.prepare(repo, 'HEAD~1', 'HEAD', bundle)


def test_browser_rejects_malformed_json_objects_instead_of_raising_attribute_error(tmp_path):
    repo = repo_at(tmp_path)
    bundle = review.Bundle(repo / '.evidence', repo)
    review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    from freetier_radar.review_browser import browser_plan, accept_browser
    plan = browser_plan(bundle)
    for result in ([], {'records': [None]}, {'records': 'wrong'}, {'records': [{'id': {}}]},
                   {'records': [{'id': 'readme', 'image_url': True}]}):
        with pytest.raises(ValueError):
            accept_browser(bundle, result, plan)


def test_report_requires_byte_checks_for_every_loaded_github_image(tmp_path):
    repo = repo_at(tmp_path)
    bundle = review.Bundle(repo / '.evidence', repo)
    scope = review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    for phase in ('sources','workflows','publication','browser'):
        bundle.save(phase, {'sha': scope['sha'], 'passed': True})
    bundle.save('browser-execution', {'sha': scope['sha'], 'records': [
        {'image_url': 'https://github.com/image.svg', 'image_path': 'assets/image.svg'}]})
    assert not review.report(bundle)['complete']
    bundle.save('publication', {'sha': scope['sha'], 'passed': True, 'checks': [
        {'url': 'https://github.com/image.svg', 'path': 'assets/image.svg', 'kind': 'github-image', 'passed': True}]})
    assert review.report(bundle)['complete']


def test_verification_log_must_prove_the_exact_produced_commit(tmp_path):
    repo = repo_at(tmp_path)
    sha = review.revision(repo, 'HEAD')
    run = {'name': 'update', 'status': 'completed', 'conclusion': 'success',
           'headSha': review.revision(repo, 'HEAD~1'), 'databaseId': 3, 'attempt': 1}
    log = 'step timestamp [main '+sha[:7]+'] chore: verification 2026-10-02'
    verified = review.produced_run(repo, sha, run, log, 'update')
    assert verified['headSha'] != sha
    assert verified['producedSha'] == sha
    for wrong_run, wrong_log in (({**run, 'conclusion': 'failure'}, log),
                                 ({**run, 'name': 'ci'}, log), (run, 'dry run'),
                                 (run, log.replace(sha[:7], run['headSha'][:7]))):
        with pytest.raises(ValueError):
            review.produced_run(repo, sha, wrong_run, wrong_log, 'update')
    assert review.workflow_state([verified], sha, {'update'}) == 'passed'


def test_browser_plan_keeps_changed_archived_provider_pages(tmp_path):
    repo = repo_at(tmp_path)
    index = json.loads((repo / 'index.json').read_text())
    index['entries'][0]['archived'] = True
    (repo / 'index.json').write_text(json.dumps(index))
    env = {**os.environ, 'GIT_AUTHOR_NAME':'a reviewer','GIT_AUTHOR_EMAIL':'t@example.com',
           'GIT_COMMITTER_NAME':'a reviewer','GIT_COMMITTER_EMAIL':'t@example.com'}
    subprocess.run(['git','-C',str(repo),'add','.'],check=True,env=env)
    subprocess.run(['git','-C',str(repo),'commit','-qm','chore: fixture archive'],check=True,env=env)
    bundle = review.Bundle(repo / '.evidence', repo)
    review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    from freetier_radar.review_browser import browser_plan
    plan = browser_plan(bundle)
    assert plan['rows'][0]['archived']
    assert len([case for case in plan['cases'] if '/provider/vendor' in case]) == 6


def test_scope_includes_registry_changes_not_exposed_in_the_public_index(tmp_path):
    repo = repo_at(tmp_path)
    (repo / 'registry.yaml').write_text('entries:\n  - id: vendor\n    probe:\n      endpoint: https://new.vendor.example/\n')
    env = {**os.environ, 'GIT_AUTHOR_NAME':'a reviewer','GIT_AUTHOR_EMAIL':'t@example.com',
           'GIT_COMMITTER_NAME':'a reviewer','GIT_COMMITTER_EMAIL':'t@example.com'}
    subprocess.run(['git','-C',str(repo),'add','.'],check=True,env=env)
    subprocess.run(['git','-C',str(repo),'commit','-qm','fix: fixture probe'],check=True,env=env)
    bundle = review.Bundle(repo / '.evidence', repo)
    scope = review.prepare(repo, 'HEAD~1', 'HEAD', bundle)
    assert scope['rows'] == ['vendor']
