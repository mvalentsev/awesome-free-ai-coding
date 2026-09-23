"""The map of the repository holds every tracked file to one line saying what
it is, what it is made from and what writes it — so a file nobody accounted
for, a generated file the map calls hand-written, or a page the site serves by
accident is a failed check rather than a surprise on the next run."""
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
    dot and underscore paths. A new directory of scripts would be published the
    day it was committed; a page left out would quietly stop being served."""
    files = ["registry.yaml", "providers/a.md", "README.md", "src/pkg/x.py"]
    assert check_layout(files=files, nodes=TINY, exclude=["src"]) == [
        "README.md is served by the Pages site and the map says it is not published — "
        "add it to exclude in _config.yml, or mark it published"]
    assert check_layout(files=files, nodes=TINY, exclude=["README.md", "src", "providers"]) == [
        "providers/a.md is left out of the Pages site by _config.yml and the map says it is "
        "published"]


def test_every_committed_file_is_on_the_map():
    assert check_layout(ROOT) == []


def test_the_map_calls_generated_exactly_what_the_render_writes(tmp_path):
    """The render's output list and the map's are the same list, so a new
    output reaches the scheduled run's commit and the hand-edit guard by being
    written, not by someone remembering to add it."""
    from freetier_radar.render import render_all
    render_all(ROOT / "registry.yaml", ROOT / "templates", tmp_path, contributing_from=ROOT)
    written = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()}
    for f in written:
        assert node_for(f) is not None and "freetier-render" in node_for(f).written_by, f
    generated = {f for f in tracked_files(ROOT) if node_for(f).kind is Kind.GENERATED}
    assert generated <= written, generated - written
    # CONTRIBUTING.md is written by hand, all but the map section the render prints
    assert {f for f in written if node_for(f).kind is not Kind.GENERATED} == {"CONTRIBUTING.md"}


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
