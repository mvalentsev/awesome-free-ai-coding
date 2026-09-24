---
layout: default
title: 'BazaarLink free tier: limits, free models, verified 2026-09-21'
description: 'OpenAI-compatible gateway to a 173-id catalog whose free page counts two models on 2026-09-14 — Qwen3.7 Flash and DeepSeek V4 Flash 0731 — beside the auto:free router. BazaarLink prints the figures on its free page: 10 requests per minute and 50 per day, ×1 for an account without credit and ×2…'
permalink: /providers/bazaarlink/
---

{% raw %}

# BazaarLink

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-21 · [bazaarlink.ai](https://bazaarlink.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway to a 173-id catalog whose free page counts two models on 2026-09-14 — Qwen3.7 Flash and DeepSeek V4 Flash 0731 — beside the auto:free router

## Free models

`qwen3.7-flash`

## Limits, in the vendor's words

BazaarLink prints the figures on its free page: 10 requests per minute and 50 per day, ×1 for an account without credit and ×2 for one that has topped up, against the models it counts as free. Past the quota "requests on free-quota models continue at the normal paid rate if you have credit; otherwise they are rate-limited until the quota resets"; everything else in the catalog is metered at list rates. The free ids are Qwen3.7 Flash and the 0731 revision of DeepSeek V4 Flash, under the catalog's own id deepseek/deepseek-v4-flash-0731free:free, described as "Rate-limited free tier." and listed on the free page as "Deepseek V4 Flash 0731free" at $0 against $0.20/$0.40, beside a metered deepseek-v4-flash-0731free twin at those rates

## Connect

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`, `deepseek/deepseek-v4-flash-0731free:free`, `auto:free`
- Note: only the two :free ids and auto:free cost nothing — the plain qwen3.7-flash beside the first is the metered twin ($0.03/$0.13 per 1M), and deepseek-v4-flash-0731free without the suffix is metered at $0.20/$0.40. auto:free picks a free model for you, and on a funded account it can fall through to the paid routing table "unless paid fallback is disabled"

## Evidence

- Probe: the models catalog at <https://api.bazaarlink.ai/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://bazaarlink.ai/free>
- Source: <https://bazaarlink.ai/en/docs>

## History

- `2026-08-17` — Free models changed: dropped deepseek-v4-flash
- `2026-08-03` — Added to the list: OpenAI-compatible gateway to 199 models, with two always-free open models and an auto:free router

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
