import sys
from datetime import date, timedelta

import httpx
import pytest
import respx

from freetier_radar import scout
from freetier_radar.discovery import Evidence, Hit
from freetier_radar.history import load_history
from freetier_radar.models import WATCH_RECHECK_DAYS, Entry, Watched, save_registry
from freetier_radar.scout import (
    FALLBACK_OPENROUTER_MODEL, OPENROUTER_BASE_URL, OVH_BASE_URL, Deadline, LLMClient, _ask,
    apply_new, apply_retirements, apply_updates, extract_yaml_block, pick_openrouter_model,
    run_scout, supersede_proposals,
)

TODAY = date(2026, 7, 19)

BASE = {
    "name": "X", "category": "api-free-tier", "url": "https://x.ai",
    "offering": "old offering", "limits": "old limits",
    # Verified today: the scout runs straight after the probes, so a live entry
    # is one the same run has just re-verified.
    "first_seen": date(2026, 1, 1), "last_verified": TODAY,
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
    applied, rejected = apply_updates(
        entries, [{"id": "x", "limits": "new limits", "id_hack": "y", "name": "Hacked"}])
    assert applied == ["x"] and rejected == []
    assert entries[0].limits == "new limits"
    assert entries[0].name == "X"
    assert entries[0].id == "x"


def test_apply_updates_reads_a_null_as_unchanged():
    """"Leave the probe alone" comes back as `probe: null` — which used to reach
    pydantic as "erase the probe" and crash the whole scout."""
    entries = [make()]
    applied, rejected = apply_updates(entries, [{"id": "x", "probe": None, "limits": "new limits"}])
    assert applied == ["x"] and rejected == []
    assert entries[0].probe.endpoint == "https://x.ai"
    assert entries[0].limits == "new limits"


def test_apply_updates_with_nothing_to_change_is_a_no_op():
    entries = [make()]
    assert apply_updates(entries, [{"id": "x", "probe": None}]) == ([], [])
    assert entries[0].limits == "old limits"


def test_apply_updates_rejects_an_invalid_update_instead_of_raising():
    entries = [make()]
    applied, rejected = apply_updates(entries, [{"id": "x", "probe": {"type": "telepathy"}}])
    assert applied == []
    assert rejected == ["x: invalid update (ValidationError)"]
    assert entries[0].probe.endpoint == "https://x.ai"  # left as it was


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
    proposed, suppressed = supersede_proposals(entries, [{"family": "old", "superseded_by": "cur"},
                                                         {"family": "nope", "superseded_by": "cur"}])
    assert proposed == ["x: old → cur"] and suppressed == []
    assert entries[0].models[0].superseded_by is None
    assert entries[0].models[1].superseded_by is None


def test_supersede_proposals_skip_marks_already_in_place():
    """PR #4 claimed four superseded families while its diff touched two."""
    entries = [make(models=[{"family": "old", "superseded_by": "cur"}, {"family": "cur"}])]
    assert supersede_proposals(entries, [{"family": "old", "superseded_by": "cur"}]) == ([], [])
    assert supersede_proposals(entries, [{"family": "cur", "superseded_by": "next"}]) \
        == (["x: cur → next"], [])


def test_a_dismissed_bump_is_reported_as_suppressed_not_proposed():
    """Nothing in the registry records a rejected bump, so the scout re-proposed
    z.ai's glm-4.7-flash → glm-5.2 in every PR. dismissed.yaml is that memory —
    and the suppression is printed, because a filter nobody sees is a filter
    nobody can correct."""
    entries = [make(models=[{"family": "old"}])]
    proposed, suppressed = supersede_proposals(
        entries, [{"family": "old", "superseded_by": "cur"}], {("x", "old", "cur")})
    assert proposed == [] and suppressed == ["x: old → cur"]
    # Dismissing one target does not dismiss the family: a later generation is
    # a different question.
    proposed, suppressed = supersede_proposals(
        entries, [{"family": "old", "superseded_by": "later"}], {("x", "old", "cur")})
    assert proposed == ["x: old → later"] and suppressed == []


def test_load_dismissed_reads_triples_and_ignores_junk(tmp_path):
    path = tmp_path / "dismissed.yaml"
    path.write_text(
        "dismissed:\n"
        "  - entry: zai-glm\n    family: glm-4.7-flash\n    superseded_by: glm-5.2\n"
        "    reason: the flagship is not on the free tier\n"
        "  - entry: half\n    family: written\n",  # no target: not a decision about anything
        encoding="utf-8")
    assert scout.load_dismissed(path) == {("zai-glm", "glm-4.7-flash", "glm-5.2")}
    assert scout.load_dismissed(tmp_path / "absent.yaml") == set()


def test_an_archived_entry_gets_no_generation_bumps():
    """GitHub Models kept drawing "gpt-4.1 → gpt-5.6" in every PR body for
    months after GitHub shut the product down."""
    llm = StubLLM({"MODEL-GENERATIONS":
                   "```yaml\nsupersede:\n  - family: old\n    superseded_by: cur\n```"})
    entries = [make(models=[{"family": "old"}], retired_on=date(2026, 6, 1))]
    result = run_scout(llm, entries, [], lambda urls: {}, TODAY)
    assert result["supersede"] == []
    assert not any("MODEL-GENERATIONS" in p for p in llm.prompts)


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


def test_run_scout_survives_a_bad_fix_and_still_discovers():
    """A single unusable correction used to abort the run — after the
    verification commit was already pushed, so it could not even be rerun."""
    llm = StubLLM({
        "FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    probe: null\n    offering: ''\n```",
        "DISCOVER-NEW": "```yaml\nnew_entries:\n"
                        "  - id: new1\n    name: New\n    category: trial\n    url: https://n.ai\n"
                        "    offering: trial\n"
                        "    probe: {type: page-keywords, endpoint: https://n.ai,"
                        " keywords: [n-flash-1, free]}\n```",
    })
    entries = [make()]
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "page gone: HTTP 410"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=evidence, verifier=lambda e: None)
    assert result["updates"] == ["x"]
    assert entries[0].probe.endpoint == "https://x.ai"  # the null did not erase it
    assert entries[0].offering == ""
    assert result["new"] == ["new1"]  # discovery still ran


