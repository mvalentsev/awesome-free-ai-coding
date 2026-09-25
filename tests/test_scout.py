import json
import sys
from datetime import date, timedelta

import httpx
import pytest
import respx

from freetier_radar import scout
from freetier_radar.discovery import Evidence, Hit
from freetier_radar.models import (SOURCE_RECHECK_DAYS, WATCH_RECHECK_DAYS, Entry, Source,
                                   Watched, save_registry)
from freetier_radar.scout import (
    FALLBACK_OPENROUTER_MODEL, OPENROUTER_BASE_URL, OVH_BASE_URL, Deadline, LLMClient, _ask,
    RETIREMENT_PAGE_CHARS, apply_new, apply_retirements, apply_updates, extract_yaml_block,
    pick_openrouter_model,
    published_model_ids, run_scout, supersede_proposals,
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
    """And says what it rejected and why. The reason goes in the PR body, which
    is the artifact a human reads; the exception type alone sent a reviewer to
    the log of a green run to find out that a fix had been found and dropped."""
    entries = [make()]
    applied, rejected = apply_updates(entries, [{"id": "x", "probe": {"type": "telepathy"}}])
    assert applied == []
    assert rejected == ["x: invalid update to probe — probe.type: Input should be "
                        "'api-models' or 'page-keywords'; probe.endpoint: Field required"]
    assert entries[0].probe.endpoint == "https://x.ai"  # left as it was


def test_apply_updates_refuses_a_fix_that_leaves_the_row_failing():
    """The shape of a correction was all anything checked, so a fix that made a
    row worse was written and reported as a repair. On 2026-09-03 kenari failed
    on one family its catalog had momentarily stopped serving, and the answer
    named six the same catalog prices in the thousands — every one of them a
    family the probe then could not find in the free lane."""
    entries = [make()]
    applied, rejected = apply_updates(
        entries, [{"id": "x", "models": [{"family": "y-pro-1"}]}],
        verifier=lambda e: "missing families: y-pro-1",
    )
    assert applied == []
    assert rejected == ["x: update to models still fails the probe — missing families: y-pro-1"]
    assert entries[0].models == []  # left as it was


def test_an_update_keeps_a_family_the_rows_own_probe_still_names():
    """The verifier asks whether the corrected row passes, and a shorter Models
    column always passes — so a reply that deletes too much was written as a
    repair. On 2026-09-21 aihubmix failed on one family, gpt-oss, and the reply
    cut the column to glm-5.3 alone: kimi-k3, glm-5, mimo-v2.5 and
    north-mini-code were still free in the catalog the verdict was read from."""
    entries = [make(models=[{"family": "x-mini-2", "tier": "strong"},
                            {"family": "x-pro-1"}, {"family": "x-old-1"}])]
    applied, rejected = apply_updates(
        entries, [{"id": "x", "models": [{"family": "x-mini-2"}]}],
        named=lambda e, family: family != "x-old-1")
    assert applied == ["x"]
    assert [m.family for m in entries[0].models] == ["x-mini-2", "x-pro-1"]
    assert rejected == ["x: the update dropped x-pro-1, which the row's own probe still "
                        "names — kept"]


def test_an_update_drops_a_family_the_probe_cannot_vouch_for():
    """Kept only on a yes. A page that could not be read answers None, and the
    drop goes through as it always did."""
    entries = [make(models=[{"family": "x-mini-2"}, {"family": "x-pro-1"}, {"family": "x-old-1"}])]
    applied, rejected = apply_updates(
        entries, [{"id": "x", "models": [{"family": "x-mini-2"}]}],
        named=lambda e, family: None if family == "x-pro-1" else False)
    assert applied == ["x"] and rejected == []
    assert [m.family for m in entries[0].models] == ["x-mini-2"]


def test_an_update_may_drop_a_family_a_reviewer_marked_superseded():
    """A family carrying `superseded_by` is one a human already said to replace,
    and replacing it is what the stale-models flag on such a row asks for."""
    entries = [make(models=[{"family": "x-mini-2", "superseded_by": "x-mini-3"}])]
    applied, rejected = apply_updates(
        entries, [{"id": "x", "models": [{"family": "x-mini-3"}]}],
        named=lambda e, family: True)
    assert applied == ["x"] and rejected == []
    assert [m.family for m in entries[0].models] == ["x-mini-3"]


def test_apply_updates_verifies_the_corrected_entry_and_not_the_old_one():
    seen = []
    entries = [make()]
    applied, rejected = apply_updates(
        entries, [{"id": "x", "limits": "new limits"}],
        verifier=lambda e: seen.append(e.limits),  # append returns None: verified
    )
    assert applied == ["x"] and rejected == []
    assert seen == ["new limits"]
    assert entries[0].limits == "new limits"


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


def test_a_proposed_row_says_what_its_free_part_is_and_a_sum_names_no_model():
    """The discovery prompt asks every proposal which kind of free it is, since
    freetier-check refuses a live row that does not say; a proposal whose credit
    is spent on the models it names is turned away with the rule, not added for a
    reviewer to find."""
    assert "free_part: models | sum | unnamed" in scout.DISCOVER_PROMPT
    entries = [make()]
    credit = {**proposal(id="credit", url="https://c.ai"), "free_part": "sum",
              "models": [{"family": "c-flash-1"}]}
    added, rejected = apply_new(entries, [credit, {**proposal(), "free_part": "models"}], TODAY)
    assert added == ["new1"] and entries[1].free_part == "models"
    assert len(rejected) == 1 and rejected[0].startswith("credit: invalid")
    assert "sum to spend" in rejected[0]


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


def test_apply_new_rejects_a_listed_vendor_proposed_at_another_of_its_hosts():
    """On 2026-09-14 the scout proposed nvidia-nim-free and zai-free, two vendors
    this list already carries, and both reached a live probe: the check compared
    the proposal's host with each row's url and nothing else, so a subdomain, a
    parent or the api host of a listed row read as a new vendor. Both probes
    failed, which is the only reason neither became a duplicate row."""
    entries = [make(url="https://z.ai", source_urls=["https://docs.z.ai/guides/overview/pricing"]),
               make(id="nvidia-nim", url="https://build.nvidia.com",
                    api={"base_url": "https://integrate.api.nvidia.com/v1"})]
    probed = []
    added, rejected = apply_new(entries, [proposal(id="zai-free", url="https://api.z.ai/api/paas/v4"),
                                          proposal(id="nvidia-nim-free", url="https://nvidia.com")],
                                TODAY, verifier=lambda e: probed.append(e.id))
    assert added == [] and probed == []
    assert rejected == ["zai-free: domain already covered", "nvidia-nim-free: domain already covered"]


def test_the_discovery_prompt_names_a_listed_repository_owner_and_not_the_whole_host():
    """Told "github.com" is covered, the model is told every repository is."""
    llm = StubLLM({})
    evidence = Evidence(hits=[Hit("https://n.ai", "New tool", "free plan", "hn")], providers=["hn"])
    run_scout(llm, [make(url="https://github.com/features/copilot")], [], lambda urls: {}, TODAY,
              evidence=evidence)
    prompt = next(p for p in llm.prompts if "DISCOVER-NEW" in p)
    assert "Domains already covered (do not repeat): github.com/features\n" in prompt


def test_apply_new_lets_a_new_repository_through_on_the_host_a_listed_row_uses():
    """Copilot's row lives at github.com/features/copilot, so an open-source agent
    proposed at its own repository was "domain already covered"."""
    entries = [make(url="https://github.com/features/copilot")]
    added, rejected = apply_new(entries, [proposal(id="agent", url="https://github.com/newvendor/agent")],
                                TODAY)
    assert added == ["agent"] and rejected == []


@respx.mock
def test_probe_check_rejects_a_proposal_naming_a_family_the_page_does_not():
    """bazaarlink's proposal invented two families that matched no id the vendor
    served. A new entry is authored from scratch, so there is no live row to
    protect and no reason to accept a Models column the page cannot back."""
    e = make(id="new1", models=[{"family": "x-mini-2", "tier": "strong"},
                                {"family": "x-ultra-9", "tier": "strong"}])
    respx.get("https://x.ai").mock(return_value=httpx.Response(
        200, text="x-mini-2 is free for everyone"))
    with httpx.Client() as client:
        assert scout.probe_check_sync(e, client) == (
            "listed families the page does not name: x-ultra-9")


@respx.mock
def test_probe_check_accepts_a_family_the_page_spells_differently():
    e = make(id="new1", models=[{"family": "x-mini-2", "tier": "strong"}])
    respx.get("https://x.ai").mock(return_value=httpx.Response(
        200, text="X Mini 2 is free for everyone, and x-mini-2 is its id"))
    with httpx.Client() as client:
        assert scout.probe_check_sync(e, client) is None


@respx.mock
def test_probe_check_reads_the_page_a_followed_index_names():
    """A row whose probe starts at a docs index is vetted, and its families
    looked for, on the page the index names — the index is a JSON blob that
    names no model."""
    e = make(id="indexed", models=[{"family": "x-mini-2", "tier": "strong"}],
             probe={"type": "page-keywords", "endpoint": "https://x.ai/api/doc-index",
                    "keywords": ["x-mini-2"],
                    "follow": {"field": "Data.TargetPrefix", "suffix": "/limits.md"}})
    respx.get("https://x.ai/api/doc-index").mock(return_value=httpx.Response(
        200, json={"Data": {"TargetPrefix": "https://docs.x.ai/2026-9-10"}}))
    respx.get("https://docs.x.ai/2026-9-10/limits.md").mock(return_value=httpx.Response(
        200, text="x-mini-2 is free for everyone"))
    with httpx.Client() as client:
        assert scout.probe_check_sync(e, client) is None
        assert scout.named_by_row(client)(e, "x-mini-2") is True


@respx.mock
def test_a_catalog_without_prices_is_read_with_its_free_list_by_the_scout_too():
    """A generation bump is measured against what the row serves free, and on a
    catalog that prices nothing only the vendor's free list says what that is:
    on 2026-09-23 NVIDIA's catalog answered moonshotai/kimi-k2.6 beside kimi-k3
    and the list marked only kimi-k3, so the catalog alone would call a family
    served that the row cannot offer."""
    e = make(id="nimmy", models=[{"family": "kimi-k3", "tier": "strong"}],
             probe={"type": "api-models", "endpoint": "https://integrate.x.ai/v1/models",
                    "require_zero_price": True, "free_list": "https://api.x.ai/search?q=free"})
    respx.get("https://integrate.x.ai/v1/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "moonshotai/kimi-k3"}, {"id": "moonshotai/kimi-k2.6"}]}))
    free = {"resultTotal": 1, "resultPageTotal": 1, "results": [{"groupValue": "ENDPOINT", "resources": [
        {"name": "kimi-k3", "labels": [
            {"key": "general", "unresolvedValues": ["playgroundtype_chat", "nim_type_preview"]},
            {"key": "publisher", "values": ["moonshotai"]}], "attributes": []}]}]}
    route = respx.get("https://api.x.ai/search?q=free").mock(
        return_value=httpx.Response(200, json=free))
    with httpx.Client() as client:
        assert scout.probe_check_sync(e, client) is None
        named = scout.named_by_row(client)
        assert named(e, "kimi-k3") is True
        assert named(e, "kimi-k2.6") is False

    route.mock(return_value=httpx.Response(403, text="denied"))
    with httpx.Client() as client:
        assert "free list" in scout.probe_check_sync(e, client)
        assert scout.named_by_row(client)(e, "kimi-k3") is None


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
    proposed, suppressed, filtered = supersede_proposals(
        entries, [{"family": "old", "superseded_by": "new"}, {"family": "nope", "superseded_by": "new"}])
    assert proposed == ["x: old → new"] and suppressed == [] and filtered == []
    assert entries[0].models[0].superseded_by is None
    assert entries[0].models[1].superseded_by is None


def test_supersede_proposals_skip_marks_already_in_place():
    """PR #4 claimed four superseded families while its diff touched two."""
    entries = [make(models=[{"family": "old", "superseded_by": "cur"}, {"family": "cur"}])]
    assert supersede_proposals(entries, [{"family": "old", "superseded_by": "cur"}]) == ([], [], [])
    assert supersede_proposals(entries, [{"family": "cur", "superseded_by": "next"}]) \
        == (["x: cur → next"], [], [])


def test_a_dismissed_bump_is_reported_as_suppressed_not_proposed():
    """Nothing in the registry records a rejected bump, so the scout re-proposed
    z.ai's glm-4.7-flash → glm-5.2 in every PR. dismissed.yaml is that memory —
    and the suppression is printed, because a filter nobody sees is a filter
    nobody can correct."""
    entries = [make(models=[{"family": "old"}])]
    proposed, suppressed, _ = supersede_proposals(
        entries, [{"family": "old", "superseded_by": "cur"}], {("x", "old", "cur")})
    assert proposed == [] and suppressed == ["x: old → cur"]
    # Dismissing one target does not dismiss the family: a later generation is
    # a different question.
    proposed, suppressed, _ = supersede_proposals(
        entries, [{"family": "old", "superseded_by": "later"}], {("x", "old", "cur")})
    assert proposed == ["x: old → later"] and suppressed == []


def test_a_bump_to_a_family_the_row_already_lists_is_filtered_out():
    """Nine of the thirty bumps on 2026-09-14 named a family already on the same
    row — kilo-code, requesty and kenari each told to trade nemotron-3-super for
    the nemotron-3-ultra they list beside it. A mark would only hide a model the
    row still hands out, and 2026-09-08's reviewer dismissed that shape each time."""
    entries = [make(models=[{"family": "nemotron-3-super"}, {"family": "nemotron-3-ultra"}])]
    proposed, suppressed, filtered = supersede_proposals(
        entries, [{"family": "nemotron-3-super", "superseded_by": "nemotron-3-ultra"}])
    assert proposed == [] and suppressed == []
    assert filtered == ["x: nemotron-3-super → nemotron-3-ultra (the row already lists it)"]


def test_a_bump_to_a_model_of_the_same_family_is_filtered_out():
    """The prompt forbids it in so many words — "nemotron is not superseded by
    nemotron-3-ultra" — and the model did it eight times on 2026-09-14, six of them
    qwen3.8 → qwen3.8-max on rows that serve only the 27B."""
    entries = [make(models=[{"family": "qwen3.8"}, {"family": "nemotron"}])]
    proposed, _, filtered = supersede_proposals(
        entries, [{"family": "qwen3.8", "superseded_by": "qwen3.8-max"},
                  {"family": "nemotron", "superseded_by": "nemotron-3-nano-omni"},
                  {"family": "qwen3.8", "superseded_by": "qwen3.9"}])
    assert filtered == ["x: qwen3.8 → qwen3.8-max (a model of the same family)",
                        "x: nemotron → nemotron-3-nano-omni (a model of the same family)"]
    assert proposed == ["x: qwen3.8 → qwen3.9"]


def test_a_bump_the_rows_own_probe_does_not_name_is_filtered_out_and_an_unread_one_is_not():
    """A newer generation this vendor does not serve cannot supersede one it
    does. Where the row's page could not be read, nothing is known, and the
    bump reaches a human as before."""
    entries = [make(models=[{"family": "qwen3.6"}]), make(id="y", models=[{"family": "qwen3.6"}])]
    asked = []

    def named(entry, family):
        asked.append((entry.id, family))
        return {"x": False, "y": None}[entry.id]

    proposed, _, filtered = supersede_proposals(
        entries, [{"family": "qwen3.6", "superseded_by": "qwen3.7-flash"}], named=named)
    assert filtered == ["x: qwen3.6 → qwen3.7-flash (not named where the row's probe reads)"]
    assert proposed == ["y: qwen3.6 → qwen3.7-flash"]
    assert asked == [("x", "qwen3.7-flash"), ("y", "qwen3.7-flash"), ("y", "qwen3.6")]


def test_a_bump_is_ruled_out_while_the_row_still_serves_the_family_it_would_hide():
    """Every Flash Google has made free kept its free column when the next one
    arrived, and AIHubMix lists coding-glm-5-free beside coding-glm-5.1-free: a
    mark there hides a model the vendor still hands out. The three bumps the
    other rules left on 2026-09-14 were all this shape, and so were the 2026-09-08
    dismissals they would have joined. What is left to propose is the bump that
    means something — the old family gone from the row's evidence, the new one
    there."""
    entries = [make(models=[{"family": "glm-5"}]), make(id="y", models=[{"family": "glm-5"}]),
               make(id="z", models=[{"family": "glm-5"}])]
    served = {("x", "glm-5"): True, ("y", "glm-5"): False, ("z", "glm-5"): None}
    proposed, _, filtered = supersede_proposals(
        entries, [{"family": "glm-5", "superseded_by": "glm-5.1"}],
        named=lambda e, f: True if f == "glm-5.1" else served[(e.id, f)])
    assert filtered == ["x: glm-5 → glm-5.1 (the row's probe still names glm-5 too)"]
    assert proposed == ["y: glm-5 → glm-5.1", "z: glm-5 → glm-5.1"]


def test_a_dismissed_or_already_listed_bump_costs_no_page_read():
    entries = [make(models=[{"family": "old"}, {"family": "cur"}])]
    asked = []
    supersede_proposals(entries, [{"family": "old", "superseded_by": "cur"},
                                  {"family": "old", "superseded_by": "gone"}],
                        {("x", "old", "gone")}, named=lambda e, f: asked.append(f))
    assert asked == []


@respx.mock
def test_the_rows_page_is_read_once_however_many_bumps_name_it():
    route = respx.get("https://x.ai").mock(return_value=httpx.Response(
        200, text="qwen3.7-flash and qwen3.9 are both free here"))
    respx.get("https://y.ai").mock(return_value=httpx.Response(403, text="denied"))
    x, y = make(), make(id="y", url="https://y.ai",
                        probe={"type": "page-keywords", "endpoint": "https://y.ai",
                               "keywords": ["y-mini-2", "free"]})
    with httpx.Client() as client:
        named = scout.named_by_row(client)
        assert named(x, "qwen3.7-flash") is True
        assert named(x, "qwen3.9") is True
        assert named(x, "qwen4") is False
        assert named(y, "qwen3.9") is None
    assert route.call_count == 1


@respx.mock
def test_a_row_is_not_read_once_the_runs_budget_is_spent():
    """The generation check runs last, on whatever the run has left."""
    route = respx.get("https://x.ai").mock(return_value=httpx.Response(200, text="qwen3.9"))
    with httpx.Client() as client:
        assert scout.named_by_row(client, time_left=lambda: 0)(make(), "qwen3.9") is None
    assert route.call_count == 0


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


def test_the_retirement_sweep_reads_no_page_of_a_delisted_row():
    """A delisted row is off the list already; its pages are the ones whose
    offer ended or never qualified, and some are on services the blocklist says
    never to fetch."""
    fetched: list[str] = []
    llm = StubLLM({"FIND-RETIREMENTS": "```yaml\nretire: []\n```"})
    entries = [make(source_urls=["https://x.ai/blog"]),
               make(id="gone", url="https://n.ai", source_urls=["https://n.ai/blog"],
                    delisted={"on": TODAY, "reason": "no free lane"})]
    run_scout(llm, entries, [], lambda urls: fetched.extend(urls) or {u: "" for u in urls}, TODAY)
    assert "https://n.ai/blog" not in fetched


def test_run_scout_skips_the_llm_when_no_page_hints_at_a_retirement():
    """Almost every sweep answers "nothing retiring". Sending 30 unremarkable
    pages to the LLM cost ~20k tokens and risked blowing a backend's context."""
    llm = StubLLM({})
    entries = [make(source_urls=["https://x.ai/blog"])]
    run_scout(llm, entries, [], lambda urls: {u: "our free tier, as always" for u in urls}, TODAY)
    assert not any("FIND-RETIREMENTS" in p for p in llm.prompts)


def test_the_retirement_sweep_names_the_entries_it_flagged(capsys):
    """The sweep reported a bare count, so learning which entry tripped it meant
    re-fetching every live entry's first source url by hand. The one that trips
    it today is google-ai-studio, on the word "Deprecations" sitting in the docs
    sidebar — benign, and invisible until someone reproduced the sweep."""
    llm = StubLLM({"FIND-RETIREMENTS": "```yaml\nretire: []\n```"})
    pages = {"https://x.ai/blog": "our free tier, as always",
             "https://y.ai/docs": "release notes deprecations libraries migration"}
    entries = [make(id="x", source_urls=["https://x.ai/blog"]),
               make(id="y", source_urls=["https://y.ai/docs"])]
    run_scout(llm, entries, [], lambda urls: {u: pages[u] for u in urls}, TODAY)
    assert "retirement sweep: 1/2 pages carry a signal (y)" in capsys.readouterr().out


def test_the_retirement_excerpt_is_cut_around_the_signal_and_not_from_the_top():
    """The signal was searched in every character the fetcher keeps while the
    model was handed the first RETIREMENT_PAGE_CHARS, so an announcement in
    the second half tripped the count on every run and could never become a
    proposal — the sentence the model must copy verbatim was not in front of
    it."""
    filler = " ".join(["pricing table row"] * 400)
    assert len(filler) > RETIREMENT_PAGE_CHARS
    notice = "the free tier will be retired on 2026-07-30, use the paid plan"
    llm = StubLLM({"FIND-RETIREMENTS": "```yaml\nretire: []\n```"})
    entries = [make(source_urls=["https://x.ai/blog"])]
    run_scout(llm, entries, [], lambda urls: {u: filler + " " + notice for u in urls}, TODAY)
    prompt = next(p for p in llm.prompts if "FIND-RETIREMENTS" in p)
    assert notice in prompt


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
    # Both halves name the field that failed. A proposal used to reach the PR as
    # "invalid (ValidationError)", which is the exception's class name and not a
    # reason: on 2026-09-10 that was the whole public account of a rejected llm7.
    assert result["rejected"] == ["x: invalid update to probe — probe.type: Input should be "
                                  "'api-models' or 'page-keywords'; probe.endpoint: Field required",
                                  "broken: invalid — name: Field required; "
                                  "category: Field required; url: Field required"]
    # The row the scout could not repair is still failing, and says so.
    assert result["unfixed"] == ["x: fail — boom"]


def test_a_fix_the_probe_rejects_leaves_the_row_on_the_unfixed_list():
    """A repair the run cannot stand behind must not read as a repair. `updates`
    is what the pull request calls fixed and what drops off `unfixed`, so an
    unverified correction there hides a failing row twice over."""
    llm = StubLLM({"FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    limits: guessed\n```"})
    entries = [make()]
    result = run_scout(llm, entries, [{"id": "x", "status": "fail", "detail": "boom"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=None, verifier=lambda e: "missing keywords: x-mini-2")
    assert result["updates"] == []
    assert entries[0].limits == "old limits"
    assert result["rejected"] == ["x: update to limits still fails the probe — "
                                  "missing keywords: x-mini-2"]
    assert result["unfixed"] == ["x: fail — boom"]


def test_a_repaired_row_keeps_its_ids_half_on_the_unfixed_list():
    """The half of a failure line the fix prompt tells the model to leave alone
    left the pull request with the row the model did answer for. On 2026-09-21
    aihubmix's line named eight ids the catalog no longer served; the scout
    answered the family half, the row dropped off `unfixed` whole, and the ids
    went on in the configs with nothing in the PR to say so."""
    llm = StubLLM({"FIX-FAILED": "```yaml\nupdates:\n  - id: x\n"
                                 "    models: [{family: x-mini-2}]\n```"})
    entries = [make(models=[{"family": "x-mini-2"}, {"family": "x-old-1"}])]
    ids_half = ("api.model_ids the catalog no longer answers for: "
                "vendor/x-old-1 is not in the catalog")
    result = run_scout(llm, entries,
                       [{"id": "x", "status": "fail",
                         "detail": f"missing families: x-old-1 | {ids_half}"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=None, verifier=lambda e: None)
    assert result["updates"] == ["x"]
    assert result["unfixed"] == [f"x: {ids_half}"]


def test_the_fix_phase_asks_the_rows_probe_before_a_family_goes():
    llm = StubLLM({"FIX-FAILED": "```yaml\nupdates:\n  - id: x\n"
                                 "    models: [{family: x-mini-2}]\n```"})
    entries = [make(models=[{"family": "x-mini-2"}, {"family": "x-pro-1"}])]
    result = run_scout(llm, entries,
                       [{"id": "x", "status": "fail", "detail": "missing families: x-old-1"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=None, verifier=lambda e: None,
                       named=lambda e, family: True)
    assert [m.family for m in entries[0].models] == ["x-mini-2", "x-pro-1"]
    assert result["rejected"] == ["x: the update dropped x-pro-1, which the row's own probe "
                                  "still names — kept"]


def test_a_stale_ids_row_is_reported_rather_than_handed_to_the_model():
    """What that row needs is an exact id copied out of a vendor catalog, and
    `api` is not a key the fix prompt may write — so every correction the model
    could return would change something that is not broken. It has to reach the
    pull request as a line for a human instead."""
    llm = StubLLM({"FIX-FAILED": "```yaml\nupdates:\n  - id: x\n    limits: guessed\n```"})
    entries = [make()]
    result = run_scout(llm, entries,
                       [{"id": "x", "status": "stale-ids",
                         "detail": "api.model_ids the catalog no longer answers for: "
                                   "vendor/gone is not in the catalog"}],
                       lambda urls: {u: "page text" for u in urls}, TODAY,
                       evidence=None, verifier=lambda e: None)
    assert result["updates"] == []
    assert entries[0].limits != "guessed"
    assert not any("FIX-FAILED" in p for p in llm.prompts)
    assert result["unfixed"] == ["x: stale-ids — api.model_ids the catalog no longer "
                                 "answers for: vendor/gone is not in the catalog"]


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
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path))
    scout.main()  # must not raise
    assert "Scout aborted: backend answered HTML" in pr_body.read_text()
    assert registry.read_text() == before  # a half-run scout writes no registry
    # Ending clean is not the same as passing unremarked: the workflow's last
    # step reads this and turns the run red once the report has landed.
    assert json.loads((tmp_path / "scout-status.json").read_text()) == {
        "llm_outages": [], "aborted": "backend answered HTML", "feed_warnings": []}


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


@respx.mock
def test_a_retired_pin_costs_a_candidate_and_not_the_endpoint():
    """What took the whole chain down on 2026-08-31: SCOUT_FALLBACK_MODEL named
    deepseek-v4-flash-free, an id opencode Zen had moved off its free pricing
    table eleven days earlier — a demotion this registry had already written
    down. A 400 is news about the model, so the ids the registry publishes for
    that base url stand behind the pin."""
    route = respx.post("https://zen.example/v1/chat/completions")
    route.side_effect = [
        httpx.Response(400, json={"error": {"message": "unknown model"}}),
        httpx.Response(200, json={"choices": [{"message": {"content": "zen"}}]}),
    ]
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://zen.example/v1",
                        custom_model="retired-free", custom_key="k",
                        models_by_base_url={"https://zen.example/v1": ["still-free"]},
                        http=http)
        assert llm.complete("hi") == "zen"
    assert b'"retired-free"' in route.calls[0].request.content
    assert b'"still-free"' in route.calls[1].request.content
    assert llm.answered_model == "still-free"


@respx.mock
def test_a_disowned_model_is_reported_with_the_vendor_s_reason():
    """A 400 is read as news about the model, and on 2026-09-16 that reading
    was wrong. The forced fallback run printed "no model this endpoint still
    serves: nemotron-3-ultra-free (400)", which sends a reader to retype the
    variable, while opencode Zen's body said why: the whole free tier had been
    locked to OpenCode's own client since 2026-09-07. The status is the same
    for both repairs; only the vendor's sentence tells them apart."""
    respx.post("https://zen.example/v1/chat/completions").mock(return_value=httpx.Response(
        400, json={"type": "error", "error": {
            "type": "MissingSessionID",
            "message": "Error from provider (Console): OpenCode's free tier can only "
                       "be used in OpenCode"}}))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://zen.example/v1", custom_model="gone-free",
                        custom_key="k", http=http, force="custom")
        with pytest.raises(RuntimeError) as failed:
            llm.complete("hi")
    assert ("gone-free (400: Error from provider (Console): OpenCode's free tier can only "
            "be used in OpenCode)") in str(failed.value)


@respx.mock
def test_an_upstream_error_answered_as_200_costs_a_candidate_and_says_why():
    """Kilo's gateway answers an overloaded upstream with HTTP 200 and an error
    object instead of choices. On 2026-09-16 the forced fallback run read that
    as "KeyError: 'choices'" and dropped the whole backend for the phase, while
    the registry lists nineteen other free ids on the same base url. The error
    is about the model it names, so it costs that candidate, and the vendor's
    sentence is what the log keeps."""
    route = respx.post("https://gw.example/v1/chat/completions")
    route.side_effect = [
        httpx.Response(200, json={"error": {
            "message": "Upstream error from Nvidia: Service temporarily overloaded", "code": 502}}),
        httpx.Response(200, json={"choices": [{"message": {"content": "routed"}}]}),
    ]
    with httpx.Client() as http:
        llm = LLMClient(fallback_base_url="https://gw.example/v1", fallback_model="big-model:free",
                        models_by_base_url={"https://gw.example/v1": ["big-model:free", "router/free"]},
                        http=http, force="custom-fallback")
        assert llm.complete("hi") == "routed"
    assert llm.answered_model == "router/free"

    route.side_effect = [httpx.Response(200, json={"error": {"message": "overloaded"}})] * 2
    with httpx.Client() as http:
        llm = LLMClient(fallback_base_url="https://gw.example/v1", fallback_model="big-model:free",
                        models_by_base_url={"https://gw.example/v1": ["big-model:free", "router/free"]},
                        http=http, force="custom-fallback")
        with pytest.raises(RuntimeError) as failed:
            llm.complete("hi")
    assert "big-model:free (no completion: overloaded)" in str(failed.value)
    assert "KeyError" not in str(failed.value)


@pytest.mark.parametrize(("body", "reason"), [
    (b'{"error": {"message": "Model  gone-free\\n is not supported"}}',
     "Model gone-free is not supported"),
    (b'{"error": "payment required"}', "payment required"),
    (b'{"message": "unknown model"}', "unknown model"),
    (b"upstream said no", "upstream said no"),
    (b"<!DOCTYPE html><html><body>400 Bad Request</body></html>", ""),
    (b"", ""),
])
def test_a_refusal_reads_as_the_vendor_s_own_sentence(body, reason):
    assert scout.refusal_reason(body) == reason


def test_a_refusal_reason_fits_a_log_line():
    assert len(scout.refusal_reason(b"x" * 10_000)) == scout.REFUSAL_REASON_CHARS


@respx.mock
def test_a_spent_wallet_fails_the_backend_and_not_one_model():
    """Ollama's $0 plan became a starter wallet between the 2026-08-27 and
    2026-08-31 runs and answered 402 for a model that had worked all month.
    Walking the endpoint's other ids on that is three more calls to a wallet
    with nothing in it."""
    route = respx.post("https://wallet.example/v1/chat/completions").mock(
        return_value=httpx.Response(402, json={"error": "payment required"}))
    respx.get(f"{OVH_BASE_URL}/models").mock(return_value=httpx.Response(
        200, json={"data": [{"id": "gpt-oss-120b"}]}))
    respx.post(f"{OVH_BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "ovh"}}]}))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://wallet.example/v1", custom_key="k",
                        models_by_base_url={"https://wallet.example/v1": ["a", "b", "c"]},
                        http=http)
        assert llm.complete("hi") == "ovh"
    assert route.call_count == 1


@respx.mock
def test_a_retired_model_is_paid_for_once_a_run():
    """Four LLM phases against one endpoint: without a memory of what it
    disowned, the run buys the same 400 four times."""
    route = respx.post("https://zen.example/v1/chat/completions")
    route.side_effect = [
        httpx.Response(400),
        httpx.Response(200, json={"choices": [{"message": {"content": "one"}}]}),
        httpx.Response(200, json={"choices": [{"message": {"content": "two"}}]}),
    ]
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://zen.example/v1", custom_model="gone",
                        models_by_base_url={"https://zen.example/v1": ["live"]}, http=http)
        assert llm.complete("hi") == "one"
        assert llm.complete("again") == "two"
    assert route.call_count == 3
    assert sum(b'"gone"' in call.request.content for call in route.calls) == 1


@respx.mock
def test_a_backend_with_no_pin_runs_on_what_the_registry_publishes():
    """SCOUT_MODEL names a deliberate choice; it is not what keeps the backend
    configured. An endpoint this registry describes needs nothing typed."""
    route = respx.post("https://zen.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "zen"}}]}))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://zen.example/v1/", custom_key="k",
                        models_by_base_url={"https://zen.example/v1": ["first", "second"]},
                        http=http)
        assert llm.complete("hi") == "zen"
    assert b'"first"' in route.calls[0].request.content


def test_published_model_ids_leaves_out_the_rows_a_vendor_has_retired():
    """A retired row's ids are precisely the ones that stopped being served."""
    entries = [
        make(id="live", api={"base_url": "https://a.example/v1", "model_ids": ["x", "y"]}),
        make(id="also-live", api={"base_url": "https://a.example/v1/", "model_ids": ["z"]}),
        make(id="gone", retired_on=date(2026, 6, 1),
             api={"base_url": "https://a.example/v1", "model_ids": ["dead"]}),
        make(id="taken-off", url="https://b.example", delisted={"on": TODAY, "reason": "no free lane"},
             api={"base_url": "https://a.example/v1", "model_ids": ["metered"]}),
        make(id="no-api"),
    ]
    assert published_model_ids(entries) == {"https://a.example/v1": ["x", "y", "z"]}


@respx.mock
def test_a_pin_the_registry_does_not_list_is_named_in_the_report():
    """The chain now survives a retired pin quietly, and a quiet recovery is
    still a decision for a human: either the variable wants retyping or the
    row's ids are wrong."""
    respx.post("https://zen.example/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "zen"}}]}))
    with httpx.Client() as http:
        llm = LLMClient(custom_base_url="https://zen.example/v1", custom_model="not-listed",
                        models_by_base_url={"https://zen.example/v1": ["listed"]}, http=http)
        assert llm.unlisted_pins == ["custom: not-listed on https://zen.example/v1"]
        # Reported, not overruled: the pin is still what gets tried first.
        assert llm.complete("hi") == "zen"
        assert llm.answered_model == "not-listed"


def test_no_claim_is_made_about_an_endpoint_the_registry_does_not_describe():
    """Point SCOUT_BASE_URL at Groq or Cerebras and this registry has nothing to
    say about the id — silence there is the only honest answer."""
    llm = LLMClient(custom_base_url="https://groq.example/v1", custom_model="whatever",
                    models_by_base_url={"https://elsewhere.example/v1": ["x"]})
    assert llm.unlisted_pins == []


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
                              "ovh-anonymous) — answered by custom-fallback (m2)")


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


def source(name: str = "someone/a-list", checked_on: str = "2026-08-01") -> Source:
    return Source.model_validate({
        "url": f"https://github.com/{name}", "name": name, "checked_on": checked_on,
        "reason": "carries no provider-level data", "reopen_if": "it starts publishing endpoints"})


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


def test_a_delisted_row_leaves_its_domain_to_its_verdict():
    """A delisted row is the record of a row, not coverage of a vendor. Its
    verdict lives in the watchlist, which expires so the question comes back;
    if the row itself counted as coverage the scout would never raise the
    vendor again — nor see its evidence."""
    entries = [make(), make(id="gone", url="https://n.ai",
                            delisted={"on": TODAY, "reason": "no free lane"})]
    added, rejected = apply_new(entries, [proposal(id="w", url="https://api.n.ai/v1")], TODAY)
    assert added == ["w"] and rejected == []


def test_a_proposal_that_reuses_an_archived_rows_id_is_reported_not_dropped():
    """An id belongs to a published page for good. A vendor coming back under
    the id its archived row holds is news for the reviewer, who restores the
    row — silently skipping it as a duplicate would lose exactly that lead."""
    entries = [make(id="gone", url="https://n.ai", delisted={"on": TODAY, "reason": "no free lane"})]
    added, rejected = apply_new(entries, [proposal(id="gone", url="https://n.ai")], TODAY)
    assert added == []
    assert rejected == ["gone: an archived row holds this id — if the offer is back, "
                        "restore that row instead of adding a second one"]


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


def test_run_scout_reports_sources_due_for_a_re_read():
    """Nothing else ever re-opens sources.yaml. The scout does not read those
    lists and cannot act on them — it carries the question to the PR body,
    which is the only recurring channel this repo has to a human."""
    expired = (TODAY - timedelta(days=SOURCE_RECHECK_DAYS + 1)).isoformat()
    result = scout.run_scout(StubLLM({}), [make()], [], lambda urls: {}, TODAY,
                             sources=[source(), source("stale/list", checked_on=expired)])
    assert result["stale_sources"] == [f"stale/list (read {expired})"]


EMPTY_RUN = {"providers": [], "updates": [], "new": [], "rejected": [], "supersede": [],
             "suppressed": [], "supersede_filtered": [], "stale_watch": [], "stale_sources": [],
             "retired": [], "skipped": [], "unfixed": [], "llm_outages": []}


class DeadChainLLM:
    """What `LLMClient.complete` raises once every backend has failed."""

    def complete(self, prompt: str) -> str:
        raise RuntimeError("all LLM backends failed: custom: HTTPStatusError: 402")


def test_a_phase_that_loses_every_backend_says_so_instead_of_going_quiet():
    """A run that could not think and a run that found nothing write the same
    empty result. On 2026-08-31 that difference sat behind a green tick for four
    days: both custom backends were dead, OVH rate-limited the third call, and
    the generation check never ran."""
    result = run_scout(DeadChainLLM(), [make(models=[{"family": "old"}])], [],
                       lambda urls: {}, TODAY)

    assert result["llm_outages"] == ["generation check"]
    # `skipped` is the phase that never asked, and the two mean opposite things
    # about the run.
    assert result["skipped"] == []


def test_main_writes_the_outage_the_workflows_last_step_reads(tmp_path, monkeypatch):
    save_registry(tmp_path / "registry.yaml", [make()])
    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence())
    monkeypatch.setattr(scout, "run_scout",
                        lambda *a, **k: {**EMPTY_RUN, "llm_outages": ["discovery"]})
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path, "--dry-run"))

    scout.main()

    assert json.loads((tmp_path / "scout-status.json").read_text()) == {
        "llm_outages": ["discovery"], "aborted": None, "feed_warnings": []}
    assert "discovery" in (tmp_path / "scout-pr.md").read_text()


