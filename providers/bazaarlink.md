---
layout: default
title: 'BazaarLink free tier: limits, free models, verified 2026-09-03'
description: 'OpenAI-compatible gateway to a 183-id catalog with exactly two zero-priced rows — Qwen3.7 Flash and the auto:free router. BazaarLink prints the figures on its free page: 10 requests per minute and 50 per day, ×1 for an account without credit and ×2 for one that has topped up, against the single…'
permalink: /providers/bazaarlink/
---

{% raw %}

# BazaarLink

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [bazaarlink.ai](https://bazaarlink.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway to a 183-id catalog with exactly two zero-priced rows — Qwen3.7 Flash and the auto:free router

## Free models

`qwen3.7-flash`

## Limits, in the vendor's words

BazaarLink prints the figures on its free page: 10 requests per minute and 50 per day, ×1 for an account without credit and ×2 for one that has topped up, against the single model it counts as free ("Free Models Right Now: 1", read 2026-08-19). Past the quota "requests on free-quota models continue at the normal paid rate if you have credit; otherwise they are rate-limited until the quota resets"; everything else in the catalog is metered at list rates. The second free id this entry was registered for is gone — deepseek/deepseek-v4-flash:free left between the 2026-08-13 and 2026-08-17 probes, and only the metered deepseek-v4-flash remains

## Connect

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`, `auto:free`
- Note: only the :free id and auto:free cost nothing — the plain qwen3.7-flash beside it in the catalog is the metered twin ($0.03/$0.13 per 1M). auto:free picks a free model for you, and on a funded account it can fall through to the paid routing table "unless paid fallback is disabled"

## Evidence

- Probe: the models catalog at <https://api.bazaarlink.ai/v1/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://bazaarlink.ai/free>
- Source: <https://bazaarlink.ai/en/docs>

## History

- `2026-08-17` — Free models changed: dropped deepseek-v4-flash
- `2026-08-03` — Added to the list: OpenAI-compatible gateway to 199 models, with two always-free open models and an auto:free router

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
