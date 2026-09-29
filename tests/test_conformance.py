"""The parts of the conformance run that decide without running LiteLLM or
Codex: which sentences it proves, the commands it reads off the files, the
config it points at its own lanes, and how it tells two requests apart."""
import json
from pathlib import Path

import yaml

from freetier_radar.conformance import (ENV_EXAMPLE, Finding, _chat_answer, as_run, bare,
                                        comment_text, floors, keyed_profile, lanes, listening,
                                        missing_sentences, point_lanes, printed_profile,
                                        printed_run, shape_differences, summary)
from freetier_radar.prober import codex_probe_body
from freetier_radar.render import CODEX_SINCE, LITELLM_BRIDGE_SINCE

ROOT = Path(__file__).resolve().parent.parent


def test_every_sentence_a_check_proves_is_in_its_file():
    """A render that rewords one fails here, before the weekly run would find
    its check proving nothing."""
    assert missing_sentences(ROOT) == []


def test_a_sentence_wrapped_across_comment_lines_reads_as_one():
    text = "# The proxy listens on\n# 0.0.0.0 unless --host\n#   says otherwise.\nmodel_list:\n"
    assert "The proxy listens on 0.0.0.0 unless --host says otherwise." in comment_text(text)


def _copied(tmp_path: Path) -> Path:
    """The files the sentences are read from, as committed."""
    for rel in ("configs/litellm.yaml", ENV_EXAMPLE, "CONTRIBUTING.md",
                *(p.relative_to(ROOT).as_posix()
                  for p in (ROOT / "configs/codex").glob("*.config.toml"))):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def test_a_reworded_sentence_is_reported(tmp_path):
    root = _copied(tmp_path)
    profile = root / "configs/codex/litellm.config.toml"
    profile.write_text(profile.read_text().replace("since every Codex turn offers them",
                                                   "since Codex offers them"))
    assert missing_sentences(root) == ["tools"]


def _keyed(root: Path, name: str = "gate", var: str = "GATE_API_KEY", filled: str = "") -> Path:
    """A keyed lane's profile beside the committed ones, and its variable in the
    env example — empty for the reader's own key, filled for one the vendor
    prints for anyone."""
    path = root / "configs/codex" / f"{name}.config.toml"
    path.write_text(
        f"# Gate's own page sets Codex CLI up on this lane.\n"
        f"#   cp configs/codex/{name}.config.toml ~/.codex/\n#   codex -p {name}\n#\n"
        f"# The key comes from ${var}, the variable free-llm.env.example exports; get one at\n"
        f"# https://gate.example/keys. With ${var} unset or empty, Codex stops before it sends\n"
        f"# anything, so no other key of yours reaches the lane.\n"
        f'[model_providers.{name}]\nbase_url = "https://gate.example/v1"\n'
        f'wire_api = "responses"\nenv_key = "{var}"\n', encoding="utf-8")
    env = root / ENV_EXAMPLE
    env.write_text(env.read_text(encoding="utf-8") + f'export {var}="{filled}"\n',
                   encoding="utf-8")
    return path


def test_the_keyed_profile_is_one_whose_key_the_reader_brings(tmp_path):
    """A lane whose key the env example leaves empty is the reader's own; one
    it fills in is the vendor's key for anyone, and its profile says nothing
    about a missing key."""
    root = _copied(tmp_path)
    assert keyed_profile(root) is None or keyed_profile(root).startswith("configs/codex/")
    for p in (root / "configs/codex").glob("*.config.toml"):
        if p.name != "litellm.config.toml" and p.name != "kilo-code.config.toml":
            p.unlink()
    assert keyed_profile(root) is None
    _keyed(root, "public", "PUBLIC_API_KEY", filled="sk-for-anyone")
    assert keyed_profile(root) is None
    _keyed(root, "gate")
    assert keyed_profile(root) == "configs/codex/gate.config.toml"


def test_the_keyed_sentences_are_read_off_a_keyed_profile_only_where_one_exists(tmp_path):
    root = _copied(tmp_path)
    for p in (root / "configs/codex").glob("*.config.toml"):
        if p.name not in ("litellm.config.toml", "kilo-code.config.toml"):
            p.unlink()
    assert missing_sentences(root) == []
    path = _keyed(root)
    assert missing_sentences(root) == []
    path.write_text(path.read_text().replace("Codex stops before it sends", "Codex stops before"))
    assert missing_sentences(root) == ["key-unset"]


