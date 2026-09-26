"""The gate a commit passes: the map's rules, run on what is about to be
committed, before it is.

CI ran every check on every push, and a push to main is a push that has
already happened: a watchlist commit that left the pages' count one behind
(b1c7f4b) was red in CI and on main until the next commit fixed it, and a
subject that swallowed its paragraph (ccac77a) stays in main's history for
good, since main refuses a force push. So the same checks run before the
commit exists, from git's own hooks (`git config core.hooksPath .githooks`):

- `pre-commit` exports the index — what is staged, not what is on disk — and
  runs freetier-check, `freetier-render --check` and the test suite on it, with
  the dates in UTC, the way the scheduled run reads them. Then it holds the
  commit to what only a command may write: history.jsonl grows by exactly the
  lines the render records for the commit's own registry, the announcer's
  ledger changes on main on the scheduled run and nowhere else, no log is
  rewritten, and the fields a probe earns (`last_verified`, `probe_failures`,
  `provisional`, `first_seen`) are never typed — a new row enters provisional,
  dated the day it is added. And no page the site has published is deleted:
  a provider's or a model's address stays, and its page says what became of
  its subject.
- `commit-msg` refuses a subject with no kind and a body with no blank line
  before it.
- `pre-push` runs the same checks on the commit being pushed, and the log and
  earned-field rules over every commit the push adds, one by one, so a
  `--no-verify` commit does not reach main unchecked.

`freetier-gate diff BASE` is the rules between BASE and the working tree for
the places no hook runs: CI (against the push's parent, and on a pull request
with the earned fields too) and the scheduled run before its own commit.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Iterator

import yaml

from .history import block_problems, parse_history
from .layout import MAP, Kind, node_for
from .models import Entry

__all__ = ["log_problems", "earned_problems", "message_problems", "history_problems", "page_problems",
           "snapshot_index", "log_base", "committed_log", "pre_commit", "diff", "main"]

LOGS = tuple(n.path for n in MAP if n.kind is Kind.LOG)
LOG_WRITERS = {n.path: n.written_by for n in MAP if n.kind is Kind.LOG}
# The log the render writes, with every commit that changes the list; every
# other log is written on the scheduled run alone.
RECORDED = tuple(n.path for n in MAP if n.kind is Kind.LOG and "freetier-render" in n.written_by)

# Written by the scheduled run's probe (prober.apply_results) and by nothing
# else: the day a row last passed, the failures since, and whether it is still
# on its first fortnight — plus the day it arrived, which its promotion and its
# page count from.
EARNED = ("first_seen", "last_verified", "probe_failures", "provisional")

# Commits that rewrote a log or typed an earned field on purpose, each with why.
# The gate refuses such a commit to everyone, so it is made once, with the hooks
# off, by the repository's owner, and named here by the commit after it; a push
# or a CI run that meets one checks the logs and the earned fields from it on.
RATIFIED: dict[str, str] = {
    "4fb0103149211db8f93503d5c15b8ce530ce77e1":
        "history.jsonl rebuilt from main's first-parent registry history, every change dated "
        "by the commit that made it, where the scheduled run had dated it up to four days "
        "late; sixteen first_seen days set to the UTC day of the commit that added the row",
}

_KIND = re.compile(r"^(?:[a-z]+(?:\([a-z0-9-]+\))?: \S|Merge |Revert \"|fixup! |squash! |amend! )")


# ---- the rules, on text and entries

def log_problems(name: str, before: str | None, after: str | None,
                 frozen: bool = False) -> list[str]:
    """What a commit does to an append-only log. `frozen`: the commit is made
    on main by hand, where the log changes on the scheduled run alone."""
    if before == after:
        return []
    if frozen:
        writers = LOG_WRITERS.get(name, ("its command",))
        verb = "writes" if len(writers) == 1 else "write"
        return [f"{name} changes in a commit on main — {' and '.join(writers)} {verb} it on "
                "the scheduled run and nowhere else"]
    if after is None:
        return [f"{name} is deleted — it is append-only and nothing regenerates it"]
    if before is None or after.startswith(before):
        return []
    old, new = before.splitlines(), after.splitlines()
    line = next((i for i, (a, b) in enumerate(zip(old, new), start=1) if a != b),
                min(len(old), len(new)) + 1)
    return [f"{name} rewrites line {line} of what is committed — it is append-only: restore "
            "the file and let its command append"]


def history_problems(before: str | None, after: str | None, registry: str | None,
                     index: str | None, now: datetime) -> list[str]:
    """What a commit appends to history.jsonl, held to what its render records:
    the changes its registry makes against the log it found, on the day its
    pages were rendered (index.json's `generated`), at one time no later than
    the commit itself. A rewrite or a deletion is `log_problems`' to report."""
    if registry is None or after is None or not after.startswith(before or ""):
        return []
    found = before or ""
    try:
        base = parse_history(found)
        block = parse_history(after[len(found):], first_line=found.count("\n") + 1)
        day = date.fromisoformat(json.loads(index)["generated"]) if index else now.date()
    except (ValueError, KeyError, TypeError) as exc:
        return [f"history.jsonl: {exc}"]
    return [f"history.jsonl: {p}"
            for p in block_problems(base, block, _registry(registry), day, now)]


def earned_problems(before: list[Entry], after: list[Entry]) -> list[str]:
    """What a commit made by hand does to the fields only the run writes."""
    problems = []
    old = {e.id: e for e in before}
    for e in after:
        was = old.get(e.id)
        if was is None:
            if not e.provisional:
                problems.append(f"registry: {e.id} is new and not provisional — a row enters "
                                "on 🧪 and the run promotes it")
            if e.first_seen != e.last_verified or e.probe_failures:
                problems.append(f"registry: {e.id} is new with first_seen {e.first_seen} and "
                                f"last_verified {e.last_verified} — a row enters with both on "
                                "the day it is added")
            continue
        for field in EARNED:
            a, b = getattr(was, field), getattr(e, field)
            if a != b:
                problems.append(f"registry: {e.id} {field} {a} → {b} — it is earned by the "
                                "scheduled run (prober.apply_results); a commit made anywhere "
                                "else leaves it as it is")
    held = {e.id for e in after}
    problems += [f"registry: {i} is gone — a row leaves the list through the Archive, never the "
                 "file" for i in old if i not in held]
    return problems


def page_problems(before: set[str], after: set[str]) -> list[str]:
    """What a commit does to the pages the site has published (layout.Node.kept):
    it may add them and never take one away. The render keeps every page it
    published and says on it what became of its row or its model, so a page
    that leaves the tree is one somebody deleted — and an address a search
    engine indexed, or an answer cited, that would now answer 404."""
    return [f"{path} is deleted — the site published this page, and a published page stays: "
            "the render keeps it and says on it what became of its row or model; restore it"
            for path in sorted(before - after)]


def _kept(paths) -> set[str]:
    return {p for p in paths if (node := node_for(p)) is not None and node.kept}


def message_problems(text: str) -> list[str]:
    lines = [line for line in text.splitlines() if not line.startswith("#")]
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines or not lines[0].strip():
        return ["the message is empty"]
    problems = []
    if not _KIND.match(lines[0]):
        problems.append("the subject does not start with a kind — `feat: …`, `fix: …`, "
                        "`chore: …`, `docs: …`")
    if len(lines) > 1 and lines[1].strip():
        problems.append("the second line of the message is not blank — git would read the "
                        "paragraph as part of the subject")
    return problems


# ---- git

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _show(repo: Path, rev: str, path: str) -> str | None:
    """A file as `rev` holds it — `rev` "" for the index — or None where it has none."""
    shown = _git(repo, "show", f"{rev}:{path}")
    return shown.stdout if shown.returncode == 0 else None


def _registry(text: str | None) -> list[Entry]:
    if text is None:
        return []
    return [Entry.model_validate(e) for e in (yaml.safe_load(text) or {}).get("entries", [])]


def _pages_at(repo: Path, rev: str) -> set[str]:
    """The published pages a commit holds; none for a revision that does not exist yet."""
    return _kept(_git(repo, "ls-tree", "-r", "--name-only", rev).stdout.splitlines())


def _pages_staged(repo: Path) -> set[str]:
    return _kept(_git(repo, "ls-files").stdout.splitlines())


def _pages_on_disk(repo: Path) -> set[str]:
    return _kept(p.relative_to(repo).as_posix() for n in MAP if n.kept for p in repo.glob(n.path))


def _branch(repo: Path) -> str:
    return _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip()


def _merging(repo: Path) -> list[str]:
    """The other parents of the commit being made, when it is a merge."""
    git_dir = Path(_git(repo, "rev-parse", "--absolute-git-dir").stdout.strip())
    head = git_dir / "MERGE_HEAD"
    return head.read_text(encoding="utf-8").split() if head.is_file() else []


def log_base(repo: Path) -> str:
    """The commit whose logs the next commit is held to: HEAD on main and in a
    merge; on any other branch the commit it left main at, since what a branch
    appended may be written again — fixing a scout PR records the scout's
    lines anew, as one block against main."""
    if _branch(repo) == "main" or _merging(repo):
        return "HEAD"
    return _git(repo, "merge-base", "HEAD", "origin/main").stdout.strip() or "HEAD"


def committed_log(path: Path) -> str | None:
    """The log at `path` as the next commit will find it — what the render
    records against — or None outside a git work tree, where there is nothing
    to find it in and the render appends to the file as it stands."""
    where = path.resolve().parent
    top = _git(where, "rev-parse", "--show-toplevel")
    if top.returncode:
        return None
    repo = Path(top.stdout.strip())
    if _git(repo, "rev-parse", "--verify", "--quiet", "HEAD").returncode:
        return ""
    rel = path.resolve().relative_to(repo.resolve()).as_posix()
    return _show(repo, log_base(repo), rel) or ""


@contextlib.contextmanager
def snapshot_index(repo: Path) -> Iterator[Path]:
    """The index exported to a directory of its own: what the commit will hold,
    not the working tree, and nothing untracked."""
    with tempfile.TemporaryDirectory(prefix="freetier-gate-") as tmp:
        exported = _git(repo, "checkout-index", "--all", f"--prefix={tmp}/")
        if exported.returncode:
            raise SystemExit(f"could not export the index: {exported.stderr.strip()}")
        yield Path(tmp)


@contextlib.contextmanager
def snapshot_commit(repo: Path, rev: str) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="freetier-gate-") as tmp:
        archive = subprocess.run(["git", "-C", str(repo), "archive", rev], capture_output=True)
        if archive.returncode:
            raise SystemExit(f"could not read {rev}: {archive.stderr.decode().strip()}")
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True)
        yield Path(tmp)


