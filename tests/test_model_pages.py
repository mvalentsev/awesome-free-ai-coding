"""A page per model, beside the page per row.

A reader — or a model answering one — often arrives with a model in mind
rather than a vendor: where is Kimi K3 free, where is GLM-5.3-Flash. The
provider pages answer for one vendor, and the site's model index answers for
every model in one fold of the front page, where no search engine can match a
title to the question. So a model the list can say something about across rows
gets a page whose title is the question, and the index of every model is a page
too. What these tests hold them to: the same families the model index names,
every row with what a reader needs to call it, dates that are the evidence's,
and a place in the sitemap, the feed of URLs sent to IndexNow and the links
from every page that names the model.
"""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

from freetier_radar.history import Event
from freetier_radar.models import ARCHIVE_AFTER_DAYS, save_registry
from freetier_radar.render import (
    MODEL_PAGE_ROWS, MODELS_DIR, PAGES_URL, build_context, build_index, build_llms_txt,
    build_model_page, build_models_index, build_provider_page, check_rendered, model_page_url,
    render_artifacts, render_readme,
)
from test_render import TODAY, make

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
STRONG = {"tier": "strong", "aa_model": "glm-5-3"}


def at(day: str, **kw) -> Event:
    return Event.model_validate({"ts": f"{day}T05:23:00Z", "event": "models", "id": "x",
                                 "name": "X", "url": "https://x.ai", **kw})


def front(page: str) -> dict:
    return yaml.safe_load(page.split("---\n")[1])


def groq(**kw):
    return make(**{"id": "groq-free", "name": "Groq", "rank": 1,
                   "offering": "Fast inference on a free plan",
                   "limits": "30 requests a minute and 1,000 a day on qwen/qwen3.8-27b",
                   "models": [{"family": "qwen3.8-27b"}, {"family": "gpt-oss-120b"}],
                   "api": {"base_url": "https://api.groq.com/openai/v1",
                           "key_url": "https://console.groq.com/keys", "auth": "api-key",
                           "model_ids": ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]},
                   **kw})


def keyless(**kw):
    return make(**{"id": "open-lane", "name": "Open Lane", "rank": 2,
                   "offering": "An anonymous lane", "models": [{"family": "qwen3.8-27b"}],
                   "api": {"base_url": "https://free.example/v1", "auth": "none",
                           "model_ids": ["Qwen/Qwen3.8-27B"]},
                   **kw})


def agent(**kw):
    return make(**{"id": "some-agent", "name": "Some Agent", "rank": 3,
                   "category": "agent-cli", "card_required": True,
                   "offering": "A coding agent with free models",
                   "models": [{"family": "qwen3.8-27b"}], **kw})


# ---- which models get a page ------------------------------------------------

def test_a_model_has_a_page_where_rows_compare_or_where_it_measures_strong():
    """A page earns its place by saying what no row's page says alone — who
    else serves the model — or by covering a model readers come for. A model
    one row serves and nothing measures would get a page that repeats that
    row's, fifty-seven times over for Alibaba's catalog alone: it stays on the
    index, beside its row. Only live rows count; an archived one serves no one."""
    assert MODEL_PAGE_ROWS == 2
    entries = [
        make(id="a", name="A", rank=1, models=[{"family": "kimi-k3"}, {"family": "solo"},
                                                {"family": "glm-5.3", **STRONG}]),
        make(id="b", name="B", rank=2, models=[{"family": "kimi-k3"}]),
        make(id="gone", name="Gone", models=[{"family": "solo"}],
             last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1)),
    ]
    models = {m["family"]: m for m in build_index(entries, TODAY)["models"]}
    assert models["kimi-k3"] == {"family": "kimi-k3", "rows": ["a", "b"],
                                 "page": model_page_url("kimi-k3")}
    assert models["glm-5.3"] == {"family": "glm-5.3", "rows": ["a"], "tier": "strong",
                                 "page": f"{PAGES_URL}/{MODELS_DIR}/glm-5.3/"}
    assert models["solo"] == {"family": "solo", "rows": ["a"]}


