from datetime import date

import httpx
import respx

from freetier_radar.discovery import Evidence, Hit
from freetier_radar.models import Entry
from freetier_radar.scout import (
    FALLBACK_OPENROUTER_MODEL, OVH_BASE_URL, LLMClient, _ask, apply_new, apply_supersede,
    apply_updates, extract_yaml_block, pick_openrouter_model, run_scout,
)

TODAY = date(2026, 7, 19)

BASE = {
    "name": "X", "category": "api-free-tier", "url": "https://x.ai",
    "offering": "old offering", "limits": "old limits",
    "first_seen": date(2026, 1, 1), "last_verified": date(2026, 1, 1),
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["free"]},
}


def make(**kw) -> Entry:
    d = {**BASE, "id": kw.pop("id", "x"), **kw}
    return Entry.model_validate(d)


def proposal(id: str = "new1", url: str = "https://n.ai") -> dict:
    return {
        "id": id, "name": "New", "category": "trial", "url": url, "offering": "trial",
        "probe": {"type": "page-keywords", "endpoint": url, "keywords": ["free"]},
    }


class StubLLM:
    def __init__(self, replies: dict[str, str]):
        self.replies = replies
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        for key, reply in self.replies.items():
            if key in prompt:
                return reply
        return "```yaml\n{}\n```"


def test_extract_yaml_block():
    assert extract_yaml_block("blah\n```yaml\na: 1\n```\nend") == "a: 1\n"
    assert extract_yaml_block("a: 1") == "a: 1"


def test_apply_updates_only_editable():
    entries = [make()]
    applied = apply_updates(entries, [{"id": "x", "limits": "new limits", "id_hack": "y", "name": "Hacked"}])
    assert applied == ["x"]
    assert entries[0].limits == "new limits"
    assert entries[0].name == "X"
    assert entries[0].id == "x"


def test_apply_new_skips_duplicates_and_invalid():
    entries = [make()]
    added, rejected = apply_new(entries, [
        {"id": "x", "name": "dup"},
        proposal(),
        {"id": "broken"},
    ], TODAY)
    assert added == ["new1"]
    assert any(r.startswith("broken") for r in rejected)
    assert len(entries) == 2
    new = entries[1]
    assert new.provisional is True and new.first_seen == TODAY and new.last_verified == TODAY


def test_apply_new_rejects_blocklisted_domain():
    entries = [make()]
    added, rejected = apply_new(entries, [proposal(id="p", url="https://developer.puter.com/x")],
                                TODAY, blocklist={"puter.com": "browser sdk"})
    assert added == []
    assert rejected == ["p: blocklisted domain"]


def test_apply_new_rejects_covered_domain():
    entries = [make()]
    added, rejected = apply_new(entries, [proposal(id="clone", url="https://www.x.ai/deep")], TODAY)
    assert added == []
    assert rejected == ["clone: domain already covered"]


def test_apply_new_uses_verifier():
    entries = [make()]
    added, rejected = apply_new(
        entries, [proposal(), proposal(id="bad", url="https://bad.ai")], TODAY,
        verifier=lambda e: None if e.id == "new1" else "missing keywords: free",
    )
    assert added == ["new1"]
    assert rejected == ["bad: probe failed (missing keywords: free)"]


def test_apply_supersede():
    entries = [make(models=[{"family": "old"}, {"family": "cur"}])]
    done = apply_supersede(entries, [{"family": "old", "superseded_by": "cur"}, {"family": "nope", "superseded_by": "cur"}])
    assert done == ["old"]
    assert entries[0].models[0].superseded_by == "cur"
    assert entries[0].models[1].superseded_by is None


