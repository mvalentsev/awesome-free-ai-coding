import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from freetier_radar.history import (
    Event, EventType, append_history, diff_state, load_history, record_changes,
    registry_state, replay,
)
from freetier_radar.models import ARCHIVE_AFTER_DAYS, Entry, save_registry

TODAY = date(2026, 8, 14)
NOW = datetime(2026, 8, 14, 6, 30, tzinfo=timezone.utc)

BASE = {
    "name": "Example",
    "category": "api-free-tier",
    "url": "https://example.com",
    "offering": "free tokens",
    "first_seen": date(2026, 1, 1),
    "probe": {"type": "page-keywords", "endpoint": "https://example.com",
              "keywords": ["example-mini-2", "free"]},
}


def make(entry_id: str = "example", **kw) -> Entry:
    return Entry.model_validate({**BASE, "id": entry_id,
                                 "last_verified": kw.pop("last_verified", TODAY), **kw})


# ---- what the history remembers -------------------------------------------

def test_a_history_with_no_events_remembers_nothing():
    assert replay([]) == {}


def test_an_id_the_history_has_never_seen_is_an_addition():
    current = registry_state([make(offering="10 free calls a day")], TODAY)

    events = diff_state(replay([]), current, NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.ADDED, "example")]
    assert events[0].detail == "10 free calls a day"
    assert events[0].ts == NOW


def test_an_addition_already_recorded_is_not_reported_again():
    current = registry_state([make()], TODAY)
    first = diff_state(replay([]), current, NOW)

    again = diff_state(replay(first), current, NOW)

    assert again == []


# ---- entries leaving and coming back --------------------------------------

def test_an_entry_that_failed_three_probes_is_archived_once():
    live = [make()]
    recorded = replay(diff_state({}, registry_state(live, TODAY), NOW))

    dead = [make(probe_failures=3)]
    events = diff_state(recorded, registry_state(dead, TODAY), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.ARCHIVED, "example")]
    assert "3 failed probes" in events[0].detail


def test_an_archived_entry_names_a_vendor_announced_shutdown_as_the_reason():
    live = [make()]
    recorded = replay(diff_state({}, registry_state(live, TODAY), NOW))

    retired = [make(retired_on=TODAY)]
    events = diff_state(recorded, registry_state(retired, TODAY), NOW)

    assert "shutdown" in events[0].detail


def test_an_entry_archived_by_the_calendar_alone_is_still_reported():
    """No byte of the registry changes — the entry simply goes unverified past
    the staleness limit. A before/after diff of the file would see nothing."""
    entries = [make(last_verified=TODAY)]
    recorded = replay(diff_state({}, registry_state(entries, TODAY), NOW))

    later = TODAY + timedelta(days=ARCHIVE_AFTER_DAYS + 1)
    events = diff_state(recorded, registry_state(entries, later), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.ARCHIVED, "example")]
    assert "unverified" in events[0].detail


def test_an_entry_that_starts_passing_again_is_restored():
    recorded = replay(diff_state({}, registry_state([make(probe_failures=3)], TODAY), NOW))

    events = diff_state(recorded, registry_state([make(probe_failures=0)], TODAY), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.RESTORED, "example")]


def test_an_id_deleted_from_the_registry_is_removed():
    recorded = replay(diff_state({}, registry_state([make()], TODAY), NOW))

    events = diff_state(recorded, registry_state([], TODAY), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.REMOVED, "example")]
    assert events[0].name == "Example"


def test_a_removed_id_that_comes_back_is_an_addition_again():
    recorded = replay(diff_state({}, registry_state([make()], TODAY), NOW))
    recorded = replay(diff_state(recorded, registry_state([], TODAY), NOW))

    events = diff_state(recorded, registry_state([make()], TODAY), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.ADDED, "example")]


# ---- the free-model list ---------------------------------------------------

