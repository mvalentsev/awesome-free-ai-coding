"""The gate is where the map's rules meet a commit: every check on the snapshot
about to be committed, the logs only ever appended to, the fields a probe
earns never typed, and a message git can show as a subject and a body."""
import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from freetier_radar.gate import (diff, earned_problems, log_problems, main, message_problems,
                                 pre_commit, snapshot_index)
from freetier_radar.history import Event, EventType
from freetier_radar.models import Entry, save_registry

BASE = {"name": "X", "category": "api-free-tier", "url": "https://x.ai", "offering": "stuff",
        "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["x-mini-2"]}}


def row(**kw) -> Entry:
    return Entry.model_validate({**BASE, "id": "x", "first_seen": date(2026, 9, 1),
                                 "last_verified": date(2026, 9, 21), **kw})


# ---- the logs

def test_a_log_is_only_ever_appended_to():
    assert log_problems("history.jsonl", "a\nb\n", "a\nb\nc\n") == []
    assert log_problems("history.jsonl", None, "a\n") == []
    assert log_problems("history.jsonl", "a\nb\n", "a\nB\nc\n") == [
        "history.jsonl rewrites line 2 of what is committed — it is append-only: restore the "
        "file and let its command append"]
    assert log_problems("history.jsonl", "a\nb\n", None) == [
        "history.jsonl is deleted — it is append-only and nothing regenerates it"]


def test_the_announcers_ledger_changes_on_main_only_on_the_scheduled_run():
    """announced.jsonl is what the announcer has posted; a line appended by hand
    would pass every consistency check there is and still be a post nobody sent."""
    assert log_problems("announced.jsonl", "a\n", "a\n", frozen=True) == []
    assert log_problems("announced.jsonl", "a\n", "a\nb\n", frozen=True) == [
        "announced.jsonl changes in a commit on main — freetier-announce writes it on the "
        "scheduled run and nowhere else"]


# ---- the fields a probe earns

def test_a_probe_earned_field_is_never_typed():
    before, after = [row()], [row(last_verified=date(2026, 9, 23), probe_failures=0)]
    assert earned_problems(before, after) == [
        "registry: x last_verified 2026-09-21 → 2026-09-23 — it is earned by the scheduled run "
        "(prober.apply_results); a commit made anywhere else leaves it as it is"]
    assert earned_problems([row(probe_failures=1)], [row()])[0].startswith(
        "registry: x probe_failures 1 → 0 —")
    assert earned_problems([row(provisional=True)], [row()])[0].startswith(
        "registry: x provisional True → False —")
    assert earned_problems([row()], [row(first_seen=date(2026, 9, 2))])[0].startswith(
        "registry: x first_seen 2026-09-01 → 2026-09-02 —")
    assert earned_problems([row()], [row(offering="new words")]) == []


def test_a_new_row_starts_provisional_on_the_day_it_is_added():
    fresh = row(id="y", first_seen=date(2026, 9, 23), last_verified=date(2026, 9, 23),
                provisional=True)
    assert earned_problems([row()], [row(), fresh]) == []
    assert earned_problems([row()], [row(), row(id="y", provisional=False)]) == [
        "registry: y is new and not provisional — a row enters on 🧪 and the run promotes it",
        "registry: y is new with first_seen 2026-09-01 and last_verified 2026-09-21 — a row "
        "enters with both on the day it is added"]


def test_a_row_the_base_holds_is_never_dropped():
    assert earned_problems([row(), row(id="y")], [row()]) == [
        "registry: y is gone — a row leaves the list through the Archive, never the file"]


# ---- the message

@pytest.mark.parametrize("text", [
    "fix: a subject\n", "feat: a subject\n\nA body.\n", "fix(tests): scoped\n",
    "Merge branch 'scout/weekly'\n", "fixup! fix: a subject\n",
    "chore: verification 2026-09-24\n# a comment git strips\n",
])
def test_a_message_git_can_show_passes(text):
    assert message_problems(text) == []


def test_a_subject_that_swallowed_the_body_is_refused():
    """ccac77a's subject ran on into its first paragraph: no blank line, and
    main refuses the force push that could have fixed it."""
    assert message_problems("feat: a subject\nthat runs on\n") == [
        "the second line of the message is not blank — git would read the paragraph as part "
        "of the subject"]


def test_a_subject_says_its_kind_in_lower_case():
    assert message_problems("Update things\n") == [
        "the subject does not start with a kind — `feat: …`, `fix: …`, `chore: …`, `docs: …`"]
    assert message_problems("\n\n") == ["the message is empty"]


# ---- the snapshot and the commit

def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True).stdout


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "announced.jsonl").write_text("a\n", encoding="utf-8")
    (repo / "note.txt").write_text("one\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: start")
    return repo


