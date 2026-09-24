"""freetier-bars: when a model a lane has served free for two weeks earns its family."""
import os
import subprocess
from datetime import date
from pathlib import Path

import yaml

from freetier_radar.bars import BAR_DAYS, arrivals, main, waiting
from freetier_radar.models import save_registry

from test_render import make as _make

TODAY = date(2026, 9, 24)


def make(**kw):
    """A row verified this week: one verified 60 days ago is archived, and an
    archived row is owed nothing."""
    return _make(last_verified=kw.pop("last_verified", date(2026, 9, 21)), **kw)
LANE = {"type": "api-models", "endpoint": "https://x.ai/v1/models", "free_marker": ":free",
        "require_zero_price": True}


def _git(repo: Path, *args: str, day: str | None = None) -> None:
    env = dict(os.environ)
    if day:
        env.update(GIT_AUTHOR_DATE=f"{day}T12:00:00Z", GIT_COMMITTER_DATE=f"{day}T12:00:00Z")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.hooksPath=/dev/null",
                    *args], cwd=repo, check=True, env=env, capture_output=True)


def _commit(repo: Path, rows: dict[str, list[str]], day: str) -> None:
    """One committed registry.yaml whose rows carry these ids, dated `day`."""
    entries = [{"id": rid, "api": {"model_ids": ids}} for rid, ids in rows.items()]
    (repo / "registry.yaml").write_text(yaml.safe_dump({"entries": entries}), encoding="utf-8")
    _git(repo, "add", "registry.yaml", day=day)
    _git(repo, "commit", "-q", "-m", day, day=day)


def test_an_id_is_dated_from_the_commit_after_which_it_never_left(tmp_path):
    """The registry's history is the record of when each id was read in a lane:
    an id is added on the read that finds it and taken out when the run says it
    left. So the bar counts from the last time it came in."""
    _git(tmp_path, "init", "-q")
    _commit(tmp_path, {"gw": ["a"]}, "2026-08-01")
    _commit(tmp_path, {"gw": ["a", "b"]}, "2026-08-05")
    _commit(tmp_path, {"gw": ["b"]}, "2026-08-10")
    _commit(tmp_path, {"gw": ["a", "b"], "other": ["b"]}, "2026-08-20")
    since = arrivals(tmp_path)
    assert since[("gw", "a")] == date(2026, 8, 20)
    assert since[("gw", "b")] == date(2026, 8, 5)
    assert since[("other", "b")] == date(2026, 8, 20)


def _gateway(**api) -> object:
    return make(id="gw", category="aggregator", models=[{"family": "big-1"}], probe=LANE,
                api={"base_url": "https://x.ai/v1", **api})


def test_an_id_no_family_names_is_due_two_weeks_after_it_arrived():
    """OpenRouter served north-mini-code free from July while its column named
    two families: the dates lived in a maintainer's notes, and the ids that
    came before the notes were never dated at all."""
    e = _gateway(model_ids=["v/big-1:free", "v/new-2:free", "v/router", "v/fresh-3:free"],
                 no_family_ids=["v/router"])
    since = {("gw", "v/big-1:free"): date(2026, 8, 1), ("gw", "v/new-2:free"): date(2026, 9, 1),
             ("gw", "v/router"): date(2026, 8, 1), ("gw", "v/fresh-3:free"): date(2026, 9, 20)}
    rows = waiting([e], since, TODAY)
    assert [(w.row, w.model_id, w.due_on) for w in rows] == [
        ("gw", "v/new-2:free", date(2026, 9, 15)), ("gw", "v/fresh-3:free", date(2026, 10, 4))]
    assert [w.due_on <= TODAY for w in rows] == [True, False]
    assert BAR_DAYS == 14


def test_an_id_the_history_has_not_seen_arrives_today():
    rows = waiting([_gateway(model_ids=["v/big-1:free", "v/new-2:free"])], {}, TODAY)
    assert [(w.model_id, w.since) for w in rows] == [("v/new-2:free", TODAY)]


def test_a_row_whose_ids_are_not_a_free_lane_has_no_bars():
    """A credit or an allowance names no free model: its ids are examples to
    paste, and its column is empty on purpose."""
    credit = make(id="credit", api={"base_url": "https://c.ai/v1", "model_ids": ["m-1"]})
    lane = make(id="lane", probe=LANE, api={"base_url": "https://l.ai/v1", "model_ids": ["m-2"]})
    since = {("credit", "m-1"): date(2026, 8, 1), ("lane", "m-2"): date(2026, 8, 1)}
    assert [w.row for w in waiting([credit, lane], since, TODAY)] == ["lane"]


def test_an_archived_row_has_no_bars():
    gone = make(id="gone", models=[{"family": "big-1"}], probe=LANE, retired_on=date(2026, 9, 1),
                api={"base_url": "https://x.ai/v1", "model_ids": ["v/new-2:free"]})
    assert waiting([gone], {("gone", "v/new-2:free"): date(2026, 8, 1)}, TODAY) == []


def test_the_report_names_what_is_due_and_when_the_rest_falls_due(tmp_path, capsys):
    _git(tmp_path, "init", "-q")
    save_registry(tmp_path / "registry.yaml",
                  [_gateway(model_ids=["v/big-1:free", "v/new-2:free"])])
    _git(tmp_path, "add", "registry.yaml", day="2026-09-01")
    _git(tmp_path, "commit", "-q", "-m", "x", day="2026-09-01")
    main(["--repo", str(tmp_path), "--today", "2026-09-24"])
    out = capsys.readouterr().out
    assert "gw: `v/new-2:free`, in api.model_ids since 2026-09-01" in out
    assert "Due" in out.split("v/new-2:free")[0]