def test_the_oldest_releases_run_are_the_ones_the_files_ask_for():
    litellm, codex = floors()
    assert (litellm, codex) == (f"{LITELLM_BRIDGE_SINCE}.0", f"{CODEX_SINCE}.0")
    profile = (ROOT / "configs/codex/litellm.config.toml").read_text(encoding="utf-8")
    assert (f"Needs Codex CLI {CODEX_SINCE} or later and LiteLLM {LITELLM_BRIDGE_SINCE} or later"
            in comment_text(profile))


def test_the_commands_are_the_ones_the_files_print():
    run = printed_run((ROOT / "configs/litellm.yaml").read_text(encoding="utf-8"))
    assert run == ["env", "-u", "OPENAI_API_KEY", "litellm", "--config", "litellm.yaml",
                   "--host", "127.0.0.1"]
    proxy, cp, codex = printed_profile(
        (ROOT / "configs/codex/litellm.config.toml").read_text(encoding="utf-8"))
    assert proxy[:4] == ["env", "-u", "OPENAI_API_KEY", "litellm"] and "--host" in proxy
    assert cp == ["cp", "configs/codex/litellm.config.toml", "~/.codex/"]
    assert codex == ["codex", "-p", "litellm"]
    proxy, cp, codex = printed_profile(
        (ROOT / "configs/codex/kilo-code.config.toml").read_text(encoding="utf-8"))
    assert proxy == [] and codex == ["codex", "-p", "kilo-code"]


def test_a_printed_command_runs_here_as_printed_or_without_its_advice():
    printed = ["env", "-u", "OPENAI_API_KEY", "litellm", "--config", "litellm.yaml",
               "--host", "127.0.0.1"]
    here = as_run(printed, "/v/bin/litellm", "/w/litellm.yaml")
    assert here == ["env", "-u", "OPENAI_API_KEY", "/v/bin/litellm", "--config",
                    "/w/litellm.yaml", "--host", "127.0.0.1"]
    assert bare(here) == ["/v/bin/litellm", "--config", "/w/litellm.yaml"]


CONFIG = {
    "model_list": [
        {"model_name": "a/one", "litellm_params": {
            "model": "openai/one", "api_base": "https://a.example/v1",
            "api_key": "os.environ/A_API_KEY", "use_chat_completions_api": True}},
        {"model_name": "free/strong", "litellm_params": {
            "model": "openai/two", "api_base": "https://b.example/v1", "api_key": "none",
            "use_chat_completions_api": True},
         "model_info": {"allowed_fails_policy": {"InternalServerErrorAllowedFails": 0}}},
    ],
    "router_settings": {"num_retries": 3},
}


def test_every_entry_goes_to_a_lane_of_its_own_and_nothing_else_changes():
    pointed = point_lanes(CONFIG, "http://127.0.0.1:9")
    assert [e["litellm_params"]["api_base"] for e in pointed["model_list"]] == [
        "http://127.0.0.1:9/lane/0/v1", "http://127.0.0.1:9/lane/1/v1"]
    for before, after in zip(CONFIG["model_list"], pointed["model_list"]):
        assert {k: v for k, v in after["litellm_params"].items() if k != "api_base"} == {
            k: v for k, v in before["litellm_params"].items() if k != "api_base"}
        assert after.get("model_info") == before.get("model_info")
    assert pointed["router_settings"] == CONFIG["router_settings"]
    assert CONFIG["model_list"][0]["litellm_params"]["api_base"] == "https://a.example/v1"


def test_an_entry_names_the_variable_its_key_is_read_from():
    got = lanes(CONFIG)
    assert [(lane.index, lane.name, lane.key) for lane in got] == [
        (0, "a/one", "A_API_KEY"), (1, "free/strong", None)]


def test_the_committed_config_has_the_groups_the_checks_use():
    got = lanes(yaml.safe_load((ROOT / "configs/litellm.yaml").read_text(encoding="utf-8")))
    strong = [lane for lane in got if lane.name == "free/strong"]
    nokey = [lane for lane in got if lane.name == "free/nokey"]
    assert len(strong) >= 3 and any(lane.key is None for lane in nokey)
    assert any(lane.key and sum(x.name == lane.name for x in got) == 1 for lane in got)


def test_the_request_codex_sends_is_held_to_the_runs_whole():
    probe = codex_probe_body("m")
    assert shape_differences(codex_probe_body("n"), probe, exact=True) == []
    sent = {**codex_probe_body("m"), "text": {"verbosity": "low"}}
    assert shape_differences(sent, probe, exact=True) == [
        "Codex sends `text`, which the run's request leaves out"]
    sent = {**codex_probe_body("m"), "include": []}
    assert shape_differences(sent, probe, exact=True) == [
        'Codex sends `include` as [] and the run\'s request as ["reasoning.encrypted_content"]']
    sent = codex_probe_body("m")
    sent["tools"] = sent["tools"] + [{"type": "custom", "name": "apply_patch"}]
    diff = shape_differences(sent, probe, exact=True)
    assert any("of kind ['custom', 'function']" in d for d in diff)


