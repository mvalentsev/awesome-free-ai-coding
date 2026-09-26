from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml

from freetier_radar.history import Event, EventType
from freetier_radar.models import WATCH_RECHECK_DAYS, Entry, Watched
from freetier_radar.render import (
    ARCHIVE_AFTER_DAYS, FEED_ENTRIES, FEED_URL, PAGES_URL, README_CHANGES, README_NOTE_TEASER,
    build_context, build_env_example, build_feed, build_index, build_litellm_config,
    build_opencode_config, env_var, is_archived, render_artifacts, render_readme,
)

TODAY = date(2026, 7, 19)

BASE = {
    "name": "X",
    "category": "api-free-tier",
    "url": "https://x.ai",
    "offering": "stuff",
    "first_seen": date(2026, 1, 1),
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["x-mini-2", "free"]},
}


def make(**kw) -> Entry:
    d = {**BASE, "id": kw.pop("id", "x"), "last_verified": kw.pop("last_verified", TODAY), **kw}
    return Entry.model_validate(d)


def test_a_provider_page_names_the_free_list_a_catalog_is_read_with():
    """The Evidence section says what the probe reads, and on a catalog that
    prices nothing "each listed family checked for a zero price" would be
    false twice over: there is no price, and the list is a second document."""
    from freetier_radar.render import build_provider_page

    search = "https://api.ngc.nvidia.com/v2/search/catalog/resources/ENDPOINT?q=free"
    page = build_provider_page(make(id="nimmy", models=[{"family": "kimi-k3"}], probe={
        "type": "api-models", "endpoint": "https://integrate.api.nvidia.com/v1/models",
        "require_zero_price": True, "free_list": search}), [], TODAY)
    assert ("- Probe: the models catalog at <https://integrate.api.nvidia.com/v1/models>, "
            f"each listed family checked for its free mark on the vendor's free list at "
            f"<{search}>") in page
    assert "zero price" not in page


def test_a_provider_page_description_names_the_free_models_from_the_column():
    """The description is what a search result shows under the page's title.
    It said the offer and the quota, and the models only where `offering`
    listed them — twenty-eight rows' did until 2026-09-26, when the rule gave
    the models to the Models line alone. So the description names them from
    that line, the one a probe reads back, and every page with a column says
    them the same way; a long column ends in how many more."""
    from freetier_radar.render import README_MODELS, build_provider_page

    def description(**kw) -> str:
        page = build_provider_page(make(**kw), [], TODAY)
        return yaml.safe_load(page.split("---\n")[1])["description"]

    assert description(id="few", offering="A free lane, no card", limits="20 requests a minute",
                       models=[{"family": "kimi-k3"}, {"family": "glm-5.3"}]) == (
        "A free lane, no card. Free models: kimi-k3, glm-5.3. 20 requests a minute")
    many = [{"family": f"m-{i}"} for i in range(README_MODELS + 3)]
    shown = ", ".join(f"m-{i}" for i in range(README_MODELS))
    assert description(id="many", offering="A catalog", models=many).startswith(
        f"A catalog. Free models: {shown} and 3 more.")
    assert description(id="sum", free_part="sum", offering="A credit",
                       limits="$5 a month") == "A credit. $5 a month"


def test_a_provider_page_says_why_its_row_names_no_model():
    """An empty column read the same on every page — "the page this row is
    verified against names no free model" — which a credit made false: Sail
    Research's page names Kimi K3 beside the $5 a month spent on it. The row's
    free part says which empty column it is."""
    from freetier_radar.render import build_provider_page

    credit = build_provider_page(make(id="credit", free_part="sum"), [], TODAY)
    assert "No model is free by itself here" in credit
    assert "names no free model" not in credit
    auto = build_provider_page(make(id="auto", free_part="unnamed"), [], TODAY)
    assert "The vendor does not say which models" in auto
    assert "names no free model" not in auto
    page = build_provider_page(make(id="page", free_part="models"), [], TODAY)
    assert "The page this row is verified against names no free model" in page


def test_a_provider_page_says_the_families_are_checked_not_that_one_fails_the_row():
    """Since 2026-09-24 a family a catalog stopped serving free flags the Models
    column while another family stands, so "required" no longer says what one
    missing family does; each is still checked, on every run."""
    from freetier_radar.render import build_provider_page

    page = build_provider_page(make(id="lane", models=[{"family": "kimi-k3"}], probe={
        "type": "api-models", "endpoint": "https://api.x.ai/v1/models", "free_marker": ":free",
        "require_zero_price": True}), [], TODAY)
    assert ("- Probe: the models catalog at <https://api.x.ai/v1/models>, free rows carrying "
            "`:free`, each listed family checked for a zero price") in page
    page = build_provider_page(make(id="laned", models=[{"family": "kimi-k3"}], probe={
        "type": "api-models", "endpoint": "https://api.x.ai/v1/models", "lane": "free"}), [], TODAY)
    assert ("- Probe: the `free` lane of the models document at <https://api.x.ai/v1/models>, "
            "each listed family checked in that lane") in page
    assert "required" not in page.split("## Evidence")[1]


def test_archive_rules():
    assert not is_archived(make(), TODAY)
    assert is_archived(make(probe_failures=3), TODAY)
    assert is_archived(make(last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1)), TODAY)
    assert not is_archived(make(last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS)), TODAY)
    assert is_archived(make(retired_on=TODAY), TODAY)
    assert is_archived(make(retired_on=TODAY - timedelta(days=1)), TODAY)
    assert not is_archived(make(retired_on=TODAY + timedelta(days=1)), TODAY)
    assert is_archived(make(delisted={"on": TODAY, "reason": "taken off by a reviewer"}), TODAY)


def test_superseded_models_never_archive():
    """A vendor shipping a newer generation means "bump the row", not "bury the
    entry" — the free tier outlives the model family listed against it."""
    superseded = make(models=[{"family": "old", "superseded_by": "new"}])
    assert not is_archived(superseded, TODAY)
    mixed = make(models=[{"family": "old", "superseded_by": "new"}, {"family": "new"}])
    assert not is_archived(mixed, TODAY)


def test_build_context_rows():
    entries = [make(models=[{"family": "a"}, {"family": "b", "superseded_by": "c"}])]
    ctx = build_context(entries, TODAY)
    assert ctx["date"] == "2026-07-19"
    section = next(s for s in ctx["sections"] if "LLM APIs" in s["title"])
    assert section["rows"][0]["models"] == "`a`"
    assert section["rows"][0]["card_flag"] == ""
    assert ctx["archived"] == []


def test_a_card_is_marked_where_it_is_asked_for_and_nowhere_else():
    """39 of 41 rows said "✅ No" in a column of their own. The exception is what
    a reader needs to see, and it is easier to see beside a name than inside a
    column of agreement."""
    ctx = build_context([make(id="free", name="Free"),
                         make(id="paid", name="Paid", card_required=True)], TODAY)
    flags = {r["name"]: r["card_flag"]
             for s in ctx["sections"] for r in s["rows"]}
    assert flags == {"Free": "", "Paid": " 💳"}
    assert (ctx["card_count"], ctx["no_card_count"]) == (1, 1)


def test_rank_orders_rows_within_section():
    entries = [make(id="worst", name="Worst", rank=99), make(id="best", name="Best", rank=1)]
    ctx = build_context(entries, TODAY)
    section = next(s for s in ctx["sections"] if "LLM APIs" in s["title"])
    assert [r["name"] for r in section["rows"]] == ["Best", "Worst"]


def test_the_readme_row_prints_what_you_get_whole_and_leaves_the_quota_to_the_row_page():
    """The README is the landing page. On 2026-09-20 it was 161 KB, 83 KB of it
    inside 93 <details> folds, and the median `limits` cell ran to 926
    characters: sixteen desktop screens of tables, thirty-one on a phone with
    the table scrolling sideways. A row on the README is one line — what the
    offer is, the models, the date — and the quota in the vendor's words is on
    the row's own page and the site, where a fold folds."""
    long_offering = ("Open-source coding agent whose gateway prices a rotating set of "
                     "models at zero — one, two, three, four, five and six of them — "
                     "inside the tool only, no sign-in; any provider via BYOK, and a "
                     "desktop app besides the terminal one")
    assert len(long_offering) > 200
    ctx = build_context([make(id="l", name="L", offering=long_offering,
                              limits="1,000,000 free tokens per model, valid 90 days. " * 8)],
                        TODAY)
    row = next(r for s in ctx["sections"] for r in s["rows"])
    assert row["offering"] == long_offering
    assert "<details>" not in row["offering"]
    assert "limits" not in row
    assert row["page"] == "https://mvalentsev.github.io/awesome-free-ai-coding/providers/l/"


def test_the_list_is_one_item_per_row_with_no_table_no_fold_and_no_limits(tmp_path: Path):
    """On 2026-09-25 the list's four tables ran to thirty-one phone screens:
    GitHub gives a table no more than the screen, so the offer got a column a
    word or two wide, a row stood a screen tall, and the models and the dates
    sat off the right edge behind a sideways scroll. The same rows as list
    items measured eighteen phone screens with nothing off the edge, and eight
    desktop screens where the tables took eleven (github-markdown-css, 390 and
    1280 pixels). A row is one list item, and the quota is on its own page."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="l", name="L", limits="a quota figure, read on a date. " * 40)])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    listing = text.split("## 📋 The list")[1].split("## 📦 Archive")[0]
    assert "| Tool |" not in listing and "| Limits |" not in listing
    assert "a quota figure" not in listing
    items = [line for line in listing.splitlines() if line.startswith("- **[")]
    assert len(items) == 1 and "<details>" not in items[0]


def test_a_list_item_is_the_name_the_offer_and_a_small_line_of_date_and_models(tmp_path: Path):
    """The flags stay beside the name, where the eye lands first. The date
    leads the small line under the offer: at the line's end a break fell inside
    it, `2026-` above `09-24`, which the narrow date column had done in every
    row. A row that names no model has the date alone."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="x", name="X", offering="An offer", card_required=True,
                             provisional=True, models=[{"family": "a"}, {"family": "b"}]),
                        make(id="y", name="Y", offering="Another offer")])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    page = "https://mvalentsev.github.io/awesome-free-ai-coding/providers/"
    assert (f"- **[X](https://x.ai)** 💳 🧪 — An offer<br><sub>[verified 2026-07-19]({page}x/)"
            " · `a` · `b`</sub>") in text
    assert (f"- **[Y](https://x.ai)** — Another offer<br>"
            f"<sub>[verified 2026-07-19]({page}y/)</sub>") in text


def test_the_readme_keeps_the_plug_it_in_heading_and_sends_the_reader_to_configs(tmp_path: Path):
    """The heading stays — its anchor is what the nav and any link from outside
    point at — and the connection table moved to configs/README.md, beside the
    files it describes, so the README lists the files and nothing else."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import PAGES_URL
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [api_entry(id="groq-free", name="Groq")])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    plug = text.split("## 🔧 Plug it into your agent")[1].split("## 📡 How this list stays fresh")[0]
    assert "[`configs/README.md`](configs/README.md)" in plug
    assert "| Provider | Base URL |" not in plug and "https://api.x.ai/v1" not in plug
    assert "[`llms.txt`](llms.txt)" in plug and "[`index.json`](index.json)" in plug
    assert f"{PAGES_URL}/#connections" in plug


def test_the_readme_lists_the_ready_made_files_as_list_items(tmp_path: Path):
    """The files were a two-column table until 2026-09-26, and GitHub gives a
    table the screen's width and no more: on a phone the LiteLLM line's
    `litellm --config … --host 127.0.0.1` held its cell open past the edge and
    the table scrolled sideways under the reader's thumb. A list item wraps."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [api_entry(id="groq-free", name="Groq")])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    plug = text.split("## 🔧 Plug it into your agent")[1].split("## 📡 How this list stays fresh")[0]
    assert not [line for line in plug.splitlines() if line.startswith("|")]
    for f in ("configs/opencode.json", "configs/litellm.yaml", "configs/claude-code.sh",
              "configs/free-llm.env.example"):
        assert any(line.startswith(f"- [`{f}`]({f}) — ") for line in plug.splitlines()), f


