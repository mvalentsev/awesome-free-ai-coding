"""What the generated configs say LiteLLM and Codex CLI do, held to the
programs themselves.

configs/litellm.yaml and configs/codex/*.config.toml say how the LiteLLM proxy
and Codex CLI behave on them — which release reads a field, where the proxy
sends a key, what Codex asks a lane — and both programs change with every
release. So this runs them on the committed files: the oldest release the
files ask for (render.LITELLM_BRIDGE_SINCE, render.CODEX_SINCE) and the newest,
the proxy started by the command the file prints, every lane pointed at one
served here that records what reaches it, Codex on the profile copied where
the profile says. Each check proves one printed sentence and names it; a
sentence reworded or gone is reported, as claims.CLAIMS reports one, since a
check whose sentence is gone proves nothing.

A failed check is a violation when the sentence no longer holds and a reader's
setup breaks or a key goes where it should not, drift when only a reason the
file gives has stopped holding, and infra when a program could not be run as
printed. Every one of them fails the run: a check that did not run proves
nothing either.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

import httpx
import yaml

from .prober import CODEX_DONE, codex_probe_body
from .render import CODEX_SINCE, LITELLM_BRIDGE_SINCE, litellm_command

__all__ = ["Sentence", "SENTENCES", "Finding", "Lane", "floors", "comment_text",
           "keyed_profile", "missing_sentences", "printed_run", "printed_profile", "as_run",
           "bare", "lanes", "point_lanes", "shape_differences", "listening", "summary", "main"]

LITELLM_YAML = "configs/litellm.yaml"
LITELLM_PROFILE = "configs/codex/litellm.config.toml"
KILO_PROFILE = "configs/codex/kilo-code.config.toml"
# Where the sentences a keyed lane's profile prints are read: the first such
# profile by name (see keyed_profile), since one function writes them all.
KEYED_PROFILE = "configs/codex/<a keyed lane>.config.toml"
ENV_EXAMPLE = "configs/free-llm.env.example"
CONTRIBUTING = "CONTRIBUTING.md"
# The port the printed command leaves LiteLLM on, and the one the profile calls.
PROXY_PORT = 4000
# What a reader's shell may hold beside the lanes' keys: the key LiteLLM hands
# an entry whose own variable is not set.
READER_KEY = "sk-reader-own-openai-key-canary"
# What a lane's variable holds while it is set here: its own name, so a key
# found at the wrong lane says whose it is.
LANE_KEY = "canary-{var}"
# The file a Codex turn is asked to read, and what it says.
NOTE = "the note says forty-two"
VERDICTS = ("violation", "drift", "infra", "reworded")


@dataclass(frozen=True)
class Sentence:
    """What a check proves: a sentence in a committed file, looked for in the
    file's words with comment markers and line breaks taken out."""
    file: str
    pattern: str


SENTENCES: dict[str, Sentence] = {
    "run": Sentence(LITELLM_YAML, r"Run: " + re.escape(litellm_command("litellm.yaml"))),
    "reader-key": Sentence(LITELLM_YAML, r"LiteLLM gives an entry whose key variable is not set "
                                         r"the OPENAI_API_KEY it runs with and sends it to that "
                                         r"lane, so the command runs it without one\."),
    "host": Sentence(LITELLM_YAML, r"The proxy listens on 0\.0\.0\.0 unless --host says "
                                   r"otherwise"),
    "flag": Sentence(LITELLM_YAML, r"every entry carries use_chat_completions_api, which "
                                   r"1\.88\.3 and earlier send on to the vendor"),
    "policy": Sentence(LITELLM_YAML, r"every group deployment carries its own "
                                     r"allowed_fails_policy, which LiteLLM reads from "
                                     + re.escape(LITELLM_BRIDGE_SINCE) + r" on\."),
    "bridge": Sentence(LITELLM_YAML, r"The flag makes the proxy's /v1/responses — the only API "
                                     r"Codex CLI speaks — call each lane's chat completions"),
    "groups": Sentence(LITELLM_YAML, r"a call falls back down that order when a lane runs out of "
                                     r"quota or has no key set here — set only the keys you "
                                     r"have, and a lane without one is skipped\."),
    "authorization": Sentence(LITELLM_YAML, r"its keyless lane answers only a call with no "
                                            r"Authorization header, and LiteLLM sends one on "
                                            r"every call\."),
    "own-keys": Sentence(CONTRIBUTING, r"A key the reader has not set never becomes another of "
                                       r"theirs\."),
    "codex": Sentence(LITELLM_PROFILE, r"Needs Codex CLI " + re.escape(CODEX_SINCE)
                                       + r" or later and LiteLLM "
                                       + re.escape(LITELLM_BRIDGE_SINCE)
                                       + r" or later; the file goes where Codex keeps its "
                                         r"config, ~/\.codex unless CODEX_HOME says otherwise"),
    "no-keys": Sentence(LITELLM_PROFILE, r"A lane whose key is not set is skipped, and "
                                         r"free/nokey needs none, so the profile answers before "
                                         r"you set any\."),
    "tools": Sentence(LITELLM_PROFILE, r"as long as the model calls tools, since every Codex "
                                       r"turn offers them\."),
    "metadata": Sentence(LITELLM_PROFILE, r"Codex warns that it has no metadata for the name, as "
                                          r"it does for any model outside OpenAI's\."),
    "same-request": Sentence(LITELLM_PROFILE, r"so the request Codex sends is the one the list's "
                                              r"run checks"),
    "web-search": Sentence(LITELLM_PROFILE, r"Web search: a tool OpenAI's servers run, which "
                                            r"LiteLLM passes on to a lane as "
                                            r"web_search_options\."),
    "sub-agents": Sentence(LITELLM_PROFILE, r"Sub-agents: Codex sends their tools as a namespace, "
                                            r"which LiteLLM " + re.escape(LITELLM_BRIDGE_SINCE)
                                            + r" and later pass on as plain functions"),
    "key": Sentence(KEYED_PROFILE, r"The key comes from \$(\w+), the variable "
                                   r"free-llm\.env\.example exports"),
    "key-unset": Sentence(KEYED_PROFILE, r"With \$(\w+) unset or empty, Codex stops before it "
                                         r"sends anything, so no other key of yours reaches the "
                                         r"lane\."),
}


@dataclass(frozen=True)
class Finding:
    sentence: str
    verdict: str          # "ok" or one of VERDICTS
    versions: str
    detail: str