def test_run_scout_reports_rejected_fixes_alongside_rejected_proposals():
    llm = StubLLM({
        "FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    probe: {type: telepathy}\n```",
        "DISCOVER-NEW": "```yaml\nnew_entries:\n  - id: broken\n```",
    })
    entries = [make()]
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "boom"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=evidence, verifier=lambda e: None)
    assert result["updates"] == []
    assert result["rejected"] == ["x: invalid update (ValidationError)",
                                  "broken: invalid (ValidationError)"]


def test_a_dead_backend_chain_keeps_the_fixes_the_scout_already_made():
    """Discovery holds the longest prompt of the run and dies first when the
    backends give out; the fix phase's work must survive that."""
    class Flaky(StubLLM):
        def complete(self, prompt: str) -> str:
            if "FIX-FAILED" not in prompt:
                self.prompts.append(prompt)
                raise RuntimeError("all LLM backends failed: openrouter: JSONDecodeError")
            return super().complete(prompt)

    llm = Flaky({"FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    limits: fixed\n```"})
    entries = [make(models=[{"family": "old"}])]
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "boom"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=evidence, verifier=lambda e: None)
    assert result["updates"] == ["x"] and entries[0].limits == "fixed"
    assert result["new"] == [] and result["supersede"] == []


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


@respx.mock
def test_llm_chain_skips_a_backend_that_answers_something_other_than_json():
    """OpenRouter returned HTTP 200 with a truncated body on 2026-08-03: the
    JSONDecodeError escaped the chain and killed the scout with OVH untried."""
    respx.get(f"{OPENROUTER_BASE_URL}/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "qwen/qwen3-coder:free"}]}
    ))
    respx.post(f"{OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, text='{"choices": [{"message": {"cont')
    )
    respx.get(f"{OVH_BASE_URL}/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "gpt-oss-120b"}]}
    ))
    respx.post(f"{OVH_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})
    )
    with httpx.Client() as http:
        assert LLMClient(openrouter_key="o", http=http).complete("hi") == "ok"


