"""index.html is the page the site serves at its root, rendered from the
registry by the same command as the README. What these tests hold it to is the
reason it exists: a vendor's sentence arrives as text and never as markup, the
figures are the registry's own, and nothing on it was typed by hand."""
import json
import re

import yaml
from datetime import date
from pathlib import Path

import pytest

from freetier_radar.models import Category, save_registry
from freetier_radar.render import (
    SITE_NAV_LABELS, SITE_PAGE, build_site_context, render_readme, render_site,
)
from test_render import TODAY, make

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def _render(entries, tmp_path, today=TODAY) -> str:
    registry = tmp_path / "registry.yaml"
    save_registry(registry, entries)
    return render_site(registry, TEMPLATES, tmp_path / SITE_PAGE, today=today)


def test_every_category_has_a_nav_label():
    """The bar is one line, so it carries short names — and a category without
    one would raise at render time, on the scheduled run, with the page half
    written."""
    assert set(SITE_NAV_LABELS) == set(Category)


def test_the_page_is_html_and_says_what_it_is(tmp_path):
    html = _render([make(models=[{"family": "a"}])], tmp_path)
    assert html.startswith("<!doctype html>")
    assert '<link rel="canonical" href="https://mvalentsev.github.io/awesome-free-ai-coding/">' in html
    assert 'lang="en"' in html
    assert 'name="viewport"' in html
    assert "prefers-color-scheme" in html
    # Self-contained: a page that fetched a script or a stylesheet would be one
    # more thing that can rot between two probe runs.
    assert not re.search(r'<script\b[^>]*\bsrc=', html), "no external scripts"
    assert not re.search(r'<link\b[^>]*rel="stylesheet"', html), "no external styles"


def test_structured_data_is_valid_json_and_cannot_close_its_own_script(tmp_path):
    html = _render([make()], tmp_path)
    block = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    graph = json.loads(block.group(1))
    assert "\\u003c" not in json.dumps(graph), "escaping is the serialiser's, not the data's"
    assert "<" not in block.group(1)
    types = {node["@type"] for node in graph["@graph"]}
    assert types == {"WebSite", "Dataset"}


def test_a_vendors_sentence_arrives_as_text(tmp_path):
    """The one thing this page must never do. Every string on it is copied out
    of the registry, where a vendor's own wording lives."""
    nasty = make(name="X <script>alert(1)</script>",
                 offering='free "quota" <b>&</b> more',
                 limits="1 < 2 & 3 > 2")
    html = _render([nasty], tmp_path)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "free &#34;quota&#34; &lt;b&gt;&amp;&lt;/b&gt; more" in html


def test_the_figures_are_the_registrys_own(tmp_path):
    entries = [
        make(id="a", name="A", models=[{"family": "m1"}],
             api={"base_url": "https://a.ai/v1", "auth": "none", "model_ids": ["m1"]}),
        make(id="b", name="B", card_required=True, models=[{"family": "m2"}]),
        make(id="gone", name="Gone", retired_on=TODAY),
    ]
    context = build_site_context(entries, TODAY)
    assert (context["active_count"], context["no_card_count"], context["card_count"]) == (2, 1, 1)
    assert (context["no_signup_count"], context["endpoint_count"]) == (1, 1)
    assert context["family_count"] == 2
    assert [r["name"] for r in context["archived"]] == ["Gone"]
    html = _render(entries, tmp_path)
    assert "<b>2</b><span>live offers</span>" in html
    # the archived row is in the Archive and in no section table
    assert html.count(">Gone<") == 1


def test_a_long_cell_folds_and_keeps_every_character(tmp_path):
    """The README folds with <details> too; here the teaser and the text are
    data, so the page can carry the whole of a 1,200-character quote without
    becoming a wall."""
    limits = "word " * 120
    html = _render([make(limits=limits.strip())], tmp_path)
    assert "<details><summary>" in html
    assert limits.strip() in html
    short = _render([make(id="s", limits="two words")], tmp_path)
    assert "two words" in short


def test_the_page_carries_the_answers_browse_html_filters_on(tmp_path):
    html = _render([
        make(id="keyless", name="Keyless",
             api={"base_url": "https://k.ai/v1", "auth": "none", "model_ids": ["m"]}),
        make(id="carded", name="Carded", card_required=True),
        make(id="fresh", name="Fresh", provisional=True),
        make(id="front", name="Front", models=[{"family": "big", "tier": "frontier"}]),
        make(id="anthropic", name="Anthropic",
             api={"base_url": "https://c.ai/v1", "anthropic_base_url": "https://c.ai"}),
    ], tmp_path)
    for tag in ("no key", "💳 card", "🧪 new", "frontier", "Claude Code"):
        assert tag in html, tag


def test_a_key_the_vendor_prints_for_anyone_is_shown_where_the_row_is_read(tmp_path):
    """The site's rows and its connection table answer "can I use it without an
    account" as the README does: a lane the vendor prints a key for needs none,
    and the key is on the page with the vendor's page it comes from."""
    html = _render([make(id="trial", name="Trial", api={
        "base_url": "https://api.trial.example/v1", "key_url": "https://trial.example/docs",
        "model_ids": ["qwen-27b"], "public_key": "lt-trial-abc"})], tmp_path)
    assert '<span class="tag nokey">no account</span>' in html
    assert "<code>lt-trial-abc</code>" in html
    assert 'href="https://trial.example/docs"' in html


