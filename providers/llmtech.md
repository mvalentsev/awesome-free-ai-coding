---
layout: default
title: 'LLM Tech free tier: limits, free models, verified 2026-10-05'
description: 'EU provider of one model whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 4 concurrent requests, tool calls included, no account. Free models: qwen3.8-27b. The public trial key shares its concurrency among all callers; the daily token budget is per IP and…'
permalink: /providers/llmtech/
last_modified_at: 2026-10-05
crumb: LLM Tech
---

{% raw %}

# LLM Tech free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-05 · [llmtech.eu](https://llmtech.eu) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU provider of one model whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 4 concurrent requests, tool calls included, no account

## Free models

[`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/)

## Limits, in the vendor's words

2,000,000 tokens/day per IP. reset at 00:00 UTC

Shared trial key: 4 requests at once per key

64 requests at once shared across the endpoint

The public trial key shares its concurrency among all callers; the daily token budget is per IP and counts both prompt and completion. Its context is 131,072 tokens; personal paid keys have the full 262,144 and share the endpoint's separate inflight ceiling. Paid keys are issued by email, per token without subscription or minimum. Prompts and completions are volatile and never persisted or trained on; metadata, including IP, is retained 13 months. The sole proprietor operates in Poland, with GPUs in Italy behind a German edge.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://llmtech.eu/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “We do not use your inputs or outputs to train, fine-tune, or evaluate any model, and we do not provide them to third parties for that purpose.” ([source](https://llmtech.eu/privacy)).

## Connect

- Base URL: `https://api.llmtech.eu/v1`
- Key: `LLMTECH_API_KEY` — no account needed: the vendor prints one for anyone at <https://llmtech.eu/docs/>, `lt-trial-ba1ef28c6d32ed6980678d8d`
- Callable ids: `nvidia/Qwen3.8-27B-NVFP4`
- Note: since 2026-09-24 "Reasoning is off unless a request asks for it with reasoning_effort or enable_thinking", and `reasoning_effort` takes low, medium or xhigh. Cline lists LLM Tech among its built-in providers; Claude Code "needs a translating proxy", LiteLLM in the vendor's own example

Try it from your terminal — the key is the vendor's printed one:

```sh
curl -s https://api.llmtech.eu/v1/chat/completions \
  -H "Authorization: Bearer lt-trial-ba1ef28c6d32ed6980678d8d" \
  -H 'Content-Type: application/json' \
  -d '{"model":"nvidia/Qwen3.8-27B-NVFP4","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://llmtech.eu/docs/>, anchored on `4 concurrent requests and 2M tokens per day per address`; ids checked in <https://api.llmtech.eu/v1/models>
- Source: <https://llmtech.eu/docs/>
- Source: <https://llmtech.eu/agents/>
- Source: <https://llmtech.eu/security/>
- Source: <https://llmtech.eu/about/>
- Source: <https://api.llmtech.eu/v1/models>
- Source: <https://llmtech.eu/pricing/>
- Source: <https://llmtech.eu/changelog/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-18` — Added: EU provider of one model, Qwen3.8 27B, whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 2 concurrent requests, tool calls included, no account

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
