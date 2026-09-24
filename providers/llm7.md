---
layout: default
title: 'LLM7.io free tier: limits, free models, verified 2026-09-24'
description: OpenAI-compatible API with an anonymous tier — no account, no key — of 500,000 tokens a day on its turbo models, GLM 5.3 Flash, MiniMax M2.7 and Codestral among them; a free token doubles it. The limits page gives anonymous callers 1 request a second, 10 a minute and 60 an hour, and "500,000…
permalink: /providers/llm7/
---

{% raw %}

# LLM7.io

🔌 LLM APIs with free tier · no card · provisional — added on 2026-09-16, a regular row from the first probe it passes on or after 2026-09-30 · **live** — last verified by a probe on 2026-09-24 · [llm7.io](https://llm7.io) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API with an anonymous tier — no account, no key — of 500,000 tokens a day on its turbo models, GLM 5.3 Flash, MiniMax M2.7 and Codestral among them; a free token doubles it

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The limits page gives anonymous callers 1 request a second, 10 a minute and 60 an hour, and "500,000 tokens per 24 hours"; a free token from dash.llm7.io raises that to 40 a minute, 100 an hour and "1,000,000 tokens per 24 hours", and Pro is $12 a month. The free models are a tier of the catalog — "`turbo` models are fast models available to anonymous and free-token users" — though two turbo rows marked usage_based_only, DeepSeek V4 Flash and Gemini 3.1 Flash Lite, answered a keyless call with 401 `Missing API key.` The operator publishes terms, last updated 9 August 2026, and names no upstream for any model. Read 2026-09-16

## Connect

- Base URL: `https://api.llm7.io/v1`
- Key: none — the lane is anonymous
- Callable ids: `GLM-5.3-Flash`, `minimax-m2.7`, `codestral-latest`, `mistral-Nemo-Instruct-2407`
- Note: no key for the anonymous tier — OpenAI SDKs want some api_key, and the quickstart passes `unused`. The ids listed are the turbo rows that answered a keyless call on 2026-09-16; DeepSeek-V4-Flash-0731 and gemini-3.1-flash-lite need a token

## Evidence

- Probe: the page at <https://docs.llm7.io/limits.md>, anchored on `500,000 tokens per 24 hours`, `1,000,000 tokens per 24 hours`; ids checked in <https://api.llm7.io/v1/models>
- Source: <https://docs.llm7.io/limits.md>
- Source: <https://docs.llm7.io/guides/models.md>
- Source: <https://docs.llm7.io/quickstart.md>
- Source: <https://github.com/chigwell/llm7.io/blob/main/TERMS.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-16` — Added: OpenAI-compatible API with an anonymous tier — no account, no key — of 500,000 tokens a day on its turbo models, GLM 5.3 Flash, MiniMax M2.7 and Codestral among them; a free token doubles it

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
