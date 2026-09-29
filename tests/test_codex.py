"""Codex CLI on the free lanes.

Codex speaks only the OpenAI Responses API, so it reaches the list through
LiteLLM, whose /v1/responses builds each call from a lane's chat
completions when the deployment sets `use_chat_completions_api`. A lane Codex
calls directly gets a profile of its own (`api.codex`): one without an account
took the request Codex sends, and every run sends it again; a keyed one rests on
the vendor's own page setting Codex up, which every run reads back.
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
    it LiteLLM passes Codex's call on to the lane's own /responses, which the run
    does not verify."""
    cfg = render.build_litellm_config(_strong_and_keyless(), TODAY)
    assert {d["model_name"] for d in cfg["model_list"]} >= {"free/strong", "free/nokey"}
    assert all(d["litellm_params"]["use_chat_completions_api"] is True
               for d in cfg["model_list"])


def test_the_litellm_header_names_the_version_that_keeps_the_flag_to_the_proxy(tmp_path):
    """The header names the LiteLLM the config needs: 1.88.3 and earlier forward
    `use_chat_completions_api` to the vendor, where a strict one refuses every
    chat call that carries it, not only Codex's, and the groups' own
    allowed_fails_policy is read from 1.98.0 on."""
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


KEYLESS_CODEX = {"base_url": "https://open.x.ai/v1"}
KEYED_CODEX = {"base_url": "https://gate.x.ai/v1", "source": "https://gate.x.ai/docs/codex",
               "quote": "Use Codex CLI with Gate"}


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


def test_api_codex_is_said_only_of_an_openai_shaped_lane_codex_can_call():
    """The Responses API is OpenAI's; the profile names the row's first id; and
    a Codex profile's headers are fixed values, so a lane that wants a new id per
    conversation in one cannot take a profile."""
    with pytest.raises(ValidationError, match="api.codex"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], openai_compatible=False,
                auth="none", codex=KEYLESS_CODEX)
    with pytest.raises(ValidationError, match="api.codex"):
        ApiInfo(base_url="https://x/v1", auth="none", codex=KEYLESS_CODEX)
    with pytest.raises(ValidationError, match="api.codex"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], auth="none",
                session_header="x-session", codex=KEYLESS_CODEX)
    assert "codex" not in ApiInfo(base_url="https://x/v1").model_dump(exclude_none=True)
    dumped = ApiInfo(base_url="https://x/v1", model_ids=["m"], auth="none",
                     codex=KEYLESS_CODEX).model_dump(exclude_none=True)
    assert dumped["codex"] == {"base_url": "https://open.x.ai/v1"}


def test_a_keyed_lane_rests_on_the_vendors_page_naming_codex():
    """A call without a key reaches only a keyed lane's route, so its block
    carries the vendor's page and words from it that name Codex — words the
    quote pass reads back, which die with the page."""
    with pytest.raises(ValidationError, match="source and quote"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], codex={"base_url": "https://x/v1"})
    with pytest.raises(ValidationError, match="go together"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"],
                codex={"base_url": "https://x/v1", "source": "https://x/docs/codex"})
    with pytest.raises(ValidationError, match="does not name Codex"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"],
                codex={**KEYED_CODEX, "quote": "one key for every model"})
    with pytest.raises(ValidationError, match="quotation marks"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"],
                codex={**KEYED_CODEX, "quote": 'set wire_api = "responses" for Codex'})
    with pytest.raises(ValidationError, match="https"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"],
                codex={**KEYED_CODEX, "source": "http://gate.x.ai/docs/codex"})
    # A key the vendor prints for anyone is asked the whole request, like a lane
    # without one: the run is its evidence.
    ApiInfo(base_url="https://x/v1", model_ids=["m"], public_key="k", key_url="https://x/k",
            codex={"base_url": "https://x/v1"})


def test_the_codex_base_is_what_codex_appends_responses_to():
    with pytest.raises(ValidationError, match="appends /responses"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], auth="none",
                codex={"base_url": "https://x/v1/responses"})
    with pytest.raises(ValidationError, match="https"):
        ApiInfo(base_url="https://x/v1", model_ids=["m"], auth="none",
                codex={"base_url": "http://x/v1"})
    assert ApiInfo(base_url="https://x/v1", model_ids=["m"], auth="none",
                   codex={"base_url": "https://x/codex/v1/"}).codex.base_url == "https://x/codex/v1"


def test_no_row_that_takes_codexs_request_is_named_like_the_litellm_profile():
    """Its profile would be written over the one for LiteLLM."""
    with pytest.raises(ValidationError, match=render.CODEX_LITELLM_PROFILE):
        Entry.model_validate({**codex_keyless(codex=KEYLESS_CODEX).model_dump(),
                              "id": render.CODEX_LITELLM_PROFILE})


