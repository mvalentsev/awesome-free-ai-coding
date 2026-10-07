---
layout: default
title: 'VLM Run Gateway free tier: limits, free models, verified 2026-10-05'
description: 'OpenAI-compatible gateway for vision and language models whose models on VLM Run''s own GPUs answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha. Free models: qwen3.8-27b. GPU-served models are public and anonymous; frontier models require paid access. All three IP…'
permalink: /providers/vlm-run-gateway/
last_modified_at: 2026-10-05
crumb: VLM Run Gateway
---

{% raw %}

# VLM Run Gateway free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-05 · [vlm.run](https://vlm.run) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha

## Free models

[`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/)

## Limits, in the vendor's words

Anonymous lane: 10 requests/minute; 30 requests/hour; 100 requests/day per IP

GPU-served models are public and anonymous; frontier models require paid access. All three IP windows apply together. The gateway is alpha and has a small catalog. Its published schema lacks a tools field, but a keyless tool request returned a tool call on 2026-09-17; that measurement does not make every model tool-capable. The operator is Autonomi AI Inc.; its terms render in a browser.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://vlm.run/terms-of-service), read 2026-09-26).

## Connect

- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `qwen/qwen3.8-27b`, `qwen/qwen3.5-0.8b`, `google/diffusiongemma-26b-a4b-it`
- Note: no key: a call with no Authorization header is anonymous, and `Bearer vlmrun` is the explicit anonymous form for a client that needs a non-empty key; 10 a minute, 30 an hour and 100 a day per IP. qwen/qwen3.5-0.8b and google/diffusiongemma-26b-a4b-it are the other chat models on VLM Run's GPUs and answered keyless calls on 2026-09-25, while the frontier models in the same catalog, Kimi K3 and Gemma 4 26B among them, answer `403 model_not_entitled` without a paid organization

Try it from your terminal — the lane takes no key:

```sh
curl -s https://gateway.vlm.run/v1/openai/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3.8-27b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.vlm.run/gateway/models>, anchored on `qwen/qwen3.8-27b`; ids checked in <https://gateway.vlm.run/v1/openai/models>
- Source: <https://docs.vlm.run/gateway/authentication>
- Source: <https://docs.vlm.run/gateway/rate-limits.md>
- Source: <https://docs.vlm.run/gateway/faq.md>
- Source: <https://docs.vlm.run/gateway/models>
- Source: <https://docs.vlm.run/gateway/introduction>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs, Qwen3.8 27B among them, answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
