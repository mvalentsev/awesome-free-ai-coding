"""Codex CLI on the free lanes.

Codex speaks only the OpenAI Responses API, which few lanes serve, so it reaches
the list through LiteLLM, whose /v1/responses builds each call from a lane's chat
completions when the deployment sets `use_chat_completions_api`. A lane that takes
Codex's request itself gets a profile of its own, and every run sends it that
request again.
"""
import re
import tomllib
from pathlib import Path

from freetier_radar import render
from freetier_radar.models import save_registry
from test_render import TODAY, make


def _strong_and_keyless():
    return [
        make(id="glm", name="GLM", rank=1,
             models=[{"family": "glm-5.3", "tier": "strong", "aa_model": "glm-5-3"}],
             api={"base_url": "https://glm.example/v1", "auth": "api-key",
                  "model_ids": ["zai/glm-5.3"]}),
        make(id="open", name="Open", rank=2, models=[{"family": "gpt-oss"}],
             api={"base_url": "https://open.example/v1", "auth": "none",
                  "model_ids": ["gpt-oss-20b"]}),
    ]


def _rendered(tmp_path: Path, entries) -> Path:
    reg = tmp_path / "registry.yaml"
    save_registry(reg, entries)
    render.render_artifacts(reg, tmp_path, today=TODAY)
    return tmp_path


def _profile(root: Path) -> tuple[str, dict]:
    path = root / render.CODEX_DIR / f"{render.CODEX_LITELLM_PROFILE}.config.toml"
    text = path.read_text(encoding="utf-8")
    return text, tomllib.loads(text)


def test_every_litellm_deployment_answers_codex_through_the_lanes_chat_completions():
    """Every deployment, grouped or named, sets `use_chat_completions_api`: without
    it LiteLLM passes Codex's call on to the lane's own /responses, which most
    lanes do not serve."""
    cfg = render.build_litellm_config(_strong_and_keyless(), TODAY)
    assert {d["model_name"] for d in cfg["model_list"]} >= {"free/strong", "free/nokey"}
    assert all(d["litellm_params"]["use_chat_completions_api"] is True
               for d in cfg["model_list"])


def test_the_litellm_header_names_the_version_that_keeps_the_flag_to_the_proxy(tmp_path):
    """The header names the first LiteLLM that keeps the flag to itself: older ones
    forward `use_chat_completions_api` to the vendor, and a strict vendor refuses
    every chat call that carries it, not only Codex's."""
    header = (_rendered(tmp_path, _strong_and_keyless()) / "configs" / "litellm.yaml"
              ).read_text(encoding="utf-8")
    assert f"LiteLLM {render.LITELLM_BRIDGE_SINCE} or later" in header
    assert "use_chat_completions_api" in header
    assert "Codex" in header


def test_the_codex_profile_points_codex_at_the_proxy_with_the_settings_the_lanes_take(
        tmp_path):
    """The LiteLLM profile points Codex at the proxy's local address with no key,
    since the proxy runs without a master key, and carries only the three settings
    that keep lanes from refusing the call (see render._codex_settings)."""
    text, profile = _profile(_rendered(tmp_path, _strong_and_keyless()))
    assert profile["model"] == render.litellm_groups(_strong_and_keyless(), TODAY)[0]
    provider = profile["model_providers"][profile["model_provider"]]
    assert set(provider) == {"name", "base_url", "wire_api"}
    assert provider["wire_api"] == "responses"
    assert profile["model_reasoning_summary"] == "none"
    assert profile["web_search"] == "disabled"
    assert profile["features"] == {"multi_agent": False}
    assert set(profile) == {"model", "model_provider", "model_reasoning_summary", "web_search",
                            "features", "model_providers"}
    # The address is where the command the file prints puts the proxy: LiteLLM
    # listens on 4000 unless told a --port.
    command = re.search(r"litellm --config \S+[^\n]*", text).group(0)
    port = re.search(r"--port (\d+)", command)
    assert provider["base_url"] == f"http://127.0.0.1:{port.group(1) if port else 4000}/v1"
    assert f"codex -p {render.CODEX_LITELLM_PROFILE}" in text
    assert f"Codex CLI {render.CODEX_SINCE}" in text
    assert f"LiteLLM {render.LITELLM_BRIDGE_SINCE}" in text


