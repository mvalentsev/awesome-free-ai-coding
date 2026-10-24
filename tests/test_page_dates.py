"""Modification dates follow page content, independently of probe provenance."""
from datetime import date
import os
from pathlib import Path
import subprocess

import pytest
import yaml

from freetier_radar.page_dates import PageDates, content_hash


def page(day="2026-10-21", body="Limit: 10 requests/day", modified="2026-10-20"):
    return (f"---\ntitle: A free API\nlast_modified_at: {modified}\n---\n"
            f"# Provider\n\n{body}\n\nLast probe: 2026-10-20\n"
            f"Generated from `registry.yaml` on {day}. Rechecked twice a week.\n")


def fields(text):
    return yaml.safe_load(text.split("---\n")[1])


def write(root, text):
    path = root / "providers/a.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_a_new_page_gets_its_publication_date_and_verification_stays_untouched(tmp_path):
    result = PageDates(tmp_path, date(2026, 10, 21)).stamp("providers/a.md", page())
    assert fields(result)["last_modified_at"] == date(2026, 10, 21)
    assert "Last probe: 2026-10-20" in result


def test_daily_rerender_and_new_empty_state_fallback_do_not_freshen_content(tmp_path):
    first = PageDates(tmp_path, date(2026, 10, 21)).stamp("providers/a.md", page())
    write(tmp_path, first)
    second = PageDates(tmp_path, date(2026, 10, 24)).stamp(
        "providers/a.md", page(day="2026-10-24", modified="2026-10-24"))
    assert fields(second)["last_modified_at"] == date(2026, 10, 21)
    assert content_hash(second) == content_hash(first)


@pytest.mark.parametrize("change", ["limit", "source", "description", "deadline"])
def test_every_substantive_correction_advances_date_without_a_history_event(tmp_path, change):
    first = PageDates(tmp_path, date(2026, 10, 21)).stamp("providers/a.md", page())
    write(tmp_path, first)
    current = {
        "limit": page(body="Limit: 20 requests/day"),
        "source": page(body="Limit: 10 requests/day\nSource: https://vendor.example/pricing"),
        "description": page().replace("title: A free API", "title: A free coding API"),
        "deadline": page(body="Limit: 10 requests/day\nOffer ends 2026-11-01"),
    }[change]
    result = PageDates(tmp_path, date(2026, 10, 24)).stamp("providers/a.md", current)
    assert fields(result)["last_modified_at"] == date(2026, 10, 24)
    assert content_hash(result) != content_hash(first)
    assert "Last probe: 2026-10-20" in result


def test_source_archive_preserves_a_stamped_page_without_git(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    stamped = PageDates(original, date(2026, 10, 21)).stamp("providers/a.md", page())
    archive = tmp_path / "archive"
    write(archive, stamped)
    result = PageDates(archive, date(2026, 10, 24)).stamp("providers/a.md", page(day="2026-10-24"))
    assert fields(result)["last_modified_at"] == date(2026, 10, 21)


def test_legacy_migration_finds_real_correction_and_ignores_daily_commits(tmp_path):
    def git(*args, day=None):
        env = dict(os.environ)
        if day:
            env.update(GIT_AUTHOR_DATE=f"2026-10-{day}T12:00:00+00:00",
                       GIT_COMMITTER_DATE=f"2026-10-{day}T12:00:00+00:00")
        return subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test",
                               "-c", "user.email=test@example.com", *args],
                              env=env, check=True, capture_output=True, text=True)
    git("init")
    for day, limit in (("21", 10), ("22", 10), ("23", 20), ("24", 20)):
        write(tmp_path, page(day=f"2026-10-{day}", body=f"Limit: {limit} requests/day"))
        git("add", "providers/a.md")
        git("commit", "-m", "test: publish page", day=day)
    result = PageDates(tmp_path, date(2026, 10, 24)).stamp(
        "providers/a.md", page(day="2026-10-24", body="Limit: 20 requests/day"))
    assert fields(result)["last_modified_at"] == date(2026, 10, 23)
    write(tmp_path, result)
    assert PageDates(tmp_path, date(2026, 10, 24)).stamp(
        "providers/a.md", page(day="2026-10-24", body="Limit: 20 requests/day")) == result
    # A shallow clone cannot establish the change date from its last daily
    # commit. Keep the existing date, then reconcile when full history arrives.
    shallow = tmp_path / "shallow"
    git("clone", "--depth=1", "--no-local", str(tmp_path), str(shallow))
    limited = PageDates(shallow, date(2026, 10, 24)).stamp(
        "providers/a.md", page(day="2026-10-24", body="Limit: 20 requests/day"))
    assert fields(limited)["last_modified_at"] == date(2026, 10, 20)
    write(shallow, limited)
    subprocess.run(["git", "-C", str(shallow), "fetch", "--unshallow"], check=True,
                   capture_output=True)
    reconciled = PageDates(shallow, date(2026, 10, 24)).stamp(
        "providers/a.md", page(day="2026-10-24", body="Limit: 20 requests/day"))
    assert fields(reconciled)["last_modified_at"] == date(2026, 10, 23)
