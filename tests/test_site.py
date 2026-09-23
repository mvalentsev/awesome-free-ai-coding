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
    """The command is written once (`_quickstart_curl`) and printed by both
    pages; until 2026-09-24 each wrote it out in full. A reader who copies it
    from either one sends the same prompt, the accuracy requirement included."""
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


def _render_everything(entries, tmp_path, watchlist=None, today=TODAY) -> dict[str, str]:
    """Every file the render writes, by path, rendered from one registry the way
    `freetier-render` renders the repository."""
    from freetier_radar.render import CONFIGS_README, render_artifacts, render_configs_readme
    tmp_path.mkdir(parents=True, exist_ok=True)
    registry = tmp_path / "registry.yaml"
    save_registry(registry, entries)
    if watchlist is not None:
        (tmp_path / "watchlist.yaml").write_text(yaml.safe_dump({"watched": watchlist}),
                                                 encoding="utf-8")
    render_readme(registry, TEMPLATES, tmp_path / "README.md", today=today)
    render_site(registry, TEMPLATES, tmp_path / SITE_PAGE, today=today)
    render_configs_readme(registry, TEMPLATES, tmp_path / CONFIGS_README, today=today)
    render_artifacts(registry, tmp_path, today=today)
    inputs = {registry, tmp_path / "watchlist.yaml"}
    return {p.relative_to(tmp_path).as_posix(): p.read_text(encoding="utf-8")
            for p in tmp_path.rglob("*") if p.is_file() and p not in inputs}


def test_the_readme_and_the_page_count_the_services_checked_alike(tmp_path):
    """Both pages link the same list of services checked and not listed, and
    that page counts every verdict on it, a verdict due for a fresh look
    included. The README counted them all and the site only the current ones,
    so from the day the oldest verdict aged past the recheck limit the two pages
    would have printed two numbers for one list."""
    current = {"domains": ["a.example"], "name": "A", "checked_on": "2026-07-01",
               "reason": "nothing free today", "reopen_if": "a free lane"}
    expired = {**current, "domains": ["b.example"], "name": "B", "checked_on": "2026-01-02"}
    pages = _render_everything([make()], tmp_path, watchlist=[current, expired])
    assert "**🔭 Checked and not listed** — 2 services" in pages["README.md"]
    assert "<b>2</b> services were checked and are not listed" in pages[SITE_PAGE]
    assert "\n2 services whose free tier" in pages["providers/checked.md"]


def test_the_shell_function_every_page_names_is_one_the_file_defines(tmp_path):
    """The site, the configs README and the file's own header told a reader to
    run `claude-openrouter-free` — typed by hand, so the day OpenRouter's row
    lost its Anthropic route or left the list, three pages would have named a
    function configs/claude-code.sh no longer defines."""
    entries = [make(id="gw-one", name="GwOne", category="aggregator",
                    api={"base_url": "https://one.example/v1",
                         "anthropic_base_url": "https://one.example", "model_ids": ["m"]})]
    pages = _render_everything(entries, tmp_path)
    assert "claude-gw-one() {" in pages["configs/claude-code.sh"]
    for path in ("configs/claude-code.sh", "configs/README.md", SITE_PAGE):
        assert "claude-gw-one" in pages[path].split("claude-gw-one() {")[0], path
    assert not [path for path, text in pages.items() if "claude-openrouter-free" in text]