def test_a_teaser_is_never_cut_inside_a_code_span():
    """GitHub pairs a backtick the teaser leaves open with the next one it meets,
    which is the same span's opening backtick in the full text, and turns all
    between them into code: `</sub></summary>` included. The fold then shows the
    whole cell with its tags printed as text. opencode's lane notice from
    2026-09-17 and its limits from 09-18 did that on the README, both cut inside
    `403 FreeTierError: …`. The README's rows fold nothing since 2026-09-21; the
    connection notes beside the configs and the archive's reasons still do."""
    long = ("The free ids work inside OpenCode and nowhere else. Since 2026-09-17 Zen has "
            "answered every other client with `403 FreeTierError: OpenCode's free tier can "
            "only be used from within OpenCode`, and on 2026-09-18 an OpenCode maintainer "
            "said the free tier is not for other harnesses. " * 2).strip()
    opens = "`" + " ".join(["an error string that runs on and on"] * 5) + "`" + ", then prose" * 30

    ctx = build_context([make(id="l", name="L", api={"base_url": "https://l.example/v1", "note": long}),
                         make(id="o", name="O", api={"base_url": "https://o.example/v1", "note": opens})],
                        TODAY)
    cells = {c["name"]: c["note"] for c in ctx["connections"]}

    teaser = cells["L"].split("<summary><sub>")[1].split("</sub></summary>")[0]
    assert teaser == ("The free ids work inside OpenCode and nowhere else. Since 2026-09-17 "
                      "Zen has answered every other client with …")
    assert long in cells["L"]
    # a span that opens the cell is kept whole: a teaser has to show something
    teaser = cells["O"].split("<summary><sub>")[1].split("</sub></summary>")[0]
    assert teaser.startswith("`") and teaser.count("`") == 2


def test_a_section_counts_itself_and_the_card_free_rows_in_it():
    entries = [make(id="a", name="A"), make(id="b", name="B"),
               make(id="c", name="C", card_required=True)]
    section = next(s for s in build_context(entries, TODAY)["sections"]
                   if "LLM APIs" in s["title"])
    assert (section["count"], section["no_card"], section["all_no_card"]) == (3, 2, False)

    free_only = next(s for s in build_context(entries[:2], TODAY)["sections"]
                     if "LLM APIs" in s["title"])
    assert free_only["all_no_card"] is True
    # an empty section claims nothing rather than claiming all of nothing
    empty = next(s for s in build_context(entries, TODAY)["sections"]
                 if "Aggregators" in s["title"])
    assert (empty["count"], empty["all_no_card"]) == (0, False)


def test_env_var_naming():
    assert env_var("groq-free") == "GROQ_API_KEY"
    assert env_var("zai-glm") == "ZAI_GLM_API_KEY"


def test_provisional_marker_and_flag():
    ctx = build_context([make(name="Prov", provisional=True),
                         make(id="solid", name="Solid")], TODAY)
    section = next(s for s in ctx["sections"] if "LLM APIs" in s["title"])
    rows = {r["name"]: r for r in section["rows"]}
    # the marker rides beside the name, where the card marker is; the date
    # column is the narrowest on the page and a second glyph wrapped it in two
    assert rows["Prov"]["new_flag"] == " 🧪"
    assert rows["Prov"]["verified"] == TODAY.isoformat()
    assert rows["Solid"]["new_flag"] == ""
    assert rows["Solid"]["verified"] == TODAY.isoformat()
    assert ctx["has_provisional"] is True
    assert build_context([make(id="solid", name="Solid")], TODAY)["has_provisional"] is False


def api_entry(**kw):
    return make(**{"api": {"base_url": "https://api.x.ai/v1",
                           "key_url": "https://x.ai/keys", "auth": "api-key"}, **kw})


def test_opencode_config_and_env_example():
    entries = [
        api_entry(id="groq-free", name="Groq", models=[{"family": "llama-4"}],
                  api={"base_url": "https://api.x.ai/v1", "key_url": "https://x.ai/keys",
                       "auth": "api-key", "model_ids": ["llama-4"]}),
        make(id="keyless", name="Keyless",
             api={"base_url": "https://free.example/v1", "auth": "none"}),
        make(id="no-api", name="NoApi"),
        make(id="not-compat", name="NC",
             api={"base_url": "https://nc.example", "openai_compatible": False}),
    ]
    entries.append(make(id="pinned", name="Pinned",
                        api={"base_url": "https://p.example/v1", "auth": "none",
                             "model_ids": ["exact-id-1"]},
                        models=[{"family": "ignored-family"}]))
    cfg = build_opencode_config(entries, TODAY)
    assert set(cfg["provider"]) == {"groq-free", "keyless", "pinned"}
    assert cfg["provider"]["pinned"]["models"] == {"exact-id-1": {"name": "exact-id-1"}}
    groq = cfg["provider"]["groq-free"]
    assert groq["options"] == {"baseURL": "https://api.x.ai/v1", "apiKey": "{env:GROQ_API_KEY}"}
    assert groq["models"] == {"llama-4": {"name": "llama-4"}}
    assert "apiKey" not in cfg["provider"]["keyless"]["options"]

    env = build_env_example(entries, TODAY)
    assert 'export GROQ_API_KEY=""' in env
    assert "no key needed" in env
    assert "NoApi" not in env


def test_the_badge_dates_the_evidence_not_the_render():
    """Rendering the README does not verify anything. The badge used to carry
    today's date regardless, so a regeneration between probe runs claimed a
    freshness no entry had; the oldest live probe is what the page can honestly
    stand behind. An entry stale enough to be archived does not drag it down —
    it is not on the page any more."""
    entries = [make(last_verified=TODAY - timedelta(days=3)),
               make(id="older", last_verified=TODAY - timedelta(days=9)),
               make(id="buried", last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1))]
    ctx = build_context(entries, TODAY)
    assert ctx["verified_through"] == (TODAY - timedelta(days=9)).isoformat()
    assert ctx["date"] == TODAY.isoformat()


def test_the_badge_says_the_date_is_a_floor_and_colours_itself_by_its_age(tmp_path: Path):
    """`min` over the live rows is a floor, and the badge read as a single check
    date: on 2026-09-12 it said "all entries verified 2026-09-07" while all but
    two rows had passed a probe two days earlier. "or later" is the whole fix to
    the reading; the colour is the fix to the other half, a hard-coded green
    that called a floor of any age fresh."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import BADGE_AMBER, BADGE_FRESH_DAYS, BADGE_GREEN, BADGE_RED

    def badge(days_behind: int) -> str:
        reg = tmp_path / f"registry-{days_behind}.yaml"
        save_registry(reg, [make(id="fresh"),
                            make(id="lagging", last_verified=TODAY - timedelta(days=days_behind))])
        text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
        return next(ln for ln in text.splitlines() if "every%20row%20verified" in ln)

    line = badge(BADGE_FRESH_DAYS)
    # The floor, not the newest row, and never today's render date.
    assert f"{(TODAY - timedelta(days=BADGE_FRESH_DAYS)).isoformat().replace('-', '--')}%20or%20later" in line
    assert line.endswith(f"-{BADGE_GREEN})")
    assert badge(BADGE_FRESH_DAYS + 1).endswith(f"-{BADGE_AMBER})")
    assert badge(ARCHIVE_AFTER_DAYS - 1).endswith(f"-{BADGE_RED})")


def test_check_rendered_catches_an_edit_that_never_reached_the_published_files(tmp_path: Path):
    """Every file this repository publishes is generated, and all of them are
    committed: a registry edit that skipped the render leaves the README, the
    index, the configs and the provider pages advertising what the registry
    stopped saying, until the next scheduled run happens to fix it. CI rendered
    to /tmp to prove rendering works and compared nothing."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import (
        CONFIGS_README, SITE_PAGE, check_rendered, render_configs_readme, render_site,
    )

    from freetier_radar.history import record_changes

    reg = tmp_path / "registry.yaml"
    save_registry(reg, [api_entry(id="x", name="X"), make(id="gone", name="Gone")])
    record_changes(reg, tmp_path / "history.jsonl", TODAY,
                   datetime(2026, 7, 19, 9, 30, tzinfo=timezone.utc))
    render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    render_site(reg, Path("templates"), tmp_path / SITE_PAGE, today=TODAY)
    render_configs_readme(reg, Path("templates"), tmp_path / CONFIGS_README, today=TODAY)
    render_artifacts(reg, tmp_path, today=TODAY)
    assert check_rendered(reg, Path("templates"), tmp_path) == []

    # The date the artifacts carry is what the check renders against, so a
    # repository nobody has touched does not go red on the calendar alone.
    assert check_rendered(reg, Path("templates"), tmp_path, today=TODAY + timedelta(days=30)) == []

    # A row renamed in the registry and nowhere else.
    save_registry(reg, [api_entry(id="x", name="Renamed"), make(id="gone", name="Gone")])
    stale = check_rendered(reg, Path("templates"), tmp_path)
    assert "README.md" in stale and "index.json" in stale and "providers/x.md" in stale
    # The site's front page is generated and committed like the rest of them,
    # and so is the connection table beside the configs.
    assert SITE_PAGE in stale and CONFIGS_README in stale

    # A page no row renders any more is still served: the check has to see a
    # file the render no longer makes, not only the ones whose bytes moved.
    (tmp_path / "providers" / "stray.md").write_text("# Stray\n", encoding="utf-8")
    assert "providers/stray.md" in check_rendered(reg, Path("templates"), tmp_path)


def test_a_provider_page_says_when_its_probe_has_started_missing(tmp_path: Path):
    """The date alone made a row mid-failure look merely unlucky in the
    scheduling. trae and inception-labs read 2026-09-07 beside rows reading
    2026-09-10 for two days with nothing saying why."""
    from freetier_radar.models import ARCHIVE_AFTER_FAILURES
    from freetier_radar.render import build_provider_page

    healthy = build_provider_page(make(id="ok"), [], TODAY)
    assert "**live** — last verified by a probe on 2026-07-19 ·" in healthy

    once = build_provider_page(make(id="slipping", probe_failures=1), [], TODAY)
    assert "the probe since has not found that evidence" in once
    assert f"{ARCHIVE_AFTER_FAILURES} misses in a row archive the row" in once

    twice = build_provider_page(make(id="slipping", probe_failures=2), [], TODAY)
    assert "the 2 probes since have not found that evidence" in twice


def test_configs_call_the_ids_a_row_lists_never_its_family_names():
    """A family names a model; an id is what a request carries. Until 2026-09-25
    a row with no api.model_ids had its family names written into litellm.yaml
    and opencode.json as ids, which is right only where a family happens to be
    one: Cloudflare's config handed out `llama-4`, which Workers AI does not
    know (its ids are @cf/ paths), and Upstage's `solar-pro-3` for the id
    solar-pro3."""
    row = api_entry(id="cf", name="CF", models=[{"family": "llama-4", "tier": "strong"}])
    assert [d for d in build_litellm_config([row], TODAY)["model_list"]
            if "llama-4" in d["litellm_params"]["model"]] == []
    assert build_opencode_config([row], TODAY)["provider"]["cf"]["models"] == {}


def test_litellm_config_names_every_free_model_of_every_connectable_entry():
    entries = [api_entry(id="groq-free", name="Groq", models=[{"family": "llama-4"}],
                         api={"base_url": "https://api.x.ai/v1", "key_url": "https://x.ai/keys",
                              "auth": "api-key", "model_ids": ["llama-4"]}),
               api_entry(id="keyless", name="NoKey", api={
                   "base_url": "https://free.example/v1", "auth": "none",
                   "model_ids": ["gpt-oss-120b"]}),
               make(id="plain"),  # no api block: nothing to point a proxy at
               # An auto-routing plan lists no free model of its own, so there is
               # no id a proxy could call: it contributes nothing rather than a
               # broken alias.
               api_entry(id="router", name="Router")]
    cfg = build_litellm_config(entries, TODAY)
    assert [d for d in cfg["model_list"] if not d["model_name"].startswith("free/")] == [
        {"model_name": "groq-free/llama-4",
         "litellm_params": {"model": "openai/llama-4",
                            "api_base": "https://api.x.ai/v1",
                            "api_key": "os.environ/GROQ_API_KEY"}},
        {"model_name": "keyless/gpt-oss-120b",
         "litellm_params": {"model": "openai/gpt-oss-120b",
                            "api_base": "https://free.example/v1",
                            "api_key": "none"}},  # LiteLLM's own spelling for "no key"
    ]