def test_main_reports_a_broken_scout_instead_of_failing_the_workflow(tmp_path, monkeypatch):
    """main() runs after the verification commit is pushed, and a failed run
    cannot be rerun — so whatever the scout hits, the job has to end clean."""
    registry = tmp_path / "registry.yaml"
    save_registry(registry, [make()])
    before = registry.read_text()
    pr_body = tmp_path / "scout-pr.md"

    def boom(*args, **kwargs):
        raise ValueError("backend answered HTML")

    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence())
    monkeypatch.setattr(scout, "run_scout", boom)
    monkeypatch.setattr(sys, "argv", [
        "freetier-scout", "--registry", str(registry), "--pr-body", str(pr_body),
        "--failures", str(tmp_path / "none.json"), "--blocklist", str(tmp_path / "none.yaml"),
    ])
    scout.main()  # must not raise
    assert "Scout aborted: backend answered HTML" in pr_body.read_text()
    assert registry.read_text() == before  # a half-run scout writes no registry


@respx.mock
def test_llm_chain_uses_the_second_endpoint_before_openrouter():
    """Two configured free providers beat one: the primary timing out should
    reach the spare, not hand the run to OpenRouter."""
    respx.post("https://primary.example/v1/chat/completions").mock(
        side_effect=httpx.ReadTimeout("too slow"))
    spare = respx.post("https://spare.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "spare"}}]}))
    openrouter = respx.post(f"{OPENROUTER_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "or"}}]}))
    with httpx.Client() as http:
        llm = LLMClient(openrouter_key="o",
                        custom_base_url="https://primary.example/v1", custom_model="m",
                        custom_key="k1",
                        fallback_base_url="https://spare.example/v1/", fallback_model="m2",
                        fallback_key="k2", http=http)
        assert llm.complete("hi") == "spare"
    assert spare.calls[0].request.headers["Authorization"] == "Bearer k2"
    assert b'"m2"' in spare.calls[0].request.content
    assert not openrouter.called


@respx.mock
def test_a_half_configured_fallback_is_ignored():
    respx.get(f"{OVH_BASE_URL}/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "gpt-oss-120b"}]}))
    respx.post(f"{OVH_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "ovh"}}]}))
    with httpx.Client() as http:
        llm = LLMClient(fallback_base_url="https://spare.example/v1", http=http)  # no model
        assert llm.complete("hi") == "ovh"


def ticking(step: float):
    """A clock that advances `step` seconds every time it is read."""
    state = {"t": 0.0}

    def clock() -> float:
        state["t"] += step
        return state["t"]
    return clock


@respx.mock
def test_a_trickling_backend_is_cut_off_at_its_wall_clock_deadline():
    """httpx restarts its timeout on every byte, so a backend that dribbles
    output is never "too slow" by that measure: OpenRouter streamed for ~9
    minutes inside a 90-second timeout on 2026-08-03 and then handed over a
    truncated body."""
    respx.post("https://slow.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, content=iter([b'{"choi', b'ces": [', b'{}]}'])))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://slow.example/v1", custom_model="m",
                        http=http, call_deadline=5.0, clock=ticking(3.0))
        with pytest.raises(RuntimeError, match="all LLM backends failed"):
            llm.complete("hi")  # no OVH mock: the chain must die having tried


def test_an_expired_run_budget_stops_a_backend_being_called_at_all():
    """The budget belongs to the run, not to the call: once it is gone, opening
    another connection only delays the report the workflow still has to write."""
    spent = Deadline(0.0, clock=ticking(1.0))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://x.example/v1", custom_model="m",
                        http=http, deadline=spent)
        with pytest.raises(RuntimeError, match="no wall-clock budget left"):
            llm.complete("hi")  # respx would raise on any unmocked request


def test_a_phase_budget_is_a_slice_of_the_run_and_expires_before_it():
    """The evidence phase runs before the first LLM call and answers to no clock
    of its own: one hung host there spends the run, and every phase after it then
    reports "skipped" while the workflow reports success. A share is how a phase
    that must not be able to do that gets its own smaller deadline."""
    now = {"t": 0.0}
    run = Deadline(100.0, clock=lambda: now["t"])
    share = run.share(0.25)
    assert share.remaining() == 25.0

    now["t"] = 30.0
    assert share.expired() and not run.expired()


def test_a_share_is_taken_from_what_is_left_not_from_the_whole_run():
    """Otherwise a phase starting late would be handed a budget the run cannot
    honour, and the cap would quietly stop capping anything."""
    now = {"t": 0.0}
    run = Deadline(100.0, clock=lambda: now["t"])
    now["t"] = 90.0
    assert run.share(0.25).remaining() == 2.5


def test_run_scout_skips_its_phases_when_the_budget_is_spent():
    llm = StubLLM({})
    entries = [make(models=[{"family": "old"}], source_urls=["https://x.ai/blog"])]
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "boom"}],
                       lambda urls: {u: "the free tier will be discontinued" for u in urls},
                       TODAY, evidence=evidence, verifier=lambda e: None,
                       deadline=Deadline(0.0, clock=ticking(1.0)))
    assert result["skipped"] == ["fixes", "discovery", "retirement sweep", "generation check"]
    assert llm.prompts == []


