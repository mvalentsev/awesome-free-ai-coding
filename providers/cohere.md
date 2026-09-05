---
layout: default
title: 'Cohere (trial keys) free tier: limits, free models, verified 2026-09-03'
description: Cohere Command models via free trial API keys that never expire, plus North Mini Code — a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type. Trial keys are "limited to 1,000 API calls a month" and rate-limited per model — 20 req/min on every Chat model, Command A and North…
permalink: /providers/cohere/
---

{% raw %}

# Cohere (trial keys)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [cohere.com](https://cohere.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cohere Command models via free trial API keys that never expire, plus North Mini Code — a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type

## Free models

`command-a`, `north-mini-code`

## Limits, in the vendor's words

Trial keys are "limited to 1,000 API calls a month" and rate-limited per model — 20 req/min on every Chat model, Command A and North Mini Code included, with Rerank at 10/min, Tokenize at 100/min, Embed at 2,000 inputs/min and audio transcription at 5/min. Two things that page does not say. Cohere's pricing page states that trial keys "are not permitted to be used for production or commercial purposes", and that every account "begins as a personal account and only has access to Trial API keys" — so the 1,000 calls are for evaluation, not for a product. And the North Mini Code page states that "for both trial keys and production keys, North Mini Code is free until rate limits are reached", which makes the one model here built for agentic coding the one that stays free on a paid key too (read 2026-08-14)

## Connect

- Base URL: `https://api.cohere.com/compatibility/v1`
- Key: `COHERE_API_KEY` — get one at <https://dashboard.cohere.com/api-keys>
- Callable ids: `north-mini-code-1-0`, `command-a-03-2025`
- Note: OpenAI-compatible endpoint; native API lives at https://api.cohere.com/v2. Both ids are the Model ID Cohere's own model pages publish — north-mini-code-1-0 is the free-on-any-key one

## Evidence

- Probe: the page at <https://docs.cohere.com/docs/rate-limits>, anchored on `trial keys`, `1,000`
- Source: <https://docs.cohere.com/docs/rate-limits>
- Source: <https://cohere.com/pricing>
- Source: <https://docs.cohere.com/docs/north-mini-code-1.0>
- Source: <https://docs.cohere.com/docs/models>

## History

- `2026-08-17` — Free models changed: added north-mini-code
- `2026-07-22` — Added to the list: Cohere Command models via free trial API keys that never expire

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