def test_the_render_writes_a_page_per_model_and_takes_away_one_that_lost_its_page(tmp_path):
    reg = tmp_path / "registry.yaml"
    both = [make(id="a", name="A", models=[{"family": "kimi-k3"}]),
            make(id="b", name="B", models=[{"family": "kimi-k3"}])]
    save_registry(reg, both)
    render_artifacts(reg, tmp_path, today=TODAY)
    assert sorted(p.name for p in (tmp_path / MODELS_DIR).iterdir()) == ["index.md", "kimi-k3.md"]
    save_registry(reg, [both[0], make(id="b", name="B", models=[{"family": "glm-5"}])])
    render_artifacts(reg, tmp_path, today=TODAY)
    assert sorted(p.name for p in (tmp_path / MODELS_DIR).iterdir()) == ["index.md"]


def test_check_rendered_sees_a_model_page_the_render_no_longer_makes(tmp_path):
    """A page left behind is still served, and would go on saying where a model
    is free after the list stopped saying it."""
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="a", name="A", models=[{"family": "kimi-k3"}]),
                        make(id="b", name="B", models=[{"family": "kimi-k3"}])])
    from freetier_radar.render import CONFIGS_README, SITE_PAGE, render_configs_readme, render_site
    render_readme(reg, TEMPLATES, tmp_path / "README.md", today=TODAY)
    render_site(reg, TEMPLATES, tmp_path / SITE_PAGE, today=TODAY)
    render_configs_readme(reg, TEMPLATES, tmp_path / CONFIGS_README, today=TODAY)
    render_artifacts(reg, tmp_path, today=TODAY)
    assert not [s for s in check_rendered(reg, TEMPLATES, tmp_path) if s.startswith(MODELS_DIR)]
    (tmp_path / MODELS_DIR / "glm-5.md").write_text("# Stray\n", encoding="utf-8")
    assert f"{MODELS_DIR}/glm-5.md" in check_rendered(reg, TEMPLATES, tmp_path)


# ---- what a model page says --------------------------------------------------

def test_a_model_page_is_titled_by_the_question_and_dated_by_the_evidence():
    """The title is what a reader types — the model, "free" — with the count and
    the date a probe confirmed it. Several rows carry several dates, and the
    oldest is a floor, so it says "or later" (the badge's rule); the sitemap's
    date is the newest change a reader could see: a probe pass or a history line."""
    entries = [groq(last_verified=date(2026, 7, 18)), keyless(), agent()]
    page = build_model_page("qwen3.8-27b", entries, [], TODAY)
    meta = front(page)
    assert meta["title"] == "qwen3.8-27b free: 3 providers, limits and ids, verified 2026-07-18 or later"
    assert meta["permalink"] == "/models/qwen3.8-27b/"
    assert meta["layout"] == "default"
    assert meta["last_modified_at"] == TODAY
    assert meta["description"].startswith(
        "qwen3.8-27b is served free by Groq, Open Lane and Some Agent.")
    assert len(meta["description"]) <= 300
    assert "{% raw %}" in page and page.rstrip().endswith("{% endraw %}")

    one = front(build_model_page("gpt-oss-120b", [groq(models=[
        {"family": "gpt-oss-120b", "tier": "strong", "aa_model": "gpt-oss-120b"}])], [], TODAY))
    assert one["title"] == "gpt-oss-120b free: 1 provider, limits and ids, verified 2026-07-19"

    moved = at("2026-07-21", id="groq-free", name="Groq", models=["qwen3.8-27b", "gpt-oss-120b"])
    assert front(build_model_page("qwen3.8-27b", entries, [moved], TODAY + timedelta(days=3))
                 )["last_modified_at"] == date(2026, 7, 21)


def test_a_model_page_opens_with_the_answer():
    """The first paragraph is the one a search result and a model's answer
    quote: who serves it, what that asks of the reader, how fresh the evidence
    is and how strong the model measures — each figure the registry's own."""
    strong = {"family": "qwen3.8-27b", "tier": "strong", "aa_model": "qwen3-8-27b"}
    entries = [groq(models=[strong]), keyless(models=[strong]), agent(models=[strong])]
    page = build_model_page("qwen3.8-27b", entries, [], TODAY)
    assert "# Where qwen3.8-27b is free" in page
    assert ("**3 rows on the list serve `qwen3.8-27b` free:** Groq, Open Lane and Some Agent. "
            "Some Agent asks for a card on file, the rest for none; Open Lane answers with no "
            "account at all. A live probe confirmed each one on 2026-07-19 and reads them again "
            "twice a week. It measures **strong**: within 25 points of the top of the "
            "[Artificial Analysis Intelligence Index]"
            "(https://artificialanalysis.ai/models/qwen3-8-27b).") in page
    assert f"[Every free model]({PAGES_URL}/models/)" in page


