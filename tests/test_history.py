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


def test_a_row_its_probe_archived_says_when_it_last_passed():
    """The Archive shows this sentence in place of a date column, and the count
    alone leaves a reader guessing whether the offer died last week or in June."""
    live = [make()]
    recorded = replay(diff_state({}, registry_state(live, TODAY), NOW))

    dead = [make(probe_failures=3, last_verified=date(2026, 8, 3))]
    events = diff_state(recorded, registry_state(dead, TODAY), NOW)

    assert events[0].detail == "3 failed probes in a row, last passed 2026-08-03"


def test_a_delisted_row_says_the_day_and_the_reason_it_left():
    live = [make()]
    recorded = replay(diff_state({}, registry_state(live, TODAY), NOW))

    delisted = [make(delisted={"on": TODAY, "reason": "the free lane is gone"})]
    events = diff_state(recorded, registry_state(delisted, TODAY), NOW)

    assert [(e.event, e.id) for e in events] == [(EventType.ARCHIVED, "example")]
    assert events[0].detail == "delisted on 2026-08-14: the free lane is gone"


def test_a_row_deleted_before_rows_were_archived_joins_the_archive_without_a_second_event():
    """Until 2026-09-17 a reviewer took a row off by deleting it, and the history
    said so as "removed". Those rows are back in the registry as delisted — the
    Archive now holds them — and their departure was announced the day it
    happened, so bringing them back must not announce it again."""
    added = diff_state({}, registry_state([make()], TODAY), NOW)
    removed = diff_state(replay(added), {}, NOW)
    assert [e.event for e in removed] == [EventType.REMOVED]

    restored = registry_state([make(delisted={"on": TODAY, "reason": "no free lane"})], TODAY)
    assert diff_state(replay(added + removed), restored, NOW) == []


def test_a_row_deleted_from_the_registry_is_refused_rather_than_recorded(tmp_path: Path):
    """A row leaves the list through the Archive and nowhere else. The run that
    finds one deleted stops before the history can call it "delisted", so the
    deletion can never be published — only undone."""
    registry, history = tmp_path / "registry.yaml", tmp_path / "history.jsonl"
    save_registry(registry, [make(), make("second")])
    record_changes(registry, history, TODAY, NOW)
    save_registry(registry, [make()])

    with pytest.raises(ValueError, match="second"):
        record_changes(registry, history, TODAY, NOW)
    assert [e.id for e in load_history(history)] == ["example", "second"]


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
    """An archived row renders as a name and why it left; its model list is off the page."""
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


# ---- recorded by the render of every change --------------------------------

LATER = NOW + timedelta(minutes=9)


def test_a_render_records_against_the_log_the_last_commit_left(tmp_path: Path):
    """The render writes the lines the commit it belongs to will carry, so a
    render run twice before a commit — a row added, then swapped for another —
    leaves one block, and nothing about the row that never reached the list."""
    registry, history = tmp_path / "registry.yaml", tmp_path / "history.jsonl"
    save_registry(registry, [make()])
    record_changes(registry, history, TODAY, NOW)
    committed = history.read_text(encoding="utf-8")

    save_registry(registry, [make(), make("draft")])
    record_changes(registry, history, TODAY, NOW + timedelta(minutes=5), committed=committed)
    save_registry(registry, [make(), make("kept")])
    written = record_changes(registry, history, TODAY, LATER, committed=committed)

    assert [(e.event, e.id, e.ts) for e in written] == [(EventType.ADDED, "kept", LATER)]
    assert history.read_text(encoding="utf-8").startswith(committed)
    assert [(e.id, e.ts) for e in load_history(history)] == [("example", NOW), ("kept", LATER)]


def test_a_render_with_nothing_new_leaves_its_block_as_it_was(tmp_path: Path):
    """Rendering again changes no byte: the run renders twice, and a check
    between the two must not find the log moved on its clock alone."""
    registry, history = tmp_path / "registry.yaml", tmp_path / "history.jsonl"
    save_registry(registry, [make()])
    record_changes(registry, history, TODAY, NOW, committed="")
    first = history.read_bytes()

    written = record_changes(registry, history, TODAY, LATER, committed="")

    assert history.read_bytes() == first
    assert [(e.id, e.ts) for e in written] == [("example", NOW)]


def test_the_lines_a_commit_appends_are_the_changes_its_registry_makes():
    """What the gate holds a commit's lines to: exactly the block its render
    records — nothing typed by hand, nothing left out, one render's clock."""
    from freetier_radar.history import block_problems

    base = diff_state({}, registry_state([make()], TODAY), NOW)
    entries = [make(), make("second")]
    block = [Event(ts=LATER, event=EventType.ADDED, id="second", name="Example",
                   url="https://example.com", detail="free tokens")]
    assert block_problems(base, block, entries, TODAY, now=LATER) == []

    forged = block + [Event(ts=LATER, event=EventType.ARCHIVED, id="example",
                            name="Example", url="https://example.com")]
    assert block_problems(base, forged, entries, TODAY, now=LATER) == [
        "line 2 of what the commit appends (archived example) is not a change this "
        "registry makes"]
    assert block_problems(base, [], entries, TODAY, now=LATER) == [
        "the registry makes a change the commit does not record: added second"]
    two_clocks = [block[0], Event(ts=NOW, event=EventType.ARCHIVED, id="example",
                                  name="Example", url="https://example.com")]
    assert block_problems(base, two_clocks, entries, TODAY, now=LATER)[0] == (
        "the commit appends lines with 2 timestamps — one render records a commit's "
        "changes at one time")
    assert block_problems(base, block, entries, TODAY, now=NOW) == [
        "the commit appends lines dated 2026-08-14T06:39:00+00:00, after the commit itself"]


# ---- the two callers -------------------------------------------------------

def test_recording_reads_the_registry_and_writes_only_what_changed(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    history = tmp_path / "history.jsonl"
    save_registry(registry, [make()])

    written = record_changes(registry, history, TODAY, NOW)
    assert [(e.event, e.id) for e in written] == [(EventType.ADDED, "example")]

    assert record_changes(registry, history, TODAY, NOW) == []
    assert len(load_history(history)) == 1
