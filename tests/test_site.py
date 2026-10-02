"""index.html is the page the site serves at its root, rendered from the
registry by the same command as the README. What these tests hold it to is the
reason it exists: a vendor's sentence arrives as text and never as markup, the
figures are the registry's own, and nothing on it was typed by hand."""
import json
import re
import shutil
import subprocess

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
    """Every string on the page is copied out of the registry, where a vendor's
    own wording lives, and reaches the reader as text, never as markup."""
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
    pages, so a reader who copies it from either one sends the same prompt, the
    accuracy requirement included."""
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
    GitHub's alert syntax and escapes a <summary> it meets inside a table cell,
    so the README and configs/README.md, written for GitHub's renderer, stay
    off the site (_config.yml's exclude)."""
    config = yaml.safe_load((TEMPLATES.parent / "_config.yml").read_text(encoding="utf-8"))
    assert "README.md" in config["exclude"]
    assert "configs/README.md" in config["exclude"]


def test_a_card_cell_breaks_a_token_with_no_space_in_it():
    """On a phone the tables become cards whose cells do not scroll, so a token
    with no space in it, such as a URL in a note, has to break or it pushes the
    whole page sideways."""
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
    count every verdict on it as that page does, a verdict due for a fresh look
    included, so the two never print two numbers for one list."""
    current = {"domains": ["a.example"], "name": "A", "checked_on": "2026-07-01",
               "reason": "nothing free today", "reopen_if": "a free lane"}
    expired = {**current, "domains": ["b.example"], "name": "B", "checked_on": "2026-01-02"}
    pages = _render_everything([make()], tmp_path, watchlist=[current, expired])
    assert "**🔭 Checked and not listed** — 2 services" in pages["README.md"]
    assert "<b>2</b> services were checked and are not listed" in pages[SITE_PAGE]
    assert "\n2 services whose free tier" in pages["providers/checked.md"]


def test_the_shell_function_every_page_names_is_one_the_file_defines(tmp_path):
    """The site, the configs README and the file's own header name a shell
    function read off configs/claude-code.sh, never a typed one, so no page
    names a function the file no longer defines."""
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
    ("STRONG_WITHIN", 30.0, "within 30 points", "within 30 points", "within 25 points"),
    ("PROVISIONAL_PROMOTE_DAYS", 21, "three weeks", "three weeks", "two weeks"),
    ("ARCHIVE_AFTER_FAILURES", 4, "fail ×4", "fails 4 probes", "fail ×3"),
    ("ARCHIVE_AFTER_DAYS", 45, "stale 45d", "goes 45\n          days", "stale 60d"),
    ("PROBE_WEEKDAYS", (1,), "once a week", "once a week", "twice a week"),
    ("MODEL_PAGE_ROWS", 3, "three rows or more serve it free", "three rows or more serve it free",
     "two rows or more"),
])
def test_every_page_states_the_rule_the_code_applies(tmp_path, monkeypatch, name, value,
                                                      readme_says, site_says, unsaid):
    """A rule the pages describe is a constant in the code, and each page reads
    the constant rather than typing its value, so changing it changes every
    page and leaves no page describing the old rule."""
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


TEN = [{"family": f"m-{i}"} for i in range(1, 11)]


def _readme_row(readme: str) -> str:
    return next(line for line in readme.splitlines() if line.startswith("- **[X]"))


def test_a_readme_row_names_eight_families_and_links_the_rest(tmp_path):
    """A README row is one list item, and a rotating lane names every model it
    has served free for two weeks, so the README shows the first eight in the
    row's own order and links the rest to the row's page. The row's page and
    the site, its model index included, keep every family."""
    pages = _render_everything([make(id="gw", category="aggregator", models=TEN)], tmp_path)
    row = _readme_row(pages["README.md"])
    assert "`m-8`" in row and "`m-9`" not in row
    assert "[+2\u00a0more](https://mvalentsev.github.io/awesome-free-ai-coding/providers/gw/)" in row
    assert "`m-10`" not in pages["README.md"]
    assert ">m-10<" in pages[SITE_PAGE]
    assert "`m-10`" in pages["providers/gw.md"]


def test_eight_families_or_fewer_are_all_on_the_readme_row(tmp_path):
    pages = _render_everything([make(id="gw", category="aggregator", models=TEN[:8])], tmp_path)
    row = _readme_row(pages["README.md"])
    assert "`m-8`" in row and "more](" not in row


def test_an_agent_in_the_start_block_names_the_same_families_on_both_pages(tmp_path):
    """The README's Start here and the site's name a starter's first
    README_STARTER_MODELS families and link its page for the rest, alike."""
    from freetier_radar.render import README_STARTER_MODELS
    last, first_left = f"m-{README_STARTER_MODELS}", f"m-{README_STARTER_MODELS + 1}"
    more = f"+{len(TEN) - README_STARTER_MODELS} more"
    pages = _render_everything([make(id="ag", category="agent-cli", models=TEN)], tmp_path)
    start = pages["README.md"].split("## 🚀 Start here")[1].split("## ")[0]
    assert f"`{last}`" in start and f"`{first_left}`" not in start
    readme_more = more.replace(" ", "&nbsp;")
    assert f"[{readme_more}](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ag/)" in start
    card = pages[SITE_PAGE].split("Agent · no card")[1].split('<p class="sub"')[0]
    assert f">{last}<" in card and f">{first_left}<" not in card
    assert f'href="https://mvalentsev.github.io/awesome-free-ai-coding/providers/ag/">{more}<' in card


def test_a_row_that_needs_a_card_never_leads_the_no_card_rows_it_ties_with(tmp_path):
    """CONTRIBUTING's rule, on the README, the site and llms.txt alike: between
    two rows of one rank, the one that asks for no card comes first, whatever
    the names."""
    entries = [make(id="ibm", name="IBM", rank=98, card_required=True),
               make(id="poll", name="Pollinations", rank=98)]
    pages = _render_everything(entries, tmp_path)
    readme, site = pages["README.md"], pages[SITE_PAGE]
    assert readme.index("[Pollinations]") < readme.index("[IBM]")
    assert site.index(">Pollinations<") < site.index(">IBM<")
    assert pages["llms.txt"].index("[Pollinations]") < pages["llms.txt"].index("[IBM]")


def test_a_provisional_page_says_the_day_its_promotion_can_come(tmp_path):
    """A provisional page names the day its promotion can come, not a fixed
    "two weeks of probes still to pass" that reads the same on every day of
    the fortnight."""
    from datetime import timedelta
    row = make(id="young", name="Young", provisional=True, first_seen=TODAY - timedelta(days=5))
    page = _render_everything([row], tmp_path)["providers/young.md"]
    promote = (TODAY - timedelta(days=5) + timedelta(days=14)).isoformat()
    assert f"the first probe it passes on or after {promote}" in page
    assert "still to pass" not in page


def test_the_frontier_bar_is_explained_only_where_a_frontier_line_is_shown(tmp_path):
    """With no free lane measured frontier the picks table has no Frontier line,
    and neither page explains the bar for one."""
    plain = [make(id="a", name="A", category="api-free-tier")]
    pages = _render_everything(plain, tmp_path / "plain")
    assert "Frontier" not in pages["README.md"].split("## 📋")[0]
    assert "Frontier" not in pages[SITE_PAGE].split('id="plug"')[0]
    top = [make(id="b", name="B", models=[{"family": "big", "tier": "frontier", "aa_model": "big"}])]
    pages = _render_everything(top, tmp_path / "top")
    assert "within 10 points" in pages["README.md"] and "within 10 points" in pages[SITE_PAGE]


def test_the_page_names_the_strong_models_the_readme_does(tmp_path):
    """One set of strong models, worked out once: the page's Start here carries
    the families the README's does, the rows beside them and the card mark."""
    strong = {"family": "kimi-k3", "tier": "strong", "aa_model": "kimi-k3"}
    entries = [make(id="a", name="A", rank=1, models=[strong]),
               make(id="b", name="B", rank=2, card_required=True, models=[strong])]
    html = _render_everything(entries, tmp_path)[SITE_PAGE]
    start = html.split('<section id="start">')[1].split("</section>")[0]
    assert ">kimi-k3<" in start
    assert '<a href="https://x.ai">A</a> · <a href="https://x.ai">B</a> 💳' in start
    assert "within 25 points" in start