def test_a_feed_that_went_quiet_reaches_the_status_file_and_the_pull_request(
        tmp_path, monkeypatch, capsys):
    """The warnings discovery collects about the curated feeds go where a human
    reads: the run's log, the pull request, and the status file the workflow's
    last step turns into annotations."""
    save_registry(tmp_path / "registry.yaml", [make()])
    warning = "someone/old-list: archived on GitHub, last pushed 2026-02-23"
    monkeypatch.setattr(scout, "gather_evidence",
                        lambda *a, **k: Evidence(feed_warnings=[warning]))
    monkeypatch.setattr(scout, "run_scout", lambda *a, **k: EMPTY_RUN)
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path, "--dry-run"))

    scout.main()

    assert json.loads((tmp_path / "scout-status.json").read_text())["feed_warnings"] == [warning]
    assert f"Curated feeds that need a look: {warning}" in (tmp_path / "scout-pr.md").read_text()
    assert f"feed warning: {warning}" in capsys.readouterr().out


def _scout_argv(tmp_path, *extra) -> list[str]:
    return ["freetier-scout", "--registry", str(tmp_path / "registry.yaml"),
            "--pr-body", str(tmp_path / "scout-pr.md"),
            "--failures", str(tmp_path / "none.json"),
            "--blocklist", str(tmp_path / "none.yaml"),
            "--dismissed", str(tmp_path / "none-dismissed.yaml"),
            "--watchlist", str(tmp_path / "none-watchlist.yaml"),
            "--sources", str(tmp_path / "none-sources.yaml"),
            "--status", str(tmp_path / "scout-status.json"), *extra]


