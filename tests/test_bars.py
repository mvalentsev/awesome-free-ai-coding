"""freetier-bars: when a model a lane has served free for two weeks earns its family."""
import os
import subprocess
from datetime import date
from pathlib import Path

import httpx
import respx
import yaml

from freetier_radar.bars import BAR_DAYS, arrivals, main, report, vendor_dates, waiting
from freetier_radar.models import save_registry

from test_prober import NGC_SEARCH, ngc_endpoint, ngc_search
from test_render import make as _make

TODAY = date(2026, 9, 24)


def make(**kw):
    """A row verified this week, so not archived (an archived row is owed
    nothing), whose free part is models unless the test says otherwise."""
    return _make(last_verified=kw.pop("last_verified", date(2026, 9, 21)),
                 free_part=kw.pop("free_part", "models"), **kw)
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
    """An id no family names, and no_family_ids does not excuse, is due BAR_DAYS
    after it arrived; one still inside the two weeks is waiting."""
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
    paste, and its column is empty on purpose. The same holds where the vendor
    names no model the free part reaches."""
    credit = make(id="credit", free_part="sum",
                  api={"base_url": "https://c.ai/v1", "model_ids": ["m-1"]})
    auto = make(id="auto", free_part="unnamed",
                api={"base_url": "https://a.ai/v1", "model_ids": ["m-3"]})
    lane = make(id="lane", probe=LANE, api={"base_url": "https://l.ai/v1", "model_ids": ["m-2"]})
    since = {("credit", "m-1"): date(2026, 8, 1), ("lane", "m-2"): date(2026, 8, 1),
             ("auto", "m-3"): date(2026, 8, 1)}
    assert [w.row for w in waiting([credit, auto, lane], since, TODAY)] == ["lane"]


def test_a_page_row_whose_free_part_is_models_owes_its_ids_a_family_too():
    """The row's `free_part` decides whether its ids are a free lane, not its probe
    or its column, so a page row with free models and an empty column is owed
    families too."""
    page = make(id="page", api={"base_url": "https://p.ai/v1", "model_ids": ["p-1"]})
    assert [(w.row, w.model_id) for w in waiting([page], {("page", "p-1"): date(2026, 8, 1)},
                                                 TODAY)] == [("page", "p-1")]


def test_an_earlier_record_of_a_free_id_brings_its_bar_forward():
    """A free_since record earlier than the id's arrival (a Wayback snapshot of the
    vendor's page) brings its bar forward and is named in the report; a later
    one moves nothing."""
    snap = "https://web.archive.org/web/20260914103442/https://x.ai/pricing"
    page = make(id="page", api={"base_url": "https://p.ai/v1", "model_ids": ["p-1", "p-2"],
                                "free_since": [{"id": "p-1", "on": "2026-09-14", "source": snap},
                                               {"id": "p-2", "on": "2026-09-30", "source": snap}]})
    since = {("page", "p-1"): date(2026, 9, 25), ("page", "p-2"): date(2026, 9, 25)}
    rows = waiting([page], since, TODAY)
    assert [(w.model_id, w.due_on) for w in rows] == [("p-1", date(2026, 9, 28)),
                                                      ("p-2", date(2026, 10, 9))]
    assert f"free on <{snap}> since 2026-09-14, in api.model_ids since 2026-09-25" in report(
        [page], since, TODAY)



def test_a_page_rows_newcomer_waits_two_weeks_from_its_record():
    """Each of a row's `newcomers`, a family with no id to date, waits two weeks
    from its own record, as an id does from its arrival."""
    snap = "https://web.archive.org/web/20260926080857/https://freebuff.com/"
    page = make(id="page", models=[{"family": "glm-5.3-flash"}],
                newcomers=[{"family": "solar-pro-4", "on": "2026-09-26", "source": snap},
                           {"family": "mimo-v2.6-flash", "on": "2026-09-08", "source": snap}])
    rows = waiting([page], {}, TODAY)
    assert [(w.model_id, w.due_on) for w in rows] == [("mimo-v2.6-flash", date(2026, 9, 22)),
                                                      ("solar-pro-4", date(2026, 10, 10))]
    text = report([page], {}, TODAY)
    assert f"page: `mimo-v2.6-flash`, free on <{snap}> since 2026-09-08 (16 days)" in text
    assert f"- 2026-10-10 page: `solar-pro-4`, free on <{snap}> since 2026-09-26" in text

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


NIM_CATALOG = "https://integrate.api.nvidia.com/v1/models"


def _nim(**api) -> object:
    """A catalog that prices nothing, read with the vendor's free list — the
    shape of the nvidia-nim row."""
    return make(id="nim", models=[{"family": "kimi-k3"}],
                probe={"type": "api-models", "endpoint": NIM_CATALOG,
                       "require_zero_price": True, "free_list": NGC_SEARCH},
                api={"base_url": "https://integrate.api.nvidia.com/v1",
                     "model_ids": ["moonshotai/kimi-k3", "z-ai/glm-5.3", "z-ai/glm-5.3-flash"],
                     **api})


def _answer(url: str, **body) -> httpx.Response:
    return httpx.Response(body.pop("status", 200), request=httpx.Request("GET", url), **body)


def test_the_vendor_s_date_for_a_free_id_brings_its_bar_forward():
    """The two weeks count from the read or from the vendor's own date for the free
    id, whichever is earlier: a vendor date after the read moves nothing, since the
    read already found the model free."""
    e = _gateway(model_ids=["v/big-1:free", "v/new-2:free", "v/old-3:free"])
    since = {("gw", "v/new-2:free"): date(2026, 9, 22), ("gw", "v/old-3:free"): date(2026, 9, 1)}
    vendor = {("gw", "v/new-2:free"): date(2026, 9, 15), ("gw", "v/old-3:free"): date(2026, 9, 5)}
    rows = waiting([e], since, TODAY, vendor)
    assert [(w.model_id, w.since, w.due_on) for w in rows] == [
        ("v/old-3:free", date(2026, 9, 1), date(2026, 9, 15)),
        ("v/new-2:free", date(2026, 9, 15), date(2026, 9, 29))]


def test_vendor_dates_are_read_off_the_free_list_each_live_row_names():
    """A free list is read once for each live row that names one: a row with no
    free list has no vendor date to read, and an archived row is owed nothing."""
    fetched = []

    def fetch(url: str) -> httpx.Response:
        fetched.append(url)
        return _answer(url, json=ngc_search(
            ngc_endpoint("z-ai", "glm-5-3", created="2026-09-15T19:47:58.961Z"),
            ngc_endpoint("moonshotai", "kimi-k3", created="2026-08-27T20:40:37.796Z")))

    gone = _nim().model_copy(update={"id": "gone", "retired_on": date(2026, 9, 1)})
    dates, notes = vendor_dates([_nim(), _gateway(model_ids=["v/new-2:free"]), gone], fetch, TODAY)
    assert dates == {("nim", "z-ai/glm-5.3"): date(2026, 9, 15),
                     ("nim", "moonshotai/kimi-k3"): date(2026, 8, 27)}
    assert notes == [] and fetched == [NGC_SEARCH]


def test_a_free_list_the_report_cannot_read_is_named_and_its_ids_keep_the_row_s_dates():
    """An unreadable free list is named in the report and its ids keep the row's
    own dates: left silent, it would read as a vendor that dates nothing."""
    def timed_out(url: str) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out", request=httpx.Request("GET", url))

    for fetch, why in ((timed_out, "ConnectTimeout"),
                       (lambda url: _answer(url, status=403, text="<html>Access denied</html>"),
                        "HTTP 403"),
                       (lambda url: _answer(url, text="<html>maintenance</html>"), "JSON")):
        dates, notes = vendor_dates([_nim()], fetch, TODAY)
        assert dates == {}
        assert len(notes) == 1 and notes[0].startswith("nim") and NGC_SEARCH in notes[0], notes
        assert why in notes[0], notes


def test_the_report_says_which_date_a_bar_counts_from_and_which_list_went_unread():
    e = _gateway(model_ids=["v/big-1:free", "v/new-2:free", "v/fresh-3:free"])
    since = {("gw", "v/new-2:free"): date(2026, 9, 22), ("gw", "v/fresh-3:free"): date(2026, 9, 23)}
    unread = f"nim: the free list at {NGC_SEARCH} could not be read"
    out = report([e], since, TODAY, {("gw", "v/new-2:free"): date(2026, 9, 15)}, [unread])
    vendor_line = next(line for line in out.splitlines() if "v/new-2:free" in line)
    assert vendor_line.startswith("- 2026-09-29 gw: ")
    assert "2026-09-15" in vendor_line and "2026-09-22" in vendor_line
    own_line = next(line for line in out.splitlines() if "v/fresh-3:free" in line)
    assert own_line.startswith("- 2026-10-07 gw: ") and "vendor" not in own_line
    assert unread in out


@respx.mock
def test_the_report_reads_the_vendor_s_free_list_itself(tmp_path, capsys):
    _git(tmp_path, "init", "-q")
    save_registry(tmp_path / "registry.yaml", [_nim()])
    _git(tmp_path, "add", "registry.yaml", day="2026-09-22")
    _git(tmp_path, "commit", "-q", "-m", "x", day="2026-09-22")
    respx.get(NGC_SEARCH).mock(return_value=httpx.Response(200, json=ngc_search(
        ngc_endpoint("moonshotai", "kimi-k3"),
        ngc_endpoint("z-ai", "glm-5-3", created="2026-09-15T19:47:58.961Z"),
        ngc_endpoint("z-ai", "glm-5-3-flash", created="2026-09-15T19:46:42.256Z"))))
    main(["--repo", str(tmp_path), "--today", "2026-09-25"])
    out = capsys.readouterr().out
    assert next(line for line in out.splitlines()
                if "`z-ai/glm-5.3`" in line).startswith("- 2026-09-29 nim: ")


def test_a_client_lane_is_dated_from_the_registry_s_history_too(tmp_path):
    """client_lane.model_ids are dated from the registry's history like
    api.model_ids: a lane served only inside the vendor's client has no api
    block."""
    _git(tmp_path, "init", "-q")
    for day, ids in (("2026-09-14", ["x-free/a-1"]), ("2026-09-23", ["x-free/a-1", "x-free/b-2"])):
        entries = [{"id": "cl", "client_lane": {"model_ids": ids}}]
        (tmp_path / "registry.yaml").write_text(yaml.safe_dump({"entries": entries}),
                                                encoding="utf-8")
        _git(tmp_path, "add", "registry.yaml", day=day)
        _git(tmp_path, "commit", "-q", "-m", day, day=day)
    assert arrivals(tmp_path) == {("cl", "x-free/a-1"): date(2026, 9, 14),
                                  ("cl", "x-free/b-2"): date(2026, 9, 23)}


def test_a_client_lane_s_ids_are_owed_a_family_as_an_api_s_are():
    e = make(id="cl", category="agent-cli", models=[{"family": "a-1"}],
             probe={"type": "api-models", "endpoint": "https://x.ai/lanes", "lane": "free"},
             client_lane={"model_ids": ["x-free/a-1", "x-free/b-2", "stealth/c"],
                          "no_family_ids": ["stealth/c"]})
    since = {("cl", "x-free/b-2"): date(2026, 9, 14)}
    assert [(w.row, w.model_id, w.due_on) for w in waiting([e], since, TODAY)] == [
        ("cl", "x-free/b-2", date(2026, 9, 28))]
    assert "`x-free/b-2`, in client_lane.model_ids since 2026-09-14" in report([e], since, TODAY)