@respx.mock
def test_forcing_a_backend_skips_the_ones_before_it():
    """The spare endpoint has never run in CI — the primary has answered every
    scheduled run since it was wired up — so the only way to exercise it is to
    ask for it by name."""
    primary = respx.post("https://primary.example/v1/chat/completions")
    spare = respx.post("https://spare.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "spare"}}]}))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://primary.example/v1", custom_model="m",
                        fallback_base_url="https://spare.example/v1", fallback_model="m2",
                        http=http, force="custom-fallback")
        assert llm.complete("hi") == "spare"
    assert spare.called and not primary.called
    assert llm.describe() == ("forced custom-fallback (configured: custom → custom-fallback → "
                              "ovh-anonymous) — answered by custom-fallback")


def test_forcing_a_backend_that_is_not_configured_is_an_error():
    """Falling through to another backend would defeat the point of asking for
    this one, and the run would report a green chain it never tested."""
    llm = LLMClient(force="gemini")  # no GEMINI_API_KEY configured
    with pytest.raises(RuntimeError, match="forced backend 'gemini' is not configured"):
        llm.complete("hi")


def test_auto_means_no_forced_backend():
    """The workflow input defaults to "auto", so the env var arrives set."""
    assert LLMClient(force="auto")._force is None
    assert LLMClient(force="")._force is None


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


def watch(domain: str = "n.ai", checked_on: str = "2026-07-01") -> Watched:
    return Watched.model_validate({
        "domains": [domain], "name": "Watched Co", "checked_on": checked_on,
        "reason": "no zero-priced row in its catalog. Every model is metered",
        "reopen_if": "a zero-priced row appears"})


def test_apply_new_rejects_a_service_the_watchlist_already_answered():
    """A watched service usually still serves a page, so without this the
    proposal would spend a live probe re-asking a question a human answered."""
    entries = [make()]
    added, rejected = apply_new(entries, [proposal(id="w", url="https://api.n.ai/v1")],
                                TODAY, watchlist=[watch()])
    assert added == []
    assert rejected == ["w: on the watchlist since 2026-07-01 — "
                        "no zero-priced row in its catalog. Every model is metered"]


