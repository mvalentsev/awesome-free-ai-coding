"""Codex CLI on the free lanes.

Codex speaks only the OpenAI Responses API: a provider it is given with
`wire_api = "chat"` has been a config error since its discussion #7782, and on
2026-09-27 seventeen of the list's 61 lanes answered POST /responses with 404
while OVHcloud's refused the request Codex sends. So Codex reaches the list
through LiteLLM, whose /v1/responses builds each call from a lane's chat
completions when the deployment says `use_chat_completions_api` — measured end
to end that day with Codex 0.157.1 and LiteLLM 1.102.1 on keyless lanes, a tool
call included.
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
    """LiteLLM answers /v1/responses for an `openai/` deployment by sending the
    call on to the lane's own /responses — 404 on LLM7, LLM Tech and VLM Run, a
    500 on Pollinations — unless the deployment carries the flag; grouped
    deployments are called by Codex as much as named ones."""
    cfg = render.build_litellm_config(_strong_and_keyless(), TODAY)
    assert {d["model_name"] for d in cfg["model_list"]} >= {"free/strong", "free/nokey"}
    assert all(d["litellm_params"]["use_chat_completions_api"] is True
               for d in cfg["model_list"])


def test_the_litellm_header_names_the_version_that_keeps_the_flag_to_the_proxy(tmp_path):
    """LiteLLM 1.88 and older send `use_chat_completions_api` on to the vendor
    in the request body, and a strict one refuses a field it does not know —
    every chat call through the file, not only Codex's, would fail there."""
    header = (_rendered(tmp_path, _strong_and_keyless()) / "configs" / "litellm.yaml"
              ).read_text(encoding="utf-8")
    assert f"LiteLLM {render.LITELLM_BRIDGE_SINCE} or later" in header
    assert "use_chat_completions_api" in header
    assert "Codex" in header


def test_the_codex_profile_points_codex_at_the_proxy_with_the_settings_the_lanes_take(
        tmp_path):
    """The three settings are the ones measured to break a lane otherwise:
    LiteLLM hands Codex's reasoning summary to the lane as a `reasoning_effort`
    object every lane tried refused, the sub-agent tools come as a `namespace`
    that LLM7 refused through LiteLLM and OVHcloud directly, and web search is
    OpenAI's hosted tool, which LiteLLM passes on as `web_search_options`.
    The proxy has no master key, so the provider names no key either."""
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
    """Until 2026-09-27 the connection tables said to paste their base URLs into
    "opencode, Codex CLI, aider, Cline or any OpenAI SDK" — Codex has taken
    none of them since it dropped the chat format. Every page that lists the
    configs names the profile instead."""
    reg = tmp_path / "registry.yaml"
    save_registry(reg, _strong_and_keyless())
    render.render_all(reg, Path("templates"), tmp_path, today=TODAY)
    for rel in ("configs/README.md", "index.html", "README.md", "llms.txt"):
        text = (tmp_path / rel).read_text(encoding="utf-8")
        assert not re.search(r"base\s+URL\s+into[^.]*Codex", text), rel
        assert "codex/litellm.config.toml" in text, rel