def test_litellm_pools_every_lane_of_a_tier_under_one_name_that_falls_back():
    """OmniRoute's pitch is one model name that keeps answering when a free tier
    runs out; LiteLLM does that with a model group and fallbacks, on lanes this
    list vouches for. free/frontier and free/strong hold every id whose family
    the registry measured at that tier, free/nokey every lane that needs no
    account. A group deployment benches itself after its first failure — a key
    the reader never set fails before any request leaves, a 429 is the quota
    spent — while a model asked for by name keeps LiteLLM's defaults: measured
    on LiteLLM 1.102 on 2026-09-21, twelve unset keys and one working lane
    answered 8 calls of 8, and one 429 on a lone model otherwise shut it for the
    whole cooldown. A keyless lane that refuses any bearer token is in none of
    it, because LiteLLM sends one on every call."""
    glm = {"api": {"base_url": "https://glm.example/v1", "auth": "api-key",
                   "model_ids": ["zai/glm-5.3", "zai/glm-5.3-flash"]},
           "models": [{"family": "glm-5.3", "tier": "frontier", "aa_model": "glm-5-3"},
                      {"family": "glm-5.3-flash", "tier": "strong", "aa_model": "glm-5-3-flash"}]}
    entries = [
        make(id="glm", name="GLM", rank=1, **glm),
        make(id="open", name="Open", rank=2, models=[{"family": "gpt-oss"}],
             api={"base_url": "https://open.example/v1", "auth": "none",
                  "model_ids": ["gpt-oss-20b"]}),
        make(id="bare", name="Bare", rank=3, models=[{"family": "qwen3.8", "tier": "strong"}],
             api={"base_url": "https://bare.example/v1", "auth": "none", "refuses_bearer": True,
                  "model_ids": ["qwen3.8-27b"]}),
        make(id="trial", name="Trial", rank=4, models=[{"family": "qwen3.8", "tier": "strong"}],
             api={"base_url": "https://trial.example/v1", "key_url": "https://trial.example/key",
                  "public_key": "pk-123", "model_ids": ["qwen3.8-27b"]}),
        # notable decides a page, not a pool: free/strong is the bar a caller asked for
        make(id="mid", name="Mid", rank=5, models=[{"family": "glm-5", "tier": "notable",
                                                     "aa_model": "glm-5"}],
             api={"base_url": "https://mid.example/v1", "key_url": "https://mid.example/key",
                  "model_ids": ["zai/glm-5"]}),
    ]
    cfg = build_litellm_config(entries, TODAY)
    groups: dict[str, list[tuple[str, str, str]]] = {}
    for d in cfg["model_list"]:
        p = d["litellm_params"]
        if d["model_name"].startswith("free/"):
            groups.setdefault(d["model_name"], []).append((p["model"], p["api_base"], p["api_key"]))
            assert d["model_info"] == {"allowed_fails_policy": {
                "AuthenticationErrorAllowedFails": 0, "InternalServerErrorAllowedFails": 0,
                "RateLimitErrorAllowedFails": 0}}
        else:
            assert "model_info" not in d
    assert groups == {
        "free/frontier": [("openai/zai/glm-5.3", "https://glm.example/v1", "os.environ/GLM_API_KEY")],
        "free/strong": [("openai/zai/glm-5.3-flash", "https://glm.example/v1", "os.environ/GLM_API_KEY"),
                        ("openai/qwen3.8-27b", "https://trial.example/v1", "os.environ/TRIAL_API_KEY")],
        "free/nokey": [("openai/gpt-oss-20b", "https://open.example/v1", "none"),
                       ("openai/qwen3.8-27b", "https://trial.example/v1", "os.environ/TRIAL_API_KEY")],
    }
    assert not [d for d in cfg["model_list"] if "bare.example" in d["litellm_params"]["api_base"]]
    assert cfg["router_settings"] == {
        "routing_strategy": "simple-shuffle", "num_retries": 3,
        "fallbacks": [{"free/frontier": ["free/strong", "free/nokey"]},
                      {"free/strong": ["free/nokey"]}]}
    # One dict per deployment: PyYAML writes a shared one as an &anchor, LiteLLM
    # then hands every deployment the same model_info and the same id, and the
    # group answered 429 to every call (measured the same day).
    assert "&id" not in yaml.safe_dump(cfg)


def test_every_page_offers_only_the_litellm_groups_the_config_defines(tmp_path: Path):
    """A group exists only while some lane is measured at its tier. On 2026-09-22
    Claude Opus 5.5 took the top of the index to 57.6, no free lane stayed within
    ten points of it, and free/frontier left litellm.yaml — while its header,
    llms.txt and the configs README went on telling readers to ask for it, a
    call LiteLLM answers with "model not found". The fix reached those three and
    left `free/strong` typed into the README's and the site's file tables."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import (SITE_PAGE, build_llms_txt, render_configs_readme,
                                       render_site)
    strong = make(id="glm", name="GLM", models=[
        {"family": "glm-5.3", "tier": "strong", "aa_model": "glm-5-3"}],
        api={"base_url": "https://glm.example/v1", "model_ids": ["zai/glm-5.3"]})
    frontier = make(id="top", name="Top", models=[
        {"family": "kimi-k3", "tier": "frontier", "aa_model": "kimi-k3"}],
        api={"base_url": "https://top.example/v1", "model_ids": ["kimi-k3"]})
    untiered = make(id="bare", name="Bare", models=[{"family": "m"}],
                    api={"base_url": "https://bare.example/v1", "model_ids": ["m"]})

    def offered(entries: list[Entry]) -> dict[str, list[str]]:
        reg = tmp_path / "registry.yaml"
        save_registry(reg, entries)
        render_artifacts(reg, tmp_path, today=TODAY)
        header = "".join(line for line in (tmp_path / "configs" / "litellm.yaml")
                         .read_text(encoding="utf-8").splitlines(keepends=True)
                         if line.startswith("#"))
        configs = render_configs_readme(reg, Path("templates"), tmp_path / "configs" / "README.md",
                                        today=TODAY)
        texts = {"header": header, "configs": configs, "llms": build_llms_txt(entries, TODAY),
                 "readme": render_readme(reg, Path("templates"), tmp_path / "README.md",
                                         today=TODAY),
                 "site": render_site(reg, Path("templates"), tmp_path / SITE_PAGE, today=TODAY)}
        return {name: [g for g in ("free/frontier", "free/strong", "free/nokey") if g in text]
                for name, text in texts.items()}

    pages = ("header", "configs", "llms", "readme", "site")
    assert offered([strong]) == {name: ["free/strong"] for name in pages}
    assert offered([strong, frontier]) == {name: ["free/frontier", "free/strong"]
                                           for name in pages}
    assert offered([untiered]) == {name: [] for name in pages}


def test_headline_counts_are_derived_from_the_registry():
    """The numbers at the top of the page are a claim about the list, so they are
    counted from it — a hand-typed "31 need no card" is one merged PR away from
    being a lie, and the archived rows must not prop any of them up."""
    entries = [
        api_entry(id="groq-free", name="Groq"),
        api_entry(id="keyless", name="Keyless",
                  api={"base_url": "https://free.example/v1", "auth": "none"}),
        make(id="paid", name="Paid", card_required=True),
        make(id="buried", last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1)),
    ]
    ctx = build_context(entries, TODAY)
    assert ctx["active_count"] == 3
    assert ctx["no_card_count"] == 2
    assert ctx["no_signup_count"] == 1
    assert ctx["endpoint_count"] == 2


def test_model_index_groups_providers_by_family():
    """The per-provider tables cannot answer "who serves qwen3 for free?" — this
    index does, most-served family first. Superseded families stay out of it:
    they are not callable any more."""
    entries = [
        make(id="a", name="A", rank=1, models=[{"family": "qwen3"}, {"family": "gpt-oss"}]),
        make(id="b", name="B", rank=2, models=[{"family": "qwen3"},
                                               {"family": "old", "superseded_by": "new"}]),
        make(id="buried", name="Buried", models=[{"family": "qwen3"}],
             last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1)),
    ]
    index = build_context(entries, TODAY)["model_index"]
    assert [m["family"] for m in index] == ["qwen3", "gpt-oss"]
    assert [p["name"] for p in index[0]["providers"]] == ["A", "B"]


def test_the_model_index_marks_a_card_where_the_rows_do(tmp_path: Path):
    """"💳 beside a name is the whole of the fine print about payment", the README
    says — and the model index named Sail Research beside kimi-k3 as free with
    no mark, while its $5 a month needs a payment method on the account."""
    from freetier_radar.models import save_registry
    entries = [make(id="a", name="A", rank=1, models=[{"family": "kimi-k3"}]),
               make(id="b", name="B", rank=2, card_required=True, models=[{"family": "kimi-k3"}])]
    ctx = build_context(entries, TODAY)
    assert [(p["name"], p["card_flag"]) for p in ctx["model_index"][0]["providers"]] == [
        ("A", ""), ("B", " 💳")]
    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    from freetier_radar.render import SITE_PAGE, render_site
    html = render_site(reg, Path("templates"), tmp_path / SITE_PAGE, today=TODAY)
    assert '<a href="https://x.ai">A</a>, <a href="https://x.ai">B</a> 💳' in html


def test_a_reader_after_one_model_is_sent_to_the_websites_index(tmp_path: Path):
    """The README carried every family and everyone who serves it free, and
    that index grows with the families rather than the rows: 70 families in
    7 KB on 2026-09-20, 149 in 18.7 KB on 09-25 — of a 70 KB page, 80 KB the
    ceiling — with thirty-six more ids due a family within two weeks. Nothing a
    scheduled run committed was checked against the ceiling, so the first a
    maintainer would have heard of it is a test refusing an unrelated commit.
    The whole index is the site's; the README names the strong models and
    links the rest."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import PAGES_URL
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="a", name="A", models=[{"family": "qwen3"}, {"family": "glm-5"}])])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    assert "| Model family | Free at |" not in text
    assert (f"[The website's model index]({PAGES_URL}/#model-index) names all 2 model families "
            "on the list and everyone who serves each one free") in text


def test_the_strong_models_are_named_with_every_row_that_serves_them_free(tmp_path: Path):
    """The question a reader brings is often a model, not a vendor: where is
    Kimi K3 free, where is DeepSeek V4 Pro. The tier marks answer it for the
    models worth coming for — measured, never typed — and the bar keeps the set
    short where the whole index is not: seventeen families of 149 on
    2026-09-25. Frontier first, then the most widely served, since every row
    beside a model is another free quota of it; a row that needs a card says so
    here as it does in the list."""
    from freetier_radar.models import save_registry
    strong = {"tier": "strong", "aa_model": "kimi-k3"}
    entries = [
        make(id="a", name="A", rank=1, models=[{"family": "kimi-k3", **strong}, {"family": "small"}]),
        make(id="b", name="B", rank=2, card_required=True, models=[{"family": "kimi-k3", **strong}]),
        make(id="c", name="C", rank=3, models=[{"family": "big", "tier": "frontier",
                                                "aa_model": "big"}]),
        make(id="d", name="D", rank=4, models=[{"family": "glm-5.3", "tier": "strong",
                                                "aa_model": "glm-5-3"}]),
    ]
    ctx = build_context(entries, TODAY)
    assert [(m["family"], m["frontier"], [p["name"] + p["card_flag"] for p in m["providers"]])
            for m in ctx["strong_models"]] == [
        ("big", True, ["C"]), ("kimi-k3", False, ["A", "B 💳"]), ("glm-5.3", False, ["D"])]
    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    start = text.split("## 🚀 Start here")[1].split("## 📋 The list")[0]
    # A list, as the rows are: in a table the model's column took a third of a
    # phone's width, and seventeen models stood two screens tall.
    # Each model links its own page, where every row that serves it has its
    # limits and the ids to call.
    assert f"\n- [`big`]({PAGES_URL}/models/big/) <sub>frontier</sub> — [C](https://x.ai)\n" in start
    assert (f"\n- [`kimi-k3`]({PAGES_URL}/models/kimi-k3/) — [A](https://x.ai) · "
            "[B](https://x.ai) 💳\n") in start
    assert "`small`" not in start


def test_the_strong_models_on_the_readme_are_capped_and_the_rest_linked(tmp_path: Path,
                                                                       monkeypatch):
    import freetier_radar.render as render
    from freetier_radar.models import save_registry
    monkeypatch.setattr(render, "README_STRONG", 1)
    entries = [make(id="a", name="A", models=[
        {"family": "kimi-k3", "tier": "strong", "aa_model": "kimi-k3"},
        {"family": "glm-5.3", "tier": "strong", "aa_model": "glm-5-3"}])]
    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    start = text.split("## 🚀 Start here")[1].split("## 📋 The list")[0]
    shown = [line for line in start.splitlines() if line.startswith("- [`")]
    assert shown == [f"- [`glm-5.3`]({PAGES_URL}/models/glm-5.3/) — [A](https://x.ai)"]
    assert "the other strong one is in [the website's model index]" in start