def test_the_page_ranks_the_strong_models_as_the_readme_chart_does(tmp_path):
    """The page's strong models run in the README chart's order, the highest
    score first, each with its score — one ranking, not a second by breadth."""
    from test_render import SCORES, _strong_rows
    registry = tmp_path / "registry.yaml"
    save_registry(registry, _strong_rows())
    html = render_site(registry, TEMPLATES, tmp_path / SITE_PAGE, today=TODAY, scores=SCORES)
    start = html.split('<section id="start">')[1].split("</section>")[0]
    # glm-5.3 has two rows and kimi-k3 one, but kimi-k3 scores higher
    assert start.index(">kimi-k3<") < start.index(">glm-5.3<")
    assert '<span class="score">45.9</span>' in start and '<span class="score">44.8</span>' in start


def test_a_link_to_the_model_index_opens_it(tmp_path):
    """The model index is folded on the page, and the README sends a reader
    after one model straight to it: the fold carries the id the link names, and
    the page's script opens a fold a link names rather than landing on a closed
    summary."""
    html = _render([make(models=[{"family": "a"}])], tmp_path)
    assert '<details id="model-index" class="fold">' in html
    script = html.split("<script>")[1]
    assert "location.hash" in script and "hashchange" in script and ".open = true" in script


def test_a_link_to_the_connection_table_opens_it(tmp_path):
    """The connection table is folded like the model index, since on a phone its
    cards would stand between the list and the rest of the page; the files that
    wire every lane at once stay in view, and the README and configs/README.md
    link the fold itself, which the page's script opens."""
    from freetier_radar.render import PAGES_URL
    rows = [make(id="k", name="Keyed", api={"base_url": "https://k.example/v1"})]
    pages = _render_everything(rows, tmp_path)
    plug = pages[SITE_PAGE].split('<section id="plug">')[1].split("</section>")[0]
    table, files = plug.split("Ready-made files")
    assert '<details id="connections" class="fold">' in table
    assert table.index('<details id="connections"') < table.index("https://k.example/v1")
    assert "configs/opencode.json" in files and "</details>" not in files
    for page in ("README.md", "configs/README.md"):
        assert f"{PAGES_URL}/#connections" in pages[page], page
        assert f"{PAGES_URL}/#plug" not in pages[page], page