@pytest.mark.parametrize("name, value, readme_says, site_says, unsaid", [
    ("FRONTIER_WITHIN", 12.0, "within 12 points", "within 12 points", "within 10 points"),
    ("PROVISIONAL_PROMOTE_DAYS", 21, "three weeks", "three weeks", "two weeks"),
    ("ARCHIVE_AFTER_FAILURES", 4, "fail ×4", "fails 4 probes", "fail ×3"),
    ("ARCHIVE_AFTER_DAYS", 45, "stale 45d", "goes 45\n          days", "stale 60d"),
    ("PROBE_WEEKDAYS", (1,), "once a week", "once a week", "twice a week"),
])
def test_every_page_states_the_rule_the_code_applies(tmp_path, monkeypatch, name, value,
                                                      readme_says, site_says, unsaid):
    """A rule the pages describe is a constant in the code, and a page that
    typed the constant's value kept describing the old rule after the code
    moved: the diagram's `fail ×3 · stale 60d`, the frontier bar's "within 10
    points", the provisional "two weeks" and "twice a week" in two dozen places.
    Each page reads the constant, so changing it changes every page."""
    import freetier_radar.render as render
    monkeypatch.setattr(render, name, value)
    entries = [
        make(id="a", name="A", provisional=True, models=[{"family": "big", "tier": "frontier",
                                                            "aa_model": "big"}],
             api={"base_url": "https://a.example/v1", "auth": "none", "model_ids": ["big"]}),
        make(id="b", name="B", category="agent-cli", models=[{"family": "big", "tier": "frontier",
                                                                "aa_model": "big"}]),
    ]
    pages = _render_everything(entries, tmp_path)
    assert readme_says in pages["README.md"]
    assert site_says in pages[SITE_PAGE]
    assert not [path for path, text in pages.items() if unsaid in text]


def test_a_row_that_needs_a_card_never_leads_the_no_card_rows_it_ties_with(tmp_path):
    """CONTRIBUTING's rule, which every sort ignored: on 2026-09-23 IBM
    watsonx.ai (card, rank 98) sat above Pollinations.AI (no card, rank 98)
    because the name broke the tie."""
    entries = [make(id="ibm", name="IBM", rank=98, card_required=True),
               make(id="poll", name="Pollinations", rank=98)]
    pages = _render_everything(entries, tmp_path)
    readme, site = pages["README.md"], pages[SITE_PAGE]
    assert readme.index("[Pollinations]") < readme.index("[IBM]")
    assert site.index(">Pollinations<") < site.index(">IBM<")
    assert pages["llms.txt"].index("[Pollinations]") < pages["llms.txt"].index("[IBM]")


def test_a_provisional_page_says_the_day_its_promotion_can_come(tmp_path):
    """"Two weeks of probes still to pass" was printed on every provisional
    page, twelve days into the fortnight as on the first."""
    from datetime import timedelta
    row = make(id="young", name="Young", provisional=True, first_seen=TODAY - timedelta(days=5))
    page = _render_everything([row], tmp_path)["providers/young.md"]
    promote = (TODAY - timedelta(days=5) + timedelta(days=14)).isoformat()
    assert f"the first probe it passes on or after {promote}" in page
    assert "still to pass" not in page


def test_the_frontier_bar_is_explained_only_where_a_frontier_line_is_shown(tmp_path):
    """With no free lane measured frontier the picks table has no Frontier line,
    and both pages went on explaining one."""
    plain = [make(id="a", name="A", category="api-free-tier")]
    pages = _render_everything(plain, tmp_path / "plain")
    assert "Frontier" not in pages["README.md"].split("## 📋")[0]
    assert "Frontier" not in pages[SITE_PAGE].split('id="plug"')[0]
    top = [make(id="b", name="B", models=[{"family": "big", "tier": "frontier", "aa_model": "big"}])]
    pages = _render_everything(top, tmp_path / "top")
    assert "within 10 points" in pages["README.md"] and "within 10 points" in pages[SITE_PAGE]


def test_a_keyed_lane_with_no_key_page_is_not_called_keyless(tmp_path):
    """The connection table printed "not needed" wherever a row named no key
    page, keyed or not."""
    keyed = make(id="k", name="Keyed", api={"base_url": "https://k.example/v1"})
    keyless = make(id="n", name="Keyless", api={"base_url": "https://n.example/v1", "auth": "none"})
    table = _render_everything([keyed, keyless], tmp_path)["configs/README.md"]
    keyed_row = next(line for line in table.splitlines() if line.startswith("| **[Keyed]"))
    keyless_row = next(line for line in table.splitlines() if line.startswith("| **[Keyless]"))
    assert "not needed" not in keyed_row
    assert keyless_row.endswith("| not needed |")