def test_a_row_whose_vendor_trains_on_what_you_send_says_so_beside_its_name(tmp_path: Path):
    """What a free offer costs besides money is often what a reader sends it:
    the Gemini API's free tier lists "Content used to improve our products"
    where the paid one says the opposite. The README carries it as one glyph
    beside the name, like the card — the vendor's sentence is on the row's page
    — and a vendor that says it does not train gets no glyph, only the page."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import build_provider_page
    yes = make(id="yes", name="Yes", rank=1, data_use={
        "trains": "yes", "quote": "Content used to improve our products",
        "url": "https://x.ai/pricing"})
    optout = make(id="optout", name="OptOut", rank=2, data_use={
        "trains": "opt-out", "quote": "Model training Opt-out", "url": "https://x.ai/plans"})
    no = make(id="no", name="No", rank=3, data_use={
        "trains": "no", "quote": "We never train on your prompts", "url": "https://x.ai/privacy"})
    silent = make(id="silent", name="Silent", rank=4)
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [yes, optout, no, silent])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    listing = text.split("## 📋 The list")[1]
    assert "- **[Yes](https://x.ai)** 👁 — " in listing
    assert "- **[OptOut](https://x.ai)** 👁 — " in listing
    assert "- **[No](https://x.ai)** — " in listing and "- **[Silent](https://x.ai)** — " in listing
    assert "**👁** — what you send may be used to train models" in listing

    from freetier_radar.render import build_llms_txt, render_site
    site = render_site(reg, Path("templates"), tmp_path / "index.html", today=TODAY)
    assert site.count("👁 may train on prompts</span>") == 1
    assert site.count("👁 may train unless you opt out</span>") == 1
    llms = build_llms_txt([yes, optout, no, silent], TODAY).splitlines()
    parts = {name: next(x for x in llms if x.startswith(f"- [{name}]")).split("; ")
             for name in ("Yes", "OptOut", "No", "Silent")}
    # The row page's sentence, as a clause — one wording wherever it is said.
    assert "what you send may be used to train or improve models" in parts["Yes"]
    assert ("what you send may be used to train or improve models unless you turn that off"
            in parts["OptOut"])
    assert "what you send is not used to train models" in parts["No"]
    assert not any("train" in p for p in parts["Silent"])

    page = build_provider_page(yes, [], TODAY)
    assert ("## What happens to what you send\n\nWhat you send may be used to train or improve "
            "models. In the vendor's words: “Content used to improve our products” "
            "([source](https://x.ai/pricing)).") in page
    assert "improve models unless you turn that off. In" in build_provider_page(optout, [], TODAY)
    assert ("What you send is not used to train models. In the vendor's words: “We never train on "
            "your prompts”") in build_provider_page(no, [], TODAY)
    assert "## What happens to what you send" not in build_provider_page(silent, [], TODAY)


def test_quickstart_is_a_registry_entry_not_a_typed_snippet():
    """The curl at the top of the README is the first thing a reader runs. Typed
    by hand it would outlive the entry it calls; generated, it is archived along
    with it. Only a keyless entry with a callable id can carry it."""
    keyless_no_ids = make(id="k1", name="NoIds",
                          api={"base_url": "https://a.example/v1", "auth": "none"})
    assert build_context([keyless_no_ids], TODAY)["quickstart"] is None
    assert build_context([api_entry(id="groq-free", name="Groq")], TODAY)["quickstart"] is None

    usable = make(id="k2", name="Keyless", rank=1,
                  api={"base_url": "https://b.example/v1/", "auth": "none",
                       "model_ids": ["gpt-oss-120b"],
                       "note": "2 requests per minute, per IP and per model"})
    quickstart = build_context([keyless_no_ids, usable], TODAY)["quickstart"]
    assert quickstart == {"name": "Keyless", "url": "https://x.ai",
                          "base_url": "https://b.example/v1",  # no double slash in the curl
                          "model_id": "gpt-oss-120b",
                          # the rate limit that pays for the missing key travels
                          # with the snippet: the reader meets it on this call
                          "note": "2 requests per minute, per IP and per model",
                          "asks": [],
                          "notice": None,
                          # written once, for the README's code block and the
                          # site's <pre> and copy button alike
                          "curl": "curl -s https://b.example/v1/chat/completions \\\n"
                                  "  -H 'Content-Type: application/json' \\\n"
                                  """  -d '{"model":"gpt-oss-120b","messages":"""
                                  """[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'"""}


def test_the_quickstart_curl_sends_the_session_header_its_lane_asks_for(tmp_path: Path):
    """A keyless lane that wants an id per conversation — opencode Zen answers
    400 MissingSessionID without x-opencode-session — would make the README's
    first command fail as printed. The curl carries the header, and the id is
    made in the reader's shell, so every reader sends their own and the page
    renders the same twice."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="zen", name="Zen", rank=1, api={
        "base_url": "https://zen.example/v1", "auth": "none", "model_ids": ["free-a"],
        "session_header": "x-zen-session"})])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    quickstart = text.split("No account at all?")[1].split("## 📋 The list")[0]
    assert '  -H "x-zen-session: quickstart-$RANDOM$RANDOM" \\\n' in quickstart
    assert "curl -s https://zen.example/v1/chat/completions \\\n" in quickstart
    assert render_readme(reg, Path("templates"), tmp_path / "README2.md", today=TODAY) == text


def test_quickstart_note_reaches_the_page(tmp_path: Path):
    """A keyless lane is rate-limited instead of authenticated, and the README's
    first command is where a reader meets that. The caveat is rendered from the
    entry rather than typed into the template, so it cannot outlive the entry."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="k2", name="Keyless", rank=1,
                             api={"base_url": "https://b.example/v1", "auth": "none",
                                  "model_ids": ["gpt-oss-120b"],
                                  "note": "2 requests per minute, per IP and per model"})])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    quickstart = text.split("No account at all?")[1].split("## 📋 The list")[0]
    assert "2 requests per minute, per IP and per model" in quickstart
    # and it is framed as the demo it is, never as the way to work
    assert "not a setup to write code on" in quickstart


def test_starters_answer_what_to_code_with_before_the_reference_table(tmp_path: Path):
    """The page opened on the keyless curl alone, which is the weakest offer on
    it — a demo capped at a couple of requests a minute. What a reader wants
    first is the agents that run on a $0 plan and the models they hand over, and
    the registry already knows both."""
    from freetier_radar.models import save_registry
    agent = dict(category="agent-cli", api={"base_url": "https://b.example/v1"})
    entries = [
        make(id="second", name="Second", rank=20, **{**agent, "models": [{"family": "m-2"}]}),
        make(id="first", name="First", rank=10, **{**agent, "models": [{"family": "m-1"}]}),
        # free and good and silent about its models — nothing to put in the row
        make(id="modelless", name="Modelless", rank=15, **agent),
        # a card is the one thing this block promises nobody needs
        make(id="paid", name="Paid", rank=1, card_required=True,
             **{**agent, "models": [{"family": "m-3"}]}),
        # an API is not an agent: it answers a different question, further down
        make(id="api", name="Api", rank=1, models=[{"family": "m-4"}]),
    ]
    starters = build_context(entries, TODAY)["starters"]
    assert [s["name"] for s in starters] == ["First", "Second"]
    assert starters[0]["families"] == ["m-1"]

    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    hero = text.split("## 🚀 Start here")[1].split("## 📋 The list")[0]
    assert "`m-1`" in hero and "`m-2`" in hero
    assert "Paid" not in hero and "Modelless" not in hero


def test_starters_are_capped_and_ordered_by_rank():
    """Four is what fits above the fold; the rest are one section down anyway."""
    entries = [make(id=f"a{i}", name=f"A{i}", rank=i, category="agent-cli",
                    models=[{"family": f"m-{i}"}]) for i in range(9, 0, -1)]
    starters = build_context(entries, TODAY)["starters"]
    assert [s["name"] for s in starters] == ["A1", "A2", "A3", "A4"]


def test_context_connections():
    entries = [api_entry(id="groq-free", name="Groq"), make(id="plain")]
    ctx = build_context(entries, TODAY)
    assert ctx["connections"] == [{"name": "Groq", "base_url": "https://api.x.ai/v1",
                                   "page": "https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/",
                                   "anthropic_base_url": "",
                                   "auth": "`GROQ_API_KEY`", "key_url": "https://x.ai/keys",
                                   "keyless": False, "note": ""}]


def test_a_long_connection_note_folds_like_the_prose_columns():
    """The one table `_fold` never reached, and the one cell that keeps growing:
    the note is where a rotating lane, an id spelling or a caveat gets explained.
    Kenari's reached 1,364 characters against a median of 280 and made its row
    four times the width of the table's median."""
    long = ("Every :free id the catalog carries is listed, and the vendor's own flag "
            "is what the probe reads. " * 5).strip()
    ctx = build_context([api_entry(id="long", name="L", api={
        "base_url": "https://api.x.ai/v1", "key_url": "https://x.ai/keys",
        "auth": "api-key", "note": long})], TODAY)
    note = ctx["connections"][0]["note"]
    assert note.startswith("<details><summary>") and note.endswith("</details>")
    assert long in note                        # every character survives the fold
    teaser = note.split("<sub>")[1].split("</sub>")[0]
    assert teaser.endswith(" …") and len(teaser) <= README_NOTE_TEASER + 2


def test_render_readme(tmp_path: Path):
    reg = tmp_path / "registry.yaml"
    from freetier_radar.models import save_registry
    save_registry(reg, [make(), make(id="dead", name="Dead Tool", probe_failures=5)])
    out = tmp_path / "README.md"
    text = render_readme(reg, Path("templates"), out, today=TODAY)
    assert "every%20row%20verified-2026--07--19%20or%20later" in text
    assert "live%20entries-1-58a6ff" in text
    assert "Coding agents & CLIs" in text
    assert "LLM APIs with free tier" in text
    assert "## 📡 How this list stays fresh" in text
    assert "```mermaid" in text
    assert "banner-dark.svg" in text
    assert "## 📦 Archive" in text
    assert "Dead Tool" in text.split("## 📦 Archive")[1]
    assert out.read_text(encoding="utf-8") == text


def watched(name: str = "Example", checked_on: str = "2026-07-01") -> Watched:
    return Watched.model_validate({
        "domains": ["example.ai"], "name": name, "checked_on": checked_on,
        "reason": "no free tier today", "reopen_if": "they publish one"})


def test_watchlist_rows_are_newest_first_and_carry_their_own_freshness():
    old = watched("Old", (TODAY - timedelta(days=WATCH_RECHECK_DAYS + 1)).isoformat())
    ctx = build_context([make()], TODAY, watchlist=[old, watched("New", TODAY.isoformat())])
    assert [w["name"] for w in ctx["watchlist"]] == ["New", "Old"]
    assert [w["current"] for w in ctx["watchlist"]] == [True, False]
    assert ctx["watch_recheck_days"] == WATCH_RECHECK_DAYS


