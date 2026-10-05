---
layout: default
title: 'Experiential Labs free tier: limits, free models, verified 2026-10-05'
description: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after card verification. The Free plan is "500 credits a month once you verify a card (a one-time $1 charge…
permalink: /providers/experiential-labs/
last_modified_at: 2026-10-05
crumb: Experiential Labs
---

{% raw %}

# Experiential Labs free tier

🧭 Aggregators (one key, many providers) · card required · requires $1 one-time card verification · **live** — last verified by a probe on 2026-10-05 · [experientiallabs.ai](https://www.experientiallabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after card verification

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

The Free plan is "500 credits a month once you verify a card (a one-time $1 charge, added to your balance)". A credit is a cent ("Flat 1¢ per credit, 0% token markup"), spent at list price: "Route on credits at each provider’s list price with nothing on top". In the public catalog with Free selected, GPT-6 Luna is 75% off and Qwen3.8 27B / DeepSeek V4 Flash are 50% off, not individually free; the 100% discounts belong to Ultra. Jev is marked Free but its entry lists no tool or streaming support. "Prompt and response storage off" is a paid-plan feature; prompts on the Free plan are stored. Read 2026-10-01

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

Generated from `registry.yaml` on 2026-10-05 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
