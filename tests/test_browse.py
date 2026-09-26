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
                models=[{"family": "a", "tier": "frontier", "aa_model": "a"},
                        {"family": "b", "tier": "notable", "aa_model": "b"},
                        {"family": "old", "superseded_by": "a"}],
                api={"base_url": "https://x.ai/v1", "auth": "api-key", "openai_compatible": True,
                     "key_url": "https://x.ai/keys", "model_ids": ["a"],
                     "anthropic_base_url": "https://x.ai", "note": "n", "public_key": "k"},
                data_use={"trains": "no", "quote": "We never train on your prompts",
                          "url": "https://x.ai/privacy"})
    live, gone, folded = build_index(
        [full, make(id="gone", retired_on=TODAY),
         make(id="folded", url="https://folded.example", duplicate_of="gone",
              delisted={"on": TODAY, "reason": "the same service as the row before it"})],
        TODAY)["entries"]
    entry = live
    used = set(re.findall(r"\be\.([a-z_]+)\b", html))
    published = set(live) | set(gone) | set(folded)
    assert used and used <= published, used - published
    # an archived row says why it left instead of a date no probe earned
    assert "e.archived_because" in html
    api_used = set(re.findall(r"\be\.api\.([a-z_]+)\b", html))
    assert api_used and api_used <= set(entry["api"]), api_used - set(entry["api"])
    family_fields = {k for m in entry["models"] for k in m}
    family_used = set(re.findall(r"\bm\.([a-z_]+)\b", html))
    assert family_used and family_used <= family_fields, family_used - family_fields


def test_browse_page_filters_on_the_answers_a_reader_asks_for():
    html = _html()
    # category, card, key, both wires, the Models column and the archive
    for field in ("category", "card_required", "archived", "provisional", "page", "offering",
                  "data_use"):
        assert f"e.{field}" in html
    # a key the vendor prints for anyone answers "no account" as well as no key does
    for field in ("auth", "public_key", "openai_compatible", "anthropic_base_url", "base_url", "key_url"):
        assert f"e.api.{field}" in html
    assert "m.superseded_by" in html


def test_browse_page_leaves_a_folded_row_to_the_row_that_holds_the_service():
    """One service, one line — the same rule the README's Archive follows. A row
    folded into another (`duplicate_of`) is published in index.json, so a
    consumer can resolve the old id, and shown nowhere a reader counts offers."""
    html = _html()
    assert "e.duplicate_of" in html
    folded = make(id="mimocode", name="MiMoCode", url="https://mimocode.ai",
                  duplicate_of="mimo-code",
                  delisted={"on": TODAY, "reason": "the same project as MiMo Code"})
    row, = build_index([folded], TODAY)["entries"]
    assert row["duplicate_of"] == "mimo-code"


def test_browse_page_links_a_model_to_its_page_from_the_index():
    """A model name in the table links the model's own page, read from
    index.json's `models` — only the fields that list publishes."""
    html = _html()
    assert "data.models" in html
    used = set(re.findall(r"\bx\.([a-z_]+)\b", html))
    index = build_index([make(id="a", models=[{"family": "kimi-k3"}]),
                         make(id="b", models=[{"family": "kimi-k3"}])], TODAY)
    fields = {k for m in index["models"] for k in m}
    assert used == {"family", "page"} and used <= fields, used - fields


def test_browse_page_filters_on_tier_values_the_registry_has():
    """The strong chip keeps rows whose families measure strong or frontier,
    compared as strings in the browser — a tier renamed in the registry would
    leave the chip matching nothing, as a Frontier chip alone did the week no
    free model reached the frontier (2026-09-26). Every tier the page names is
    one the registry has; notable decides a model's page, not a strong mark."""
    from freetier_radar.models import Tier

    html = _html()
    named = set(re.findall(r'm\.tier === "([a-z]+)"', html))
    assert named <= {t.value for t in Tier}, named
    assert named == {Tier.FRONTIER.value, Tier.STRONG.value}, named


def test_browse_page_says_so_when_nothing_matches():
    html = _html()
    assert "No row matches all of these filters" in html
    # the Frontier chip is shown only while a live row carries a frontier family
    assert 'id="frontier-chip" hidden' in html
