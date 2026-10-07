---
layout: default
title: 'BazaarLink free tier: limits, free models, verified 2026-10-05'
description: 'OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router. Free models: qwen3.7-flash, deepseek-v4-flash. The free models share each account''s daily weighted allowance, reset at 00:00 UTC. Longer inputs can consume more units. Account concurrency and the…'
permalink: /providers/bazaarlink/
last_modified_at: 2026-10-05
crumb: BazaarLink
---

{% raw %}

# BazaarLink free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-05 · [bazaarlink.ai](https://bazaarlink.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router

## Free models

[`qwen3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-flash/), [`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/)

## Limits, in the vendor's words

Without credit: 10 requests/minute; 60 weighted units/day per account

With credit: 20 requests/minute; 120 weighted units/day per account

Free models: 2 requests at once per account

Free models: 15 requests/minute shared across the endpoint

The free models share each account's daily weighted allowance, reset at 00:00 UTC. Longer inputs can consume more units. Account concurrency and the site-wide rate also apply. Paid fallback happens only when enabled and the account has sufficient credit. Free IDs and their metered twins are separate catalog routes.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://bazaarlink.ai/en/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`, `deepseek/deepseek-v4-flash-0731free:free`, `auto:free`
- Note: only the two :free ids and auto:free cost nothing — the plain qwen3.7-flash beside the first is the metered twin (from $0.03/$0.13 per 1M, with higher long-prompt tiers), and deepseek-v4-flash-0731free without the suffix is metered at $0.20/$0.40. auto:free picks a free model for you, and on a funded account it can fall through to the paid routing table "unless paid fallback is disabled"

Try it from your terminal with your key in `BAZAARLINK_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.bazaarlink.ai/v1/chat/completions \
  -H "Authorization: Bearer $BAZAARLINK_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3.7-flash:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.bazaarlink.ai/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://bazaarlink.ai/free>
- Source: <https://bazaarlink.ai/en/docs>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-28` — Free models changed: added deepseek-v4-flash
- `2026-08-19` — Free models changed: dropped deepseek-v4-flash
- `2026-08-03` — Added: OpenAI-compatible gateway to 199 models, with two always-free open models and an auto:free router

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