def test_the_watchlist_is_a_page_of_its_own_and_the_readme_links_it(tmp_path: Path):
    """140 verdicts were 108 KB of a 260 KB README on 2026-09-16, loaded by every
    reader who came for the list above them. They live on one page now, with the
    reason, what would reopen it and whether the verdict is still current."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import build_checked_page
    old = watched("Old", (TODAY - timedelta(days=WATCH_RECHECK_DAYS + 1)).isoformat())
    page = build_checked_page([old, watched("New", TODAY.isoformat())], TODAY)
    meta = yaml.safe_load(page.split("---\n")[1])
    assert meta["permalink"] == "/providers/checked/"
    # Dated for the sitemap like every other page under providers/: by its
    # newest verdict, not by the day it was rendered.
    assert meta["last_modified_at"] == TODAY
    assert yaml.safe_load(build_checked_page([old], TODAY).split("---\n")[1])[
        "last_modified_at"] == TODAY - timedelta(days=WATCH_RECHECK_DAYS + 1)
    assert page.index("**New**") < page.index("**Old**")
    assert "no free tier today <sub>**Reopens if:** they publish one</sub>" in page
    assert f"`{(TODAY - timedelta(days=WATCH_RECHECK_DAYS + 1)).isoformat()}` ⏰" in page
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make()])
    (tmp_path / "watchlist.yaml").write_text(yaml.safe_dump({"watched": [
        {"domains": ["example.ai"], "name": "Example", "checked_on": TODAY.isoformat(),
         "reason": "a reason only the page carries", "reopen_if": "they publish one"}]}), encoding="utf-8")
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/providers/checked/" in text
    assert "a reason only the page carries" not in text


def test_a_registry_with_no_watchlist_renders_exactly_as_before():
    assert build_context([make()], TODAY)["watchlist"] == []


def test_index_publishes_the_watchlist_beside_the_entries():
    index = build_index([make()], TODAY, [watched()])
    assert [e["id"] for e in index["entries"]] == ["x"]
    assert index["watchlist"] == [
        {"domains": ["example.ai"], "name": "Example", "checked_on": "2026-07-01",
         "reason": "no free tier today", "reopen_if": "they publish one", "current": True}]


# ---- what changed, and the feed that carries it ---------------------------

def ev(**kw) -> Event:
    return Event.model_validate({"ts": "2026-07-18T05:23:00Z", "event": "added",
                                 "id": "x", "name": "X", "url": "https://x.ai", **kw})


def test_a_registry_with_no_history_renders_exactly_as_before():
    assert build_context([make()], TODAY)["changes"] == []


FIRST_EVENT = datetime(2026, 6, 1, 5, 23, tzinfo=timezone.utc)


def test_the_what_changed_rows_are_newest_first_and_capped():
    events = [ev(id=f"e{n}", name=f"E{n}", ts=FIRST_EVENT + timedelta(days=n))
              for n in range(README_CHANGES + 3)]
    rows = build_context([make()], TODAY, history=events)["changes"]
    assert len(rows) == README_CHANGES
    newest = README_CHANGES + 2
    assert [r["name"] for r in rows] == [f"E{n}" for n in range(newest, newest - README_CHANGES, -1)]
    assert rows[0]["date"] == (FIRST_EVENT + timedelta(days=newest)).date().isoformat()


def test_each_kind_of_event_is_labelled_for_a_reader():
    kinds = ["added", "archived", "restored", "removed", "models"]
    rows = build_context([make()], TODAY,
                         history=[ev(event=k, id=k) for k in kinds])["changes"]
    assert len({r["label"] for r in rows}) == len(kinds)
    assert all(r["label"] for r in rows)


def test_a_pipe_in_an_event_detail_cannot_split_the_table_row():
    rows = build_context([make()], TODAY,
                         history=[ev(detail="free | not free")])["changes"]
    assert rows[0]["detail"] == r"free \| not free"


def test_the_feed_is_well_formed_atom():
    feed = ElementTree.fromstring(build_feed([ev()], TODAY))
    ns = "{http://www.w3.org/2005/Atom}"
    assert feed.tag == f"{ns}feed"
    assert feed.findtext(f"{ns}id") == FEED_URL
    assert feed.findtext(f"{ns}title")
    assert feed.findtext(f"{ns}updated") == "2026-07-18T05:23:00Z"
    assert any(link.get("rel") == "self" and link.get("href") == FEED_URL
               for link in feed.findall(f"{ns}link"))
    entry = feed.find(f"{ns}entry")
    assert entry.findtext(f"{ns}title") == "Added: X"
    assert entry.findtext(f"{ns}updated") == "2026-07-18T05:23:00Z"
    assert entry.findtext(f"{ns}summary") is not None
    assert entry.find(f"{ns}link").get("href") == "https://x.ai"


def test_every_feed_entry_has_its_own_permanent_id():
    events = [ev(id="a", ts="2026-07-18T05:23:00Z"),
              ev(id="a", event="models", ts="2026-07-18T05:23:00Z"),
              ev(id="a", event="models", ts="2026-07-18T06:23:00Z")]
    ns = "{http://www.w3.org/2005/Atom}"
    ids = [e.findtext(f"{ns}id")
           for e in ElementTree.fromstring(build_feed(events, TODAY)).findall(f"{ns}entry")]
    assert len(set(ids)) == 3
    assert all(i.startswith("tag:") for i in ids)


def test_the_feed_escapes_what_would_otherwise_break_the_xml():
    feed = build_feed([ev(name="A & B <script>", detail="1 < 2 & 3 > 2")], TODAY)
    assert "<script>" not in feed
    entry = ElementTree.fromstring(feed).find("{http://www.w3.org/2005/Atom}entry")
    assert entry.findtext("{http://www.w3.org/2005/Atom}title") == "Added: A & B <script>"


def test_the_feed_carries_the_newest_events_first_and_stops_at_the_cap():
    events = [ev(id=f"e{n}", ts=FIRST_EVENT + timedelta(days=n))
              for n in range(FEED_ENTRIES + 3)]
    ns = "{http://www.w3.org/2005/Atom}"
    parsed = ElementTree.fromstring(build_feed(events, TODAY))
    stamps = [e.findtext(f"{ns}updated") for e in parsed.findall(f"{ns}entry")]
    assert len(stamps) == FEED_ENTRIES
    assert stamps == sorted(stamps, reverse=True)
    assert parsed.findtext(f"{ns}updated") == stamps[0]


def test_an_empty_history_still_produces_a_valid_feed():
    ns = "{http://www.w3.org/2005/Atom}"
    parsed = ElementTree.fromstring(build_feed([], TODAY))
    assert parsed.findall(f"{ns}entry") == []
    assert parsed.findtext(f"{ns}updated") == "2026-07-19T00:00:00Z"


def test_render_writes_the_feed_beside_the_other_artifacts(tmp_path: Path):
    from freetier_radar.history import append_history
    from freetier_radar.models import save_registry
    save_registry(tmp_path / "registry.yaml", [make()])
    append_history(tmp_path / "history.jsonl", [ev()])

    render_artifacts(tmp_path / "registry.yaml", tmp_path, today=TODAY)

    feed = (tmp_path / "feed.xml").read_text(encoding="utf-8")
    assert feed.startswith("<?xml")
    assert "Added: X" in feed


def test_the_readme_shows_what_changed_and_links_the_feed(tmp_path: Path):
    from freetier_radar.history import append_history
    from freetier_radar.models import save_registry
    save_registry(tmp_path / "registry.yaml", [make()])
    append_history(tmp_path / "history.jsonl", [ev(name="Newcomer", detail="10 free calls")])

    text = render_readme(tmp_path / "registry.yaml", Path("templates"),
                         tmp_path / "README.md", today=TODAY)

    changed = text.split("## 📦 Archive")[0]
    assert "Newcomer" in changed
    assert "10 free calls" in changed
    assert FEED_URL in text


def test_a_departing_entry_is_not_summarised_by_the_models_it_no_longer_serves():
    ns = "{http://www.w3.org/2005/Atom}"
    feed = build_feed([ev(event="removed", models=["gpt-oss"], detail="")], TODAY)
    summary = ElementTree.fromstring(feed).find(f"{ns}entry").findtext(f"{ns}summary")
    assert "gpt-oss" not in summary


def test_an_event_with_nothing_to_say_renders_a_dash_like_every_other_empty_cell():
    rows = build_context([make()], TODAY, history=[ev(event="removed", detail="")])["changes"]
    assert rows[0]["detail"] == "—"


def test_a_delisting_event_says_why_from_the_row_the_archive_keeps():
    """"➖ Delisted Kenari —" was all the page said about four rows on
    2026-09-17. The rows are in the Archive now, each with its reason, and the
    events the history already holds read it from there."""
    gone = make(id="gone", name="Gone", delisted={"on": TODAY, "reason": "the free lane is gone"})
    delisting = ev(event="removed", id="gone", name="Gone", detail="")
    rows = build_context([make(), gone], TODAY, history=[delisting])["changes"]
    assert rows[0]["detail"] == "the free lane is gone"
    ns = "{http://www.w3.org/2005/Atom}"
    feed = ElementTree.fromstring(build_feed([delisting], TODAY, entries=[make(), gone]))
    assert feed.find(f"{ns}entry").findtext(f"{ns}summary") == "the free lane is gone"


def test_an_event_about_an_archived_row_links_its_page_not_the_vendor():
    """Kenari is on the blocklist for pooled consumer accounts, and on 2026-09-17
    "What changed" and three feed entries still linked kenari.id. An event about
    a row in the Archive links the row's page, like the Archive does."""
    gone = make(id="gone", name="Gone", url="https://gone.example",
                delisted={"on": TODAY, "reason": "rejected for cause"})
    events = [ev(id="gone", name="Gone", url="https://gone.example"),
              ev(event="removed", id="gone", name="Gone", url="https://gone.example",
                 ts="2026-07-19T05:23:00Z")]
    page = "https://mvalentsev.github.io/awesome-free-ai-coding/providers/gone/"
    rows = build_context([make(), gone], TODAY, history=events)["changes"]
    assert [r["url"] for r in rows] == [page, page]
    feed = build_feed(events, TODAY, entries=[make(), gone])
    assert "https://gone.example" not in feed and page in feed


def test_a_provider_page_says_why_a_row_was_delisted_once_and_not_which_models_it_had():
    """The header says why the row left, with the reviewer's date. A deletion
    recorded before rows were archived carries no reason of its own, and the
    page used to borrow the header's under the older date — Puter's history
    read "2026-07-19 — Delisted: … the endpoint read on 2026-09-14 …"."""
    from freetier_radar.render import build_provider_page
    gone = make(id="gone", name="Gone", models=[{"family": "a"}],
                delisted={"on": TODAY, "reason": "the free lane is gone"})
    page = build_provider_page(gone, [ev(id="gone", name="Gone"),
                                      ev(event="removed", id="gone", name="Gone", models=["a"],
                                         ts="2026-07-19T05:23:00Z")], TODAY)
    body = page.split("{% raw %}")[1]
    assert body.count("the free lane is gone") == 1
    assert _history_lines(page)[0] == "- `2026-07-19` — Delisted"


@pytest.mark.parametrize("kind, word", [
    ("added", "Added"), ("archived", "Archived"), ("restored", "Restored"),
    ("removed", "Delisted"), ("models", "Free models changed")])
def test_an_event_goes_by_one_word_wherever_it_is_named(kind, word):
    """The README said "➕ Added", the row's page "Added to the list" and the
    feed "New:", each from a table of its own: four tables for five events, and
    a word changed in one never reached the others."""
    from freetier_radar.announce import build_digest
    from freetier_radar.render import build_provider_page

    row = make(id="row", name="Row")
    event = ev(event=kind, id="row", name="Row", detail="what happened")
    label = build_context([row], TODAY, history=[event])["changes"][0]["label"]
    assert label.split(" ", 1)[1] == word
    ns = "{http://www.w3.org/2005/Atom}"
    feed = ElementTree.fromstring(build_feed([event], TODAY, entries=[row]))
    assert feed.find(f"{ns}entry").findtext(f"{ns}title") == f"{word}: Row"
    assert _history_lines(build_provider_page(row, [event], TODAY)) == [
        f"- `2026-07-18` — {word}: what happened"]
    _, digest = build_digest([row], [event], date(2026, 8, 3))
    assert f"— {word}: **Row** — what happened" in digest


def test_the_digest_says_why_a_row_was_delisted_as_the_readme_does():
    """The monthly digest composed its lines on its own and printed a deletion
    recorded before rows were archived as a bare "Delisted", where the README
    and the feed read the reason the Archive keeps."""
    from freetier_radar.announce import build_digest
    gone = make(id="gone", name="Gone", delisted={"on": TODAY, "reason": "the free lane is gone"})
    removal = ev(event="removed", id="gone", name="Gone", detail="")
    _, digest = build_digest([make(), gone], [removal], date(2026, 8, 3))
    assert "— Delisted: **Gone** — the free lane is gone" in digest


def test_the_archive_says_why_each_row_left_and_links_its_page_not_the_vendor(tmp_path: Path):
    """On 2026-09-17 every row in the Archive showed a "Last verified" date later
    than the day its vendor had ended the offer: the probes anchored on pages
    that outlived the offers and kept passing until a reviewer entered the
    vendor's date. And the heading said the rows had "stopped verifying" when
    all three were archived by that date with their probes still passing. A row
    in the Archive says why it left, and links the page carrying the evidence
    rather than a vendor page that is dead, or worse."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    retired = make(id="gone", name="Gone", url="https://gone.example",
                   retired_on=TODAY - timedelta(days=30), last_verified=TODAY - timedelta(days=10))
    save_registry(reg, [make(), retired])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    archive = text.split("## 📦 Archive")[1].split("\n## ")[0]
    assert "[Gone](https://mvalentsev.github.io/awesome-free-ai-coding/providers/gone/)" in archive
    assert "vendor-announced shutdown on 2026-06-19" in archive
    assert "https://gone.example" not in archive
    assert "2026-07-09" not in archive
    assert "stopped verifying" not in archive


def test_the_archive_lists_the_latest_departure_first():
    older = make(id="older", name="Older", retired_on=TODAY - timedelta(days=40))
    newer = make(id="newer", name="Newer", delisted={"on": TODAY - timedelta(days=2), "reason": "taken off"})
    assert [r["name"] for r in build_context([older, make(), newer], TODAY)["archived"]] == ["Newer", "Older"]


def test_rendering_refuses_a_registry_that_lost_a_row_the_history_recorded(tmp_path: Path):
    """The page is where a deleted row would silently disappear from, so the
    render is the last place that can refuse it: a row leaves through the Archive."""
    from freetier_radar.history import append_history
    from freetier_radar.models import save_registry
    save_registry(tmp_path / "registry.yaml", [make()])
    append_history(tmp_path / "history.jsonl", [ev(), ev(id="gone", name="Gone")])
    with pytest.raises(ValueError, match="gone"):
        render_readme(tmp_path / "registry.yaml", Path("templates"), tmp_path / "README.md", today=TODAY)
    with pytest.raises(ValueError, match="gone"):
        render_artifacts(tmp_path / "registry.yaml", tmp_path, today=TODAY)


def test_picks_answer_by_need_from_the_registry():
    """The question a reader arrives with is rarely "what is on the list" and
    usually "which one, for me" — the strongest models, the key that gets the
    most done, no account at all. Other lists type that table by hand and it
    rots; here every cell is the top of a section in the registry's own order,
    so a row that dies takes its recommendation with it."""
    entries = [
        make(id="api-1", name="Api1", rank=10, models=[{"family": "f-1", "tier": "frontier"}]),
        # rank orders a row inside its section only; across sections the
        # frontier answer leads with whoever hands over the most such families
        make(id="api-2", name="Api2", rank=20,
             models=[{"family": "f-4", "tier": "frontier"}, {"family": "f-5", "tier": "frontier"}]),
        make(id="api-3", name="Api3", rank=30),
        make(id="api-4", name="Api4", rank=40),
        # a card is the one thing this block promises nobody needs
        make(id="api-card", name="ApiCard", rank=1, card_required=True,
             models=[{"family": "f-2", "tier": "frontier"}]),
        make(id="agent", name="Agent", rank=5, category="agent-cli",
             models=[{"family": "f-3", "tier": "frontier"}, {"family": "s-1"}]),
        # a superseded family is no longer what the row hands you
        make(id="old", name="Old", rank=99, category="agent-cli",
             models=[{"family": "f-old", "tier": "frontier", "superseded_by": "f-new"}]),
        make(id="agg", name="Agg", rank=1, category="aggregator"),
        make(id="trial", name="Trial", rank=1, category="trial"),
        make(id="trial-card", name="TrialCard", rank=0, category="trial", card_required=True),
        make(id="keyless", name="Keyless", rank=50,
             api={"base_url": "https://k.example/v1", "auth": "none", "model_ids": ["m"]}),
    ]
    picks = build_context(entries, TODAY)["picks"]
    # capped, ranked, and never a row that asks for a card
    assert [p["name"] for p in picks["apis"]] == ["Api1", "Api2", "Api3"]
    # the frontier answer names the families that earn it, across sections
    assert [(p["name"], p["families"]) for p in picks["frontier"]] == [
        ("Api2", ["f-4", "f-5"]), ("Agent", ["f-3"]), ("Api1", ["f-1"])]
    assert [p["name"] for p in picks["aggregators"]] == ["Agg"]
    assert [p["name"] for p in picks["keyless"]] == ["Keyless"]
    assert [p["name"] for p in picks["trials"]] == ["Trial"]


def test_picks_are_capped_at_the_same_three_per_need():
    entries = [make(id=f"a{i}", name=f"A{i}", rank=i) for i in range(6, 0, -1)]
    picks = build_context(entries, TODAY)["picks"]
    assert [p["name"] for p in picks["apis"]] == ["A1", "A2", "A3"]
    assert picks["frontier"] == [] and picks["keyless"] == []


def test_picks_render_between_the_starters_and_the_list(tmp_path: Path):
    from freetier_radar.models import save_registry
    entries = [
        make(id="agent", name="Agent", rank=5, category="agent-cli",
             models=[{"family": "f-3", "tier": "frontier"}]),
        make(id="api-1", name="Api1", rank=10),
        make(id="agg", name="Agg", rank=1, category="aggregator"),
    ]
    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    hero = text.split("## 🚀 Start here")[1].split("## 📋 The list")[0]
    assert "**Or pick by what you need:**" in hero
    assert "- **Frontier-tier models on a $0 plan** — [Agent](https://x.ai) `f-3`" in hero
    assert "[Api1](https://x.ai)" in hero and "[Agg](https://x.ai)" in hero
    # a need nobody on the registry answers is not a line that says so
    assert "No account at all" not in hero.split("**Or pick by what you need:**")[1]
    assert "asks for no card" not in hero.split("**Or pick by what you need:**")[1]


def test_the_hero_counters_fit_a_phone(tmp_path: Path):
    """GitHub pads every table cell thirteen pixels a side, so five counters
    spent 130 of the 309 pixels a phone gives the README on padding alone, and
    the table under the badges scrolled sideways with its last figure cut off
    (2026-09-25, 390 pixels). Four fit with room to spare; the count of
    OpenAI-compatible endpoints that the fifth carried is stated under Plug it
    into your agent, where the connections are."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="a", name="A", models=[{"family": "m"}])])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    hero = text.split("## 🚀 Start here")[0]
    counters = next(line for line in hero.splitlines() if line.startswith("| **"))
    assert counters.count("|") - 1 == 4
    assert "<sub>live offers</sub>" in hero and "<sub>free model families</sub>" in hero