def test_the_pr_body_carries_every_line_the_template_promises(tmp_path, monkeypatch):
    """The template is formatted once, in main, from the keys run_scout put in
    the result. A key added to one and not the other fails nowhere else: on the
    scheduled run, in CI, after the verification commit is already pushed."""
    save_registry(tmp_path / "registry.yaml", [make()])
    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence())
    monkeypatch.setattr(scout, "run_scout", lambda *a, **k: {
        **EMPTY_RUN, "stale_sources": ["someone/a-list (read 2026-01-01)"]})
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path, "--dry-run"))

    scout.main()

    body = (tmp_path / "scout-pr.md").read_text()
    assert "someone/a-list (read 2026-01-01)" in body
    assert f"older than {SOURCE_RECHECK_DAYS} days" in body


def test_the_pr_body_shows_the_bumps_it_filtered_out(tmp_path, monkeypatch):
    """A filter nobody can see is a filter nobody can correct."""
    save_registry(tmp_path / "registry.yaml", [make()])
    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence())
    monkeypatch.setattr(scout, "run_scout", lambda *a, **k: {
        **EMPTY_RUN, "supersede_filtered": ["x: qwen3.8 → qwen3.8-max (a model of the same family)"]})
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path, "--dry-run"))

    scout.main()

    assert "x: qwen3.8 → qwen3.8-max (a model of the same family)" in (
        tmp_path / "scout-pr.md").read_text()


