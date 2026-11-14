---
layout: default
title: 'BazaarLink free tier: limits, free models, verified 2026-11-12'
description: 'OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router. Free models: nemotron-3.5-lightning, deepseek-v4-flash, qwen3.7-flash. The free models share each account''s daily weighted allowance, reset at 00:00 UTC. Longer inputs can consume more units. Account…'
permalink: /providers/bazaarlink/
last_modified_at: 2026-11-12
crumb: BazaarLink
model_sort: true
---

{% raw %}

# BazaarLink free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-11-12 · [bazaarlink.ai](https://bazaarlink.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router

## Free models

<span data-model-sort-inline><span data-model-family="nemotron-3.5-lightning">[`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/)</span>, <span data-model-family="deepseek-v4-flash">[`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/)</span>, <span data-model-family="qwen3.7-flash">[`qwen3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-flash/)</span></span>

## Limits, in the vendor's words

Without credit: 10 requests/rolling minute; 60 weighted units/day per account

With credit: 20 requests/rolling minute; 120 weighted units/day per account

Free models: 2 requests at once per account

Free models: 20 requests/minute shared across the endpoint

Additional IP guard: Requests allowance: amount not published (period not published) per IP

The free models share each account's daily weighted allowance, reset at 00:00 UTC. Longer inputs can consume more units. Account concurrency and the site-wide rate also apply. The platform grants free eligibility per model; a regular ID can have a free quota alongside its paid price. After the free quota, paid fallback needs an enabled setting and sufficient account credit.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://bazaarlink.ai/en/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `nvidia/nemotron-3.5-lightning-free:free`, `deepseek/deepseek-v4-flash-0731free:free`, `qwen/qwen3.7-flash:free`, `auto:free`, `stealth/glyph-cluster:free`
- Note: The listed :free routes use the shared free allowance. auto:free uses its own free routing pool and can use paid routing on a funded account "unless paid fallback is disabled". Glyph Cluster is a stealth model with an undisclosed identity.

Try it from your terminal with your key in `BAZAARLINK_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.bazaarlink.ai/v1/chat/completions \
  -H "Authorization: Bearer $BAZAARLINK_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek/deepseek-v4-flash-0731free:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.bazaarlink.ai/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://bazaarlink.ai/free>
- Source: <https://bazaarlink.ai/en/docs>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-10` — Free models changed: added qwen3.7-flash
- `2026-11-02` — Free models changed: added nemotron-3.5-lightning
- `2026-10-19` — Free models changed: dropped qwen3.7-flash
- `2026-09-28` — Free models changed: added deepseek-v4-flash
- `2026-08-19` — Free models changed: dropped deepseek-v4-flash
- `2026-08-03` — Added: OpenAI-compatible gateway to 199 models, with two always-free open models and an auto:free router

---

Generated from `registry.yaml` on 2026-11-14 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
