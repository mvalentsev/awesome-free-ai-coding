---
layout: default
title: 'Experiential Labs free tier: limits, free models, verified 2026-10-26'
description: Open-source AI gateway backed by Y Combinator; its pricing page advertises a recurring Free core-model pool, separate from paid wallet credits. The pricing page advertises Luna and DeepSeek chat in the Free core pool, but their current model catalog applies zero-price plan discounts only on paid…
permalink: /providers/experiential-labs/
last_modified_at: 2026-10-29
crumb: Experiential Labs
---

{% raw %}

# Experiential Labs free tier

🧭 Aggregators (one key, many providers) · card required · requires $1 one-time card verification · **live** — last verified by a probe on 2026-10-26 · [experientiallabs.ai](https://www.experientiallabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source AI gateway backed by Y Combinator; its pricing page advertises a recurring Free core-model pool, separate from paid wallet credits

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Free core models: 10 requests/minute; 250,000 tokens/minute; 1,000,000 tokens/day per service plan. reset at 00:00 UTC

The pricing page advertises Luna and DeepSeek chat in the Free core pool, but their current model catalog applies zero-price plan discounts only on paid plans. This eligibility conflict remains unresolved. The earlier Astra and Fable promotional free tiers have ended. Free has no general monthly credits. A temporary $1 card verification is refunded rather than credited to the wallet. Clef and Luna Decisions use decision APIs rather than chat. Free prompt and response storage cannot be disabled without a paid plan.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.experientiallabs.ai/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.experientiallabs.ai/v1`
- Key: `EXPERIENTIAL_LABS_API_KEY` — get one at <https://platform.experientiallabs.ai>
- Callable ids: none listed — Current pricing advertises Free core chat, but the model catalog discounts it only on paid plans; confirm eligible IDs in your account.
- Note: An API key is required. There is no ready-to-use free chat ID listed while the pricing-page core offers conflict with the model catalog. The earlier Astra and Fable :free promotions have ended; plain model IDs can spend paid credit. Confirm account-specific eligibility before calling a model.

Check your key from your terminal — with it in `EXPERIENTIAL_LABS_API_KEY`, the vendor's catalog lists the models it can call:

```sh
curl -s https://api.experientiallabs.ai/v1/models \
  -H "Authorization: Bearer $EXPERIENTIAL_LABS_API_KEY"
```

## Evidence

- Probe: the page at <https://www.experientiallabs.ai/pricing>, anchored on `Free core models share one pool`, `1M input and output tokens a day`
- Source: <https://www.experientiallabs.ai/pricing>
- Source: <https://www.experientiallabs.ai/>
- Source: <https://platform.experientiallabs.ai/models>
- Source: <https://platform.experientiallabs.ai/llms.txt>
- Source: <https://api.experientiallabs.ai/api/models/gpt-6-luna>
- Source: <https://api.experientiallabs.ai/api/models/deepseek-v4.1-flash>
- Source: <https://api.experientiallabs.ai/api/models/clef-flash>
- Source: <https://api.experientiallabs.ai/api/models/gpt-6-astra>
- Source: <https://api.experientiallabs.ai/api/models/claude-fable-5.1>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-26` — Restored: Open-source AI gateway backed by Y Combinator with recurring model-specific free quotas after a settled payment, separate from its paid credit wallet
- `2026-10-26` — Archived: delisted on 2026-10-26: no confirmed free chat allowance after the general monthly credit was withdrawn
- `2026-09-21` — Added: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check

---

Generated from `registry.yaml` on 2026-10-30 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
