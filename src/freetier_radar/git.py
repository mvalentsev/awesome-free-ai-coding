"""What git says about this repository's past: a file as a commit holds it,
and the commits a range lists. The gate, the IndexNow ping and the bars each
ask git these questions, and read the answers one way.

The commits come from `git rev-list`, not `git log`: the plumbing reads no
`log.*` setting of whoever runs it, so a `log.showSignature` in someone's
config cannot put a signature check between the lines.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

__all__ = ["run", "show", "commits"]


def run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """`git -C repo *args`, its output as text; the caller reads its return code."""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def show(repo: Path, rev: str, path: str) -> str | None:
    """A file as `rev` holds it — `rev` "" for the index — or None where git has
    no such commit or no such file there: a new branch's all-zero `before`, a
    clone too shallow to reach it, a file the commit deleted."""
    shown = run(repo, "show", f"{rev}:{path}")
    return shown.stdout if shown.returncode == 0 else None


def commits(repo: Path, *args: str, field: str = "", check: bool = False) -> list[tuple[str, str]]:
    """(sha, `field`) for each commit `git rev-list *args` lists, in its order —
    `field` one --format placeholder such as %ct, %an or %s, "" for the sha
    alone. A range git cannot read lists no commit, or raises with `check`."""
    listed = run(repo, "rev-list", f"--format=%H {field}".rstrip(), *args)
    if listed.returncode != 0:
        if check:
            raise subprocess.CalledProcessError(listed.returncode, listed.args,
                                                listed.stdout, listed.stderr)
        return []
    # rev-list heads each formatted line with a "commit <sha>" line of its own.
    return [(sha, rest) for sha, _, rest in (line.partition(" ")
                                             for line in listed.stdout.splitlines()
                                             if not line.startswith("commit "))]