def test_the_start_blocks_are_lists_like_the_rows(tmp_path: Path):
    """The agents and the picks were tables, and a phone gives a table the
    screen's width and no more: the agents' models broke at every hyphen,
    `mimo-` above `v2.5`, in a column a third of the screen wide, and four
    agents stood 773 pixels tall. As list items they take the whole width."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="ag", name="Ag", category="agent-cli",
                             models=[{"family": "m-1"}, {"family": "m-2"}]),
                        make(id="api", name="Api")])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    start = text.split("## 🚀 Start here")[1].split("## 📋 The list")[0]
    assert "\n- **[Ag](https://x.ai)** — `m-1` · `m-2`\n" in start
    assert "\n- **An API key that gets the most done for free** — [Api](https://x.ai)\n" in start
    assert "| Agent |" not in start and "| I want… |" not in start


def test_a_registry_with_nothing_to_pick_renders_no_picks_table(tmp_path: Path):
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="paid", name="Paid", card_required=True)])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    assert "Or pick by what you need" not in text


def test_a_lane_that_wants_a_session_id_per_conversation_stays_out_of_the_static_configs(
        tmp_path: Path):
    """opencode Zen has answered a free id without x-opencode-session with 400
    MissingSessionID since 2026-09-07, and the rule OpenCode's team gives other
    clients is a stable id per conversation. A LiteLLM or opencode.json entry is
    written once and cannot mint one, so either would hand a reader a model
    that fails on its first call. The row is left out of both, and everything
    that tells a reader how to connect names the header instead."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import build_llms_txt, build_provider_page
    zen = api_entry(id="zen", name="Zen", api={
        "base_url": "https://zen.example/v1", "key_url": "https://zen.example/auth",
        "model_ids": ["free-a"], "session_header": "x-zen-session"})
    plain = api_entry(id="plain", name="Plain", models=[{"family": "m"}],
                      api={"base_url": "https://api.x.ai/v1", "model_ids": ["m"]})
    entries = [zen, plain]

    assert [m["model_name"] for m in build_litellm_config(entries, TODAY)["model_list"]] == [
        "plain/m"]
    assert set(build_opencode_config(entries, TODAY)["provider"]) == {"plain"}

    env = build_env_example(entries, TODAY)
    assert 'export ZEN_API_KEY=""' in env
    assert "x-zen-session" in env.split("# ── Zen")[1].split("# ──")[0]

    by_name = {c["name"]: c for c in build_context(entries, TODAY)["connections"]}
    assert "`x-zen-session`" in by_name["Zen"]["auth"]
    assert "session" not in by_name["Plain"]["auth"]

    assert "- Session header: `x-zen-session`" in build_provider_page(zen, [], TODAY)
    assert "x-zen-session" in build_llms_txt(entries, TODAY)

    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    render_artifacts(reg, tmp_path, today=TODAY)
    litellm = (tmp_path / "configs" / "litellm.yaml").read_text(encoding="utf-8")
    assert "zen/free-a" not in litellm
    assert "# Left out: Zen" in litellm and "x-zen-session" in litellm
    assert "plain/m" in litellm


def test_claude_code_picks_and_connections_come_from_the_anthropic_field(tmp_path: Path):
    """"Claude Code on a free lane" is the question the 27,000-star routers
    answer by re-exposing paid sessions. The legal answer is a gateway whose
    vendor documents an Anthropic-format route, and the registry now names it
    per row — so the picks table, the connection table and the shell file all
    read the same field, and a route the probe reports gone leaves all three."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import build_claude_code_sh
    entries = [
        make(id="gw-one", name="GwOne", rank=10, category="aggregator",
             api={"base_url": "https://one.example/v1", "key_url": "https://one.example/keys",
                  "anthropic_base_url": "https://one.example",
                  "model_ids": ["vendor/model-a:free", "vendor/model-b:free"]}),
        make(id="gw-card", name="GwCard", rank=1, category="aggregator", card_required=True,
             api={"base_url": "https://card.example/v1", "anthropic_base_url": "https://card.example"}),
        make(id="gw-plain", name="GwPlain", rank=5, category="aggregator",
             api={"base_url": "https://plain.example/v1"}),
        make(id="gw-noids", name="GwNoIds", rank=20,
             api={"base_url": "https://noids.example/v1", "anthropic_base_url": "https://noids.example/anthropic"}),
    ]
    ctx = build_context(entries, TODAY)
    assert [p["name"] for p in ctx["picks"]["claude_code"]] == ["GwOne", "GwNoIds"]
    by_name = {c["name"]: c for c in ctx["connections"]}
    assert by_name["GwOne"]["anthropic_base_url"] == "https://one.example"
    assert by_name["GwPlain"]["anthropic_base_url"] == ""

    sh = build_claude_code_sh(entries, TODAY)
    assert "claude-gw-one()" in sh and "claude-gw-noids()" in sh and "claude-gw-card()" in sh
    assert "claude-gw-plain" not in sh
    block = sh.split("claude-gw-one()")[1].split("claude-gw-")[0]
    assert 'ANTHROPIC_BASE_URL="https://one.example"' in block
    assert 'ANTHROPIC_AUTH_TOKEN="$GW_ONE_API_KEY"' in block
    assert 'ANTHROPIC_API_KEY=""' in block
    assert 'ANTHROPIC_MODEL="vendor/model-a:free"' in block
    noids = sh.split("claude-gw-noids()")[1]
    assert "ANTHROPIC_MODEL=" not in noids.split("}")[0]

    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    hero = text.split("## 🚀 Start here")[1].split("## 📋 The list")[0]
    assert "- **Claude Code on a free lane** — [GwOne](https://x.ai) · [GwNoIds](https://x.ai)\n" in hero
    from freetier_radar.render import CONFIGS_README, render_configs_readme
    plug = render_configs_readme(reg, Path("templates"), tmp_path / CONFIGS_README, today=TODAY)
    assert "`https://one.example`" in plug and "claude-code.sh" in plug
    render_artifacts(reg, tmp_path, today=TODAY)
    assert "claude-gw-one()" in (tmp_path / "configs" / "claude-code.sh").read_text(encoding="utf-8")


def test_a_provider_page_carries_the_evidence_and_the_history():
    """Search lands on a question — "groq free tier limits" — not on a list of
    fifty rows. A page per provider answers it with the row's own fields, the
    evidence the probe reads and the row's history, and it is generated, so it
    can never say something the registry stopped backing."""
    from freetier_radar.render import build_provider_page, provider_page_url
    e = make(id="groq-free", name="Groq", limits="30 req/min on the free plan",
             source_urls=["https://x.ai/docs/limits"],
             models=[{"family": "llama-3.3"}, {"family": "old", "superseded_by": "new"}],
             api={"base_url": "https://api.x.ai/v1", "key_url": "https://x.ai/keys",
                  "model_ids": ["llama-3.3-70b"], "anthropic_base_url": "https://x.ai/anthropic",
                  "note": "ids are case-sensitive"})
    events = [Event(ts=datetime(2026, 7, 1, tzinfo=timezone.utc), event=EventType.ADDED,
                    id="groq-free", name="Groq", url="https://x.ai", models=["llama-3.3"],
                    detail="stuff"),
              Event(ts=datetime(2026, 7, 2, tzinfo=timezone.utc), event=EventType.ADDED,
                    id="other", name="Other", url="https://o.ai")]
    page = build_provider_page(e, events, TODAY)
    front = yaml.safe_load(page.split("---\n")[1])
    assert front["permalink"] == "/providers/groq-free/"
    assert "Groq" in front["title"] and "2026-07-19" in front["title"]
    assert "30 req/min" in front["description"]
    # Liquid never sees the vendor's words: a "{{" in a quote cannot break the build
    body = page.split("{% raw %}")[1].split("{% endraw %}")[0]
    assert "30 req/min on the free plan" in body
    assert "`llama-3.3`" in body and "`old`" not in body
    assert "https://api.x.ai/v1" in body and "GROQ_API_KEY" in body and "https://x.ai/keys" in body
    assert "https://x.ai/anthropic" in body and "llama-3.3-70b" in body and "case-sensitive" in body
    assert "https://x.ai/docs/limits" in body and "https://x.ai" in body
    assert "2026-07-01" in body and "stuff" in body and "Other" not in body
    assert provider_page_url("groq-free") == "https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/"


def _history_lines(page: str) -> list[str]:
    block = page.split("## History")[1].split("\n---\n")[0]
    return [line for line in block.splitlines() if line.startswith("- ")]


def test_the_render_records_a_change_before_it_writes_the_pages(tmp_path: Path):
    """history.jsonl was written by the scheduled run alone, so a row added by
    hand was on the README the day it was committed and in its own page's
    history days later: Sail Research read "added on 2026-09-21" above
    "2026-09-24 — Added to the list", and the lines between a commit and the
    run were a guess without a date. The render records every change the
    commit makes, before it writes a page that shows it."""
    from freetier_radar.history import load_history
    from freetier_radar.models import save_registry
    from freetier_radar.render import render_repository

    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="new", name="New", offering="free models, no card")])
    now = datetime(2026, 7, 19, 9, 30, tzinfo=timezone.utc)
    written = render_repository(reg, Path("templates"), tmp_path, today=TODAY, now=now,
                                committed="")

    assert [(e.event, e.id, e.ts) for e in written] == [(EventType.ADDED, "new", now)]
    assert load_history(tmp_path / "history.jsonl") == written
    page = (tmp_path / "providers" / "new.md").read_text(encoding="utf-8")
    assert _history_lines(page) == ["- `2026-07-19` — Added: free models, no card"]
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "| `2026-07-19` | ➕ Added **[New]" in readme


def test_the_check_finds_a_history_the_registry_has_moved_past(tmp_path: Path):
    """A commit that changed the registry and not the log would publish pages
    with no line for the change and a feed that never mentions it."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import check_rendered, render_all, render_repository

    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="a", name="A")])
    render_repository(reg, Path("templates"), tmp_path, today=TODAY,
                      now=datetime(2026, 7, 19, 9, 30, tzinfo=timezone.utc), committed="")
    assert check_rendered(reg, Path("templates"), tmp_path) == []

    save_registry(reg, [make(id="a", name="A"), make(id="b", name="B")])
    render_all(reg, Path("templates"), tmp_path, today=TODAY)
    assert check_rendered(reg, Path("templates"), tmp_path) == ["history.jsonl"]