@respx.mock
async def test_a_keyless_lane_that_takes_codexs_request_is_a_note_to_say_so():
    """A keyless lane that takes Codex's request without api.codex set is a
    note to set it: the run asks every lane without an account that has just
    answered a chat call, as it asks about a bearer token."""
    _keyless_lane_answers()
    respx.post("https://open.x.ai/v1/responses").mock(return_value=COMPLETED)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyless(), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "set api.codex.base_url to https://open.x.ai/v1" in result.detail


@respx.mock
async def test_the_call_is_the_request_codex_sends_under_this_lists_profiles():
    """The probe sends every field Codex sends, as a stream, with the profiles'
    settings: a lane can refuse any one of them (OVHcloud refused `include`)."""
    _keyless_lane_answers()
    route = respx.post("https://open.x.ai/v1/responses").mock(return_value=COMPLETED)
    async with httpx.AsyncClient() as client:
        await probe_entry(client, codex_keyless(codex=KEYLESS_CODEX), backoff=0)
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
        result = await probe_entry(client, codex_keyless(codex=KEYLESS_CODEX), backoff=0)
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
        result = await probe_entry(client, codex_keyless(codex=KEYLESS_CODEX), backoff=0)
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
        result = await probe_entry(client, codex_keyed(codex=KEYED_CODEX), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert json.loads(route.calls.last.request.content)["model"] == "glm-5.3"


@respx.mock
async def test_a_keyed_route_that_is_gone_is_a_note_not_a_failure():
    respx.get("https://gate.x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://gate.x.ai/v1/responses").mock(return_value=httpx.Response(404))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyed(codex=KEYED_CODEX), backoff=0)
    assert result.status is ProbeStatus.STALE_IDS
    assert "codex route gone" in result.detail and "HTTP 404" in result.detail


