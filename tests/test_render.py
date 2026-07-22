from datetime import date, timedelta
from pathlib import Path

from freetier_radar.models import Entry
from freetier_radar.render import (
    ARCHIVE_AFTER_DAYS, build_context, build_env_example, build_opencode_config,
    env_var, is_archived, render_readme,
)

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
    section = next(s for s in ctx["sections"] if "LLM APIs" in s["title"])
    assert section["rows"][0]["models"] == "a"
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
    assert "last%20verified-2026--07--19" in text
    assert "live%20entries-1-58a6ff" in text
    assert "Coding agents & CLIs" in text
    assert "LLM APIs with free tier" in text
    assert "## How this list stays fresh" in text
    assert "```mermaid" in text
    assert "banner-dark.svg" in text
    assert "## Archive" in text
    assert "Dead Tool" in text.split("## Archive")[1]
    assert out.read_text(encoding="utf-8") == text
