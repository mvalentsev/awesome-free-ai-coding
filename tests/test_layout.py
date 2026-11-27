"""The map of the repository holds every tracked file to one line saying what
it is, what it is made from and what writes it — so a file nobody accounted
for, a generated file the map calls hand-written, or a page the site serves by
accident is a failed check rather than a surprise on the next run."""
import os
import sys
import subprocess
from pathlib import Path

import pytest
import yaml

from freetier_radar.layout import (MAP, Kind, Node, check_layout, main, markdown_table,
                                   node_for, run_paths, tracked_files)

ROOT = Path(__file__).resolve().parent.parent

TINY = (
    Node("registry.yaml", Kind.DATA, "the rows", published=True),
    Node("providers/*.md", Kind.GENERATED, "a page per row", made_from=("registry.yaml",),
         written_by=("freetier-render",), published=True),
    Node("README.md", Kind.GENERATED, "the landing page", made_from=("registry.yaml",),
         written_by=("freetier-render",)),
    Node("announced.jsonl", Kind.LOG, "the announcer's ledger",
         written_by=("freetier-announce",), published=True, optional=True),
    Node("src/pkg/*.py", Kind.CODE, "the package"),
)


def test_a_file_is_found_by_the_line_that_names_it():
    assert node_for("providers/groq-free.md", TINY).path == "providers/*.md"
    assert node_for("README.md", TINY).kind is Kind.GENERATED
    # a star stops at a slash, the way a shell glob does
    assert node_for("providers/old/groq-free.md", TINY) is None
    assert node_for("notes.txt", TINY) is None


def test_the_real_map_knows_what_each_kind_of_file_is():
    assert node_for("registry.yaml").kind is Kind.DATA
    assert node_for("history.jsonl").kind is Kind.LOG
    assert node_for("README.md").kind is Kind.GENERATED
    assert node_for("providers/groq-free.md").kind is Kind.GENERATED
    assert node_for("browse.html").kind is Kind.PAGE
    assert node_for("src/freetier_radar/render.py").kind is Kind.CODE


def test_a_file_the_map_does_not_name_is_reported():
    files = ["registry.yaml", "providers/a.md", "README.md", "src/pkg/x.py", "notes.txt"]
    assert check_layout(files=files, nodes=TINY, exclude=["README.md", "src"]) == [
        "notes.txt is on no line of the map (layout.MAP) — say what it is, what it is made "
        "from and what writes it"]


def test_a_line_of_the_map_that_names_no_file_is_reported():
    files = ["registry.yaml", "README.md", "src/pkg/x.py"]
    assert check_layout(files=files, nodes=TINY, exclude=["README.md", "src"]) == [
        "providers/*.md is on the map and names no tracked file — the file is gone, or the "
        "line names it wrong"]


def test_a_file_two_lines_claim_is_reported():
    nodes = TINY + (Node("providers/index.md", Kind.GENERATED, "the index", published=True,
                         written_by=("freetier-render",)),)
    files = ["registry.yaml", "providers/index.md", "README.md", "src/pkg/x.py"]
    assert check_layout(files=files, nodes=nodes, exclude=["README.md", "src"]) == [
        "providers/index.md is on two lines of the map, providers/*.md and providers/index.md"]


def test_the_site_serves_what_the_map_publishes_and_nothing_else():
    """Jekyll serves every file the site's `exclude` does not name, apart from
    paths that start with a dot, an underscore, # or ~, backups ending in ~, and
    node_modules or vendor. A new directory of scripts would be published the
    day it was committed; a page left out would quietly stop being served."""
    files = ["registry.yaml", "providers/a.md", "README.md", "src/pkg/x.py"]
    assert check_layout(files=files, nodes=TINY, exclude=["src"]) == [
        "README.md is served by the Pages site and the map says it is not published — "
        "add it to exclude in _config.yml, or mark it published"]
    assert check_layout(files=files, nodes=TINY, exclude=["README.md", "src", "providers"]) == [
        "providers/a.md is left out of the Pages site by _config.yml and the map says it is "
        "published"]


