---
layout: default
title: 'uncloseai (unturf) free tier: limits, free models, verified 2026-10-08'
description: Keyless OpenAI-compatible chat endpoint — no signup, no key, no account. Hermes is the public text lane. qwen.ai.unturf.com requires a key and rejects anonymous traffic with 403. A down model's hostname returns 502; that temporary failure does not establish shutdown. Query Model Discovery for…
permalink: /providers/uncloseai/
last_modified_at: 2026-10-08
crumb: uncloseai (unturf)
---

{% raw %}

# uncloseai (unturf) free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [uncloseai.com](https://uncloseai.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Keyless OpenAI-compatible chat endpoint — no signup, no key, no account

## Free models

The row names no free model family; the ids its lane serves, where the row has them, are under Connect.

## Limits, in the vendor's words

Hermes public endpoint: 3 requests/second per IP

Hermes is the public text lane. qwen.ai.unturf.com requires a key and rejects anonymous traffic with 403. A down model's hostname returns 502; that temporary failure does not establish shutdown. Query Model Discovery for current callable IDs, since static examples can name an older ID.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://uncloseai.com/terms-of-use.html), read 2026-09-26).

## Connect

- Base URL: `https://hermes.ai.unturf.com/v1`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/uncloseai.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/uncloseai.config.toml) — copy it to `~/.codex/`, then `codex -p uncloseai`
- Callable ids: `turboderp/Qwen3.8-27B-exl3`
- Note: Send requests without an Authorization header. One model is served at a time and it rotates. Hostnames are routing labels: hermes serves a Qwen build. Query the catalog for the current callable ID.

Try it from your terminal — the lane takes no key:

```sh
curl -s https://hermes.ai.unturf.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"turboderp/Qwen3.8-27B-exl3","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://hermes.ai.unturf.com/v1/models>
- Source: <https://uncloseai.com/>
- Source: <https://uncloseai.com/inference.html>
- Source: <https://hermes.ai.unturf.com/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-30` — Added: Keyless OpenAI-compatible chat endpoint — no signup, no key, no account

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