def test_a_row_names_its_first_families_and_folds_the_rest(tmp_path):
    """A row shows the families its README line names and folds the rest under
    their count, rather than standing a column of chips tall beside a few lines
    of offer; the folded ones stay in the page, where the search and a
    browser's find reach them."""
    from freetier_radar.render import SITE_MODELS
    families = [f"fam-{i}" for i in range(SITE_MODELS + 4)]
    html = _render([make(id="wide", name="Wide",
                         models=[{"family": f} for f in families])], tmp_path)
    cell = html.split('data-label="Free models">')[1].split("</td>")[0]
    shown, folded = cell.split('<details class="more">')
    assert all(f">{f}<" in shown for f in families[:SITE_MODELS])
    assert all(f">{f}<" in folded for f in families[SITE_MODELS:])
    assert "+4 more" in folded
    (tmp_path / "narrow").mkdir()
    narrow = _render([make(id="narrow", models=[{"family": f} for f in families[:SITE_MODELS]])],
                     tmp_path / "narrow")
    assert '<details class="more">' not in narrow


def test_a_keyed_lane_with_no_key_page_is_not_called_keyless(tmp_path):
    """The connection table says a key is "not needed" only for a keyless lane,
    not for a keyed one that names no key page."""
    keyed = make(id="k", name="Keyed", api={"base_url": "https://k.example/v1"})
    keyless = make(id="n", name="Keyless", api={"base_url": "https://n.example/v1", "auth": "none"})
    table = _render_everything([keyed, keyless], tmp_path)["configs/README.md"]
    keyed_row = next(line for line in table.splitlines() if line.startswith("| **[Keyed]"))
    keyless_row = next(line for line in table.splitlines() if line.startswith("| **[Keyless]"))
    assert "not needed" not in keyed_row
    assert keyless_row.endswith("| not needed |")


def test_the_page_has_one_heading_and_it_names_the_list(tmp_path):
    """The heading is text — the list's name and what it is, beside the radar
    the README's hero draws — so a search engine, a screen reader and a phone
    all read it at any width."""
    html = _render([make(models=[{"family": "a"}])], tmp_path)
    assert html.count("<h1") == 1
    heading = html.split("<h1>")[1].split("</h1>")[0]
    assert '<span class="name">awesome-free-ai-coding</span>' in heading
    assert "Legal free LLM APIs &amp; coding agents" in heading
    assert '<img src="assets/readme/radar.svg" width="300" height="300" alt="">' in html