@dataclass(frozen=True)
class Lane:
    """An entry of litellm.yaml's model_list, by its place in the list."""
    index: int
    name: str
    model: str
    key: str | None       # the variable its api_key reads, None for `api_key: none`


def floors() -> tuple[str, str]:
    """The oldest LiteLLM and Codex CLI releases the files ask for: the first
    of the minor each names."""
    return f"{LITELLM_BRIDGE_SINCE}.0", f"{CODEX_SINCE}.0"


def comment_text(text: str) -> str:
    """A file's words with comment markers and line breaks taken out, so a
    sentence wrapped across comment lines reads as one."""
    lines = [re.sub(r"^\s*#+\s?", "", line) for line in text.splitlines()]
    return " ".join(" ".join(lines).split())


def keyed_profile(root: Path) -> str | None:
    """The first Codex profile, by name, of a lane that takes the reader's own
    key — its env_key a variable free-llm.env.example leaves empty, where a key
    the vendor prints for anyone comes filled in — or None while no row has
    one."""
    env = (root / ENV_EXAMPLE).read_text(encoding="utf-8")
    empty = set(re.findall(r'(?m)^export (\w+)=""$', env))
    for path in sorted((root / "configs/codex").glob("*.config.toml")):
        found = re.search(r'(?m)^env_key = "(\w+)"$', path.read_text(encoding="utf-8"))
        if found and found.group(1) in empty:
            return path.relative_to(root).as_posix()
    return None


def _sentence_file(root: Path, s: Sentence) -> str | None:
    """The file a sentence is read from: its own, or for the keyed profile's
    sentences the profile keyed_profile finds — none while no row has one."""
    return keyed_profile(root) if s.file == KEYED_PROFILE else s.file


def missing_sentences(root: Path, sentences: dict[str, Sentence] = SENTENCES) -> list[str]:
    texts: dict[str, str] = {}
    gone = []
    for key, s in sentences.items():
        file = _sentence_file(root, s)
        if file is None:
            continue
        if file not in texts:
            texts[file] = comment_text((root / file).read_text(encoding="utf-8"))
        if not re.search(s.pattern, texts[file]):
            gone.append(key)
    return gone


def printed_run(text: str) -> list[str]:
    """The command litellm.yaml's header says to start the proxy with."""
    found = re.search(r"(?m)^# Run: (.+)$", text)
    if found is None:
        raise ValueError("litellm.yaml prints no `# Run:` line")
    return shlex.split(found.group(1))


def printed_profile(text: str) -> tuple[list[str], list[str], list[str]]:
    """The three commands a Codex profile's header prints — the proxy, the
    copy, Codex — each as its words."""
    steps = [shlex.split(m) for m in re.findall(r"(?m)^#   (\S.*)$", text)]
    proxy = next((s for s in steps if "litellm" in s), None)
    copy_ = next((s for s in steps if s[:1] == ["cp"]), None)
    codex = next((s for s in steps if s[:1] == ["codex"]), None)
    if copy_ is None or codex is None:
        raise ValueError("the profile prints no `cp …` and `codex …` commands")
    return proxy or [], copy_, codex


def as_run(argv: list[str], litellm: str, config: str) -> list[str]:
    """A printed proxy command with the program and the config it names put
    where they are here."""
    if "litellm" not in argv or "--config" not in argv:
        raise ValueError(f"not a LiteLLM command: {' '.join(argv)}")
    out = [litellm if a == "litellm" else a for a in argv]
    out[out.index("--config") + 1] = config
    return out


def bare(argv: list[str]) -> list[str]:
    """The printed command as a reader who skips its advice runs it: no
    OPENAI_API_KEY isolation or --host; retain settings needed for startup."""
    out = list(argv)
    if out[:3] == ["env", "-u", "OPENAI_API_KEY"]:
        del out[1:3]
    if out[:1] == ["env"] and (len(out) == 1 or "=" not in out[1]):
        del out[0]
    if "--host" in out:
        at = out.index("--host")
        del out[at:at + 2]
    return out


def lanes(config: dict) -> list[Lane]:
    out = []
    for i, entry in enumerate(config["model_list"]):
        params = entry["litellm_params"]
        key = str(params.get("api_key", ""))
        out.append(Lane(i, entry["model_name"], params["model"],
                        key.removeprefix("os.environ/") if key.startswith("os.environ/") else None))
    return out


def point_lanes(config: dict, base: str) -> dict:
    """The config with every entry sent to its own lane under `base`, and
    nothing else changed."""
    out = copy.deepcopy(config)
    for i, entry in enumerate(out["model_list"]):
        entry["litellm_params"]["api_base"] = f"{base}/lane/{i}/v1"
    return out


# What a request's shape is made of: its fields, its tools' kinds and fields,
# and the settings a Codex profile decides.
SETTINGS = ("tool_choice", "parallel_tool_calls", "reasoning", "store", "stream", "include")


def shape_differences(sent: dict, probe: dict, exact: bool) -> list[str]:
    """How a request Codex sent differs from the one the list's run sends.
    Exact: the same fields, tool kinds, tool fields and settings. Otherwise
    (an older Codex): nothing the run's request leaves out."""
    out = []
    fields, probe_fields = set(sent), set(probe)
    extra, absent = sorted(fields - probe_fields), sorted(probe_fields - fields)
    if extra:
        out.append("Codex sends " + ", ".join(f"`{f}`" for f in extra) + ", which the run's "
                   "request leaves out")
    if absent and exact:
        out.append("the run's request sends " + ", ".join(f"`{f}`" for f in absent)
                   + ", which Codex no longer does")

    def kinds(body: dict) -> set[str]:
        return {str(t.get("type")) for t in body.get("tools") or []}

    def tool_fields(body: dict) -> set[tuple[str, ...]]:
        return {tuple(sorted(t)) for t in body.get("tools") or []}

    if kinds(sent) - kinds(probe) or (exact and kinds(sent) != kinds(probe)):
        out.append(f"Codex offers tools of kind {sorted(kinds(sent))} and the run's request "
                   f"{sorted(kinds(probe))}")
    if tool_fields(sent) - tool_fields(probe):
        out.append(f"Codex's tools carry {sorted(tool_fields(sent))} and the run's "
                   f"{sorted(tool_fields(probe))}")
    if exact:
        for s in SETTINGS:
            if s in sent and s in probe and sent[s] != probe[s]:
                out.append(f"Codex sends `{s}` as {json.dumps(sent[s])} and the run's request as "
                           f"{json.dumps(probe[s])}")
    return out