def test_the_map_calls_generated_exactly_what_the_render_writes(tmp_path, render_source):
    """The render's output list and the map's are the same list, so a new
    output reaches the scheduled run's commit and the hand-edit guard by being
    written, not by someone remembering to add it."""
    from freetier_radar.render import render_all
    from test_render import TODAY
    out = tmp_path / 'rendered'
    out.mkdir()
    render_all(render_source / "registry.yaml", ROOT / "templates", out,
               today=TODAY, contributing_from=ROOT)
    written = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    for f in written:
        assert node_for(f) is not None and "freetier-render" in node_for(f).written_by, f
    generated = {n.path for n in MAP if n.kind is Kind.GENERATED}
    covered = {node_for(f).path for f in written if node_for(f).kind is Kind.GENERATED}
    assert generated == covered
    assert (out / 'llms.txt').read_text(encoding='utf-8').startswith('# awesome-free-ai-coding')


def test_the_scheduled_run_commits_every_file_it_writes():
    """The workflow's `git add` is the map's list, so a file the run starts
    writing is committed by the run that first writes it."""
    paths = run_paths()
    assert "registry.yaml" in paths and "history.jsonl" in paths and "providers" in paths
    for f in tracked_files(ROOT):
        node = node_for(f)
        if node.kind is Kind.GENERATED:
            assert f in paths or any(f.startswith(p + "/") for p in paths), f
    assert "watchlist.yaml" not in paths, "the run never writes a curated file"


def test_the_workflow_commits_the_maps_list():
    workflow = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    commit = next(s for s in workflow["jobs"]["update"]["steps"]
                  if s.get("id") == "commit")
    assert "freetier-map paths run" in commit["run"]