def test_run_scout_hands_the_generation_check_its_page_reader():
    llm = StubLLM({"MODEL-GENERATIONS":
                   "```yaml\nsupersede:\n  - family: old\n    superseded_by: newer\n```"})
    result = run_scout(llm, [make(models=[{"family": "old"}])], [], lambda urls: {}, TODAY,
                       named=lambda e, f: False)
    assert result["supersede"] == []
    assert result["supersede_filtered"] == ["x: old → newer (not named where the row's probe reads)"]


def test_the_pr_body_says_how_many_hits_each_search_kept(tmp_path, monkeypatch):
    save_registry(tmp_path / "registry.yaml", [make()])
    monkeypatch.setattr(scout, "gather_evidence", lambda *a, **k: Evidence(
        hits=[Hit("https://n.dev", "N", "", "hn")], providers=["hn", "github"]))
    monkeypatch.setattr(scout, "run_scout", lambda *a, **k: {**EMPTY_RUN, "providers": ["hn", "github"]})
    monkeypatch.setattr(sys, "argv", _scout_argv(tmp_path, "--dry-run"))

    scout.main()

    assert "Discovery sources used: hn (1 hit kept), github (0 hits kept)" in (
        tmp_path / "scout-pr.md").read_text()


def test_answered_domains_are_the_current_watchlist_and_the_whole_blocklist():
    """What leaves the models.dev digest: verdicts the curated files still
    stand behind. An expired watchlist line has stopped answering for its
    service — the same rule format_watchlist applies — so its domain goes back
    into the digest and the question comes round again."""
    today = date(2026, 9, 5)
    watchlist = [
        Watched(domains=["current.ai", "api.current.ai"], name="Current", checked_on=today,
                reason="nothing free", reopen_if="a free lane"),
        Watched(domains=["expired.ai"], name="Expired",
                checked_on=today - timedelta(days=WATCH_RECHECK_DAYS + 1),
                reason="nothing free", reopen_if="a free lane"),
    ]
    blocklist = {"relay.example": "pooled access"}
    assert scout.answered_domains(watchlist, blocklist, today) == {
        "current.ai", "api.current.ai", "relay.example"}