def test_every_row_says_what_it_asks_and_how_to_call_the_model():
    """What a reader copies: the ids of this model and no other, the base URL,
    the key and where it comes from — or that there is no key, or that there is
    no endpoint to paste. The limits are the row's own, whole; the row's page
    has the evidence."""
    entries = [groq(), keyless(), agent()]
    page = build_model_page("qwen3.8-27b", entries, [], TODAY)
    groq_block = page.split("### [Groq]")[1].split("\n### ")[0]
    assert groq_block.startswith(f"({PAGES_URL}/providers/groq-free/)")
    assert "🔌 LLM APIs with free tier · no card · verified 2026-07-19" in groq_block
    assert "Fast inference on a free plan" in groq_block
    assert ("- Limits, in the vendor's words: 30 requests a minute and 1,000 a day on "
            "qwen/qwen3.8-27b") in groq_block
    assert ("- Base URL: `https://api.groq.com/openai/v1`\n"
            "- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>\n"
            "- Callable ids: `qwen/qwen3.8-27b`\n") in groq_block
    assert "gpt-oss-120b" not in groq_block
    open_block = page.split("### [Open Lane]")[1].split("\n### ")[0]
    assert "- Key: none — the lane is anonymous\n- Callable ids: `Qwen/Qwen3.8-27B`" in open_block
    agent_block = page.split("### [Some Agent]")[1].split("\n## ")[0]
    assert "🤖 Coding agents & CLIs · card required · verified 2026-07-19" in agent_block
    assert "- No API endpoint to paste: this row is a tool you install or sign in to." in agent_block
    assert "The vendor publishes no figure for this tier." in agent_block


