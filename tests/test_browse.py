"""browse.html is a static page that reads index.json in the browser, so the
only contract between them is the field names — checked here against what
build_index actually publishes, so a renamed field cannot leave the page
silently showing nothing."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

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
                access={"initial_payment_usd": 1, "source": "https://x.ai/pricing"},
                models=[{"family": "a", "tier": "frontier", "aa_model": "a"},
                        {"family": "b", "tier": "notable", "aa_model": "b"},
                        {"family": "old", "superseded_by": "a"}],
                api={"base_url": "https://x.ai/v1", "auth": "api-key", "openai_compatible": True,
                     "key_url": "https://x.ai/keys", "model_ids": ["a"],
                     "anthropic_base_url": "https://x.ai", "note": "n", "public_key": "k"},
                data_use={"trains": "no", "quote": "We never train on your prompts",
                          "url": "https://x.ai/privacy"},
                border={"left_out": ["RU"], "on": TODAY, "source": "https://x.ai/terms"})
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
    from freetier_radar.models import Border
    border_used = set(re.findall(r"\be\.border\.([a-z_]+)\b", html))
    assert border_used and border_used <= set(Border.model_fields), border_used - set(Border.model_fields)
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
    """The strong chip compares tiers as strings in the browser, so a tier
    renamed in the registry would leave it matching nothing. Every tier the
    page names is one the registry has; notable decides a model's page, not a
    strong mark."""
    from freetier_radar.models import Tier

    html = _html()
    named = set(re.findall(r'm\.tier === "([a-z]+)"', html))
    assert named <= {t.value for t in Tier}, named
    assert named == {Tier.FRONTIER.value, Tier.STRONG.value}, named


def test_a_name_a_date_or_an_address_never_breaks_inside_a_word_and_a_phone_gets_cards():
    """A model name or a date is one word to a reader, and an address breaks
    after a slash; a phone gets a card per row instead of a table wider than
    its screen."""
    html = _html()
    assert "break-all" not in html
    assert ".fam, .nowrap { white-space: nowrap; }" in html
    assert 'el("span", "fam")' in html and 'el("span", "nowrap", e.last_verified)' in html
    assert 'el("wbr")' in html and "address(e.api.base_url)" in html
    phone = html[html.index("@media (max-width: 760px)"):]
    assert "thead { display: none; }" in phone and "td[data-label]::before" in phone


def test_browse_page_says_so_when_nothing_matches():
    html = _html()
    assert "No row matches all of these filters" in html
    # the Frontier chip is shown only while a live row carries a frontier family
    assert 'id="frontier-chip" hidden' in html


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node to run the page's script")
def test_browse_page_finds_a_model_written_the_way_its_vendor_writes_it():
    """The site's search and the 404 page send a model name here as a reader
    writes it: "nemotron 3 ultra" finds a row that lists nemotron-3-ultra. The
    page's own functions run on a row index.json publishes."""
    from test_site import _js_function

    html = _html()
    row = build_index([make(offering="A free lane",
                            models=[{"family": "nemotron-3-ultra"}, {"family": "qwen3-8b"}])],
                      TODAY)["entries"][0]
    harness = "\n".join(_js_function(html, n) for n in ("families", "haystack", "written")) + f"""
    var e = {json.dumps(row)};
    function finds(q) {{ return haystack(e).indexOf(written(q.trim().toLowerCase())) !== -1; }}
    console.log(JSON.stringify(["Nemotron 3 Ultra", "nemotron-3-ultra", "a free lane",
                                "qwen 3.8", "qwen3 8b"].map(finds)));"""
    run = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout) == [True, True, True, False, True]


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node to run the page's script")
def test_browse_page_keeps_to_the_offers_that_reach_where_the_reader_is():
    """Where a reader is comes from the countries index.json names; a row
    stays when its allow-list names the country or its deny-list does not, and
    a row with no border answers anywhere."""
    from test_site import _js_function

    html = _html()
    assert 'id="where"' in html and 'params.get("where")' in html
    allow = build_index([make(border={"served": ["US", "CA"], "on": TODAY,
                                      "source": "https://x.ai/regions"})], TODAY)["entries"][0]
    deny = build_index([make(border={"left_out": ["RU", "CN"], "on": TODAY,
                                     "source": "https://x.ai/terms"})], TODAY)["entries"][0]
    harness = _js_function(html, "reaches") + f"""
    var allow = {json.dumps(allow)}, deny = {json.dumps(deny)}, none = {{}};
    console.log(JSON.stringify([reaches(allow, "US"), reaches(allow, "RU"), reaches(deny, "RU"),
                                reaches(deny, "DE"), reaches(none, "RU"), reaches(allow, "")]));"""
    run = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout) == [True, False, False, True, True, True]


def test_the_index_names_every_country_a_border_can_name():
    """The picker offers every country and territory the borders are recorded
    in, under the name a reader looks for — not "the United Arab Emirates"
    filed under T."""
    from freetier_radar.countries import COUNTRIES
    countries = build_index([make()], TODAY)["countries"]
    assert [c["code"] for c in countries if c["code"] in COUNTRIES] == [c["code"] for c in countries]
    assert {c["code"] for c in countries} == set(COUNTRIES)
    names = {c["code"]: c["name"] for c in countries}
    assert names["AE"] == "United Arab Emirates" and names["RU"] == "Russia"
    from freetier_radar.render import _country_key
    keys = [_country_key(c["name"]) for c in countries]
    assert keys == sorted(keys)
    order = [c["code"] for c in countries]
    assert order.index("AX") < order.index("AL") and order.index("CN") < order.index("CO")