@pytest.mark.parametrize('history_changed', [False, True])
def test_expiry_workflow_publishes_a_history_only_change(tmp_path, history_changed):
    workflow = yaml.safe_load((ROOT / '.github/workflows/expire.yml').read_text())
    publish = next(s for s in workflow['jobs']['expire']['steps'] if s.get('id') == 'publish')
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    history = tmp_path / 'history.jsonl'
    history.write_text('previous\n')
    (tmp_path / 'registry.yaml').write_text('unchanged\n')
    subprocess.run(['git', 'add', '.'], cwd=tmp_path, check=True)
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.test',
                    'commit', '-qm', 'base'], cwd=tmp_path, check=True)
    if history_changed:
        history.write_text('previous\narchived\n')

    stub = '''
uv() {
    if [ "$2" = freetier-map ]; then echo 'history.jsonl registry.yaml'; fi
}
git() {
    if [ "$1" = push ]; then
        command git diff-tree --no-commit-id --name-only -r HEAD > pushed.txt
    else
        command git "$@"
    fi
}
'''
    result = subprocess.run(['bash', '-eo', 'pipefail', '-c', stub + publish['run']],
                            cwd=tmp_path, env={**os.environ, 'GITHUB_OUTPUT': 'result.txt'},
                            capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    if history_changed:
        assert (tmp_path / 'pushed.txt').read_text() == 'history.jsonl\n'
        assert (tmp_path / 'result.txt').read_text() == 'changed=true\n'
    else:
        assert not (tmp_path / 'pushed.txt').exists()
        assert not (tmp_path / 'result.txt').exists()


def test_the_run_checks_what_ci_would_before_it_commits():
    """CI never runs on the scheduled run's own push — GITHUB_TOKEN starts no
    workflow — so a commit that broke a test CI runs would sit on main until
    the maintainer's next commit met it at the pre-commit gate, with nothing to
    say which change did it. What CI runs, the run runs before it commits, and
    reports the result before it publishes."""
    workflow = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["update"]["steps"]
    check = next(s for s in steps if s.get("name") == "Check what the run is about to commit")
    commit = next(s for s in steps if s.get("id") == "commit")
    assert steps.index(check) < steps.index(commit)
    ci_runs = "\n".join(s.get("run", "") for s in ci["jobs"]["test"]["steps"])
    for command in ("pytest", "freetier-check", "freetier-render"):
        assert command in ci_runs and command in check["run"], command


@pytest.mark.parametrize("failed", [False, True])
def test_scout_branch_check_reports_failure_and_returns_its_status(tmp_path, failed):
    workflow = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text())
    steps = workflow["jobs"]["update"]["steps"]
    check = next(s for s in steps if s.get("name") == "Check the scout's branch")
    report = tmp_path / "scout-pr.md"
    report.write_text("## Scout proposals\n")
    fake_uv = f'''
uv() {{
    if [ "$2" = freetier-check ] && [ "{int(failed)}" = 1 ]; then
        echo "suppression matches nothing"
        return 1
    fi
}}
'''
    result = subprocess.run(["bash", "-eo", "pipefail", "-c", fake_uv + check["run"]],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == int(failed)
    body = report.read_text()
    assert "## Scout proposals" in body and "✓ `pytest -q`" in body
    assert ("suppression matches nothing" in body) is failed


def test_ci_runs_locked_and_minimum_dependency_checks():
    """Pytest covers the matrix; tree checks cover both dependency sets and the
    commit range is checked once."""
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    test = ci["jobs"]["test"]
    assert [s["run"] for s in test["steps"] if s.get("run", "").startswith("uv sync")] \
        == ["uv sync --locked"]
    gates = [step for step in test["steps"] if "freetier-gate diff" in step.get("run", "")]
    gate, = gates
    assert gate["if"] == "strategy.job-index == 0"
    curated, = [step for step in test["steps"] if step.get("run") == "uv run freetier-check"]
    assert curated["if"] == gate["if"]
    rendered, = [step for step in test["steps"] if "freetier-render" in step.get("run", "")]
    assert rendered["if"] == gate["if"]
    assert any(step.get("run") == "uv run pytest -q" and "if" not in step for step in test["steps"])
    floors = ci["jobs"]["floors"]
    assert floors["env"]["UV_RESOLUTION"] == "lowest-direct"
    runs = [s.get("run", "") for s in floors["steps"]]
    # --locked would refuse the lock the lowest versions resolve to.
    assert "uv sync" in runs
    for command in ("pytest", "freetier-check", "freetier-render"):
        assert any(command in r for r in runs), command


def test_a_real_run_waits_for_the_one_before_it_and_builds_on_what_it_pushed():
    """Of two runs pushing to main, the later one's push is refused, and GitHub
    starts a scheduled run hours late, onto whatever was dispatched by hand. So
    a real run queues behind the one in progress — never cancelling it, which
    could stop it between its commit and its push — and checks out the branch
    as it is when the job starts; a dry run, which commits nothing, stays out
    of the queue."""
    workflow = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    assert workflow["concurrency"] == {
        "group": "${{ inputs.dry_run && github.run_id || 'update' }}", "cancel-in-progress": False,
        "queue": "max"}
    checkout = next(s for s in workflow["jobs"]["update"]["steps"]
                    if s.get("uses", "").startswith("actions/checkout"))
    assert checkout["with"]["ref"] == "${{ github.ref }}"


def test_a_dry_run_reaches_the_checks_when_a_row_fails():
    """A dry run is how a change to the workflow is tried before a real run,
    and the probe exits 1 on a dry run that finds a failing row — which a person
    chaining it in a shell wants — so in a dry run the probe step carries on,
    and one failing row does not skip the checks the dry run was dispatched to
    try. A real run's probe exits 0 whatever it finds, and a scheduled run has
    no inputs at all."""
    workflow = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text(encoding="utf-8"))
    probe = next(s for s in workflow["jobs"]["update"]["steps"]
                 if s.get("name") == "Probe all entries")
    assert probe.get("continue-on-error") == "${{ inputs.dry_run == true }}"



def test_a_failed_family_report_is_visible_even_when_tee_succeeds(tmp_path):
    workflow = yaml.safe_load((ROOT / ".github/workflows/update.yml").read_text())
    steps = workflow["jobs"]["update"]["steps"]
    report = next(step for step in steps if "freetier-bars" in step.get("run", ""))
    summary = tmp_path / "summary"
    command = 'uv() { echo "Registry history unreadable"; return 17; }\n' + report["run"]
    result = subprocess.run(["bash", "-e", "-c", command], cwd=tmp_path,
                            env={**os.environ, "GITHUB_STEP_SUMMARY": str(summary)},
                            capture_output=True, text=True)
    assert summary.read_text() == "Registry history unreadable\n"
    assert result.returncode == 17
    assert report["continue-on-error"] is True