def test_run_scout_orchestration():
    llm = StubLLM({
        "FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    limits: fixed\n```",
        "DISCOVER-NEW": "```yaml\nnew_entries:\n"
                        "  - id: new1\n    name: New\n    category: trial\n    url: https://n.ai\n"
                        "    offering: trial\n"
                        "    probe: {type: page-keywords, endpoint: https://n.ai, keywords: [free]}\n```",
        "MODEL-GENERATIONS": "```yaml\nsupersede:\n  - family: old\n    superseded_by: cur\n```",
    })
    entries = [make(models=[{"family": "old"}])]
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "boom"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=evidence, verifier=lambda e: None)
    assert result["updates"] == ["x"]
    assert result["new"] == ["new1"]
    assert result["supersede"] == ["old"]
    assert result["providers"] == ["hn"]
    assert entries[0].limits == "fixed"
    assert entries[0].models[0].superseded_by == "cur"
    assert any("FAILURE: fail — boom" in p for p in llm.prompts)


def test_run_scout_skips_discovery_without_evidence():
    llm = StubLLM({})
    entries = [make()]
    result = run_scout(llm, entries, [], lambda urls: {}, TODAY, evidence=Evidence())
    assert result["new"] == []
    assert not any("DISCOVER-NEW" in p for p in llm.prompts)


@respx.mock
def test_pick_openrouter_model_prefers_known_free():
    respx.get("https://openrouter.ai/api/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "vendor/paid-model"},
                            {"id": "qwen/qwen3-coder:free"},
                            {"id": "acme/other:free"}]}
    ))
    with httpx.Client() as http:
        assert pick_openrouter_model(http) == "qwen/qwen3-coder:free"


@respx.mock
def test_pick_openrouter_model_falls_back_on_error():
    respx.get("https://openrouter.ai/api/v1/models").mock(return_value=httpx.Response(500))
    with httpx.Client() as http:
        assert pick_openrouter_model(http) == FALLBACK_OPENROUTER_MODEL


@respx.mock
def test_llm_chain_falls_back_to_keyless_ovh(monkeypatch):
    import freetier_radar.scout as scout_mod
    monkeypatch.setattr(scout_mod, "RETRY_429_SLEEP", 0)
    respx.get(f"{OVH_BASE_URL}/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "Meta-Llama-3_3-70B"}, {"id": "gpt-oss-120b"}]}
    ))
    route = respx.post(f"{OVH_BASE_URL}/chat/completions")
    route.side_effect = [
        httpx.Response(429),
        httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]}),
    ]
    with httpx.Client() as http:
        llm = LLMClient(http=http)  # zero keys configured
        assert llm.complete("hi") == "ok"
    assert route.call_count == 2
    assert "Authorization" not in route.calls[0].request.headers
    assert b"gpt-oss-120b" in route.calls[0].request.content


@respx.mock
def test_llm_chain_skips_backend_on_empty_content():
    respx.post("https://nim.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": None}}]})
    )
    respx.get(f"{OVH_BASE_URL}/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "gpt-oss-120b"}]}
    ))
    respx.post(f"{OVH_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})
    )
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://nim.example/v1", custom_model="m",
                        custom_key="k", http=http)
        assert llm.complete("hi") == "ok"


def test_ask_retries_malformed_yaml_then_degrades():
    class FlakyLLM:
        def __init__(self, replies: list[str]):
            self.replies = replies

        def complete(self, prompt: str) -> str:
            return self.replies.pop(0)

    bad = "```yaml\nnew_entries:\n- id: x\n 百家乐 GLM-4.6 desencadenado\n```"
    good = "```yaml\nnew_entries: []\n```"
    assert _ask(FlakyLLM([bad, good]), "p") == {"new_entries": []}
    assert _ask(FlakyLLM([bad, bad]), "p") == {}


@respx.mock
def test_llm_chain_custom_endpoint_first():
    route = respx.post("https://nim.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "custom"}}]})
    )
    with httpx.Client() as http:
        llm = LLMClient(gemini_key="g", openrouter_key="o",
                        custom_base_url="https://nim.example/v1/", custom_model="m",
                        custom_key="k", http=http)
        assert llm.complete("hi") == "custom"
    assert route.calls[0].request.headers["Authorization"] == "Bearer k"