def test_the_search_reads_what_the_page_renders(tmp_path):
    """The search builds its answers out of the page's own rows, model index and
    Archive, so a renamed class or a dropped attribute would leave it quietly
    empty. Every attribute its script reads is held to the rendered page here,
    the way browse.html is held to index.json."""
    entries = [make(id="a", name="A", models=[{"family": "m1", "tier": "strong", "aa_model": "m1"}],
                    api={"base_url": "https://a.ai/v1", "auth": "none", "model_ids": ["m1"]}),
               make(id="b", name="B", card_required=True, models=[{"family": "m1"}]),
               make(id="gone", name="Gone", retired_on=TODAY)]
    html = _render(entries, tmp_path)
    row = re.search(r'<tr id="row-a" data-id="a" data-section="api-free-tier"\s+'
                    r'data-flags="([^"]*)">', html)
    assert row and row.group(1).split() == ["nocard", "nokey", "strong"], row
    assert re.search(r'<tr id="row-b" data-id="b" [^>]*data-flags=""', html)
    assert re.search(r'<tr id="model-m1" data-family="m1" data-tier="strong"\s+'
                     r'data-rows="a b">', html)
    assert '<tr data-id="gone">' in html
    # The pages are read off the links the rows already carry.
    assert re.search(r'<td class="when" data-label="Verified">\s*<a href="[^"]+/providers/a/">', html)
    script = html.split('id="search-config">')[1]
    for selector in ('"section.listing tbody tr[data-id]"', '"#model-index tr[data-family]"',
                     '"#archive tbody tr[data-id]"', '"a.name"', '"td.what"', '"td.limits"',
                     '"td.models .chip"', '".tags"', '"td.when a"', '"th a"'):
        assert selector in script, selector
    for attr in ("id", "section", "flags"):
        assert f'data-{attr}="' in html and f"dataset.{attr}" in script, attr
    for attr in ("family", "tier", "rows"):
        assert f'data-{attr}="' in html and f"dataset.{attr}" in script, attr


def _js_function(script: str, name: str) -> str:
    """One function of the page's script, its braces matched."""
    start = script.index(f"function {name}(")
    depth = 0
    for i in range(script.index("{", start), len(script)):
        depth += {"{": 1, "}": -1}.get(script[i], 0)
        if depth == 0:
            return script[start:i + 1]
    raise AssertionError(f"{name} does not close")


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node to run the page's script")
def test_the_search_finds_a_model_written_the_way_its_vendor_writes_it(tmp_path):
    """A reader types "Nemotron 3 Ultra", not nemotron-3-ultra, and no
    description spells a model out, so the name as the vendor writes it has to
    find the row's models and the model itself, though a lone "3" may only
    start a name. The page's own functions run here."""
    script = _render([make()], tmp_path).split('id="search-config">')[1]
    names = ("fold", "squash", "written", "prepareOffer", "prepareModel",
             "scoreOffer", "wholeOffer", "scoreModel", "spelled", "withAccess", "snippet")
    harness = "\n".join(_js_function(script, n) for n in names) + """
    function q(s) { return fold(s).split(" ").filter(Boolean); }
    function offer(models, limits, access, modelAccess, name) {
      var o = {name: name || "Row", models: models, what: "A gateway", limits: limits || "",
               access: access || "", modelAccess: modelAccess || {}};
      prepareOffer(o); return o;
    }
    function model(f) { var m = {family: f}; prepareModel(m); return m; }
    console.log(JSON.stringify({
      family: scoreModel(model("nemotron-3-ultra"), q("Nemotron 3 Ultra")),
      exact: scoreModel(model("glm-5"), q("GLM 5")),
      prefix: scoreModel(model("glm-5.3"), q("glm 5")),
      version: scoreModel(model("qwen3-8b"), q("qwen 3.8")),
      letter: scoreModel(model("mimo-v2.5"), q("m")),
      inside: scoreModel(model("kimi-k3"), q("m")),
      row: scoreOffer(offer(["nemotron-3-ultra"]), q("nemotron 3 ultra")),
      waiting: scoreOffer(offer(["gemma-4-31b"], "gemini/gemma-4-26b-moe is free"), q("gemma 4 26b")),
      other: scoreOffer(offer(["kimi-k3"]), q("nemotron 3 ultra")),
      terms: scoreOffer(offer(["kimi-k3"]), q("kimi k3")),
      snippet: snippet(offer(["ling-3.0-flash-fin", "nemotron-3.5-lightning", "nemotron-3-ultra"]),
                       q("nemotron 3 ultra")),
      said: snippet(offer(["gemma-4-31b"], "Free: gemini/gemma-4-31b and gemini/gemma-4-26b-moe."),
                    q("gemma 4 26b")),
      funded: snippet(offer(["preview", "unfunded"], "", "", {
        preview: "requires $5 one-time top-up + 8% fee; free until 2026-10-06 23:59+03:00"
      }), q("preview")),
      account: snippet(offer(["preview"], "", "requires $1 one-time top-up"), q("preview")),
      vendor: snippet(offer(["minimax-preview"], "MiniMax is a short promotion.", "", {
        "minimax-preview": "requires $5 one-time top-up + 8% fee; free until 2026-10-06 23:59+03:00"
      }, "LLMTR"), q("LLMTR MiniMax"))
    }));"""
    run = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    got = json.loads(run.stdout)
    assert got["family"] == got["exact"] == 32, got
    assert got["prefix"] == 20 and got["version"] == 0, got
    assert got["letter"] > 0 and got["inside"] == 0, got
    assert got["row"] > 0 and got["waiting"] > 0 and got["other"] == 0 and got["terms"] > 0, got
    # why the row came up: the model the query spells, first — not a "3" in another name
    assert got["snippet"] == ("Free models: nemotron-3-ultra, nemotron-3.5-lightning, "
                              "ling-3.0-flash-fin"), got
    # a model the column does not carry yet: the sentence that names it
    assert got["said"] == "Free: gemini/gemma-4-31b and gemini/gemma-4-26b-moe.", got
    assert got["funded"] == ("Free models: preview (requires $5 one-time top-up + 8% fee; "
                             "free until 2026-10-06 23:59+03:00), unfunded"), got
    assert got["account"] == "Free models: preview (requires $1 one-time top-up)", got
    assert got["vendor"] == ("Free models: minimax-preview (requires $5 one-time top-up + 8% fee; "
                             "free until 2026-10-06 23:59+03:00)"), got



