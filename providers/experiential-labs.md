---
layout: default
title: 'Experiential Labs free tier: limits, free models, verified 2026-10-19'
description: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after card verification. The monthly credit requires a one-time $1 card check. A credit is one cent. Pricing…
permalink: /providers/experiential-labs/
last_modified_at: 2026-10-19
crumb: Experiential Labs
---

{% raw %}

# Experiential Labs free tier

🧭 Aggregators (one key, many providers) · card required · requires $1 one-time card verification · **live** — last verified by a probe on 2026-10-19; the probe since has not found that evidence, and 3 misses in a row archive the row · [experientiallabs.ai](https://www.experientiallabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after card verification

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

500 credits/month per account

The monthly credit requires a one-time $1 card check. A credit is one cent. Pricing advertises no per-token charge on three models, but the Free-selected model catalog and provider plan discounts still price its chat models; independently free chat access is unconfirmed. Free decision models use a separate structured-decision API. Prompt and response storage is enabled on Free; disabling it requires a paid plan.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.experientiallabs.ai/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.experientiallabs.ai/v1`
- Key: `EXPERIENTIAL_LABS_API_KEY` — get one at <https://platform.experientiallabs.ai>
- Callable ids: `gpt-6-luna`, `deepseek-v4.1-flash`
- `gpt-6-luna`: requires $1 one-time card verification ([conditions](https://www.experientiallabs.ai/pricing))
- `deepseek-v4.1-flash`: requires $1 one-time card verification ([conditions](https://www.experientiallabs.ai/pricing))
- Note: The public catalog uses model slugs as API IDs. These chat IDs are examples for the credit balance; the Free catalog prices them despite conflicting homepage claims. Native decision models use /v1/systemone rather than chat completions. An API key is required.

Try it from your terminal with your key in `EXPERIENTIAL_LABS_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.experientiallabs.ai/v1/chat/completions \
  -H "Authorization: Bearer $EXPERIENTIAL_LABS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-6-luna","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.experientiallabs.ai/pricing>, anchored on `500 credits/mo after a one-time $1 card check`
- Source: <https://www.experientiallabs.ai/pricing>
- Source: <https://www.experientiallabs.ai/>
- Source: <https://platform.experientiallabs.ai/models>
- Source: <https://platform.experientiallabs.ai/llms.txt>
- Source: <https://api.experientiallabs.ai/api/models/gpt-6-luna>
- Source: <https://api.experientiallabs.ai/api/models/deepseek-v4.1-flash>
- Source: <https://api.experientiallabs.ai/api/models/clef-flash>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-21` — Added: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check

---

Generated from `registry.yaml` on 2026-10-23 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
