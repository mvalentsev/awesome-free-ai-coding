"""browse.html is a static page that reads index.json in the browser, so the
only contract between them is the field names — checked here against what
build_index actually publishes, so a renamed field cannot leave the page
silently showing nothing."""
import re
from pathlib import Path

from freetier_radar.render import build_index
from test_render import TODAY, make

PAGE = Path(__file__).resolve().parent.parent / "browse.html"


def _html() -> str:
    return PAGE.read_text(encoding="utf-8")


def test_browse_page_is_self_contained_and_reads_index_json_beside_itself():
    html = _html()
    assert 'fetch("index.json"' in html
    assert not re.search(r'<script\b[^>]*\bsrc=', html), "no external scripts"
    assert not re.search(r'<link\b[^>]*rel="stylesheet"', html), "no external styles"
    assert "prefers-color-scheme" in html
    assert 'name="viewport"' in html


def test_browse_page_reads_only_fields_index_json_publishes():
    html = _html()
    full = make(card_required=True, provisional=True,
                models=[{"family": "a", "tier": "frontier", "released": "2026-01"},
                        {"family": "old", "superseded_by": "a"}],
                api={"base_url": "https://x.ai/v1", "auth": "api-key", "openai_compatible": True,
                     "key_url": "https://x.ai/keys", "model_ids": ["a"],
                     "anthropic_base_url": "https://x.ai", "note": "n"})
    entry = build_index([full], TODAY)["entries"][0]
    used = set(re.findall(r"\be\.([a-z_]+)\b", html))
    assert used and used <= set(entry), used - set(entry)
    api_used = set(re.findall(r"\be\.api\.([a-z_]+)\b", html))
    assert api_used and api_used <= set(entry["api"]), api_used - set(entry["api"])
    family_fields = {k for m in entry["models"] for k in m}
    family_used = set(re.findall(r"\bm\.([a-z_]+)\b", html))
    assert family_used and family_used <= family_fields, family_used - family_fields


def test_browse_page_filters_on_the_answers_a_reader_asks_for():
    html = _html()
    # category, card, key, both wires, the Models column and the archive
    for field in ("category", "card_required", "archived", "provisional", "page", "offering"):
        assert f"e.{field}" in html
    for field in ("auth", "openai_compatible", "anthropic_base_url", "base_url", "key_url"):
        assert f"e.api.{field}" in html
    assert "m.superseded_by" in html