def test_an_archived_provider_page_says_so_and_why():
    from freetier_radar.render import build_provider_page
    page = build_provider_page(make(id="dead", name="Dead", probe_failures=3), [], TODAY)
    front = yaml.safe_load(page.split("---\n")[1])
    assert "archived" in front["title"].lower()
    assert "3 failed probes" in page


def test_an_archived_page_is_an_epitaph_not_instructions():
    """On 2026-09-17 an archived page still carried a Connect section — AI21's
    sent a reader to a sign-up that now lands on a homepage — flagged a dead row
    as provisional, and closed with "re-verified twice a week" about a row no
    probe reads. The title said "when it stopped verifying" of three rows that
    were still passing their probes when their vendors' dates archived them."""
    from freetier_radar.render import build_provider_page
    gone = make(id="gone", name="Gone", provisional=True, retired_on=TODAY,
                api={"base_url": "https://api.gone.example/v1", "key_url": "https://gone.example/signup"})
    page = build_provider_page(gone, [], TODAY)
    front = yaml.safe_load(page.split("---\n")[1])
    assert "stopped verifying" not in front["title"]
    assert "## Connect" not in page and "https://gone.example/signup" not in page
    assert "provisional" not in page
    assert "re-verified twice a week" not in page
    assert "No probe reads this row any more" in page


def test_a_row_its_probe_archived_is_still_read_and_its_page_says_so():
    from freetier_radar.render import build_provider_page
    page = build_provider_page(make(id="failing", probe_failures=3), [], TODAY)
    assert "the first probe it passes brings it back" in page


def test_the_page_of_a_row_on_a_blocklisted_domain_links_nowhere_near_it():
    """Two archived rows sit on the blocklist, one of them a page that plants
    instructions for AI agents. The Archive keeps the record as text: no link on
    this site sends a reader, or an agent reading along, to the service."""
    from freetier_radar.render import build_provider_page
    row = make(id="bad", name="Bad", url="https://bad.example", source_urls=["https://bad.example/docs"],
               delisted={"on": TODAY, "reason": "rejected for cause"},
               probe={"type": "page-keywords", "endpoint": "https://bad.example/pricing",
                      "keywords": ["bad-mini-2"]})
    page = build_provider_page(row, [], TODAY, blocked=True)
    assert "](https://bad.example" not in page and "<https://bad.example" not in page
    assert "bad.example" in page


def test_the_providers_index_says_why_each_archived_row_left():
    from freetier_radar.render import build_providers_index
    gone = make(id="gone", name="Gone", retired_on=TODAY - timedelta(days=30),
                last_verified=TODAY - timedelta(days=10))
    archived = build_providers_index([make(), gone], TODAY).split("## Archived")[1]
    assert "vendor-announced shutdown on 2026-06-19" in archived
    assert "2026-07-09" not in archived


def test_the_litellm_command_this_repo_prints_listens_on_localhost_only(tmp_path: Path):
    """LiteLLM's proxy binds 0.0.0.0 unless told otherwise (`--host` defaults to
    it in proxy_cli.py), and the config this repo generates sets no master key —
    the reader's own provider keys ride in from the environment. Run as printed,
    it put every one of those keys in front of the whole network the laptop was
    on. Both places the command is printed name the loopback address."""
    import re
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(api={"base_url": "https://api.x.ai/v1", "model_ids": ["m"]})])
    render_artifacts(reg, tmp_path, today=TODAY)
    readme = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    header = (tmp_path / "configs" / "litellm.yaml").read_text(encoding="utf-8")
    for text in (header, readme):
        commands = re.findall(r"litellm --config \S+[^`\n]*", text)
        assert commands and all("--host 127.0.0.1" in c for c in commands), commands


def test_render_writes_a_page_per_entry_and_removes_the_stale_ones(tmp_path: Path):
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="b", name="B"), make(id="a", name="A", probe_failures=3)])
    providers = tmp_path / "providers"
    providers.mkdir()
    (providers / "gone.md").write_text("a row that left the registry", encoding="utf-8")
    (providers / "notes.txt").write_text("not ours", encoding="utf-8")
    render_artifacts(reg, tmp_path, today=TODAY)
    assert sorted(p.name for p in providers.iterdir()) == ["a.md", "b.md", "checked.md", "index.md", "notes.txt"]
    index = (providers / "index.md").read_text(encoding="utf-8")
    assert yaml.safe_load(index.split("---\n")[1])["permalink"] == "/providers/"
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/providers/b/" in index
    # live rows first, the archive after
    assert index.index("[B]") < index.index("[A]")


def test_the_readme_dates_link_to_the_provider_pages(tmp_path: Path):
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="x", name="X"), make(id="gone", name="Gone", probe_failures=3)])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    assert "[verified 2026-07-19](https://mvalentsev.github.io/awesome-free-ai-coding/providers/x/)" in text
    assert "[Gone](https://mvalentsev.github.io/awesome-free-ai-coding/providers/gone/)" in text
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/providers/" in text
    index = build_index([make()], TODAY)
    assert index["entries"][0]["page"] == "https://mvalentsev.github.io/awesome-free-ai-coding/providers/x/"


def test_the_evidence_line_names_the_keywords_that_live_in_the_page_data():
    """Upstage and trae anchor entirely on bytes a reader never sees, and the
    evidence line rendered "anchored on " and stopped there."""
    from freetier_radar.render import build_provider_page
    probe = {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": [],
             "machinery_keywords": ['"name":"free"', '"basic_usage_limit":3']}
    page = build_provider_page(make(probe=probe), [], TODAY)
    assert 'anchored on `"name":"free"`, `"basic_usage_limit":3` in the page\'s own data' in page
    both = build_provider_page(make(probe={**probe, "keywords": ["5000 / month"]}), [], TODAY)
    assert 'anchored on `5000 / month` and `"name":"free"`, ' \
           '`"basic_usage_limit":3` in the page\'s own data' in both


def test_the_evidence_line_names_the_lane_a_family_must_sit_in():
    """A lane document lists paid models too — Cline's names the ClinePass plan
    beside the free lane — so "the models catalog at" that URL would tell a
    reader every model in it is the evidence."""
    from freetier_radar.render import build_provider_page
    probe = {"type": "api-models", "endpoint": "https://x.ai/recommended-models", "lane": "free"}
    page = build_provider_page(make(probe=probe), [], TODAY)
    evidence = next(line for line in page.splitlines() if line.startswith("- Probe:"))
    assert "`free`" in evidence and "<https://x.ai/recommended-models>" in evidence


# ---- llms.txt: the whole list as one text file an LLM search can read


def _api(**kw) -> dict:
    return {"base_url": "https://x.ai/v1", "auth": "none", "openai_compatible": True, **kw}


def test_llms_txt_opens_with_the_title_and_links_the_machine_readable_files():
    from freetier_radar.render import build_llms_txt
    text = build_llms_txt([make()], TODAY)
    assert text.startswith("# awesome-free-ai-coding\n\n> ")
    assert "2026-07-19" in text.split("\n\n")[1]
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/index.json" in text
    assert FEED_URL in text
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/providers/" in text


def test_llms_txt_lists_live_rows_under_their_section_and_archived_rows_apart():
    from freetier_radar.render import build_llms_txt
    live = make(id="x", name="X", offering="stuff", api=_api(),
                models=[{"family": "a"}, {"family": "old", "superseded_by": "a"}])
    gone = make(id="gone", name="Gone", probe_failures=3)
    text = build_llms_txt([live, gone], TODAY)
    assert "## LLM APIs with free tier" in text
    line = next(l for l in text.splitlines() if l.startswith("- [X]"))
    assert line.startswith("- [X](https://mvalentsev.github.io/awesome-free-ai-coding/providers/x/): stuff")
    assert "no card" in line and "no key" in line and "https://x.ai/v1" in line
    assert "`a`" in line and "old" not in line
    archived = text.split("## Archived")[1]
    assert "- [Gone](https://mvalentsev.github.io/awesome-free-ai-coding/providers/gone/)" in archived
    assert "[X]" not in archived


def test_llms_txt_says_why_an_archived_row_left():
    from freetier_radar.render import build_llms_txt
    text = build_llms_txt([make(), make(id="gone", name="Gone", probe_failures=3)], TODAY)
    assert "stopped answering their probe" not in text
    assert "no longer listed — 3 failed probes in a row, last passed 2026-07-19" in text


def test_index_json_says_why_an_archived_row_left():
    rows = build_index([make(), make(id="gone", retired_on=TODAY)], TODAY)["entries"]
    assert "archived_because" not in rows[0]
    assert rows[1]["archived_because"] == "vendor-announced shutdown on 2026-07-19"


def test_llms_txt_says_when_a_row_wants_a_card_or_a_key():
    from freetier_radar.render import build_llms_txt
    row = make(card_required=True, api=_api(auth="api-key", key_url="https://x.ai/keys"))
    line = next(l for l in build_llms_txt([row], TODAY).splitlines() if l.startswith("- [X]"))
    assert "card required" in line
    assert "key from https://x.ai/keys" in line
    assert "no key" not in line


def test_render_artifacts_writes_llms_txt(tmp_path: Path):
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make()])
    render_artifacts(reg, tmp_path, today=TODAY)
    assert (tmp_path / "llms.txt").read_text(encoding="utf-8").startswith("# awesome-free-ai-coding")


def test_the_readme_links_the_browse_page_and_llms_txt(tmp_path: Path):
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make()])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    assert "https://mvalentsev.github.io/awesome-free-ai-coding/browse.html" in text
    assert "[`llms.txt`](llms.txt)" in text


NOTICE = {"since": "2026-07-18", "text": "The vendor refuses every client but its own.",
          "url": "https://github.com/zen/zen/issues/1"}


def _noticed(**api) -> Entry:
    return make(id="zen", name="Zen", rank=1, api={
        "base_url": "https://zen.example/v1", "auth": "none", "model_ids": ["free-a"],
        "note": "rate-limited per IP", "notice": NOTICE, **api})


def test_a_notice_on_the_quickstart_lane_is_a_warning_right_under_the_curl(tmp_path: Path):
    """The README's first command is where a reader finds out a lane stopped
    working. When the list knows — opencode Zen refusing every client but
    OpenCode from 2026-09-17, with the vendor silent — the page says so in a
    callout directly under the command, dated and linked, above the lane's
    usual caveat; and a lane with nothing to own up to renders no callout."""
    from freetier_radar.models import save_registry
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [_noticed()])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    quickstart = text.split("No account at all?")[1].split("## 📋 The list")[0]
    after_curl = quickstart.split("```bash\n")[1].split("```\n", 1)[1]
    assert after_curl.startswith(
        "> [!WARNING]\n"
        "> **This command does not work right now** — [since 2026-07-18]"
        "(https://github.com/zen/zen/issues/1). The vendor refuses every client but its own.\n")
    assert after_curl.index("[!WARNING]") < after_curl.index("rate-limited per IP")

    save_registry(reg, [_noticed(notice=None)])
    plain = render_readme(reg, Path("templates"), tmp_path / "README2.md", today=TODAY)
    assert "[!WARNING]" not in plain


def test_a_notice_reaches_every_place_that_tells_a_reader_how_to_connect(tmp_path: Path):
    """A reader copying the base URL from the connection table, landing on the
    provider page from a search, or asking a model that read llms.txt meets the
    same lane — so each of them carries the notice, not only the quickstart."""
    from freetier_radar.render import build_llms_txt, build_provider_page
    row = _noticed()
    note = build_context([row], TODAY)["connections"][0]["note"]
    assert note.startswith("⚠️ <sub>**Does not work as published since "
                           "[2026-07-18](https://github.com/zen/zen/issues/1).**</sub><br>")
    assert "The vendor refuses every client but its own." in note
    assert note.index("refuses every client") < note.index("rate-limited per IP")

    page = build_provider_page(row, [], TODAY)
    body = page.split("{% raw %}")[1].split("## What you get")[0]
    assert ("> ⚠️ **Does not work as published since [2026-07-18]"
            "(https://github.com/zen/zen/issues/1).** The vendor refuses every client but its own."
            ) in body

    line = next(l for l in build_llms_txt([row], TODAY).splitlines() if l.startswith("- [Zen]"))
    assert ("no key; does not work as published since 2026-07-18: "
            "The vendor refuses every client but its own") in line


def test_the_quickstart_context_carries_its_notice():
    quickstart = build_context([_noticed()], TODAY)["quickstart"]
    assert quickstart["notice"] == {"since": "2026-07-18",
                                    "text": "The vendor refuses every client but its own.",
                                    "url": "https://github.com/zen/zen/issues/1"}