# ---- the checks, run on a snapshot

def _run(snap: Path, *argv: str) -> str:
    """Run a command of the package on the snapshot's own code, the way CI runs
    it; its output when it fails, "" when it passes."""
    env = {**os.environ, "TZ": "UTC", "PYTHONPATH": str(snap / "src"),
           "PYTHONDONTWRITEBYTECODE": "1"}
    done = subprocess.run([sys.executable, *argv], cwd=snap, env=env, capture_output=True,
                          text=True)
    return "" if done.returncode == 0 else (done.stdout + done.stderr).strip()


def _command(module: str, *args: str) -> tuple[str, ...]:
    """A command of the package called through its `main` — not `python -m`,
    which runs nothing in a module without a `__main__` guard and exits 0, the
    way an unchecked render passed the first version of this gate."""
    call = (f"import sys; from freetier_radar.{module} import main; "
            f"sys.argv = {['freetier', *args]!r}; main()")
    return ("-c", call)


Step = tuple[str, Callable[[Path], str]]
CHECKS: list[Step] = [
    ("freetier-check", lambda snap: _run(snap, *_command("validate", "--root", "."))),
    ("freetier-render --check", lambda snap: _run(snap, *_command("render", "--check"))),
    ("pytest", lambda snap: _run(snap, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x")),
]


def _run_steps(snap: Path, steps: list[Step]) -> list[str]:
    problems = []
    for name, step in steps:
        out = step(snap)
        if out:
            tail = "\n".join(out.splitlines()[-40:])
            problems.append(f"{name} failed on what is about to be committed:\n{tail}")
    return problems


def pre_commit(repo: Path, steps: list[Step] | None = None) -> list[str]:
    steps = CHECKS if steps is None else steps
    with snapshot_index(repo) as snap:
        problems = _run_steps(snap, steps)
    merging = _merging(repo)
    on_main = _branch(repo) == "main" and not merging
    problems += page_problems(_pages_at(repo, "HEAD"), _pages_staged(repo))
    fork = log_base(repo)
    for name in LOGS:
        staged = _show(repo, "", name)
        for parent in [fork, *merging]:
            problems += log_problems(name, _show(repo, parent, name), staged,
                                     frozen=on_main and name not in RECORDED)
    if not merging:
        for name in RECORDED:
            problems += history_problems(_show(repo, fork, name), _show(repo, "", name),
                                         _show(repo, "", "registry.yaml"),
                                         _show(repo, "", "index.json"),
                                         datetime.now(timezone.utc))
        problems += earned_problems(_registry(_show(repo, "HEAD", "registry.yaml")),
                                    _registry(_show(repo, "", "registry.yaml")))
    return problems


def _history_by_commit(repo: Path, base: str, local: str) -> list[str]:
    """The history rule for each commit from `base` to `local` along main's
    line, against the log its parent left and at the time it was made: a range
    read whole would take a registry change and its line one commit later for
    a commit that recorded what it changed."""
    problems = []
    listed = _git(repo, "rev-list", "--reverse", "--first-parent", "--format=%H %ct",
                  f"{base}..{local}").stdout.splitlines()
    for line in listed:
        if line.startswith("commit "):
            continue
        sha, _, stamp = line.partition(" ")
        made = datetime.fromtimestamp(int(stamp), timezone.utc)
        for name in RECORDED:
            problems += [f"{sha[:7]}: {p}" for p in history_problems(
                _show(repo, f"{sha}^", name), _show(repo, sha, name),
                _show(repo, sha, "registry.yaml"), _show(repo, sha, "index.json"), made)]
    return problems


def _checked_from(repo: Path, base: str, local: str) -> str:
    """`base`, or the newest commit RATIFIED names on main's line from it to
    `local`."""
    listed = _git(repo, "rev-list", "--first-parent", f"{base}..{local}").stdout.split()
    return next((sha for sha in listed if sha in RATIFIED), base)


def diff(repo: Path, base: str, earned: bool) -> list[str]:
    """The log rules — and with `earned` the earned fields — between `base` and
    the working tree: for CI, and for the scheduled run before it commits."""
    base = _checked_from(repo, base, "HEAD")
    problems = page_problems(_pages_at(repo, base), _pages_on_disk(repo))
    for name in LOGS:
        now = (repo / name).read_text(encoding="utf-8") if (repo / name).is_file() else None
        problems += log_problems(name, _show(repo, base, name), now)
    problems += _history_by_commit(repo, base, "HEAD")

    def on_disk(name: str) -> str | None:
        return (repo / name).read_text(encoding="utf-8") if (repo / name).is_file() else None
    # The working tree, where the scheduled run checks what it is about to
    # commit; a tree that is HEAD's own was read with HEAD's commit above.
    for name in RECORDED:
        if all(on_disk(n) == _show(repo, "HEAD", n) for n in (name, "registry.yaml", "index.json")):
            continue
        problems += history_problems(_show(repo, "HEAD", name), on_disk(name),
                                     on_disk("registry.yaml"), on_disk("index.json"),
                                     datetime.now(timezone.utc))
    if earned:
        registry = repo / "registry.yaml"
        problems += earned_problems(_registry(_show(repo, base, "registry.yaml")),
                                    _registry(registry.read_text(encoding="utf-8")))
    return problems


_ZERO = "0" * 40


def pre_push(repo: Path, lines: list[str], steps: list[Step] | None = None) -> list[str]:
    """git feeds the hook `<local ref> <local sha> <remote ref> <remote sha>`, a
    line per ref pushed."""
    steps = CHECKS if steps is None else steps
    problems = []
    for line in lines:
        parts = line.split()
        if len(parts) != 4 or parts[1] == _ZERO:
            continue
        local, remote = parts[1], parts[3]
        if remote == _ZERO:
            base = _git(repo, "merge-base", local, "origin/main").stdout.strip() or None
        else:
            base = remote
        with snapshot_commit(repo, local) as snap:
            problems += _run_steps(snap, steps)
        if base is None:
            continue
        base = _checked_from(repo, base, local)
        problems += page_problems(_pages_at(repo, base), _pages_at(repo, local))
        for name in LOGS:
            problems += log_problems(name, _show(repo, base, name), _show(repo, local, name))
        problems += _history_by_commit(repo, base, local)
        problems += _earned_by_commit(repo, base, local)
    return problems


def _earned_by_commit(repo: Path, base: str, local: str) -> list[str]:
    """The earned-field rule for each commit the push adds that the scheduled
    run did not make — its own verification commits are where those fields are
    written."""
    problems = []
    listed = _git(repo, "rev-list", "--reverse", "--no-merges", "--format=%H %an",
                  f"{base}..{local}").stdout.splitlines()
    for line in listed:
        if line.startswith("commit "):
            continue
        sha, _, author = line.partition(" ")
        if author == "freetier-bot":
            continue
        problems += [f"{sha[:7]}: {p}" for p in earned_problems(
            _registry(_show(repo, f"{sha}^", "registry.yaml")),
            _registry(_show(repo, sha, "registry.yaml")))]
    return problems


def _report(problems: list[str], what: str) -> None:
    if not problems:
        print(f"freetier-gate: {what} — every check passed")
        return
    for p in problems:
        print(f"✗ {p}")
    print(f"freetier-gate: {what} refused — {len(problems)} problem(s). The map of what "
          "depends on what is `uv run freetier-map` and CONTRIBUTING's \"What depends on what\".")
    raise SystemExit(1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="The checks a commit passes before it exists (see CONTRIBUTING).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("pre-commit", help="check what is staged")
    msg = sub.add_parser("commit-msg", help="check a commit message file")
    msg.add_argument("file", type=Path)
    sub.add_parser("pre-push", help="check what a push adds (reads git's refs on stdin)")
    between = sub.add_parser("diff", help="the log rules between BASE and the working tree")
    between.add_argument("base")
    between.add_argument("--earned", action="store_true",
                         help="the earned-field rules too (a pull request)")
    args = parser.parse_args(argv)
    repo = Path(_git(Path("."), "rev-parse", "--show-toplevel").stdout.strip() or ".")
    if args.command == "pre-commit":
        _report(pre_commit(repo), "commit")
    elif args.command == "commit-msg":
        _report(message_problems(args.file.read_text(encoding="utf-8")), "message")
    elif args.command == "pre-push":
        _report(pre_push(repo, sys.stdin.read().splitlines()), "push")
    else:
        _report(diff(repo, args.base, args.earned), f"changes since {args.base}")


if __name__ == "__main__":
    main(sys.argv[1:])
