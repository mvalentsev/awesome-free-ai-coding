from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

from freetier_radar.history import Event
from freetier_radar.models import WATCH_RECHECK_DAYS, Entry, Watched
from freetier_radar.render import (
    ARCHIVE_AFTER_DAYS, FEED_ENTRIES, FEED_URL, README_CHANGES, build_context,
    build_env_example, build_feed, build_index, build_litellm_config,
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


def test_archive_rules():
    assert not is_archived(make(), TODAY)
    assert is_archived(make(probe_failures=3), TODAY)
    assert is_archived(make(last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS + 1)), TODAY)
    assert not is_archived(make(last_verified=TODAY - timedelta(days=ARCHIVE_AFTER_DAYS)), TODAY)
    assert is_archived(make(retired_on=TODAY), TODAY)
    assert is_archived(make(retired_on=TODAY - timedelta(days=1)), TODAY)
    assert not is_archived(make(retired_on=TODAY + timedelta(days=1)), TODAY)


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
    assert section["rows"][0]["card"] == "✅ No"
    assert ctx["archived"] == []


def test_rank_orders_rows_within_section():
    entries = [make(id="worst", name="Worst", rank=99), make(id="best", name="Best", rank=1)]
    ctx = build_context(entries, TODAY)
    section = next(s for s in ctx["sections"] if "LLM APIs" in s["title"])
    assert [r["name"] for r in section["rows"]] == ["Best", "Worst"]


def test_env_var_naming():
    assert env_var("groq-free") == "GROQ_API_KEY"
    assert env_var("zai-glm") == "ZAI_GLM_API_KEY"


def test_provisional_marker_and_flag():
    ctx = build_context([make(name="Prov", provisional=True),
                         make(id="solid", name="Solid")], TODAY)
    section = next(s for s in ctx["sections"] if "LLM APIs" in s["title"])
    verified = {r["name"]: r["verified"] for r in section["rows"]}
    assert verified["Prov"].endswith("🧪")
    assert verified["Solid"] == TODAY.isoformat()
    assert ctx["has_provisional"] is True
    assert build_context([make(id="solid", name="Solid")], TODAY)["has_provisional"] is False


def api_entry(**kw):
    return make(**{"api": {"base_url": "https://api.x.ai/v1",
                           "key_url": "https://x.ai/keys", "auth": "api-key"}, **kw})


def test_opencode_config_and_env_example():
    entries = [
        api_entry(id="groq-free", name="Groq", models=[{"family": "llama-4"}]),
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


def test_litellm_config_names_every_free_model_of_every_connectable_entry():
    entries = [api_entry(id="groq-free", name="Groq", models=[{"family": "llama-4"}]),
               api_entry(id="keyless", name="NoKey", api={
                   "base_url": "https://free.example/v1", "auth": "none",
                   "model_ids": ["gpt-oss-120b"]}),
               make(id="plain"),  # no api block: nothing to point a proxy at
               # An auto-routing plan lists no free model of its own, so there is
               # no id a proxy could call: it contributes nothing rather than a
               # broken alias.
               api_entry(id="router", name="Router")]
    cfg = build_litellm_config(entries, TODAY)
    assert cfg["model_list"] == [
        {"model_name": "groq-free/llama-4",
         "litellm_params": {"model": "openai/llama-4",
                            "api_base": "https://api.x.ai/v1",
                            "api_key": "os.environ/GROQ_API_KEY"}},
        {"model_name": "keyless/gpt-oss-120b",
         "litellm_params": {"model": "openai/gpt-oss-120b",
                            "api_base": "https://free.example/v1",
                            "api_key": "none"}},  # LiteLLM's own spelling for "no key"
    ]


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
                       "model_ids": ["gpt-oss-120b"]})
    quickstart = build_context([keyless_no_ids, usable], TODAY)["quickstart"]
    assert quickstart == {"name": "Keyless", "url": "https://x.ai",
                          "base_url": "https://b.example/v1",  # no double slash in the curl
                          "model_id": "gpt-oss-120b"}


def test_context_connections():
    entries = [api_entry(id="groq-free", name="Groq"), make(id="plain")]
    ctx = build_context(entries, TODAY)
    assert ctx["connections"] == [{"name": "Groq", "base_url": "https://api.x.ai/v1",
                                   "auth": "`GROQ_API_KEY`", "key_url": "https://x.ai/keys",
                                   "note": ""}]


def test_render_readme(tmp_path: Path):
    reg = tmp_path / "registry.yaml"
    from freetier_radar.models import save_registry
    save_registry(reg, [make(), make(id="dead", name="Dead Tool", probe_failures=5)])
    out = tmp_path / "README.md"
    text = render_readme(reg, Path("templates"), out, today=TODAY)
    assert "all%20entries%20verified-2026--07--19" in text
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
    assert entry.findtext(f"{ns}title") == "New: X"
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
    assert entry.findtext("{http://www.w3.org/2005/Atom}title") == "New: A & B <script>"


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
    assert "New: X" in feed


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
