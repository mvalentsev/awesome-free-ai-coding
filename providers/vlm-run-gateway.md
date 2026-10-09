---
layout: default
title: 'VLM Run Gateway free tier: limits, free models, verified 2026-10-08'
description: 'OpenAI-compatible gateway whose GPU-served vision and language models accept anonymous callers — no signup or key — in beta. Free models: qwen3.8-27b, diffusiongemma, qwen3.5-0.8b. GPU-served models are public and anonymous; frontier models require paid access. All three IP windows apply together…'
permalink: /providers/vlm-run-gateway/
last_modified_at: 2026-10-09
crumb: VLM Run Gateway
---

{% raw %}

# VLM Run Gateway free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [vlm.run](https://vlm.run) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway whose GPU-served vision and language models accept anonymous callers — no signup or key — in beta

## Free models

[`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), [`diffusiongemma`](https://mvalentsev.github.io/awesome-free-ai-coding/models/diffusiongemma/), `qwen3.5-0.8b`

## Limits, in the vendor's words

Anonymous lane: 10 requests/minute; 30 requests/hour; 100 requests/day per IP

GPU-served models are public and anonymous; frontier models require paid access. All three IP windows apply together and are shared by callers behind the same NAT or proxy. The gateway is beta; anonymous access is intended for evaluation. The operator is Autonomi AI Inc.; its terms render in a browser.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://vlm.run/terms-of-service), read 2026-09-26).

## Connect

- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `qwen/qwen3.8-27b`, `qwen/qwen3.5-0.8b`, `google/diffusiongemma-26b-a4b-it`
- Note: Omit Authorization; generic bearer tokens return 401. Checked 2026-10-09: `Bearer vlmrun` also worked despite docs saying unrecognized tokens are invalid. Only qwen/qwen3.8-27b advertises tools; tools on the other two IDs returned 500. Ordinary chat completed on all three; streaming completed on 0.8B and DiffusionGemma. OpenCode 2.0.24 requested 32,000 output tokens for the 27B ID: HTTP 400, reply budget 16,000. The catalog omits that output limit. A complete agent tool cycle was not established.

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

- `2026-10-09` — Free models changed: added diffusiongemma, qwen3.5-0.8b
- `2026-09-17` — Added: OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs, Qwen3.8 27B among them, answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