def listening(port: int, tables: list[str]) -> set[str]:
    """The addresses a TCP port is listened on at, read from
    /proc/net/tcp-style tables."""
    found = set()
    for table in tables:
        for line in table.splitlines()[1:]:
            cols = line.split()
            if len(cols) < 4 or cols[3] != "0A":          # 0A: LISTEN
                continue
            address, hex_port = cols[1].rsplit(":", 1)
            if int(hex_port, 16) != port:
                continue
            raw = bytes.fromhex(address)
            if len(raw) == 4:
                found.add(socket.inet_ntop(socket.AF_INET, raw[::-1]))
            else:
                words = b"".join(raw[i:i + 4][::-1] for i in range(0, 16, 4))
                found.add(socket.inet_ntop(socket.AF_INET6, words))
    return found


def _tables() -> list[str]:
    return [Path(p).read_text() for p in ("/proc/net/tcp", "/proc/net/tcp6") if Path(p).exists()]


def _listening_now(port: int) -> set[str]:
    return listening(port, _tables())


def _held_by_group(pgid: int, port: int) -> bool:
    """Whether the port's listener is a socket a process of this group holds:
    what answers on the port is then the proxy started here, and not one left
    over from before."""
    inodes = {f"socket:[{cols[9]}]" for table in _tables() for cols in
              (line.split() for line in table.splitlines()[1:])
              if len(cols) > 9 and cols[3] == "0A" and int(cols[1].rsplit(":", 1)[1], 16) == port}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if int((proc / "stat").read_text().rsplit(")", 1)[1].split()[2]) != pgid:
                continue
            if any(os.readlink(fd) in inodes for fd in (proc / "fd").iterdir()):
                return True
        except (OSError, ValueError, IndexError):
            continue
    return False


# ---- the lanes served here

@dataclass
class _Record:
    lane: str             # an entry's index, or "capture"
    path: str
    authorization: str | None
    body: object


@dataclass
class _Lanes:
    """Every entry's lane at /lane/<index>/v1, and /capture/v1/responses, which
    records a Codex request and answers the shortest stream Codex accepts."""
    records: list[_Record] = field(default_factory=list)
    status: dict[int, int] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def since(self, mark: int) -> list[_Record]:
        with self.lock:
            return list(self.records[mark:])

    def mark(self) -> int:
        with self.lock:
            return len(self.records)

    def failing(self, status: dict[int, int]) -> None:
        with self.lock:
            self.status = dict(status)


def _sse(events: list[dict], named: bool = False) -> bytes:
    return "".join((f"event: {e['type']}\n" if named else "") + f"data: {json.dumps(e)}\n\n"
                   for e in events).encode() + (b"" if named else b"data: [DONE]\n\n")


def _shell_call(tools: list[dict]) -> dict | None:
    """A call of the tool a Codex turn runs a command with."""
    functions = [t.get("function") or t for t in tools if t.get("type") == "function"]
    for f in sorted(functions, key=lambda f: f.get("name") != "exec_command"):
        props = (f.get("parameters") or {}).get("properties") or {}
        if "cmd" in props:
            return {"name": f["name"], "arguments": json.dumps({"cmd": "cat note.txt"})}
    return None


def _chat_answer(body: dict) -> tuple[dict, str]:
    """What a lane says to a chat request: a call of the shell tool when one
    is offered and nothing has run yet, the tool's output once it has, "pong"
    otherwise. Returns the message and its finish reason."""
    messages = body.get("messages") or []
    results = [m for m in messages if m.get("role") == "tool"]
    call = _shell_call(body.get("tools") or []) if not results else None
    if call:
        message = {"role": "assistant", "content": None,
                   "tool_calls": [{"id": "call_1", "type": "function", "function": call}]}
        return message, "tool_calls"
    if results:
        said = results[-1].get("content")
        if isinstance(said, list):
            said = " ".join(p.get("text", "") for p in said if isinstance(p, dict))
        return {"role": "assistant", "content": f"The file says: {said}"}, "stop"
    return {"role": "assistant", "content": "pong"}, "stop"


def _handler(lanes_: _Lanes):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, status: int, data: bytes, ctype: str = "application/json") -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            # Codex may read a provider's model list before its first turn: what
            # the capture lane is asked that way is recorded too, since a key
            # can ride on it.
            if self.path.startswith("/capture/"):
                with lanes_.lock:
                    lanes_.records.append(_Record("capture-get", self.path,
                                                  self.headers.get("Authorization"), None))
            self._send(200, b'{"object":"list","data":[]}')

        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            try:
                body = json.loads(raw or b"{}")
            except ValueError:
                body = raw.decode(errors="replace")
            m = re.match(r"^/(?:lane/(\d+)|(capture))/v1/(chat/completions|responses)$",
                         self.path)
            lane = (m.group(1) or m.group(2)) if m else "?"
            with lanes_.lock:
                lanes_.records.append(_Record(lane, self.path, self.headers.get("Authorization"),
                                              body))
                status = lanes_.status.get(int(lane), 200) if lane.isdigit() else 200
            if m is None or not isinstance(body, dict):
                return self._send(404, b'{"error":{"message":"no such route"}}')
            if m.group(2):
                return self._capture(body)
            if m.group(3) == "responses":
                return self._send(404, b'{"error":{"message":"no /responses here"}}')
            if status != 200:
                kind = "rate_limit_exceeded" if status == 429 else "server_error"
                return self._send(status, json.dumps(
                    {"error": {"message": f"answered {status} here", "type": kind}}).encode())
            message, finish = _chat_answer(body)
            base = {"id": "chatcmpl-1", "created": int(time.time()), "model": body.get("model")}
            usage = {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6}
            if body.get("stream"):
                delta = {k: v for k, v in message.items() if v is not None}
                if "tool_calls" in delta:
                    delta["tool_calls"] = [dict(c, index=0) for c in delta["tool_calls"]]
                return self._send(200, _sse([
                    {**base, "object": "chat.completion.chunk",
                     "choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                    {**base, "object": "chat.completion.chunk",
                     "choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
                     "usage": usage}]), "text/event-stream")
            return self._send(200, json.dumps({
                **base, "object": "chat.completion", "usage": usage,
                "choices": [{"index": 0, "message": message, "finish_reason": finish}]}).encode())

        def _capture(self, body: dict) -> None:
            item = {"id": "msg_1", "type": "message", "role": "assistant", "status": "completed",
                    "content": [{"type": "output_text", "text": "pong", "annotations": []}]}
            done = {"id": "resp_1", "object": "response", "created_at": int(time.time()),
                    "status": "completed", "model": body.get("model"), "output": [item],
                    "usage": {"input_tokens": 5, "output_tokens": 1, "total_tokens": 6,
                              "input_tokens_details": {"cached_tokens": 0},
                              "output_tokens_details": {"reasoning_tokens": 0}}}
            self._send(200, _sse([
                {"type": "response.created", "response": {**done, "status": "in_progress",
                                                          "output": []}},
                {"type": "response.output_item.done", "output_index": 0, "item": item},
                {"type": CODEX_DONE, "response": done}], named=True), "text/event-stream")

    return Handler


