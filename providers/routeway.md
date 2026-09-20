---
layout: default
title: 'Routeway free tier: limits, free models, verified 2026-09-17'
description: OpenAI-compatible gateway whose :free lane rotates — three zero-priced ids on 2026-09-16, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 257 metered rows in the same catalog. Free models — every id ending :free — are capped at 5 requests per minute and 200 per day and…
permalink: /providers/routeway/
---

{% raw %}

# Routeway

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-17 · [routeway.ai](https://routeway.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway whose :free lane rotates — three zero-priced ids on 2026-09-16, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 257 metered rows in the same catalog

## Free models

`deepseek-v4-flash`, `minimax-m2.7`, `muse-glimmer-30b`

## Limits, in the vendor's words

Free models — every id ending :free — are capped at 5 requests per minute and 200 per day and answer 429 past either; the pay-as-you-go ids beside them have no API-level rate limits, only edge DDoS protection (docs.routeway.ai, read 2026-08-30). The lane itself rotates: ten zero-priced ids on 2026-08-14, three on 2026-09-16, with ids joining and leaving within days while their metered twins stay. The gateway publishes no legal entity or terms of service and is supported through Discord alone: a fallback lane, not a dependency

## Connect

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Callable ids: `muse-glimmer-30b:free`, `deepseek-v4-flash:free`, `minimax-m2.7:free`
- Note: the three :free ids are every zero-priced row in the catalog on 2026-09-16, all marked available; only the :free suffix is free, and the same catalog meters Claude and GPT at list rates. An id joins the Models column only after two weeks in the lane, since every family there is re-checked on every run and three misses archive the row

## Evidence

- Probe: the models catalog at <https://api.routeway.ai/v1/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://api.routeway.ai/v1/models>
- Source: <https://routeway.ai/docs>
- Source: <https://docs.routeway.ai/getting-started/rate-limits>

## History

- `2026-09-17` — Free models changed: added deepseek-v4-flash, minimax-m2.7
- `2026-09-14` — Free models changed: added muse-glimmer-30b
- `2026-09-07` — Free models changed: dropped gemma-4, gpt-oss
- `2026-08-31` — Free models changed: dropped llama-3.3, step-3.7-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash
- `2026-08-05` — Free models changed: added gemma-4, llama-3.3
- `2026-08-05` — Added to the list: OpenAI-compatible gateway whose catalog carries eleven live :free ids priced at zero — gpt-oss-120b, Ling 3.0 Flash, Step 3.7 Flash, Gemma 4 and the Llama 3.x line — beside a metered 100+ model catalog

---

Generated from `registry.yaml` on 2026-09-20 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