def test_a_model_page_says_how_to_connect_in_the_row_pages_own_lines():
    """The model page does not word a connection its own way: every line the
    row's page gives under Connect — a key the vendor prints for anyone, the
    User-Agent and the session header a lane asks for, the Anthropic route —
    is the model page's line too, from the same function, so a way in added
    to one page cannot be missing from the other. Only the ids differ: the row
    page lists them all, the model page this model's."""
    row = groq(api={"base_url": "https://api.groq.com/openai/v1", "auth": "api-key",
                    "key_url": "https://console.groq.com/keys", "public_key": "sk-shared",
                    "client_user_agent": True, "session_header": "x-session",
                    "anthropic_base_url": "https://api.groq.com/anthropic",
                    "model_ids": ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"], "note": "A note."})
    def lines(block: str) -> set[str]:
        return {line for line in block.splitlines() if line.startswith("- ")
                and not line.startswith(("- Callable ids:", "- Note:", "- Limits,"))
                and "train" not in line}
    connect = build_provider_page(row, [], TODAY).split("## Connect")[1].split("\n## ")[0]
    model = build_model_page("qwen3.8-27b", [row, keyless()], [], TODAY)
    block = model.split("### [Groq]")[1].split("\n### ")[0]
    assert len(lines(connect)) == 5
    assert lines(block) == lines(connect)
    assert "- Callable ids: `qwen/qwen3.8-27b`" in block
    assert "- Callable ids: `qwen/qwen3.8-27b`, `openai/gpt-oss-120b`" in connect


def test_a_lane_served_inside_its_client_names_the_ids_to_pick_there():
    """Cline's free models are picked in Cline's own model list; both the row's
    page and the model's name the ids there, from the same lines."""
    cline = make(id="cline", name="Cline", category="agent-cli", free_part="models",
                 models=[{"family": "muse-spark-1.3-contributor"}, {"family": "glm-5.3-flash"}],
                 client_lane={"model_ids": ["cline-free/muse-spark-1.3-contributor",
                                            "cline-free/glm-5.3-flash"]},
                 probe={"type": "api-models", "endpoint": "https://api.cline.bot/models",
                        "lane": "free"})
    row_page = build_provider_page(cline, [], TODAY)
    assert ("- In Cline's own model list: `cline-free/muse-spark-1.3-contributor`, "
            "`cline-free/glm-5.3-flash`") in row_page
    model = build_model_page("glm-5.3-flash", [cline, keyless(models=[{"family": "glm-5.3-flash"}])],
                             [], TODAY)
    assert "- In Cline's own model list: `cline-free/glm-5.3-flash`\n" in model


def test_a_row_says_what_the_vendor_does_with_what_a_reader_sends():
    quoted = {"trains": "no", "quote": "We never train on your prompts.",
              "url": "https://console.groq.com/docs/legal"}
    page = build_model_page("qwen3.8-27b", [groq(data_use=quoted), keyless()], [], TODAY)
    assert ("- What you send is not used to train models "
            "([the vendor's words](https://console.groq.com/docs/legal)).") in page


def test_a_row_says_since_when_the_list_has_carried_the_model_there():
    """The list's own date, never the vendor's: the day the row's free models
    last took the family in. A family that left and came back counts from its
    return, and a row the history does not know says nothing."""
    events = [
        at("2026-07-01", event="added", id="groq-free", name="Groq", models=["qwen3.8-27b"]),
        at("2026-07-05", id="groq-free", name="Groq", models=["gpt-oss-120b"]),
        at("2026-07-09", id="groq-free", name="Groq", models=["gpt-oss-120b", "qwen3.8-27b"]),
        at("2026-07-12", id="groq-free", name="Groq", models=["qwen3.8-27b", "gpt-oss-120b"]),
    ]
    page = build_model_page("qwen3.8-27b", [groq(), keyless()], events, TODAY)
    groq_block = page.split("### [Groq]")[1].split("\n### ")[0]
    assert "· verified 2026-07-19 · listed since 2026-07-09" in groq_block
    open_block = page.split("### [Open Lane]")[1]
    assert "listed since" not in open_block


def test_a_lane_that_does_not_work_says_so_on_the_model_page_too():
    notice = {"since": "2026-07-10", "text": "The vendor refuses every call.",
              "url": "https://x.ai/issue"}
    page = build_model_page("qwen3.8-27b", [groq(), keyless(api={
        "base_url": "https://free.example/v1", "auth": "none", "model_ids": ["Qwen/Qwen3.8-27B"],
        "notice": notice})], [], TODAY)
    block = page.split("### [Open Lane]")[1]
    assert ("> ⚠️ **Does not work as published since [2026-07-10](https://x.ai/issue).** "
            "The vendor refuses every call.") in block
    assert block.index("⚠️") < block.index("- Base URL:"), "before the base URL, as on its page"


def test_related_models_with_a_page_of_their_own_are_linked():
    entries = [
        make(id="a", name="A", models=[{"family": "glm-5.3", **STRONG}, {"family": "glm-5.2"},
                                       {"family": "glm-4.7-flash"}, {"family": "kimi-k3"}]),
        make(id="b", name="B", models=[{"family": "glm-5.2"}, {"family": "kimi-k3"}]),
    ]
    page = build_model_page("glm-5.3", entries, [], TODAY)
    related = page.split("## Related models")[1]
    assert f"[`glm-5.2`]({PAGES_URL}/models/glm-5.2/)" in related
    assert "glm-4.7-flash" not in related, "one row, no tier: no page to link"
    assert "kimi-k3" not in related, "another family"


# ---- the index of every model --------------------------------------------------

def test_the_models_index_names_every_family_and_links_the_pages():
    entries = [
        make(id="a", name="A", rank=1, models=[{"family": "kimi-k3"}, {"family": "solo"}]),
        make(id="b", name="B", rank=2, card_required=True, models=[{"family": "kimi-k3"}]),
    ]
    page = build_models_index(entries, TODAY)
    meta = front(page)
    assert meta["permalink"] == "/models/"
    assert meta["title"] == "Free LLM models by name: who serves each one free, verified 2026-07-19"
    assert meta["last_modified_at"] == TODAY
    assert (f"| [`kimi-k3`]({PAGES_URL}/models/kimi-k3/) | [A]({PAGES_URL}/providers/a/), "
            f"[B]({PAGES_URL}/providers/b/) 💳 |") in page
    assert f"| `solo` | [A]({PAGES_URL}/providers/a/) |" in page
    assert "two rows or more serve it free, or it measures strong or frontier" in page


# ---- where the pages are linked from ---------------------------------------------

def test_the_pages_that_name_a_model_link_its_page(tmp_path):
    """The site's model index and strong models, the README's strong models and
    the provider page's free models all name the model; each is a way in."""
    from freetier_radar.render import SITE_PAGE, render_site
    entries = [make(id="a", name="A", rank=1, models=[{"family": "glm-5.3", **STRONG},
                                                      {"family": "solo"}])]
    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    readme = render_readme(reg, TEMPLATES, tmp_path / "README.md", today=TODAY)
    assert f"\n- [`glm-5.3`]({PAGES_URL}/models/glm-5.3/) — [A](https://x.ai)\n" in readme
    assert f"({PAGES_URL}/models/)" in readme
    html = render_site(reg, TEMPLATES, tmp_path / SITE_PAGE, today=TODAY)
    assert f'<a class="chip" href="{PAGES_URL}/models/glm-5.3/">glm-5.3</a>' in html
    assert f'<a href="{PAGES_URL}/models/glm-5.3/"><code>glm-5.3</code></a>' in html
    assert "<th scope=\"row\"><code>solo</code></th>" in html
    page = build_provider_page(entries[0], [], TODAY, registry=entries)
    assert f"[`glm-5.3`]({PAGES_URL}/models/glm-5.3/), `solo`" in page
    ctx = build_context(entries, TODAY)
    assert ctx["model_index"][0]["page"] == model_page_url("glm-5.3")


def test_llms_txt_names_the_model_pages():
    entries = [make(id="a", name="A", rank=1, models=[{"family": "glm-5.3", **STRONG}]),
               make(id="b", name="B", rank=2, card_required=True,
                    models=[{"family": "glm-5.3", **STRONG}])]
    text = build_llms_txt(entries, TODAY)
    section = text.split("## Free models by name")[1].split("\n## ")[0]
    assert f"- [glm-5.3]({PAGES_URL}/models/glm-5.3/): strong; A, B (card required)" in section
    assert f"- [Model pages]({PAGES_URL}/models/)" in text


def test_a_provider_page_is_dated_for_the_sitemap_by_its_newest_change():
    """jekyll-sitemap writes <lastmod> and jekyll-seo-tag `dateModified` from
    `last_modified_at`; without it 98 of the sitemap's 100 URLs carried no date,
    and a crawler deciding what to re-read had nothing to go on."""
    e = groq(last_verified=date(2026, 7, 15))
    assert front(build_provider_page(e, [], TODAY))["last_modified_at"] == date(2026, 7, 15)
    later = at("2026-07-17", id="groq-free", name="Groq", models=["qwen3.8-27b"])
    other = at("2026-07-18", id="someone-else", name="S", models=["x"])
    assert front(build_provider_page(e, [later, other], TODAY))["last_modified_at"] == date(2026, 7, 17)


def test_every_family_is_a_path_segment():
    """The family is the page's file name and URL: a slash or a space would put
    the page somewhere its links do not point. The registry refuses it where it
    is read — freetier-check, the probe, the scout — not the render halfway
    through a scheduled run."""
    import pytest
    with pytest.raises(ValueError, match="not a page name"):
        make(models=[{"family": "Qwen 3/8"}])
    make(models=[{"family": "qwen3.8-2.4t-a95b"}])


def test_every_page_the_render_writes_is_one_indexnow_submits(tmp_path):
    """The render writes the pages; IndexNow tells the engines about them, from
    index.json. A page kind the second forgot would never be announced, and an
    address it sent that the render no longer writes is a 404 an engine is
    asked to read. So the two are held to one set: every page's permalink, as
    the URL its links use."""
    from freetier_radar.indexnow import site_urls
    import json
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [make(id="a", name="A", models=[{"family": "kimi-k3"}, {"family": "solo"}]),
                        make(id="b", name="B", models=[{"family": "kimi-k3"}]),
                        make(id="gone", name="Gone", probe_failures=3)])
    render_artifacts(reg, tmp_path, today=TODAY)
    pages = [p for d in ("providers", MODELS_DIR) for p in (tmp_path / d).glob("*.md")]
    written = {PAGES_URL + front(p.read_text(encoding="utf-8"))["permalink"] for p in pages}
    assert len(written) == len(pages) == 7, "a, b, gone, the checked page, the provider index, kimi-k3, the model index"
    index = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    others = {f"{PAGES_URL}/", f"{PAGES_URL}/feed.xml", f"{PAGES_URL}/llms.txt",
              f"{PAGES_URL}/browse.html"}
    assert set(site_urls(index)) - others == written


def test_the_render_dates_are_utc_days():
    """An event at 23:30 UTC belongs to its UTC day, as every date on the pages does."""
    late = Event.model_validate({"ts": datetime(2026, 7, 20, 23, 30, tzinfo=timezone.utc),
                                 "event": "models", "id": "groq-free", "name": "Groq",
                                 "models": ["qwen3.8-27b"]})
    page = build_model_page("qwen3.8-27b", [groq(), keyless()], [late], TODAY + timedelta(days=2))
    assert front(page)["last_modified_at"] == date(2026, 7, 20)
