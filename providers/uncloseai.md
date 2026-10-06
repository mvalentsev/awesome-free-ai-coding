---
layout: default
title: 'uncloseai (unturf) free tier: limits, free models, verified 2026-10-05'
description: Keyless OpenAI-compatible chat endpoint — no signup, no key, no account. The offer is a sentence — "we offer free AI services powered by multiple AI models and a TTS (text-to-speech) endpoint … embodying the principles of both free as in beer & free as in freedom" — and the inference page draws…
permalink: /providers/uncloseai/
last_modified_at: 2026-10-05
crumb: uncloseai (unturf)
---

{% raw %}

# uncloseai (unturf) free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-05 · [uncloseai.com](https://uncloseai.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Keyless OpenAI-compatible chat endpoint — no signup, no key, no account

## Free models

The row names no free model family; the ids its lane serves, where the row has them, are under Connect.

## Limits, in the vendor's words

The offer is a sentence — "we offer free AI services powered by multiple AI models and a TTS (text-to-speech) endpoint … embodying the principles of both free as in beer & free as in freedom" — and the inference page draws the line between its two text hostnames: "hermes.ai.unturf.com : public, 3 requests per second per IP" and "qwen.ai.unturf.com : API key required; anonymous traffic gets 403". Hermes is the lane, and "A hostname whose model is down gets a 502 instead of silently answering as whatever else is up": check the response before choosing a model; temporary failures do not establish a shutdown. The served id is not the one the page's own examples call, and the vendor says so — "See our Model Discovery docs to query the current model IDs being hosted" — query Model Discovery for current callable IDs instead of relying on static examples. Read 2026-10-05

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

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
