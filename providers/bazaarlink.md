---
layout: default
title: 'BazaarLink free tier: limits, free models, verified 2026-09-28'
description: 'OpenAI-compatible gateway to a 128-id catalog whose free page counts two models on 2026-09-27, beside the auto:free router. Free models: qwen3.7-flash. BazaarLink prints the figures on its free page, one allowance shared across the free models: "No credit: 10 RPM and 50 weighted units/day. With…'
permalink: /providers/bazaarlink/
last_modified_at: 2026-09-28
crumb: BazaarLink
---

{% raw %}

# BazaarLink free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-28 · [bazaarlink.ai](https://bazaarlink.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway to a 128-id catalog whose free page counts two models on 2026-09-27, beside the auto:free router

## Free models

[`qwen3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-flash/)

## Limits, in the vendor's words

BazaarLink prints the figures on its free page, one allowance shared across the free models: "No credit: 10 RPM and 50 weighted units/day. With credit: 20 RPM and 100 weighted units/day." Where weighted limits are on, "Longer inputs consume more daily units"; the counter resets at 00:00 UTC, beside a "Site-wide free cap: 10 RPM" and "Concurrent free requests per account: 2". "After a limit, paid use is possible only when fallback is enabled and the account has sufficient credit"; everything else in the catalog is metered at list rates. The free ids are Qwen3.7 Flash and the 0731 revision of DeepSeek V4 Flash, under the catalog's own id deepseek/deepseek-v4-flash-0731free:free, described as "Rate-limited free tier." and listed on the free page as "Deepseek V4 Flash 0731free", priced $0 beside a metered deepseek-v4-flash-0731free twin at $0.20/$0.40. Read 2026-09-27

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://bazaarlink.ai/en/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`, `deepseek/deepseek-v4-flash-0731free:free`, `auto:free`
- Note: only the two :free ids and auto:free cost nothing — the plain qwen3.7-flash beside the first is the metered twin ($0.03/$0.13 per 1M), and deepseek-v4-flash-0731free without the suffix is metered at $0.20/$0.40. auto:free picks a free model for you, and on a funded account it can fall through to the paid routing table "unless paid fallback is disabled"

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

- `2026-08-19` — Free models changed: dropped deepseek-v4-flash
- `2026-08-03` — Added: OpenAI-compatible gateway to 199 models, with two always-free open models and an auto:free router

---

Generated from `registry.yaml` on 2026-09-28 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