ADDED_AT = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
RENDERED_AT = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


def _line(event: str, entry_id: str, ts: datetime = RENDERED_AT, detail: str = "stuff") -> str:
    ev = Event(ts=ts, event=EventType(event), id=entry_id, name="X", url="https://x.ai",
               detail=detail)
    return json.dumps(ev.model_dump(mode="json"), ensure_ascii=False) + "\n"


def _history_repo(tmp_path: Path) -> Path:
    """A registry of one row, the line that recorded it, and the day the pages
    were rendered on — what a commit's lines are held to."""
    repo = _repo(tmp_path)
    save_registry(repo / "registry.yaml", [row()])
    (repo / "history.jsonl").write_text(_line("added", "x", ADDED_AT), encoding="utf-8")
    (repo / "index.json").write_text('{"generated": "2026-09-21"}\n', encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: the list")
    return repo


def _add_row(repo: Path, line: str | None) -> None:
    fresh = row(id="y", first_seen=date(2026, 9, 21), provisional=True)
    save_registry(repo / "registry.yaml", [row(), fresh])
    if line is not None:
        with (repo / "history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(line)
    _git(repo, "add", ".")


def test_a_commit_on_main_appends_the_lines_its_render_records(tmp_path):
    repo = _history_repo(tmp_path)
    _add_row(repo, _line("added", "y"))
    assert pre_commit(repo, steps=[]) == []


def test_a_history_line_no_render_wrote_is_refused(tmp_path):
    """Appending is what the render does on every commit now, so on main an
    appended line is held to the change it records: a line typed by hand,
    for a change the registry never made, is refused."""
    repo = _history_repo(tmp_path)
    with (repo / "history.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(_line("archived", "x", detail="gone"))
    _git(repo, "add", "history.jsonl")
    assert pre_commit(repo, steps=[]) == [
        "history.jsonl: line 1 of what the commit appends (archived x) is not a change this "
        "registry makes"]


def test_a_registry_change_the_commit_does_not_record_is_refused(tmp_path):
    repo = _history_repo(tmp_path)
    _add_row(repo, None)
    assert pre_commit(repo, steps=[]) == [
        "history.jsonl: the registry makes a change the commit does not record: added y"]


def test_each_commit_a_push_adds_is_held_to_its_own_lines(tmp_path):
    """CI and the pre-push hook read a push as a range, and a range hides which
    commit wrote a line: a registry change and its line one commit later read
    as right. Each commit is held to its own."""
    repo = _history_repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").strip()
    _add_row(repo, None)
    _git(repo, "commit", "-q", "-m", "feat: y")
    missing = _git(repo, "rev-parse", "--short", "HEAD").strip()
    (repo / "note.txt").write_text("two\n", encoding="utf-8")
    with (repo / "history.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(_line("added", "y"))
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "fix: the line")
    assert diff(repo, base, earned=False) == [
        f"{missing}: history.jsonl: the registry makes a change the commit does not record: "
        "added y"]


def test_the_snapshot_is_what_is_staged_not_what_is_on_disk(tmp_path):
    repo = _repo(tmp_path)
    (repo / "note.txt").write_text("staged\n", encoding="utf-8")
    _git(repo, "add", "note.txt")
    (repo / "note.txt").write_text("not staged\n", encoding="utf-8")
    (repo / "untracked.txt").write_text("x\n", encoding="utf-8")
    with snapshot_index(repo) as snap:
        assert (snap / "note.txt").read_text(encoding="utf-8") == "staged\n"
        assert not (snap / "untracked.txt").exists()


def test_the_scheduled_run_holds_what_it_is_about_to_commit_to_the_same_rule(tmp_path):
    """No hook runs on the runner: `freetier-gate diff HEAD` reads the working
    tree before the verification commit exists."""
    repo = _history_repo(tmp_path)
    _add_row(repo, _line("added", "y"))
    assert diff(repo, "HEAD", earned=False) == []
    _add_row(repo, _line("archived", "x", detail="gone"))
    assert diff(repo, "HEAD", earned=False) == [
        "history.jsonl: line 2 of what the commit appends (archived x) is not a change this "
        "registry makes"]


def test_a_push_is_checked_from_the_commit_its_owner_ratified(tmp_path, monkeypatch):
    """A rewrite the gate refuses to everyone — the log rebuilt from main's own
    history, a first_seen typed to the day a row really arrived — is made once,
    with the hooks off, by the repository's owner, and named in RATIFIED by the
    commit after it. A push or a CI run that meets it checks from it on; the
    commits after it are held as ever."""
    from freetier_radar import gate
    from freetier_radar.gate import pre_push

    repo = _history_repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").strip()
    (repo / "history.jsonl").write_text(_line("added", "x", RENDERED_AT), encoding="utf-8")
    save_registry(repo / "registry.yaml", [row(first_seen=date(2026, 9, 2))])
    _git(repo, "commit", "-qam", "fix: the log rebuilt")
    rebuilt = _git(repo, "rev-parse", "HEAD").strip()
    refused = diff(repo, base, earned=True)
    assert [p.split(" — ")[0] for p in refused] == [
        "history.jsonl rewrites line 1 of what is committed",
        "registry: x first_seen 2026-09-01 → 2026-09-02"]

    monkeypatch.setattr(gate, "RATIFIED", {rebuilt: "the log rebuilt from main's history"})
    assert diff(repo, base, earned=True) == []
    assert pre_push(repo, [f"refs/heads/main {rebuilt} refs/heads/main {base}"], steps=[]) == []

    with (repo / "history.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(_line("archived", "x", detail="gone"))
    _git(repo, "commit", "-qam", "fix: a line by hand")
    forged = _git(repo, "rev-parse", "HEAD").strip()
    assert diff(repo, base, earned=True) == [
        f"{forged[:7]}: history.jsonl: line 1 of what the commit appends (archived x) is not a "
        "change this registry makes"]
    assert pre_push(repo, [f"refs/heads/main {forged} refs/heads/main {base}"], steps=[]) == [
        f"{forged[:7]}: history.jsonl: line 1 of what the commit appends (archived x) is not a "
        "change this registry makes"]


def test_the_gate_refuses_a_commit_on_main_that_touches_the_announcers_ledger(tmp_path):
    repo = _repo(tmp_path)
    (repo / "announced.jsonl").write_text("A\n", encoding="utf-8")
    _git(repo, "add", "announced.jsonl")
    ran = []
    problems = pre_commit(repo, steps=[("a step", lambda snap: ran.append(snap) or "")])
    assert ran, "the checks run on the snapshot"
    assert problems == ["announced.jsonl changes in a commit on main — freetier-announce "
                        "writes it on the scheduled run and nowhere else"]


def test_the_gate_refuses_a_commit_that_rewrites_the_history(tmp_path):
    repo = _history_repo(tmp_path)
    (repo / "history.jsonl").write_text(_line("added", "x", ADDED_AT, detail="other words"),
                                        encoding="utf-8")
    _git(repo, "add", "history.jsonl")
    assert pre_commit(repo, steps=[]) == [
        "history.jsonl rewrites line 1 of what is committed — it is append-only: restore the "
        "file and let its command append"]


def test_the_gate_reports_a_check_that_fails_on_the_snapshot(tmp_path):
    repo = _repo(tmp_path)
    problems = pre_commit(repo, steps=[("freetier-check", lambda snap: "✗ something is off"),
                                       ("pytest", lambda snap: "")])
    assert problems == ["freetier-check failed on what is about to be committed:\n"
                        "✗ something is off"]


def test_the_commit_msg_hook_exits_non_zero_on_a_bad_message(tmp_path, capsys):
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text("fix: subject\nbody\n", encoding="utf-8")
    with pytest.raises(SystemExit) as refused:
        main(["commit-msg", str(message)])
    assert refused.value.code == 1
    assert "second line" in capsys.readouterr().out
    message.write_text("fix: subject\n\nbody\n", encoding="utf-8")
    main(["commit-msg", str(message)])


def test_each_check_fails_on_a_snapshot_it_should_refuse(tmp_path):
    """The first version called the render as `python -m freetier_radar.render`,
    which runs nothing in a module with no `__main__` guard and exits 0: a hand
    edit of the README passed the gate. Each step is run here on a copy of the
    repository with a hand-edited README, and the render's step has to say so."""
    import shutil
    from freetier_radar.gate import CHECKS
    from freetier_radar.layout import tracked_files
    root = Path(__file__).resolve().parent.parent
    snap = tmp_path / "snap"
    for f in tracked_files(root):
        (snap / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / f, snap / f)
    readme = snap / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8").replace("live offers", "live deals"),
                      encoding="utf-8")
    render = dict(CHECKS)["freetier-render --check"]
    assert "stale: README.md" in render(snap)
    check = dict(CHECKS)["freetier-check"]
    assert check(snap) == ""
