from datetime import date, timedelta
from pathlib import Path

from freetier_radar.models import Entry
from freetier_radar.render import ARCHIVE_AFTER_DAYS, build_context, is_archived, render_readme

TODAY = date(2026, 7, 19)

BASE = {
    "name": "X",
    "category": "api-free-tier",
    "url": "https://x.ai",
    "offering": "stuff",
    "first_seen": date(2026, 1, 1),
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["free"]},
}


def make(**kw) -> Entry:
    d = {**BASE, "id": kw.pop("id", "x"), "last_verified": kw.pop("last_verified", TODAY), **kw}
    return Entry.model_validate(d)


def test_archive_rules():
    assert not is_archived(make(), TODAY)
    assert is_archived(make(probe_failures=3), TODAY)
    assert is_archived(make(last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1)), TODAY)
    assert not is_archived(make(last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS)), TODAY)
    superseded = make(models=[{"family": "old", "superseded_by": "new"}])
    assert is_archived(superseded, TODAY)
    mixed = make(models=[{"family": "old", "superseded_by": "new"}, {"family": "new"}])
    assert not is_archived(mixed, TODAY)


def test_build_context_rows():
    entries = [make(models=[{"family": "a"}, {"family": "b", "superseded_by": "c"}])]
    ctx = build_context(entries, TODAY)
    assert ctx["date"] == "2026-07-19"
    section = next(s for s in ctx["sections"] if s["title"].startswith("LLM APIs"))
    assert section["rows"][0]["models"] == "a"
    assert section["rows"][0]["card"] == "❌ No"
    assert ctx["archived"] == []


def test_render_readme(tmp_path: Path):
    reg = tmp_path / "registry.yaml"
    from freetier_radar.models import save_registry
    save_registry(reg, [make(), make(id="dead", name="Dead Tool", probe_failures=5)])
    out = tmp_path / "README.md"
    text = render_readme(reg, Path("templates"), out, today=TODAY)
    assert "last%20verified-2026-07-19" in text
    assert "### Coding agents & CLIs" in text
    assert "### LLM APIs with free tier" in text
    assert "Русский" not in text
    assert "## Archive" in text
    assert "Dead Tool" in text.split("## Archive")[1]
    assert out.read_text(encoding="utf-8") == text