def test_a_long_watch_reason_is_cut_by_length_not_at_the_first_full_stop():
    """The reasons are full of hostnames and prices, so splitting on '.' cuts
    'api.llm7.io' in half and reads as a typo in the PR body."""
    entries = [make()]
    long_reason = watch()
    long_reason.reason = "api.llm7.io serves 35 models and " + "every one of them is metered " * 8
    _, rejected = apply_new(entries, [proposal(id="w", url="https://api.n.ai/v1")],
                            TODAY, watchlist=[long_reason])
    quoted = rejected[0].split(" — ", 1)[1]
    assert quoted.startswith("api.llm7.io serves 35 models")
    assert quoted.endswith("…") and len(quoted) <= scout.WATCH_REASON_IN_PR + 1


def test_an_expired_watch_verdict_lets_the_proposal_through():
    entries = [make()]
    stale = watch(checked_on=(TODAY - timedelta(days=WATCH_RECHECK_DAYS + 1)).isoformat())
    added, rejected = apply_new(entries, [proposal(id="w", url="https://api.n.ai/v1")],
                                TODAY, watchlist=[stale])
    assert added == ["w"] and rejected == []


def test_the_discovery_prompt_carries_only_verdicts_the_file_still_trusts():
    fresh, stale = watch("fresh.ai"), watch("stale.ai", checked_on="2026-01-01")
    text = scout.format_watchlist([fresh, stale], TODAY)
    assert "fresh.ai" in text and "reopen if: a zero-priced row appears" in text
    assert "stale.ai" not in text
    assert scout.format_watchlist([], TODAY) == "none"


def test_run_scout_reports_verdicts_due_for_a_recheck():
    """The loop-closer: an expired verdict stops suppressing silently and starts
    appearing in the PR body instead, so the question reaches a human."""
    expired = (TODAY - timedelta(days=WATCH_RECHECK_DAYS + 1)).isoformat()
    result = scout.run_scout(StubLLM({}), [make()], [], lambda urls: {}, TODAY,
                             watchlist=[watch("fresh.ai"), watch("stale.ai", checked_on=expired)])
    assert result["stale_watch"] == [f"Watched Co (checked {expired})"]


EMPTY_RUN = {"providers": [], "updates": [], "new": [], "rejected": [], "supersede": [],
             "suppressed": [], "stale_watch": [], "retired": [], "skipped": []}


def _scout_argv(tmp_path, *extra) -> list[str]:
    return ["freetier-scout", "--registry", str(tmp_path / "registry.yaml"),
            "--pr-body", str(tmp_path / "scout-pr.md"),
            "--failures", str(tmp_path / "none.json"),
            "--blocklist", str(tmp_path / "none.yaml"),
            "--dismissed", str(tmp_path / "none-dismissed.yaml"),
            "--watchlist", str(tmp_path / "none-watchlist.yaml"), *extra]


def test_main_records_what_the_scout_changed_in_the_history(tmp_path, monkeypatch):
    """The scout is the other command that writes registry.yaml, and the only
    one that ever adds a row."""
    save_registry(tmp_path / "registry.yaml", [make()])
    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence())
    monkeypatch.setattr(scout, "run_scout",
                        lambda llm, entries, *a, **k: entries.append(
                            make(id="newcomer", name="Newcomer")) or EMPTY_RUN)
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path))

    scout.main()

    events = load_history(tmp_path / "history.jsonl")
    assert [(e.event.value, e.id) for e in events] == [("added", "newcomer"), ("added", "x")]


def test_a_dry_run_scout_records_no_history(tmp_path, monkeypatch):
    save_registry(tmp_path / "registry.yaml", [make()])
    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence())
    monkeypatch.setattr(scout, "run_scout", lambda *a, **k: EMPTY_RUN)
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path, "--dry-run"))

    scout.main()

    assert not (tmp_path / "history.jsonl").exists()