def test_without_a_group_the_codex_profile_names_the_first_model_the_proxy_serves(tmp_path):
    keyed = make(id="glm", name="GLM", models=[{"family": "glm-5.3"}],
                 api={"base_url": "https://glm.example/v1", "auth": "api-key",
                      "model_ids": ["zai/glm-5.3"]})
    _, profile = _profile(_rendered(tmp_path, [keyed]))
    assert profile["model"] == "glm/zai/glm-5.3"


def test_a_codex_profile_with_no_lane_behind_it_names_no_model(tmp_path):
    text, profile = _profile(_rendered(tmp_path, [make(id="plain")]))
    assert "model" not in profile
    assert profile["model_provider"] in profile["model_providers"]


def test_no_page_tells_a_reader_to_paste_a_chat_base_url_into_codex(tmp_path):
    """Codex takes no chat base URL since it dropped the chat format, so every page
    that lists the configs names the LiteLLM profile instead."""
    reg = tmp_path / "registry.yaml"
    save_registry(reg, _strong_and_keyless())
    render.render_all(reg, Path("templates"), tmp_path, today=TODAY)
    for rel in ("configs/README.md", "index.html", "README.md", "llms.txt"):
        text = (tmp_path / rel).read_text(encoding="utf-8")
        assert not re.search(r"base\s+URL\s+into[^.]*Codex", text), rel
        assert "codex/litellm.config.toml" in text, rel


# ---- lanes that take the request Codex sends, called directly

import json

import httpx
import pytest
import respx
from pydantic import ValidationError

from freetier_radar.models import ApiInfo, Entry, load_registry
from freetier_radar.prober import ProbeStatus, probe_entry
from test_prober import BASE, KEYLESS_CATALOG, completion


def _sse(*events: dict) -> httpx.Response:
    """A Responses stream as Kilo's gateway sends it: data lines only, no
    `event:` lines."""
    body = "".join(f"data: {json.dumps(e)}\n\n" for e in events)
    return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})


COMPLETED = _sse({"type": "response.created", "response": {"id": "resp_1"}},
                 {"type": "response.output_text.delta", "delta": "pong"},
                 {"type": "response.completed", "response": {"id": "resp_1", "status": "completed"}})


def codex_keyless(**api) -> Entry:
    return Entry.model_validate({
        **BASE, "id": "open", "name": "Open",
        "models": [{"family": "gpt-oss", "tier": "strong"}],
        "api": {"base_url": "https://open.x.ai/v1", "auth": "none",
                "model_ids": ["gpt-oss-120b", "qwen3-coder-30b"], **api},
        "probe": {"type": "api-models", "endpoint": "https://open.x.ai/v1/models"},
    })


def codex_keyed(**api) -> Entry:
    return Entry.model_validate({
        **BASE, "id": "gate", "name": "Gate",
        "api": {"base_url": "https://gate.x.ai/v1", "model_ids": ["glm-5.3"], **api},
        "probe": {"type": "page-keywords", "endpoint": "https://gate.x.ai/pricing",
                  "keywords": ["qwen3-coder"]},
    })


def _keyless_lane_answers():
    respx.get("https://open.x.ai/v1/models").mock(
        return_value=httpx.Response(200, json=KEYLESS_CATALOG))
    respx.post("https://open.x.ai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=completion("gpt-oss-120b")))


def test_responses_api_is_said_only_of_an_openai_shaped_lane_codex_can_call():
    """The Responses API is OpenAI's; the profile names the row's first id; and
    Codex sends no header of a vendor's naming, so a lane that wants an id per
    conversation in one cannot take a profile."""
    with pytest.raises(ValidationError, match="responses_api"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], openai_compatible=False,
                responses_api=True)
    with pytest.raises(ValidationError, match="responses_api"):
        ApiInfo(base_url="https://x/v1", responses_api=True)
    with pytest.raises(ValidationError, match="responses_api"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], auth="none",
                session_header="x-session", responses_api=True)
    assert "responses_api" not in ApiInfo(base_url="https://x/v1").model_dump()
    assert ApiInfo(base_url="https://x/v1", model_ids=["m"],
                   responses_api=True).model_dump()["responses_api"] is True