@respx.mock
async def test_a_keyed_route_that_cannot_be_checked_is_said_so():
    respx.get("https://gate.x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    respx.post("https://gate.x.ai/v1/responses").mock(side_effect=httpx.ConnectError("boom"))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, codex_keyed(codex=KEYED_CODEX), backoff=0, attempts=2)
    assert result.status is ProbeStatus.STALE_IDS
    assert "could not be checked" in result.detail


def _direct(**over):
    return make(id=over.pop("id", "kilo"), name=over.pop("name", "Kilo"), rank=over.pop("rank", 1),
                models=[{"family": "gpt-oss"}],
                api={"base_url": "https://kilo.example/api/gateway", "auth": "none",
                     "model_ids": ["kilo-auto/free", "gpt-oss-20b"],
                     "codex": {"base_url": "https://kilo.example/api/gateway"},
                     **over.pop("api", {})}, **over)


def test_a_row_that_takes_codexs_request_gets_a_profile_of_its_own(tmp_path):
    """The same three settings as the LiteLLM profile, so the request Codex
    sends through either is the one the run sends; the key, where the lane
    takes one, from the variable free-llm.env.example exports."""
    keyed = _direct(id="gate", name="Gate", rank=2,
                    api={"auth": "api-key", "base_url": "https://gate.example/v1",
                         "codex": {"base_url": "https://gate.example/codex/v1",
                                   "source": "https://gate.example/docs/codex",
                                   "quote": "Use Codex CLI with Gate"}})
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
    gate = tomllib.loads((root / render.CODEX_DIR / "gate.config.toml").read_text(encoding="utf-8"))
    assert gate["model_providers"]["gate"]["base_url"] == "https://gate.example/codex/v1"


def test_a_profile_says_what_it_rests_on(tmp_path):
    """A lane without an account took the request, and every run sends it again;
    a keyed lane rests on its vendor's page, which the run reads back, and says
    what Codex does while the key is missing — a sentence the conformance run
    holds to Codex itself."""
    from freetier_radar.conformance import comment_text
    keyed = _direct(id="gate", name="Gate", rank=2,
                    api={"auth": "api-key", "base_url": "https://gate.example/v1",
                         "key_url": "https://gate.example/keys",
                         "codex": {"base_url": "https://gate.example/v1",
                                   "source": "https://gate.example/docs/codex",
                                   "quote": "Use Codex CLI with Gate"}})
    root = _rendered(tmp_path, [_direct(), keyed])
    kilo = comment_text((root / render.CODEX_DIR / "kilo.config.toml").read_text(encoding="utf-8"))
    gate = comment_text((root / render.CODEX_DIR / "gate.config.toml").read_text(encoding="utf-8"))
    assert "The lane takes the request Codex sends, and every run of the list sends it again." in kilo
    assert "No key: the lane is anonymous." in kilo
    assert "https://gate.example/docs/codex" in gate and "only a key can run a turn" in gate
    assert "The key comes from $GATE_API_KEY, the variable free-llm.env.example exports" in gate
    assert render.codex_unset_words("GATE_API_KEY") in gate
    assert "takes the request Codex sends" not in gate


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
    assert kilo["api"]["codex"] == {"base_url": "https://kilo.example/api/gateway"}


def test_a_keyed_rows_page_names_the_vendors_codex_page_and_a_base_of_its_own(tmp_path):
    reg = tmp_path / "registry.yaml"
    save_registry(reg, [_direct(id="gate", name="Gate",
                                api={"auth": "api-key", "base_url": "https://gate.example/v1",
                                     "codex": {"base_url": "https://gate.example/codex/v1",
                                               "source": "https://gate.example/docs/codex",
                                               "quote": "Use Codex CLI with Gate"}})])
    render.render_all(reg, Path("templates"), tmp_path, today=TODAY)
    page = (tmp_path / "providers" / "gate.md").read_text(encoding="utf-8")
    line = next(x for x in page.splitlines() if x.startswith("- Codex CLI:"))
    assert "`https://gate.example/codex/v1`" in line
    assert "<https://gate.example/docs/codex>" in line and '"Use Codex CLI with Gate"' in line


def test_the_codex_pick_names_the_rows_codex_calls_directly_in_rank_order():
    rows = [_direct(id="b", name="B", rank=2), _direct(id="a", name="A", rank=1),
            _direct(id="c", name="C", rank=3, card_required=True)]
    picks = render.picks(rows, TODAY)
    assert [p["name"] for p in picks["codex"]] == ["A", "B"]


@respx.mock
async def test_a_keyed_route_is_asked_at_the_codex_base_the_vendor_names():
    """Vercel serves Codex at /codex/v1: the route asked is the one the profile
    points Codex at, not the lane's chat base."""
    respx.get("https://gate.x.ai/pricing").mock(return_value=httpx.Response(200, text="qwen3-coder"))
    apart = respx.post("https://gate.x.ai/codex/v1/responses").mock(
        return_value=httpx.Response(401))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(
            client, codex_keyed(codex={**KEYED_CODEX, "base_url": "https://gate.x.ai/codex/v1"}),
            backoff=0)
    assert result.status is ProbeStatus.PASS
    assert apart.called


@respx.mock
async def test_a_keyless_lane_is_asked_at_its_codex_base():
    _keyless_lane_answers()
    apart = respx.post("https://open.x.ai/codex/v1/responses").mock(return_value=COMPLETED)
    async with httpx.AsyncClient() as client:
        result = await probe_entry(
            client, codex_keyless(codex={"base_url": "https://open.x.ai/codex/v1"}), backoff=0)
    assert result.status is ProbeStatus.PASS
    assert apart.called


def _routeway_like(endpoints: dict[str, list[str] | None]) -> tuple[Entry, dict]:
    """A keyed api-models row whose catalog lists the paths it serves each
    model at, the way Routeway's does."""
    rows = [{"id": mid, "pricing": {"prompt": "0", "completion": "0"},
             **({"endpoints": paths} if paths is not None else {})}
            for mid, paths in endpoints.items()]
    entry = Entry.model_validate({
        **BASE, "id": "route", "name": "Route",
        "models": [{"family": "deepseek-v4-flash"}],
        "api": {"base_url": "https://route.x.ai/v1", "model_ids": list(endpoints),
                "codex": {"base_url": "https://route.x.ai/v1",
                          "source": "https://route.x.ai/docs/codex",
                          "quote": "Use Codex with Route"}},
        "probe": {"type": "api-models", "endpoint": "https://route.x.ai/v1/models",
                  "require_zero_price": True},
    })
    return entry, {"object": "list", "data": rows}


@pytest.mark.parametrize("endpoints, gap", [
    ({"deepseek-v4-flash:free": ["/v1/chat/completions", "/v1/responses"],
      "muse-glimmer-30b:free": ["/v1/chat/completions"]}, False),
    ({"muse-glimmer-30b:free": ["/v1/chat/completions"],
      "deepseek-v4-flash:free": ["/v1/chat/completions", "/v1/responses"]}, True),
    ({"deepseek-v4-flash:free": None}, False),
])
@respx.mock
async def test_the_profiles_id_is_held_to_the_paths_its_catalog_serves_it_at(endpoints, gap):
    """A vendor's Codex page speaks of its gateway, a catalog listing each
    model's paths of the model: the first id served at chat completions alone
    cannot take Codex's request, whatever the page says. A catalog that lists
    no paths says nothing either way."""
    entry, catalog = _routeway_like(endpoints)
    respx.get("https://route.x.ai/v1/models").mock(return_value=httpx.Response(200, json=catalog))
    respx.post("https://route.x.ai/v1/responses").mock(return_value=httpx.Response(401))
    async with httpx.AsyncClient() as client:
        result = await probe_entry(client, entry, backoff=0)
    if gap:
        assert result.status is ProbeStatus.STALE_IDS
        assert "codex profile names muse-glimmer-30b:free" in result.detail
        assert "/v1/chat/completions only" in result.detail
    else:
        assert result.status is ProbeStatus.PASS, result.detail


def test_the_quote_pass_reads_a_keyed_lanes_codex_page_back():
    from freetier_radar.quotes import row_quotes, row_urls
    entry = codex_keyed(codex=KEYED_CODEX)
    assert ("api.codex.quote", "Use Codex CLI with Gate") in row_quotes(entry)
    assert "https://gate.x.ai/docs/codex" in row_urls(entry)