@pytest.mark.skipif(shutil.which("node") is None, reason="needs node to run the page's script")
def test_tab_keeps_to_the_search_dialog_it_promises_is_modal(tmp_path):
    """The dialog says aria-modal, so Tab never walks out of it onto the page
    behind: Tab past the last control comes back to the first, Shift+Tab before
    the first goes to the last, and anywhere in between the browser moves focus
    itself."""
    script = _render([make()], tmp_path).split('id="search-config">')[1]
    harness = _js_function(script, "wrapFocus") + """
    console.log(JSON.stringify([wrapFocus(4, 3, false), wrapFocus(4, 0, true),
                                wrapFocus(4, 1, false), wrapFocus(4, 2, true),
                                wrapFocus(4, -1, true), wrapFocus(0, 0, false)]));"""
    run = subprocess.run(["node", "-e", harness], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout) == [0, 3, -1, -1, 3, -1]

def test_the_search_filters_on_the_answers_the_rows_carry(tmp_path):
    """Its filters are generated from the categories and the four answers a
    row's flags carry, so a filter can never ask for a flag no row has."""
    from freetier_radar.render import SEARCH_FILTERS, SEARCH_SECTION_WORDS
    assert set(SEARCH_SECTION_WORDS) == set(Category)
    html = _render([make(id="a", name="A")], tmp_path)
    config = json.loads(re.search(r'id="search-config">(.*?)</script>', html, re.S).group(1))
    assert [s["id"] for s in config["sections"]] == [c.value for c in Category]
    assert [s["label"] for s in config["sections"]] == [SITE_NAV_LABELS[c] for c in Category]
    assert [f["id"] for f in config["filters"]] == [f[0] for f in SEARCH_FILTERS]
    flags = {f for m in re.finditer(r'data-flags="([^"]*)"', html) for f in m.group(1).split()}
    assert flags <= {f[0] for f in SEARCH_FILTERS}
    words = [w for group in (*config["sections"], *config["filters"]) for w in group["words"]]
    assert len(words) == len(set(words)), "a word selects one filter"


def test_without_a_script_the_page_shows_no_search_it_cannot_run(tmp_path):
    """Progressive enhancement: the dialog and the ways into it are hidden in
    the markup and shown by the script, like the copy buttons; and the search
    is the page's one filter, with no `find` box and no `shown` rows beside
    it."""
    html = _render([make()], tmp_path)
    assert re.search(r'<div id="search" class="palette" [^>]*hidden>', html)
    opens = re.findall(r'<button class="(\w+)" type="button" data-search-open hidden', html)
    assert opens == ["searchbox", "navsearch"]
    assert 'id="find"' not in html and 'class="shown"' not in html