def test_no_row_that_takes_codexs_request_is_named_like_the_litellm_profile():
    """Its profile would be written over the one for LiteLLM."""
    with pytest.raises(ValidationError, match=render.CODEX_LITELLM_PROFILE):
        Entry.model_validate({**codex_keyless(responses_api=True).model_dump(),
                              "id": render.CODEX_LITELLM_PROFILE})


@respx.mock
async def test_a_keyless_lane_that_takes_codexs_request_is_a_note_to_say_so():
    """A keyless lane that takes Codex's request without api.responses_api set is a
    note to set it: the run asks every lane without an account that has just
    answered a chat call, as it asks about a bearer token."""
    _keyless_lane_answers()
    respx.post("https://open.x.ai/v1/responses").mock(return_value=COMPLETED)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyless(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "set api.responses_api: true" in result.detail


@respx.mock
async def test_the_call_is_the_request_codex_sends_under_this_lists_profiles():
    """The probe sends every field Codex sends, as a stream, with the profiles'
    settings: a lane can refuse any one of them (OVHcloud refused `include`)."""
    _keyless_lane_answers()
    route = respx.post("https://open.x.ai/v1/responses").mock(return_value=COMPLETED)
    async with httpx.AsyncClient() as client:
        await probe_entry(client, codex_keyless(responses_api=True), backoff=0)
    sent = route.calls.last.request
    body = json.loads(sent.content)
    assert body["model"] == "gpt-oss-120b"
    assert body["stream"] is True and body["store"] is False
    assert body["include"] == ["reasoning.encrypted_content"]
    assert body["reasoning"] == {}
    assert body["tool_choice"] == "auto" and body["parallel_tool_calls"] is True
    assert [t["type"] for t in body["tools"]] == ["function"]
    assert body["input"][0]["content"][0]["type"] == "input_text"
    assert body["prompt_cache_key"] and body["client_metadata"]["session_id"]
    assert sent.headers["accept"] == "text/event-stream"
    assert "authorization" not in sent.headers


@respx.mock
async def test_a_lane_that_still_takes_codexs_request_is_a_pass():
    _keyless_lane_answers()
    route = respx.post("https://open.x.ai/v1/responses").mock(return_value=COMPLETED)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyless(responses_api=True), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert route.called


@pytest.mark.parametrize("answer", [
    httpx.Response(422, text="include[0]: unknown variant `reasoning.encrypted_content`"),
    _sse({"type": "response.created", "response": {"id": "r"}},
         {"type": "response.failed", "response": {"id": "r", "status": "failed"}}),
    httpx.Response(200, json={"object": "response", "status": "completed"}),
])
@respx.mock
async def test_a_lane_that_stops_taking_codexs_request_is_a_note(answer):
    """A refusal, a stream that fails, and a whole JSON answer to a request for
    a stream all end Codex's turn the same way. The row stays verified by its
    page; what broke is a connection detail the list publishes."""
    _keyless_lane_answers()
    respx.post("https://open.x.ai/v1/responses").mock(return_value=answer)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyless(responses_api=True), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "no longer takes the request Codex CLI sends" in result.detail


@respx.mock
async def test_a_keyless_lane_without_the_route_says_nothing():
    """A 404 is the ordinary answer of a lane nothing says serves Codex."""
    _keyless_lane_answers()
    route = respx.post("https://open.x.ai/v1/responses").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyless(), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert route.called


@respx.mock
async def test_a_keyed_route_answering_anything_but_gone_is_a_pass():
    """A keyless call cannot complete a keyed lane's turn and does not try to:
    a 401 is the route saying it exists, the Anthropic check's reading."""
    respx.get("https://gate.x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    route = respx.post("https://gate.x.ai/v1/responses").mock(return_value=httpx.Response(401))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyed(responses_api=True), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert json.loads(route.calls.last.request.content)["model"] == "glm-5.3"


@respx.mock
async def test_a_keyed_route_that_is_gone_is_a_note_not_a_failure():
    respx.get("https://gate.x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://gate.x.ai/v1/responses").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyed(responses_api=True), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "codex route gone" in result.detail and "HTTP 404" in result.detail


@respx.mock
async def test_a_keyed_route_that_cannot_be_checked_is_said_so():
    respx.get("https://gate.x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://gate.x.ai/v1/responses").mock(side_effect=httpx.ConnectError("boom"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyed(responses_api=True), backoff=0, attempts=2)
    assert result.status is ProbeStatus.STALE_IDS
    assert "could not be checked" in result.detail


def _direct(**over):
    return make(id=over.pop("id", "kilo"), name=over.pop("name", "Kilo"), rank=over.pop("rank", 1),
                models=[{"family": "gpt-oss"}],
                api={"base_url": "https://kilo.example/api/gateway", "auth": "none",
                     "model_ids": ["kilo-auto/free", "gpt-oss-20b"], "responses_api": True,
                     **over.pop("api", {})}, **over)


def test_a_row_that_takes_codexs_request_gets_a_profile_of_its_own(tmp_path):
    """The same three settings as the LiteLLM profile, so the request Codex
    sends through either is the one the run sends; the key, where the lane
    takes one, from the variable free-llm.env.example exports."""
    keyed = _direct(id="gate", name="Gate", rank=2,
                    api={"auth": "api-key", "base_url": "https://gate.example/v1"})
    root = _rendered(tmp_path, [_direct(), keyed])
    _, over_litellm = _profile(root)
    for e, env in (("kilo", None), ("gate", "GATE_API_KEY")):
        profile = tomllib.loads((root / render.CODEX_DIR / f"{e}.config.toml").read_text(
            encoding="utf-8"))
        assert profile["model_provider"] == e
        provider = profile["model_providers"][e]
        assert provider["wire_api"] == "responses"
        assert provider.get("env_key") == env
        for key in ("model_reasoning_summary", "web_search", "features"):
            assert profile[key] == over_litellm[key]
    kilo = tomllib.loads((root / render.CODEX_DIR / "kilo.config.toml").read_text(encoding="utf-8"))
    assert kilo["model"] == "kilo-auto/free"
    assert kilo["model_providers"]["kilo"]["base_url"] == "https://kilo.example/api/gateway"


def test_a_profile_is_taken_away_with_the_field_and_its_absence_is_checked(tmp_path):
    root = _rendered(tmp_path, [_direct()])
    stray = root / render.CODEX_DIR / "gone.config.toml"
    stray.write_text("model = \"x\"\n", encoding="utf-8")
    render.render_artifacts(root / "registry.yaml", root, today=TODAY)
    assert not stray.exists()
    stray.write_text("model = \"x\"\n", encoding="utf-8")
    stale = render.check_rendered(root / "registry.yaml", Path("templates"), root, today=TODAY)
    assert f"{render.CODEX_DIR}/gone.config.toml" in stale


def test_the_pages_that_say_how_to_connect_name_the_rows_codex_profile(tmp_path):
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [_direct(), make(id="other", name="Other", rank=2,
                                        models=[{"family": "gpt-oss"}],
                                        api={"base_url": "https://o.example/v1",
                                             "model_ids": ["gpt-oss-20b"]})])
    render.render_all(reg, Path("templates"), tmp_path, today=TODAY)
    command = "codex -p kilo"
    profile = f"{render.CODEX_DIR}/kilo.config.toml"
    page = (tmp_path / "providers" / "kilo.md").read_text(encoding="utf-8")
    assert command in page and profile in page
    assert "codex -p" not in (tmp_path / "providers" / "other.md").read_text(encoding="utf-8")
    for rel in ("configs/README.md", "index.html", "README.md"):
        text = (tmp_path / rel).read_text(encoding="utf-8")
        assert command in text, rel
    assert profile in (tmp_path / "llms.txt").read_text(encoding="utf-8")
    index = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    kilo = next(e for e in index["entries"] if e["id"] == "kilo")
    assert kilo["api"]["responses_api"] is True


def test_the_codex_pick_names_the_rows_that_take_its_request_in_rank_order():
    rows = [_direct(id="b", name="B", rank=2), _direct(id="a", name="A", rank=1),
            _direct(id="c", name="C", rank=3, card_required=True)]
    picks = render.picks(rows, TODAY)
    assert [p["name"] for p in picks["codex"]] == ["A", "B"]
