"""How a lane lets a client in, decided once and said everywhere.

The key a lane takes and what every request must carry besides it are said by
the README's connection table, the site's, the provider and model pages,
llms.txt, the env example and the quickstart, and acted on by three configs
and the probe. Each used to decide for itself — eight copies of "is there a
session header" — so a vendor's next requirement would have reached some of
them and not others. `ApiInfo.key_kind` and `ApiInfo.asks` decide; every place
that words an ask keeps its words in a table keyed by `models.ASKS`, and these
tests refuse a table that is missing one.
"""
from freetier_radar import render
from freetier_radar.models import ASKS, KEY_KINDS, ApiInfo
from test_render import TODAY, make


def test_every_place_that_words_an_ask_words_every_ask():
    tables = {name: getattr(render, name) for name in dir(render)
              if name.startswith("_ASK_") or name == "ASK_CONFIG"}
    assert len(tables) == 7, sorted(tables)
    for name, table in tables.items():
        assert tuple(table) == ASKS, name
    everything = ApiInfo(base_url="https://x.example/v1", client_user_agent=True,
                         session_header="x-session")
    assert tuple(name for name, _ in everything.asks()) == ASKS


def test_the_key_kind_is_decided_in_one_place():
    assert ApiInfo(base_url="https://x/v1", auth="none").key_kind == "none"
    assert ApiInfo(base_url="https://x/v1", key_url="https://x/k", public_key="sk-1",
                   model_ids=["m"]).key_kind == "public"
    assert ApiInfo(base_url="https://x/v1").key_kind == "own"
    assert KEY_KINDS == ("none", "public", "own")


def _lane(entry_id: str, **api):
    return make(id=entry_id, name=entry_id.upper(), models=[{"family": "glm-5"}],
                api={"base_url": f"https://{entry_id}.example/v1", "model_ids": ["glm-5"],
                     "anthropic_base_url": f"https://{entry_id}.example/anthropic", **api})


def test_a_config_written_once_leaves_out_a_lane_it_cannot_call():
    """A stable id per conversation is the calling client's to make up, and a
    keyless lane that refuses a bearer refuses Claude Code's token of "none":
    litellm.yaml, opencode.json and claude-code.sh all leave such a lane out,
    and the connection table and the row's page still say how to reach it."""
    rows = [_lane("plain", auth="none"),
            _lane("session", auth="none", session_header="x-session"),
            _lane("nobearer", auth="none", refuses_bearer=True)]
    shell = render.build_claude_code_sh(rows, TODAY)
    assert "claude-plain()" in shell
    assert "claude-session()" not in shell and "claude-nobearer()" not in shell
    assert set(render.build_opencode_config(rows, TODAY)["provider"]) == {"plain", "nobearer"}
    litellm = {m["litellm_params"]["api_base"] for m in
               render.build_litellm_config(rows, TODAY)["model_list"]}
    assert litellm == {"https://plain.example/v1"}
    page = render.build_provider_page(rows[1], [], TODAY)
    assert "- Session header: `x-session` — a stable id per conversation" in page


def test_the_quickstart_sends_every_ask_its_lane_makes():
    row = make(id="open", name="Open", models=[{"family": "glm-5"}],
               api={"base_url": "https://open.example/v1", "auth": "none",
                    "model_ids": ["glm-5"], "client_user_agent": True,
                    "session_header": "x-session"})
    curl = render.build_context([row], TODAY)["quickstart"]["curl"]
    assert f"  -H 'User-Agent: {render.QUICKSTART_USER_AGENT}' \\\n" in curl
    assert '  -H "x-session: quickstart-$RANDOM$RANDOM" \\\n' in curl
    assert curl.index("User-Agent") < curl.index("x-session")