def test_the_map_is_printed_as_a_table_with_one_row_per_line():
    table = markdown_table(TINY)
    lines = table.splitlines()
    assert lines[0].startswith("| File |")
    assert len(lines) == 2 + len(TINY)
    assert "`providers/*.md`" in table and "`freetier-render`" in table


def test_the_hand_edit_guard_refuses_a_generated_file_and_a_log(capsys):
    """What the editor hook asks before a hand edit: a generated file is
    rewritten by the next render and a log is written by the run alone."""
    with pytest.raises(SystemExit) as refused:
        main(["may-edit", "README.md"])
    assert refused.value.code == 1
    assert "templates/README.md.j2" in capsys.readouterr().out
    with pytest.raises(SystemExit) as refused:
        main(["may-edit", "history.jsonl"])
    assert refused.value.code == 1
    main(["may-edit", "registry.yaml", "templates/README.md.j2"])


def test_tracked_files_are_read_from_git_or_from_the_directory(tmp_path):
    """In the repository the list is git's; in a snapshot of the index — where
    the pre-commit gate runs its checks — it is the files that are there."""
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "x.pyc").write_text("", encoding="utf-8")
    assert tracked_files(tmp_path) == ["a.txt", "sub/b.txt"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "a.txt"], check=True)
    assert tracked_files(tmp_path) == ["a.txt"]


def test_every_line_of_the_map_says_what_the_file_is():
    for node in MAP:
        assert node.about, node.path
        if node.kind is Kind.GENERATED:
            assert node.made_from and "freetier-render" in node.written_by, node.path


def test_read_page_workflow_keeps_failed_responses_but_reports_only_readable_evidence(tmp_path):
    workflow = yaml.safe_load((ROOT / '.github/workflows/read-page.yml').read_text())
    step = next(step for step in workflow['jobs']['read']['steps'] if step.get('name') == 'Read the pages')
    wrapper = tmp_path / 'read-fixture.py'
    wrapper.write_text('''
import sys

import respx
from freetier_radar import page_reader

page_reader._addresses = lambda host: []
with respx.mock(assert_all_called=True) as mock:
    mock.get('https://vendor.example/live').respond(200, text='<p>Free quota — café</p>')
    mock.get('https://vendor.example/gone').respond(404, text='<p>Free quota</p>')
    mock.get('https://vendor.example/empty').respond(
        200, headers={'content-type': 'text/html'},
        text='<html><head><title>Free quota</title></head><body><div id="root"></div>'
             '<script src="/entry.js" type="module"></script></body></html>')
    exec(compile(sys.stdin.read(), 'workflow', 'exec'), {'__name__': '__main__'})
''')
    run = subprocess.run(
        ['bash', '-eo', 'pipefail', '-c', 'uv() { "$TEST_PYTHON" "$TEST_WRAPPER"; }\n' + step['run']],
        cwd=tmp_path, capture_output=True, text=True,
        env={**os.environ, 'TEST_PYTHON': sys.executable, 'TEST_WRAPPER': str(wrapper),
             'GITHUB_STEP_SUMMARY': str(tmp_path / 'summary.md'), 'KEYWORDS': 'Free quota',
             'URLS': ' '.join(f'https://vendor.example/{name}' for name in ('live', 'gone', 'empty'))})
    assert run.returncode == 2, run.stderr
    assert run.stdout.count('`Free quota` — rendered text') == 1
    raw = (tmp_path / 'pages/https_vendor.example_live.html').read_bytes()
    assert raw == '<p>Free quota — café</p>'.encode() and f'{len(raw)} bytes' in run.stdout
    sections = dict(section.split('\n', 1) for section in run.stdout.split('## ')[1:])
    for name in ('gone', 'empty'):
        assert 'Free quota' in (tmp_path / f'pages/https_vendor.example_{name}.html').read_text()
        assert 'Page evidence unavailable' in sections[f'https://vendor.example/{name}']


def test_the_published_pages_are_kept():
    """A page the site published stays (gate.page_problems): the provider
    pages and the model pages, and no other file."""
    assert [n.path for n in MAP if n.kept] == ["providers/*.md", "models/*.md"]