def test_an_older_codex_is_held_only_to_asking_nothing_the_run_leaves_out():
    probe = codex_probe_body("m")
    older = {k: v for k, v in codex_probe_body("m").items() if k != "prompt_cache_key"}
    older.update(parallel_tool_calls=False, reasoning=None, include=[])
    assert shape_differences(older, probe, exact=False) == []
    assert shape_differences(older, probe, exact=True) != []
    assert shape_differences({**older, "service_tier": "flex"}, probe, exact=False) == [
        "Codex sends `service_tier`, which the run's request leaves out"]


TCP = """  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid
   0: 0100007F:0FA0 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000
   1: 00000000:1F90 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000
   2: 0100007F:0FA0 0100007F:D431 01 00000000:00000000 00:00000000 00000000  1000
"""
TCP6 = """  sl  local_address                         remote_address                        st
   0: 00000000000000000000000001000000:0FA0 00000000000000000000000000000000:0000 0A
"""


def test_a_port_is_read_as_listened_on_where_its_listener_is():
    assert listening(4000, [TCP]) == {"127.0.0.1"}
    assert listening(8080, [TCP]) == {"0.0.0.0"}
    assert listening(4000, [TCP, TCP6]) == {"127.0.0.1", "::1"}
    assert listening(5000, [TCP, TCP6]) == set()


SHELL = {"type": "function", "function": {"name": "exec_command", "parameters": {
    "type": "object", "properties": {"cmd": {"type": "string"}}}}}


def test_the_lane_calls_the_shell_then_reads_its_output_back():
    first, finish = _chat_answer({"messages": [{"role": "user", "content": "go"}],
                                  "tools": [SHELL]})
    call = first["tool_calls"][0]["function"]
    assert finish == "tool_calls" and call["name"] == "exec_command"
    assert json.loads(call["arguments"]) == {"cmd": "cat note.txt"}
    second, finish = _chat_answer({"tools": [SHELL], "messages": [
        {"role": "user", "content": "go"},
        {"role": "tool", "tool_call_id": "call_1", "content": "the note says hi"}]})
    assert finish == "stop" and second["content"] == "The file says: the note says hi"
    plain, _ = _chat_answer({"messages": [{"role": "user", "content": "hi"}]})
    assert plain["content"] == "pong"


def test_the_summary_leads_with_what_failed_and_counts_it():
    text = summary([Finding("run", "ok", "LiteLLM 1.98.0", "every entry answered"),
                    Finding("flag", "violation", "LiteLLM 1.99.0", "the flag | reached a lane")],
                   ["1.98.0", "1.99.0"], ["0.134.0"])
    assert "**1 of 2 checks failed.**" in text
    rows = [line for line in text.splitlines() if line.startswith("| ✓") or line.startswith("| ✗")]
    assert rows[0].startswith("| ✗ violation") and rows[1].startswith("| ✓")
    assert "the flag \\| reached a lane" in rows[0]


def test_the_summary_names_a_keyed_profiles_variable_as_var():
    """The keyed sentences match whichever variable the lane has; the summary
    prints the sentence a reader can read."""
    text = summary([Finding("key-unset", "ok", "Codex 0.158.0", "exit 1, 0 requests")],
                   ["1.98.0"], ["0.158.0"])
    assert "With $VAR unset or empty, Codex stops before it sends anything" in text
    assert "(w+)" not in text


def test_the_workflow_runs_the_oldest_and_the_newest_of_both_programs():
    """The oldest from the constants the files print, the newest looked up on
    the day; every Wednesday, and on a push that changes what is checked."""
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/conformance.yml").read_text(encoding="utf-8"))
    trigger = workflow.get("on", workflow.get(True))
    assert {"schedule", "workflow_dispatch", "push"} <= set(trigger)
    assert {"configs/litellm.yaml", "configs/codex/*.config.toml",
            "src/freetier_radar/conformance.py", "src/freetier_radar/prober.py"} <= set(
        trigger["push"]["paths"])
    steps = workflow["jobs"]["conformance"]["steps"]
    assert any("freetier-conformance floors" in s.get("run", "") for s in steps)
    run = next(s["run"] for s in steps if "freetier-conformance run" in s.get("run", ""))
    for given in ('--litellm "$LITELLM_OLDEST=', '--litellm "$LITELLM_NEWEST=',
                  '--codex "$CODEX_OLDEST=', '--codex "$CODEX_NEWEST='):
        assert given in run, given
