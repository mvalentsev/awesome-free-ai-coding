from datetime import date

import httpx
import respx

from freetier_radar.discovery import Evidence, Hit
from freetier_radar.models import Entry
from freetier_radar.scout import (
    FALLBACK_OPENROUTER_MODEL, OVH_BASE_URL, LLMClient, _ask, apply_new, apply_retirements,
    apply_updates, extract_yaml_block, pick_openrouter_model, run_scout, supersede_proposals,
)

TODAY = date(2026, 7, 19)

BASE = {
    "name": "X", "category": "api-free-tier", "url": "https://x.ai",
    "offering": "old offering", "limits": "old limits",
    "first_seen": date(2026, 1, 1), "last_verified": date(2026, 1, 1),
    "probe": {"type": "page-keywords", "endpoint": "https://x.ai", "keywords": ["x-mini-2", "free"]},
}


def make(**kw) -> Entry:
    d = {**BASE, "id": kw.pop("id", "x"), **kw}
    return Entry.model_validate(d)


def proposal(id: str = "new1", url: str = "https://n.ai") -> dict:
    return {
        "id": id, "name": "New", "category": "trial", "url": url, "offering": "trial",
        "probe": {"type": "page-keywords", "endpoint": url, "keywords": ["n-flash-1", "free"]},
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


def test_supersede_is_proposed_never_written():
    """A mark decides what the README calls free, but the model proposing it sees
    only family names. z.ai's free glm-4.7-flash got buried behind paid glm-5.2
    that way, so the registry is left alone and a human decides."""
    entries = [make(models=[{"family": "old"}, {"family": "cur"}])]
    proposed = supersede_proposals(entries, [{"family": "old", "superseded_by": "cur"},
                                             {"family": "nope", "superseded_by": "cur"}])
    assert proposed == ["x: old → cur"]
    assert entries[0].models[0].superseded_by is None
    assert entries[0].models[1].superseded_by is None


def test_supersede_proposals_skip_marks_already_in_place():
    """PR #4 claimed four superseded families while its diff touched two."""
    entries = [make(models=[{"family": "old", "superseded_by": "cur"}, {"family": "cur"}])]
    assert supersede_proposals(entries, [{"family": "old", "superseded_by": "cur"}]) == []
    assert supersede_proposals(entries, [{"family": "cur", "superseded_by": "next"}]) == ["x: cur → next"]


def test_apply_retirements_needs_the_quote_on_the_page():
    pages = {"https://x.ai": "we are shutting the free tier down on 30 september 2026, thanks"}
    entries = [make(source_urls=["https://x.ai"])]

    invented = apply_retirements(entries, [{
        "id": "x", "retired_on": "2026-09-30",
        "quote": "the free tier will be discontinued next quarter"}], pages)
    assert invented == [] and entries[0].retired_on is None

    grounded = apply_retirements(entries, [{
        "id": "x", "retired_on": "2026-09-30",
        "quote": "We are shutting the free tier down on 30 September 2026"}], pages)
    assert grounded == ["x (2026-09-30)"] and entries[0].retired_on == date(2026, 9, 30)


def test_apply_retirements_ignores_bad_dates_and_short_quotes():
    pages = {"https://x.ai": "the free tier ends soon, we are shutting the free tier down"}
    entries = [make(source_urls=["https://x.ai"])]
    assert apply_retirements(entries, [
        {"id": "x", "retired_on": "soon", "quote": "we are shutting the free tier down"},
        {"id": "x", "retired_on": "2026-09-30", "quote": "ends soon"},
        {"id": "nobody", "retired_on": "2026-09-30", "quote": "we are shutting the free tier down"},
    ], pages) == []
    assert entries[0].retired_on is None


def test_run_scout_sweeps_live_entries_for_retirements():
    """GitHub Models announced its shutdown weeks ahead; the scout only ever saw
    an entry once its probe failed, i.e. on the day the tier died."""
    page = "the free tier for github models will be retired on 2026-07-30, use the paid plan"
    llm = StubLLM({"FIND-RETIREMENTS": "```yaml\nretire:\n  - id: x\n    retired_on: '2026-07-30'\n"
                                       f"    quote: {page[:60]}\n```"})
    entries = [make(source_urls=["https://x.ai/blog"])]
    result = run_scout(llm, entries, [], lambda urls: {u: page for u in urls}, TODAY)
    assert result["retired"] == ["x (2026-07-30)"]
    assert entries[0].retired_on == date(2026, 7, 30)


def test_run_scout_skips_the_llm_when_no_page_hints_at_a_retirement():
    """Almost every sweep answers "nothing retiring". Sending 30 unremarkable
    pages to the LLM cost ~20k tokens and risked blowing a backend's context."""
    llm = StubLLM({})
    entries = [make(source_urls=["https://x.ai/blog"])]
    run_scout(llm, entries, [], lambda urls: {u: "our free tier, as always" for u in urls}, TODAY)
    assert not any("FIND-RETIREMENTS" in p for p in llm.prompts)


def test_retirement_sweep_failure_does_not_sink_the_run():
    class Flaky(StubLLM):
        def complete(self, prompt: str) -> str:
            if "FIND-RETIREMENTS" in prompt:
                self.prompts.append(prompt)
                raise RuntimeError("all LLM backends failed: context too long")
            return super().complete(prompt)

    llm = Flaky({"MODEL-GENERATIONS": "```yaml\nsupersede:\n  - family: old\n    superseded_by: cur\n```"})
    entries = [make(source_urls=["https://x.ai/blog"], models=[{"family": "old"}])]
    result = run_scout(llm, entries, [],
                       lambda urls: {u: "the free tier will be discontinued" for u in urls}, TODAY)
    assert result["retired"] == []
    assert result["supersede"] == ["x: old → cur"]  # the rest of the scout still ran


def test_run_scout_orchestration():
    llm = StubLLM({
        "FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    limits: fixed\n```",
        "DISCOVER-NEW": "```yaml\nnew_entries:\n"
                        "  - id: new1\n    name: New\n    category: trial\n    url: https://n.ai\n"
                        "    offering: trial\n"
                        "    probe: {type: page-keywords, endpoint: https://n.ai,"
                        " keywords: [n-flash-1, free]}\n```",
        "MODEL-GENERATIONS": "```yaml\nsupersede:\n  - family: old\n    superseded_by: cur\n```",
    })
    entries = [make(models=[{"family": "old"}])]
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "boom"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=evidence, verifier=lambda e: None)
    assert result["updates"] == ["x"]
    assert result["new"] == ["new1"]
    assert result["supersede"] == ["x: old → cur"]
    assert result["providers"] == ["hn"]
    assert entries[0].limits == "fixed"
    assert entries[0].models[0].superseded_by is None  # proposed, not written
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
