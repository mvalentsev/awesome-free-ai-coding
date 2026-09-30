"""What git says about the repository's past, read one way by the gate, the
IndexNow ping and the bars."""
import os
import subprocess
from pathlib import Path

import pytest

from freetier_radar import git

# The author named outright: GIT_AUTHOR_NAME and the rest, wherever a shell
# or a hook sets them, outrank a repository's own config.
_AS = {**os.environ, "GIT_AUTHOR_NAME": "a reviewer", "GIT_AUTHOR_EMAIL": "t@example.com",
       "GIT_COMMITTER_NAME": "a reviewer", "GIT_COMMITTER_EMAIL": "t@example.com"}


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True, env=_AS)
    for text, subject in (("one\n", "chore: the first"), ("two\n", "fix: the second, with spaces")):
        (repo / "note.txt").write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True, env=_AS)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", subject], check=True, env=_AS)
    return repo


def test_a_range_lists_each_commit_once_with_the_field_asked_for(tmp_path: Path):
    """rev-list heads every formatted line with a "commit <sha>" line of its
    own; the list holds each commit once, the field whole, spaces and all."""
    repo = _repo(tmp_path)
    listed = git.commits(repo, "--reverse", "HEAD", field="%s")
    assert [subject for _, subject in listed] == ["chore: the first", "fix: the second, with spaces"]
    assert [sha for sha, _ in git.commits(repo, "HEAD~1..HEAD")] == [listed[1][0]]
    assert git.commits(repo, "HEAD", field="%an")[0][1] == "a reviewer"


def test_a_range_git_cannot_read_lists_nothing_or_raises_when_asked(tmp_path: Path):
    repo = _repo(tmp_path)
    assert git.commits(repo, f"{'0' * 40}..HEAD") == []
    with pytest.raises(subprocess.CalledProcessError):
        git.commits(repo, f"{'0' * 40}..HEAD", check=True)


def test_a_file_is_shown_as_a_commit_holds_it_and_none_where_it_has_none(tmp_path: Path):
    repo = _repo(tmp_path)
    assert git.show(repo, "HEAD~1", "note.txt") == "one\n"
    assert git.show(repo, "HEAD", "note.txt") == "two\n"
    assert git.show(repo, "HEAD", "missing.txt") is None
    assert git.show(repo, "0" * 40, "note.txt") is None