def test_a_notice_is_shown_where_the_row_is_read(tmp_path):
    html = _render([make(
        api={"base_url": "https://x.ai/v1", "auth": "none", "model_ids": ["m"],
             "notice": {"since": "2026-09-17", "text": "the lane answers 403",
                        "url": "https://example.test/issue"}})], tmp_path)
    assert "Does not work as published" in html
    assert "the lane answers 403" in html
    assert 'href="https://example.test/issue"' in html


def test_the_quickstart_command_survives_both_places_it_is_printed(tmp_path):
    """It is printed in a <pre> and in the copy button's attribute, and it
    carries both quote characters — assembled in the template, the first of them
    would have closed the attribute."""
    html = _render([make(api={"base_url": "https://x.ai/v1/", "auth": "none",
                              "model_ids": ["m-free"]})], tmp_path)
    assert "curl -s https://x.ai/v1/chat/completions" in html
    button = re.search(r'<button class="copy"[^>]*data-copy="([^"]*)"', html)
    assert "&#34;model&#34;:&#34;m-free&#34;" in button.group(1)
    assert "&#39;Content-Type: application/json&#39;" in button.group(1)


def test_the_readme_and_the_page_ask_the_quickstart_lane_the_same_question(tmp_path):
    """The README template and `_site_quickstart` each write the command out in
    full, so its question is typed in two places. A reader who copies it from
    either one has to send the same prompt, the accuracy requirement included."""
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [make(api={"base_url": "https://x.ai/v1/", "auth": "none",
                                       "model_ids": ["m-free"]})])
    readme = render_readme(registry, TEMPLATES, tmp_path / "README.md", today=TODAY)
    html = render_site(registry, TEMPLATES, tmp_path / SITE_PAGE, today=TODAY)
    assert '"content":"2+2? MAKE NO MISTAKES."' in readme
    assert "&#34;content&#34;:&#34;2+2? MAKE NO MISTAKES.&#34;" in html


def test_the_readme_and_the_page_are_rendered_from_one_registry(tmp_path):
    """Both are committed, both are compared with the registry by --check, and
    the numbers a reader is shown have to agree between them."""
    entries = [make(id="a", name="A"), make(id="b", name="B", card_required=True)]
    registry = tmp_path / "registry.yaml"
    save_registry(registry, entries)
    readme = render_readme(registry, TEMPLATES, tmp_path / "README.md", today=TODAY)
    html = render_site(registry, TEMPLATES, tmp_path / SITE_PAGE, today=TODAY)
    for name in ("A", "B"):
        assert name in readme and name in html
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/" in readme


@pytest.mark.parametrize("path", ["browse.html", "llms.txt", "index.json"])
def test_the_page_links_the_files_beside_it(tmp_path, path):
    html = _render([make()], tmp_path)
    assert f'href="{path}"' in html


def test_the_committed_page_is_what_the_committed_registry_renders(tmp_path):
    """The same contract as the README's: what is served is what the registry
    says today. `freetier-render --check` enforces it in CI; this catches it
    before the push, and renders into a temporary directory so a test run never
    touches a tracked file."""
    root = Path(__file__).resolve().parent.parent
    committed = (root / SITE_PAGE).read_text(encoding="utf-8")
    generated = date.fromisoformat(json.loads(
        (root / "index.json").read_text(encoding="utf-8"))["generated"])
    fresh = render_site(root / "registry.yaml", TEMPLATES, tmp_path / SITE_PAGE, today=generated)
    assert fresh == committed


def test_jekyll_leaves_every_markdown_written_for_github_off_the_site():
    """kramdown does not read Markdown inside a block-level <div>, does not know
    GitHub's alert syntax and escapes a <summary> it meets inside a table cell:
    the root README was served half-rendered until _config.yml excluded it, and
    configs/README.md is written for GitHub's renderer the same way."""
    config = yaml.safe_load((TEMPLATES.parent / "_config.yml").read_text(encoding="utf-8"))
    assert "README.md" in config["exclude"]
    assert "configs/README.md" in config["exclude"]


def test_a_card_cell_breaks_a_token_with_no_space_in_it():
    """On a phone the tables become cards whose cells no longer scroll, so a
    note carrying `ANTHROPIC_BASE_URL=https://tokenhub.tencentmaas.com` ran 74
    px past its card and the whole page moved sideways at 390 px (found
    2026-09-22)."""
    css = (TEMPLATES / "index.html.j2").read_text(encoding="utf-8")
    phone = css[css.index("@media (max-width: 760px)"):]
    phone = phone[:phone.index("\n}\n")]
    rule = re.search(r"^\s*table\.rows th, table\.rows td \{[^}]*\}", phone, re.M).group(0)
    assert "overflow-wrap: anywhere" in rule