@contextmanager
def _serve_lanes() -> Iterator[tuple[_Lanes, str]]:
    lanes_ = _Lanes()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(lanes_))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield lanes_, f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


# ---- the programs

def _base_env(home: Path) -> dict[str, str]:
    """Nothing of the runner's own: a PATH, a home of its own, no telemetry,
    and LiteLLM's model map read from its package instead of fetched."""
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home),
            "LANG": "C.UTF-8", "LITELLM_TELEMETRY": "False",
            "LITELLM_LOCAL_MODEL_COST_MAP": "True"}


class _Unstarted(Exception):
    pass


@contextmanager
def _proxy(argv: list[str], env: dict[str, str], log: Path) -> Iterator[subprocess.Popen]:
    if _port_taken(PROXY_PORT):
        raise _Unstarted(f"port {PROXY_PORT} is taken here, and the printed command sets no "
                         "other")
    with log.open("w") as out:
        proc = subprocess.Popen(argv, env=env, stdout=out, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.monotonic() + 240
        while True:
            if proc.poll() is not None:
                raise _Unstarted(f"exited {proc.returncode}: "
                                 + " ".join(log.read_text(errors="replace").split()[-60:]))
            try:
                if (httpx.get(f"http://127.0.0.1:{PROXY_PORT}/health/liveliness",
                              timeout=5).status_code == 200
                        and _held_by_group(proc.pid, PROXY_PORT)):
                    break
            except httpx.HTTPError:
                pass
            if time.monotonic() > deadline:
                raise _Unstarted("did not answer /health/liveliness in 240 s")
            time.sleep(1)
        yield proc
    finally:
        for sig, wait in ((signal.SIGTERM, 10), (signal.SIGKILL, 30)):
            try:
                os.killpg(proc.pid, sig)
                proc.wait(timeout=wait)
                break
            except ProcessLookupError:
                break
            except subprocess.TimeoutExpired:
                continue
        for _ in range(30):
            if not _port_taken(PROXY_PORT):
                break
            time.sleep(1)


def _port_taken(port: int) -> bool:
    """Whether a listener answers on the port. Whose it is, once the proxy has
    started, is _held_by_group's to say."""
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _chat(model: str, **extra) -> httpx.Response:
    return httpx.post(f"http://127.0.0.1:{PROXY_PORT}/v1/chat/completions", timeout=180, json={
        "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5,
        **extra})


def _codex(binary: str, home: Path, cwd: Path, args: list[str],
           extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8",
           **(extra or {})}
    try:
        return subprocess.run([binary, "exec", *args], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
        return subprocess.CompletedProcess(exc.cmd, -1, out or "", (err or "") + "\n(timed out)")


def _tail(text: str, words: int = 40) -> str:
    return " ".join(text.split()[-words:])


# ---- the checks

@dataclass
class _Run:
    root: Path
    work: Path
    litellm: dict[str, str]
    codex: dict[str, str]
    findings: list[Finding] = field(default_factory=list)
    started: float = field(default_factory=time.monotonic)

    def note(self, sentence: str, verdict: str, versions: str, detail: str) -> None:
        self.findings.append(Finding(sentence, verdict, versions, detail))
        self.say(f"{'ok' if verdict == 'ok' else verdict.upper()} {sentence} [{versions}] {detail}")

    def say(self, line: str) -> None:
        print(f"[{time.monotonic() - self.started:6.1f} s] {line}", file=sys.stderr, flush=True)


def _key_env(lanes_: list[Lane], keys: bool) -> dict[str, str]:
    env = {"OPENAI_API_KEY": READER_KEY}
    if keys:
        env.update({lane.key: LANE_KEY.format(var=lane.key) for lane in lanes_ if lane.key})
    return env


def _foreign_keys(records: list[_Record], by_index: dict[int, Lane]) -> list[str]:
    """Every request that carried a key other than its lane's own."""
    out = []
    for r in records:
        if not r.lane.isdigit() or not r.authorization:
            continue
        lane = by_index[int(r.lane)]
        own = f"Bearer {LANE_KEY.format(var=lane.key)}" if lane.key else "Bearer none"
        if r.authorization != own:
            said = "the reader's OPENAI_API_KEY" if READER_KEY in r.authorization else (
                r.authorization.removeprefix("Bearer "))
            out.append(f"{lane.name} (entry {lane.index}) got {said}")
    return out


def _check_keys_set(run: _Run, version: str, binary: str, config: Path, lanes_: list[Lane],
                    served: _Lanes, argv: list[str]) -> None:
    """Every lane's variable set: each entry answers through the proxy with its
    own key and without the flag, the proxy's /v1/responses reaches the lanes'
    chat completions, and a group whose lanes are all out of quota falls back."""
    v = f"LiteLLM {version}"
    by_index = {lane.index: lane for lane in lanes_}
    home = run.work / f"home-keys-{version}"
    home.mkdir(parents=True, exist_ok=True)
    env = {**_base_env(home), **_key_env(lanes_, keys=True)}
    run.say(f"LiteLLM {version}, every lane's key set: starting the proxy as printed")
    try:
        with _proxy(as_run(argv, binary, str(config)), env, run.work / f"proxy-keys-{version}.log"):
            run.say("the proxy answers")
            where = _listening_now(PROXY_PORT)
            run.note("host", "ok" if where == {"127.0.0.1"} else "violation", v,
                     f"--host 127.0.0.1 left it listening on {sorted(where)}")
            counts = Counter(lane.name for lane in lanes_)
            singles = [lane for lane in lanes_ if counts[lane.name] == 1]
            mark = served.mark()
            with ThreadPoolExecutor(8) as pool:
                answers = dict(zip([lane.name for lane in singles],
                                   pool.map(lambda lane: _chat(lane.name).status_code, singles)))
            records = served.since(mark)
            failed = sorted(n for n, s in answers.items() if s != 200)
            run.note("run", "violation" if failed else "ok", v,
                     f"{len(singles) - len(failed)} of {len(singles)} entries answered through the "
                     "printed command" + (f"; not {', '.join(failed[:8])}" if failed else ""))
            flagged = sorted({by_index[int(r.lane)].name for r in records
                              if r.lane.isdigit() and isinstance(r.body, dict)
                              and "use_chat_completions_api" in r.body})
            run.note("flag", "violation" if flagged else "ok", v,
                     (f"use_chat_completions_api reached {', '.join(flagged[:8])}" if flagged else
                      f"no request of {len(records)} carried use_chat_completions_api"))
            foreign = _foreign_keys(records, by_index)
            run.note("own-keys", "violation" if foreign else "ok", v,
                     "; ".join(foreign[:6]) if foreign else
                     f"each of {len(records)} requests carried its own lane's key")
            keyless = [r for r in records if r.lane.isdigit() and not by_index[int(r.lane)].key]
            bare_ = [by_index[int(r.lane)].name for r in keyless if not r.authorization]
            which = f" ({', '.join(sorted(set(bare_))[:5])})" if bare_ else ""
            run.note("authorization", "drift" if bare_ or not keyless else "ok", v,
                     f"{len(keyless)} calls to keyless lanes, {len(bare_)} without "
                     f"Authorization{which}")
            _check_bridge(run, v, served, singles)
            _check_fallback(run, v, served, lanes_)
    except _Unstarted as exc:
        run.note("run", "violation", v, f"the printed command did not start the proxy: {exc}")


def _check_bridge(run: _Run, v: str, served: _Lanes, singles: list[Lane]) -> None:
    for model in (next(lane.name for lane in singles if lane.key), "free/strong"):
        mark = served.mark()
        body = codex_probe_body(model)
        try:
            with httpx.stream("POST", f"http://127.0.0.1:{PROXY_PORT}/v1/responses", json=body,
                              timeout=180) as resp:
                text = resp.read().decode(errors="replace")
                status = resp.status_code
        except httpx.HTTPError as exc:
            run.note("bridge", "violation", v, f"/v1/responses for {model}: {exc}")
            continue
        paths = sorted({r.path.split("/v1/", 1)[-1] for r in served.since(mark)})
        ok = status == 200 and CODEX_DONE in text and paths == ["chat/completions"]
        run.note("bridge", "ok" if ok else "violation", v,
                 f"/v1/responses for {model} answered {status}"
                 + (", a stream ending in response.completed" if CODEX_DONE in text else
                    f": {_tail(text)}") + f"; the lanes were asked at {paths or 'nothing'}")


def _check_fallback(run: _Run, v: str, served: _Lanes, lanes_: list[Lane]) -> None:
    """Every free/strong lane out of quota: the call falls back to free/nokey."""
    strong = [lane for lane in lanes_ if lane.name == "free/strong"]
    served.failing({lane.index: 429 for lane in strong})
    mark = served.mark()
    resp = _chat("free/strong")
    answered_by = [lanes_[int(r.lane)].name for r in served.since(mark)
                   if r.lane.isdigit() and served.status.get(int(r.lane), 200) == 200]
    served.failing({})
    ok = resp.status_code == 200 and answered_by and set(answered_by) == {"free/nokey"}
    run.note("groups", "ok" if ok else "violation", v,
             f"every free/strong lane answering 429: the call answered {resp.status_code}, "
             f"from {sorted(set(answered_by)) or 'no lane'}")


# LiteLLM's router on the file's model_list and router_settings, as the proxy
# builds it: `calls` calls to a group, `pace` seconds apart, and how long they
# took.
_ROUTER_CALLS = """
import asyncio, json, sys, time
from litellm import Router
config = json.load(open(sys.argv[1]))
group, calls, pace = sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
router = Router(model_list=config["model_list"], **config.get("router_settings", {}))
async def main():
    answered, t0 = 0, time.monotonic()
    for _ in range(calls):
        try:
            await router.acompletion(model=group, messages=[{"role": "user", "content": "hi"}],
                                     max_tokens=5)
            answered += 1
        except Exception:
            pass
        await asyncio.sleep(pace)
    print(json.dumps({"answered": answered, "seconds": time.monotonic() - t0}))
asyncio.run(main())
"""
# How long LiteLLM benches a deployment unless told otherwise
# (DEFAULT_COOLDOWN_TIME_SECONDS in litellm/constants.py, 1.98 and 1.103).
BENCH_SECONDS = 5


def _check_policy(run: _Run, version: str, binary: str, config_json: Path, lanes_: list[Lane],
                  served: _Lanes) -> None:
    """All but one of free/strong's lanes answer 500 and twenty calls go out
    back to back: a router that reads each deployment's allowed_fails_policy
    asks every failing lane once a bench (BENCH_SECONDS) and sends the rest to
    the lane left, where 1.89's asked each five times in two seconds. The
    router is asked directly, built from the file as the proxy builds it:
    through the proxy, 1.98 and 1.103 recorded one failure a request on
    2026-09-28, so a burst there benches the lanes a request at a time."""
    v = f"LiteLLM {version}"
    strong = [lane for lane in lanes_ if lane.name == "free/strong"]
    if len(strong) < 3:
        run.note("policy", "infra", v, f"free/strong has {len(strong)} lanes; the check needs 3")
        return
    healthy, failing = strong[0], strong[1:]
    home = run.work / f"home-router-{version}"
    home.mkdir(parents=True, exist_ok=True)
    served.failing({lane.index: 500 for lane in failing})
    mark = served.mark()
    try:
        done = subprocess.run([str(Path(binary).parent / "python"), "-c", _ROUTER_CALLS,
                               str(config_json), "free/strong", "20", "0.05"],
                              env={**_base_env(home), **_key_env(lanes_, keys=True)},
                              capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        run.note("policy", "infra", v, "LiteLLM's router did not finish twenty calls in 600 s")
        return
    finally:
        served.failing({})
    if done.returncode != 0:
        run.note("policy", "infra", v, f"LiteLLM's router exited {done.returncode}: "
                                       + _tail(done.stderr))
        return
    try:
        took = float(json.loads(done.stdout.strip().splitlines()[-1])["seconds"])
    except (ValueError, KeyError, IndexError):
        run.note("policy", "infra", v, "LiteLLM's router said nothing readable: "
                                       + _tail(done.stdout))
        return
    asked = Counter(r.lane for r in served.since(mark))
    most = max(asked.get(str(lane.index), 0) for lane in failing)
    held = asked.get(str(healthy.index), 0)
    # A lane benched at the first call is back once a bench has passed.
    allowed = 1 + int(took // BENCH_SECONDS)
    ok = most <= allowed and held >= 10
    run.note("policy", "ok" if ok else "violation", v,
             f"LiteLLM's router, {len(failing)} of {len(strong)} free/strong lanes answering 500, "
             f"20 calls in {took:.1f} s: a failing lane asked at most {most} "
             f"time{'s' if most != 1 else ''} ({allowed} allowed), the other lane {held} times")


def _check_no_keys(run: _Run, version: str, binary: str, config: Path, lanes_: list[Lane],
                   served: _Lanes, argv: list[str], codex_versions: list[str]) -> None:
    """No lane's variable set, the reader's OPENAI_API_KEY in the shell: the
    groups still answer, from keyless lanes, the reader's key reaches none,
    and Codex runs a turn on the profile as printed."""
    v = f"LiteLLM {version}"
    by_index = {lane.index: lane for lane in lanes_}
    home = run.work / f"home-nokeys-{version}"
    home.mkdir(parents=True, exist_ok=True)
    env = {**_base_env(home), **_key_env(lanes_, keys=False)}
    mark = served.mark()
    run.say(f"LiteLLM {version}, no key set: starting the proxy as the Codex profile prints it")
    try:
        with _proxy(as_run(argv, binary, str(config)), env,
                    run.work / f"proxy-nokeys-{version}.log"):
            run.say("the proxy answers")
            resp = _chat("free/strong")
            asked = [by_index[int(r.lane)] for r in served.since(mark) if r.lane.isdigit()]
            ok = resp.status_code == 200 and asked and all(lane.key is None for lane in asked)
            named = sorted({lane.name + (" (keyed)" if lane.key else "") for lane in asked})
            run.note("no-keys", "ok" if ok else "violation", v,
                     f"free/strong with no key set answered {resp.status_code}, from "
                     f"{named or 'no lane'}")
            for c in codex_versions:
                _check_codex_turn(run, version, c, served, newest=c == codex_versions[-1])
    except _Unstarted as exc:
        run.note("codex", "violation", v, f"the profile's proxy command did not start: {exc}")
        return
    foreign = _foreign_keys(served.since(mark), by_index)
    run.note("own-keys", "violation" if foreign else "ok", v + ", no key set",
             "; ".join(foreign[:6]) if foreign else
             "no lane got the reader's OPENAI_API_KEY or any key but its own")


def _codex_home(run: _Run, tag: str, profile: str,
                base_url: str | None = None) -> tuple[Path, Path]:
    """A home with the profile copied where its header says, and a project
    with the note in it."""
    text = (run.root / profile).read_text(encoding="utf-8")
    _, cp, _ = printed_profile(text)
    home = run.work / f"codex-{tag}"
    shutil.rmtree(home, ignore_errors=True)
    dest = Path(cp[-1].replace("~", str(home / "home"), 1))
    dest.mkdir(parents=True, exist_ok=True)
    if base_url:
        text = re.sub(r'(?m)^base_url = ".*"$', f'base_url = "{base_url}"', text)
    (dest / Path(cp[1]).name).write_text(text, encoding="utf-8")
    (home / "project").mkdir(parents=True)
    (home / "project" / "note.txt").write_text(NOTE + "\n")
    return home / "home", home / "project"


def _check_codex_turn(run: _Run, litellm_version: str, codex_version: str, served: _Lanes,
                      newest: bool) -> None:
    v = f"Codex {codex_version} + LiteLLM {litellm_version}"
    _, _, codex_cmd = printed_profile((run.root / LITELLM_PROFILE).read_text(encoding="utf-8"))
    home, project = _codex_home(run, f"{codex_version}-{litellm_version}", LITELLM_PROFILE)
    mark = served.mark()
    done = _codex(run.codex[codex_version], home, project,
                  [*codex_cmd[1:], "--skip-git-repo-check",
                   "--dangerously-bypass-approvals-and-sandbox",
                   "Run `cat note.txt` and tell me what the file says."])
    records = [r for r in served.since(mark) if r.lane.isdigit()]
    reached = any(NOTE in json.dumps(r.body) for r in records[1:])
    ok = done.returncode == 0 and NOTE in done.stdout and reached
    printed = ("and Codex printed it" if NOTE in done.stdout else
               "and Codex did not print it: " + _tail(done.stdout + done.stderr))
    run.note("codex", "ok" if ok else "violation", v,
             f"`codex exec {' '.join(codex_cmd[1:])}` from ~/.codex, no key set: exit "
             f"{done.returncode}, the command's output {'reached' if reached else 'never reached'} "
             f"the lane, {printed}")
    first = records[0].body if records and isinstance(records[0].body, dict) else {}
    tools = first.get("tools") or []
    run.note("tools", "ok" if tools else "drift", v,
             f"the first request of the turn offered {len(tools)} tools")
    if newest:
        warned = re.search(r"(?i)metadata", done.stderr) is not None
        run.note("metadata", "ok" if warned else "drift", v,
                 "Codex warned: " + next((line.strip() for line in done.stderr.splitlines()
                                          if "etadata" in line), "") if warned else
                 "Codex printed no warning about the model's metadata")
        _check_codex_setting(run, v, codex_version, litellm_version, served, "web-search",
                             'web_search="live"')
        _check_codex_setting(run, v, codex_version, litellm_version, served, "sub-agents",
                             "features.multi_agent=true")


def _check_codex_setting(run: _Run, v: str, codex_version: str, litellm_version: str,
                         served: _Lanes, sentence: str, override: str) -> None:
    """A setting the profiles turn off, on: what LiteLLM hands the lane."""
    _, _, codex_cmd = printed_profile((run.root / LITELLM_PROFILE).read_text(encoding="utf-8"))
    home, project = _codex_home(run, f"{codex_version}-{litellm_version}-{sentence}",
                                LITELLM_PROFILE)
    mark = served.mark()
    _codex(run.codex[codex_version], home, project,
           [*codex_cmd[1:], "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox",
            "-c", override, "Say pong."])
    bodies = [r.body for r in served.since(mark) if r.lane.isdigit() and isinstance(r.body, dict)]
    if not bodies:
        run.note(sentence, "infra", v, f"with {override}, no request reached a lane")
        return
    first = bodies[0]
    if sentence == "web-search":
        ok = "web_search_options" in first
        run.note(sentence, "ok" if ok else "drift", v,
                 f"with {override}, the lane's request " + ("carried web_search_options" if ok else
                                                             f"carried {sorted(first)}"))
    else:
        tools = first.get("tools") or []
        kinds = sorted({str(t.get("type")) for t in tools})
        names = [((t.get("function") or {}).get("name") or "") for t in tools]
        ok = kinds == ["function"] and any("agent" in n for n in names)
        run.note(sentence, "ok" if ok else "drift", v,
                 f"with {override}, the lane got tools of kind {kinds}, the sub-agents' among them "
                 + ("as functions" if ok else "not as functions"))


def _check_bare(run: _Run, version: str, binary: str, config: Path, lanes_: list[Lane],
                served: _Lanes, argv: list[str]) -> None:
    """The command without its advice: what the header says happens then."""
    v = f"LiteLLM {version}"
    home = run.work / f"home-bare-{version}"
    home.mkdir(parents=True, exist_ok=True)
    env = {**_base_env(home), **_key_env(lanes_, keys=False)}
    keyed = next(lane for lane in lanes_ if lane.key
                 and Counter(x.name for x in lanes_)[lane.name] == 1)
    run.say(f"LiteLLM {version}: starting the proxy without the command's advice")
    try:
        with _proxy(bare(as_run(argv, binary, str(config))), env,
                    run.work / f"proxy-bare-{version}.log"):
            run.say("the proxy answers")
            where = _listening_now(PROXY_PORT)
            run.note("host", "ok" if "0.0.0.0" in where else "drift", v,
                     f"with no --host it listened on {sorted(where)}")
            mark = served.mark()
            _chat(keyed.name)
            got = [r.authorization or "" for r in served.since(mark) if r.lane == str(keyed.index)]
            leaked = any(READER_KEY in a for a in got)
            run.note("reader-key", "ok" if leaked else "drift", v,
                     f"started without `env -u OPENAI_API_KEY`, {keyed.name} with {keyed.key} "
                     "unset " + ("got the reader's OPENAI_API_KEY" if leaked else
                                 f"did not get it ({len(got)} requests)"))
    except _Unstarted as exc:
        run.note("host", "infra", v, f"the command without its advice did not start: {exc}")


def _check_capture(run: _Run, served: _Lanes, base: str, codex_versions: list[str]) -> None:
    """The request Codex sends a lane under the profiles' settings, beside the
    one the list's run sends."""
    probe = codex_probe_body("m")
    for c in codex_versions:
        newest = c == codex_versions[-1]
        v = f"Codex {c}"
        _, _, codex_cmd = printed_profile((run.root / KILO_PROFILE).read_text(encoding="utf-8"))
        for override, sentence in ((None, "same-request"),) + (
                (("features.multi_agent=true", "sub-agents"),) if newest else ()):
            home, project = _codex_home(run, f"{c}-capture-{sentence}", KILO_PROFILE,
                                        base_url=f"{base}/capture/v1")
            mark = served.mark()
            _codex(run.codex[c], home, project,
                   [*codex_cmd[1:], "--skip-git-repo-check",
                    *(("-c", override) if override else ()), "Say pong."])
            sent = next((r.body for r in served.since(mark) if r.lane == "capture"), None)
            if not isinstance(sent, dict):
                run.note(sentence, "infra", v, "Codex sent the capture lane nothing")
                continue
            if sentence == "same-request":
                diff = shape_differences(sent, probe, exact=newest)
                same = ("the same fields, tools and settings as the run's request" if newest else
                        "nothing the run's request leaves out")
                run.note(sentence, "violation" if diff else "ok",
                         v + (" (newest)" if newest else ""), "; ".join(diff) or same)
            else:
                kinds = sorted({str(t.get("type")) for t in sent.get("tools") or []})
                run.note(sentence, "ok" if "namespace" in kinds else "drift", v,
                         f"with {override}, Codex offered tools of kind {kinds}")


def _check_keyed(run: _Run, served: _Lanes, base: str, codex_versions: list[str]) -> None:
    """What a keyed lane's profile says Codex does with the reader's key: the
    variable it names goes to the lane as the bearer token, and while it is
    unset or empty nothing goes at all — with the reader's own OpenAI key in
    OPENAI_API_KEY beside it, and in the auth.json Codex keeps once signed in
    with a key. A profile written for one keyed lane is written for all of them
    by the same function, so the first one stands for the rest."""
    rel = keyed_profile(run.root)
    if rel is None:
        return
    text = (run.root / rel).read_text(encoding="utf-8")
    found = re.search(r'(?m)^env_key = "(\w+)"$', text)
    if found is None:
        run.note("key", "infra", "—", f"{rel} names no env_key")
        return
    var = found.group(1)
    _, _, codex_cmd = printed_profile(text)
    canary = LANE_KEY.format(var=var)
    reader = {"auth_mode": "apikey", "OPENAI_API_KEY": READER_KEY}
    cases = (("key", "set", {var: canary, "OPENAI_API_KEY": READER_KEY}, False),
             ("key-unset", "unset, the reader's key in OPENAI_API_KEY and auth.json",
              {"OPENAI_API_KEY": READER_KEY}, True),
             ("key-unset", "empty, the reader's key in OPENAI_API_KEY",
              {var: "", "OPENAI_API_KEY": READER_KEY}, False))
    for c in codex_versions:
        v = f"Codex {c}"
        for n, (sentence, how, extra, auth_json) in enumerate(cases):
            home, project = _codex_home(run, f"{c}-keyed-{n}", rel, base_url=f"{base}/capture/v1")
            if auth_json:
                (home / ".codex" / "auth.json").write_text(json.dumps(reader), encoding="utf-8")
            mark = served.mark()
            done = _codex(run.codex[c], home, project,
                          [*codex_cmd[1:], "--skip-git-repo-check", "Say pong."], extra)
            got = [r for r in served.since(mark) if r.lane.startswith("capture")]
            said = sorted({r.authorization or "no Authorization" for r in got})
            said = [a.replace(READER_KEY, "<the reader's own key>") for a in said]
            if sentence == "key":
                ok = (done.returncode == 0 and any(r.lane == "capture" for r in got)
                      and all(r.authorization == f"Bearer {canary}" for r in got))
            else:
                ok = done.returncode != 0 and not got
            run.note(sentence, "ok" if ok else "violation", v,
                     f"`{' '.join(codex_cmd)}` on {rel} with ${var} {how}: exit "
                     f"{done.returncode}, {len(got)} request{'' if len(got) == 1 else 's'} "
                     "reached the lane"
                     + (f", carrying {', '.join(said)}" if got else "")
                     + ("" if ok else " — " + _tail(done.stdout + done.stderr)))


def run_checks(root: Path, litellm: dict[str, str], codex: dict[str, str],
               work: Path) -> list[Finding]:
    run = _Run(root, work, litellm, codex)
    gone = missing_sentences(root)
    for key in gone:
        s = SENTENCES[key]
        run.note(key, "reworded", "—", f"{s.file} no longer says `{s.pattern}` — point the "
                                       "check at the sentence that says it now")
    order = lambda v: tuple(int(x) for x in v.split("."))  # noqa: E731
    litellm_versions = sorted(litellm, key=order)
    codex_versions = sorted(codex, key=order)
    want_litellm, want_codex = floors()
    if litellm_versions[0] != want_litellm or codex_versions[0] != want_codex:
        run.note("codex", "infra", "—", f"the oldest releases given are LiteLLM "
                 f"{litellm_versions[0]} and Codex {codex_versions[0]}; the files ask for "
                 f"{want_litellm} and {want_codex}")
    config = yaml.safe_load((root / LITELLM_YAML).read_text(encoding="utf-8"))
    run_argv = printed_run((root / LITELLM_YAML).read_text(encoding="utf-8"))
    profile_argv, _, _ = printed_profile((root / LITELLM_PROFILE).read_text(encoding="utf-8"))
    lanes_ = lanes(config)
    with _serve_lanes() as (served, base):
        pointed = run.work / "litellm.yaml"

        class _NoAliases(yaml.SafeDumper):
            def ignore_aliases(self, data):
                return True

        pointed.write_text(yaml.dump(point_lanes(config, base), Dumper=_NoAliases,
                                     sort_keys=False), encoding="utf-8")
        pointed_json = run.work / "litellm.json"
        pointed_json.write_text(json.dumps(point_lanes(config, base)), encoding="utf-8")
        try:
            for version in litellm_versions:
                binary = litellm[version]
                _check_policy(run, version, binary, pointed_json, lanes_, served)
                _check_keys_set(run, version, binary, pointed, lanes_, served, run_argv)
                _check_no_keys(run, version, binary, pointed, lanes_, served,
                               profile_argv or run_argv, codex_versions)
                _check_bare(run, version, binary, pointed, lanes_, served, run_argv)
            _check_capture(run, served, base, codex_versions)
            _check_keyed(run, served, base, codex_versions)
        finally:
            with (run.work / "requests.jsonl").open("w", encoding="utf-8") as fh:
                for r in served.since(0):
                    fh.write(json.dumps({"lane": r.lane, "path": r.path,
                                         "authorization": r.authorization, "body": r.body}) + "\n")
    return run.findings


def summary(findings: list[Finding], litellm: list[str], codex: list[str]) -> str:
    marks = {"ok": "✓", "violation": "✗ violation", "drift": "✗ drift", "infra": "✗ infra",
             "reworded": "✗ reworded"}
    failed = [f for f in findings if f.verdict != "ok"]
    head = [f"## What the configs say LiteLLM and Codex CLI do, run",
            "",
            f"LiteLLM {', '.join(litellm)} and Codex CLI {', '.join(codex)} — the oldest release "
            "the files ask for and the newest — on the committed files, every lane pointed at "
            "one served by the check.",
            "",
            (f"**{len(failed)} of {len(findings)} checks failed.**" if failed else
             f"**All {len(findings)} checks held.**"),
            "",
            "| | Sentence | Run on | What happened |",
            "|---|---|---|---|"]
    rows = []
    for f in sorted(findings, key=lambda f: (f.verdict == "ok", list(SENTENCES).index(f.sentence))):
        s = SENTENCES[f.sentence]
        # A keyed profile's variable is whichever the lane's is: shown as $VAR.
        said = re.sub(r"\\(.)", r"\1", s.pattern.replace(r"\$(\w+)", "$VAR")).replace("|", "\\|")
        detail = f.detail.replace("|", "\\|")
        rows.append(f"| {marks[f.verdict]} | `{s.file}`: {said} | {f.versions} | {detail} |")
    return "\n".join(head + rows) + "\n"


def _pairs(values: list[str]) -> dict[str, str]:
    out = {}
    for v in values:
        version, _, path = v.partition("=")
        if not path:
            raise SystemExit(f"expected VERSION=PATH, got {v!r}")
        out[version.removeprefix("rust-v")] = path
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="freetier-conformance",
                                     description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("floors", help="print the oldest releases the files ask for, as KEY=VALUE lines")
    go = sub.add_parser("run", help="run the checks")
    go.add_argument("--root", type=Path, default=Path("."))
    go.add_argument("--litellm", action="append", required=True, metavar="VERSION=PATH",
                    help="a LiteLLM release and its `litellm` program; give the oldest and newest")
    go.add_argument("--codex", action="append", required=True, metavar="VERSION=PATH",
                    help="a Codex CLI release and its program; give the oldest and newest")
    go.add_argument("--summary", type=Path, help="append the Markdown summary here too")
    go.add_argument("--work", type=Path, help="keep the logs and homes here")
    args = parser.parse_args(argv)
    if args.command == "floors":
        litellm, codex = floors()
        print(f"litellm={litellm}\ncodex={codex}")
        return 0
    litellm, codex = _pairs(args.litellm), _pairs(args.codex)
    work = args.work or Path(tempfile.mkdtemp(prefix="freetier-conformance-"))
    work.mkdir(parents=True, exist_ok=True)
    findings = run_checks(args.root.resolve(), litellm, codex, work.resolve())
    order = lambda v: tuple(int(x) for x in v.split("."))  # noqa: E731
    text = summary(findings, sorted(litellm, key=order), sorted(codex, key=order))
    print(text)
    if args.summary:
        with args.summary.open("a", encoding="utf-8") as fh:
            fh.write(text)
    return 1 if any(f.verdict != "ok" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