def test_a_proposal_brings_no_tier_of_its_own():
    """A tier is read from Artificial Analysis by freetier-tiers, never taken
    from a model's say-so: a new family arrives without one, and a family the
    registry has already measured arrives with the registry's marks, so the
    pull request never contradicts one tier per family."""
    measured = make(id="known", models=[{"family": "glm-5.3", "tier": "frontier", "aa_model": "glm-5-3"}])
    entries = [measured]
    added, rejected = apply_new(entries, [{**proposal(), "models": [
        {"family": "glm-5.3", "tier": "strong"},
        {"family": "n-flash-1", "tier": "frontier", "aa_model": "made-up"}]}], TODAY)
    assert added == ["new1"] and rejected == []
    new = next(e for e in entries if e.id == "new1")
    assert [(m.family, m.tier, m.aa_model) for m in new.models] == [
        ("glm-5.3", "frontier", "glm-5-3"), ("n-flash-1", None, None)]


def test_an_update_keeps_the_marks_the_registry_measured():
    e = make(models=[{"family": "x-mini-2", "tier": "strong", "aa_model": "x-mini-2"}])
    entries = [e]
    applied, rejected = apply_updates(entries, [{"id": "x", "models": [
        {"family": "x-mini-2"}, {"family": "x-mini-3", "tier": "frontier"}]}])
    assert applied == ["x"] and rejected == []
    assert [(m.family, m.tier, m.aa_model) for m in entries[0].models] == [
        ("x-mini-2", "strong", "x-mini-2"), ("x-mini-3", None, None)]