def _own_ua(**api) -> Entry:
    return make(id="zen", name="Zen", rank=1, api={
        "base_url": "https://zen.example/v1", "auth": "none", "model_ids": ["free-a"],
        "session_header": "x-zen-session", "client_user_agent": True, **api})


def test_the_quickstart_curl_names_its_own_user_agent_where_the_lane_asks_for_one(tmp_path: Path):
    """curl sends `curl/8.x` unless told otherwise — exactly the "generic SDK or
    HTTP-library name" OpenCode's client rules exclude — so a README command for
    such a lane would break the vendor's rules as printed. It names itself, and a
    lane that does not ask for it keeps the shorter command."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import QUICKSTART_USER_AGENT
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [_own_ua()])
    text = render_readme(reg, Path("templates"), tmp_path / "README.md", today=TODAY)
    curl = text.split("```bash\n")[1].split("```")[0]
    assert f"  -H 'User-Agent: {QUICKSTART_USER_AGENT}' \\\n" in curl
    assert curl.index("User-Agent") < curl.index("x-zen-session")
    assert QUICKSTART_USER_AGENT.split("/")[0] and "/" in QUICKSTART_USER_AGENT

    save_registry(reg, [_own_ua(client_user_agent=False)])
    plain = render_readme(reg, Path("templates"), tmp_path / "README2.md", today=TODAY)
    assert "User-Agent" not in plain.split("```bash\n")[1].split("```")[0]


def test_every_place_that_tells_a_reader_how_to_connect_names_both_headers():
    from freetier_radar.render import build_llms_txt, build_provider_page
    row = _own_ua()
    auth = build_context([row], TODAY)["connections"][0]["auth"]
    assert "your client's own `User-Agent`" in auth and "`x-zen-session` per conversation" in auth

    page = build_provider_page(row, [], TODAY)
    assert ("- User-Agent: your client's own name and version, such as `my-coding-agent/1.0` — not an "
            "SDK's or an HTTP library's") in page

    line = next(l for l in build_llms_txt([row], TODAY).splitlines() if l.startswith("- [Zen]"))
    assert "every request names its client in its own User-Agent" in line


def _trial(**api) -> Entry:
    return make(id="trial", name="Trial", rank=5, api={
        "base_url": "https://api.trial.example/v1", "key_url": "https://trial.example/docs",
        "model_ids": ["qwen-27b"], "public_key": "lt-trial-abc", **api})


def test_a_public_key_reaches_every_place_that_tells_a_reader_how_to_connect():
    """A reader copying the base URL from the connection table, landing on the
    provider page from a search, sourcing the env example or asking a model that
    read llms.txt needs the key the vendor prints for anyone — and needs to know
    it is the vendor's own, from the vendor's page, and not somebody's secret."""
    from freetier_radar.render import build_llms_txt, build_provider_page
    row = _trial()
    auth = build_context([row], TODAY)["connections"][0]["auth"]
    assert "`TRIAL_API_KEY`" in auth and "`lt-trial-abc`" in auth

    env = build_env_example([row], TODAY)
    assert 'export TRIAL_API_KEY="lt-trial-abc"' in env

    page = build_provider_page(row, [], TODAY)
    key_line = next(l for l in page.splitlines() if l.startswith("- Key:"))
    assert "`lt-trial-abc`" in key_line and "https://trial.example/docs" in key_line

    line = next(l for l in build_llms_txt([row], TODAY).splitlines() if l.startswith("- [Trial]"))
    assert "no account" in line and "`lt-trial-abc`" in line and "https://trial.example/docs" in line
    assert "no key" not in line


def test_a_lane_the_vendor_prints_a_key_for_needs_no_account():
    """An account is what a reader with the vendor's public key skips, so the
    row answers "No account at all" beside the keyless ones and counts as
    needing no signup. The README's first command stays a keyless one: it is the
    curl with nothing to paste into it."""
    rows = [_trial(), make(id="keyless", name="Keyless", rank=50,
                             api={"base_url": "https://k.example/v1", "auth": "none",
                                  "model_ids": ["m"]})]
    ctx = build_context(rows, TODAY)
    assert [p["name"] for p in ctx["picks"]["keyless"]] == ["Trial", "Keyless"]
    assert ctx["no_signup_count"] == 2
    assert ctx["quickstart"]["name"] == "Keyless"


def test_the_evidence_line_names_the_index_a_probe_follows():
    """The page a followed index names changes with each release, so the line
    says where the probe starts and what it follows, not a dated URL that would
    be the stale one by the next release."""
    from freetier_radar.render import build_provider_page
    row = make(probe={"type": "page-keywords", "endpoint": "https://x.ai/api/doc-index",
                      "keywords": ["200 credits a day"],
                      "follow": {"field": "Data.TargetPrefix", "suffix": "/dist/limits.md"}})
    line = next(l for l in build_provider_page(row, [], TODAY).splitlines() if l.startswith("- Probe:"))
    assert ("the page the index at <https://x.ai/api/doc-index> names in `Data.TargetPrefix`, "
            "followed by `/dist/limits.md`, anchored on `200 credits a day`") in line


def _mimo_rows() -> list[Entry]:
    """The two rows that named one project: Xiaomi's agent, archived on the day
    its anonymous channel ended, and the placeholder from the list's first day
    at a domain that has never resolved, folded into it."""
    holder = make(id="mimo-code", name="MiMo Code", url="https://mimo.xiaomi.com/coder",
                  offering="Xiaomi's terminal coding agent", retired_on=TODAY)
    folded = make(id="mimocode", name="MiMoCode", url="https://mimocode.ai",
                  offering="Coding agent with free tier", limits="TBD by scout",
                  delisted={"on": TODAY, "reason": "the same project as MiMo Code"},
                  duplicate_of="mimo-code")
    return [holder, folded]


def test_a_folded_row_is_not_a_second_line_in_the_archive():
    """The Archive is what the list carried, one line per service. MiMo Code and
    MiMoCode sat in it two lines apart for two months, and a reader counting
    dead offers counted Xiaomi's agent twice."""
    from freetier_radar.render import build_llms_txt, build_providers_index, build_site_context
    entries = _mimo_rows()
    assert [r["name"] for r in build_context(entries, TODAY)["archived"]] == ["MiMo Code"]
    assert [r["name"] for r in build_site_context(entries, TODAY)["archived"]] == ["MiMo Code"]
    assert "MiMoCode" not in build_llms_txt(entries, TODAY)
    assert "MiMoCode" not in build_providers_index(entries, TODAY)


def test_a_folded_rows_page_sends_the_reader_to_the_row_that_holds_the_service():
    """Its id stays taken — the id is the page's URL — so the page stays, and
    what it says is where the project is. What it must not do is publish the
    claim that was never verified as though the list had carried it."""
    from freetier_radar.render import build_provider_page, provider_page_url
    holder, folded = _mimo_rows()
    page = build_provider_page(folded, [], TODAY, registry=[holder, folded])
    assert f"[MiMo Code]({provider_page_url('mimo-code')})" in page
    assert "## What it offered" not in page and "TBD by scout" not in page
    assert "Coding agent with free tier" not in page
    assert "the same project as MiMo Code" in page


def test_the_row_that_holds_the_service_names_the_id_folded_into_it():
    """So nothing the list published disappears without a word: a reader who
    followed the old link, or the old name, lands here and reads why."""
    from freetier_radar.render import build_provider_page, provider_page_url
    holder, folded = _mimo_rows()
    page = build_provider_page(holder, [], TODAY, registry=[holder, folded])
    assert f"[MiMoCode]({provider_page_url('mimocode')})" in page


def test_the_connection_table_is_a_readme_beside_the_configs(tmp_path: Path):
    """Base URL, key name and the notes that matter, for every live
    OpenAI-compatible API — the table the README carried as 34 KB of reference
    for a reader who has already decided. GitHub renders a folder's README under
    its file list, so it sits beside the four files it describes, and every
    link in it is written from there."""
    from freetier_radar.models import save_registry
    from freetier_radar.render import CONFIGS_README, PAGES_URL, render_configs_readme
    assert CONFIGS_README == "configs/README.md"
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [api_entry(id="groq-free", name="Groq",
                                  api={"base_url": "https://api.x.ai/v1", "key_url": "https://x.ai/keys",
                                       "anthropic_base_url": "https://api.x.ai"}),
                        make(id="plain", name="Plain")])
    out = tmp_path / CONFIGS_README
    text = render_configs_readme(reg, Path("templates"), out, today=TODAY)
    assert out.read_text(encoding="utf-8") == text
    assert "| Provider | Base URL | Key env var | Get a key |" in text
    assert f"**[Groq]({PAGES_URL}/providers/groq-free/)**" in text
    assert "`https://api.x.ai/v1`" in text and "Anthropic format: `https://api.x.ai`" in text
    assert "`GROQ_API_KEY`" in text and "[key](https://x.ai/keys)" in text
    assert "Plain" not in text
    # written from configs/: the files beside it by name, the rest one level up
    for link in ("[`opencode.json`](opencode.json)", "[`litellm.yaml`](litellm.yaml)",
                 "[`claude-code.sh`](claude-code.sh)",
                 "[`free-llm.env.example`](free-llm.env.example)",
                 "[`../llms.txt`](../llms.txt)", "[`../index.json`](../index.json)",
                 "(../README.md)", "(../registry.yaml)", f"{PAGES_URL}/#connections"):
        assert link in text, link
    assert "do not edit" in text.lower()


def test_the_published_readme_stays_a_landing_page(tmp_path: Path):
    """A visitor scrolls the README on GitHub; the site is where a row is read
    whole. On 2026-09-20 the README ran to 161 KB and thirty-one desktop
    screens, sixteen of them tables, and the file list above it was the first
    thing on the page. The list grows a row at a time and a row is one line, so
    the budget is what keeps the reference job from creeping back in."""
    import json
    from freetier_radar.render import README_BUDGET
    pinned = date.fromisoformat(json.loads(Path("index.json").read_text(encoding="utf-8"))["generated"])
    text = render_readme(Path("registry.yaml"), Path("templates"), tmp_path / "README.md",
                         today=pinned)
    assert len(text.encode("utf-8")) <= README_BUDGET


def test_a_provider_page_offers_the_call_that_checks_a_key_in_the_readers_own_terminal():
    """"Does my key work here?" is answered by a command the reader runs, with
    the key read from their own environment — never by a page that asks for
    it (turned down on 2026-09-26). A keyless lane needs no header, a key the
    vendor prints for anyone is its own, and an endpoint that is not
    OpenAI-shaped gets no command a reader could not run."""
    from freetier_radar.render import build_provider_page, env_var
    keyed = build_provider_page(make(id="keyed-free", api={
        "base_url": "https://k.ai/v1/", "key_url": "https://k.ai/keys", "model_ids": ["k-1", "k-2"]}),
        [], TODAY)
    assert (f"Try it from your terminal with your key in `{env_var('keyed-free')}` — it goes "
            "from your machine to the vendor and nowhere else:") in keyed
    assert ("```sh\ncurl -s https://k.ai/v1/chat/completions \\\n"
            f'  -H "Authorization: Bearer ${env_var("keyed-free")}" \\\n'
            "  -H 'Content-Type: application/json' \\\n"
            """  -d '{"model":"k-1","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'\n```""") in keyed
    keyless = build_provider_page(make(id="open", api={
        "base_url": "https://o.ai/v1", "auth": "none", "model_ids": ["o-1"]}), [], TODAY)
    assert "the lane takes no key" in keyless and "Authorization" not in keyless
    public = build_provider_page(make(id="pub", api={
        "base_url": "https://p.ai/v1", "public_key": "pk-123", "key_url": "https://p.ai/key",
        "model_ids": ["p-1"]}), [], TODAY)
    assert '-H "Authorization: Bearer pk-123"' in public
    odd = build_provider_page(make(id="odd", api={
        "base_url": "https://x.ai/api", "openai_compatible": False, "model_ids": ["x-1"]}), [], TODAY)
    assert "Try it from your terminal" not in odd


def test_a_row_that_can_list_no_id_says_why_and_checks_the_key_on_the_catalog():
    """Where the vendor publishes no id a request carries, the page says why,
    and the key is checked against the catalog, which answers only a key."""
    import pytest
    from pydantic import ValidationError
    from freetier_radar.render import build_provider_page, env_var
    page = build_provider_page(make(id="shy", api={
        "base_url": "https://s.ai/v1/", "no_ids": "the catalog answers only a key"}), [], TODAY)
    assert "- Callable ids: none listed — the catalog answers only a key" in page
    assert ("```sh\ncurl -s https://s.ai/v1/models \\\n"
            f'  -H "Authorization: Bearer ${env_var("shy")}"\n```') in page
    with pytest.raises(ValidationError, match="no_ids"):
        make(id="both", api={"base_url": "https://s.ai/v1", "model_ids": ["s-1"], "no_ids": "none"})