def test_a_changed_free_model_list_names_what_moved():
    before = [make(models=[{"family": "gpt-oss"}, {"family": "ling-3.0-flash"}])]
    recorded = replay(diff_state({}, registry_state(before, TODAY), NOW))

    after = [make(models=[{"family": "gpt-oss"}, {"family": "ling-3.0-tiny"}])]
    events = diff_state(recorded, registry_state(after, TODAY), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.MODELS, "example")]
    assert events[0].detail == "added ling-3.0-tiny; dropped ling-3.0-flash"
    assert events[0].models == ["gpt-oss", "ling-3.0-tiny"]


def test_reordering_the_free_model_list_is_not_an_event():
    before = [make(models=[{"family": "a"}, {"family": "b"}])]
    recorded = replay(diff_state({}, registry_state(before, TODAY), NOW))

    after = [make(models=[{"family": "b"}, {"family": "a"}])]

    assert diff_state(recorded, registry_state(after, TODAY), NOW) == []


def test_a_superseded_family_is_not_part_of_the_published_list():
    """The README hides superseded families, so the feed must not announce one
    arriving or leaving — that is a note to a reviewer, not a change to the offer."""
    before = [make(models=[{"family": "a"}])]
    recorded = replay(diff_state({}, registry_state(before, TODAY), NOW))

    after = [make(models=[{"family": "a"}, {"family": "b", "superseded_by": "c"}])]

    assert diff_state(recorded, registry_state(after, TODAY), NOW) == []


def test_the_model_list_of_an_archived_entry_is_not_announced():
    """An archived row renders as a name and a date; its model list is off the page."""
    recorded = replay(diff_state({}, registry_state(
        [make(probe_failures=3, models=[{"family": "a"}])], TODAY), NOW))

    after = [make(probe_failures=3, models=[{"family": "b"}])]

    assert diff_state(recorded, registry_state(after, TODAY), NOW) == []


# ---- the file --------------------------------------------------------------

def test_appending_leaves_the_lines_already_there_untouched(tmp_path: Path):
    path = tmp_path / "history.jsonl"
    first = Event(ts=NOW, event=EventType.ADDED, id="a", name="A")
    append_history(path, [first])
    original = path.read_text(encoding="utf-8")

    append_history(path, [Event(ts=NOW, event=EventType.ADDED, id="b", name="B")])

    assert path.read_text(encoding="utf-8").startswith(original)
    assert [e.id for e in load_history(path)] == ["a", "b"]


def test_a_missing_history_file_reads_as_no_events(tmp_path: Path):
    assert load_history(tmp_path / "nothing.jsonl") == []


def test_a_malformed_history_line_names_its_line_number(tmp_path: Path):
    path = tmp_path / "history.jsonl"
    append_history(path, [Event(ts=NOW, event=EventType.ADDED, id="a", name="A")])
    with path.open("a", encoding="utf-8") as fh:
        fh.write("{not json}\n")

    with pytest.raises(ValueError, match="line 2"):
        load_history(path)


def test_a_blank_line_is_not_a_malformed_event(tmp_path: Path):
    path = tmp_path / "history.jsonl"
    append_history(path, [Event(ts=NOW, event=EventType.ADDED, id="a", name="A")])
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n")

    assert [e.id for e in load_history(path)] == ["a"]


def test_an_event_is_one_line_of_json(tmp_path: Path):
    path = tmp_path / "history.jsonl"
    append_history(path, [Event(ts=NOW, event=EventType.ADDED, id="a", name="A",
                                url="https://a.example", models=["m"], detail="d")])

    line = json.loads(path.read_text(encoding="utf-8").strip())
    assert line["event"] == "added"
    assert line["ts"].startswith("2026-08-14T06:30:00")


# ---- the two callers -------------------------------------------------------

def test_recording_reads_the_registry_and_writes_only_what_changed(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    history = tmp_path / "history.jsonl"
    save_registry(registry, [make()])

    written = record_changes(registry, history, TODAY, NOW)
    assert [(e.event, e.id) for e in written] == [(EventType.ADDED, "example")]

    assert record_changes(registry, history, TODAY, NOW) == []
    assert len(load_history(history)) == 1
