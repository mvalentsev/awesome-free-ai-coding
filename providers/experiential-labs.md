---
layout: default
title: 'Experiential Labs free tier: limits, free models, verified 2026-10-08'
description: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after card verification. Free requires a one-time $1 card-verification charge, added to the balance. Credits…
permalink: /providers/experiential-labs/
last_modified_at: 2026-10-08
crumb: Experiential Labs
---

{% raw %}

# Experiential Labs free tier

🧭 Aggregators (one key, many providers) · card required · requires $1 one-time card verification · **live** — last verified by a probe on 2026-10-08 · [experientiallabs.ai](https://www.experientiallabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after card verification

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

500 credits/month per account

Free requires a one-time $1 card-verification charge, added to the balance. Credits spend at provider list prices with no token markup; a credit is one cent. Free catalog discounts are reductions from price, not individually free models. Jev is marked Free but lists no tool or streaming support. Prompt and response storage is enabled on Free; disabling it requires a paid plan.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.experientiallabs.ai/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.experientiallabs.ai/v1`
- Key: `EXPERIENTIAL_LABS_API_KEY` — get one at <https://platform.experientiallabs.ai>
- Callable ids: none listed — its /v1/models answers only a gateway key, and no page it publishes says which name a request carries
- Note: the catalog at /v1/models answers only a gateway key; the model list with prices is public at platform.experientiallabs.ai/models

Check your key from your terminal — with it in `EXPERIENTIAL_LABS_API_KEY`, the vendor's catalog lists the models it can call:

```sh
curl -s https://api.experientiallabs.ai/v1/models \
  -H "Authorization: Bearer $EXPERIENTIAL_LABS_API_KEY"
```

## Evidence

- Probe: the page at <https://www.experientiallabs.ai/pricing>, anchored on `500 credits a month once you verify a card`
- Source: <https://www.experientiallabs.ai/pricing>
- Source: <https://www.experientiallabs.ai/>
- Source: <https://platform.experientiallabs.ai/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-21` — Added: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
