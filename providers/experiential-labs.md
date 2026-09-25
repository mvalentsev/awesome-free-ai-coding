---
layout: default
title: 'Experiential Labs free tier: limits, free models, verified 2026-09-24'
description: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check. The Free plan is "500 credits a month once you verify a card (a one-time $1…
permalink: /providers/experiential-labs/
---

{% raw %}

# Experiential Labs

🧭 Aggregators (one key, many providers) · card required · provisional — added on 2026-09-21, a regular row from the first probe it passes on or after 2026-10-05 · **live** — last verified by a probe on 2026-09-24 · [experientiallabs.ai](https://www.experientiallabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

The Free plan is "500 credits a month once you verify a card (a one-time $1 charge, credited to your balance)", a credit being a cent ("2,000 credits / month · 1¢ each" on Pro), spent at list price: "Route on credits at each provider’s list price with nothing on top". So the $5 buys what the catalog prices — Claude Opus 5 at $5 in / $25 out per 1M tokens. The one model its list marks Free is TypeSafe's Jev, whose catalog entry supports neither tools nor streaming, so not one to code with, and the other promotions are discounts, GPT-6 Luna at 75% off. "Prompt-capture opt-out" is a Pro feature, so prompts on the free plan are captured. Read 2026-09-25

## Connect

- Base URL: `https://api.experientiallabs.ai/v1`
- Key: `EXPERIENTIAL_LABS_API_KEY` — get one at <https://platform.experientiallabs.ai>
- Note: the catalog at /v1/models answers only a gateway key; the model list with prices is public at platform.experientiallabs.ai/models

## Evidence

- Probe: the page at <https://www.experientiallabs.ai/pricing>, anchored on `500 credits a month once you verify a card`
- Source: <https://www.experientiallabs.ai/pricing>
- Source: <https://www.experientiallabs.ai/>
- Source: <https://platform.experientiallabs.ai/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-21` — Added: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check

---

Generated from `registry.yaml` on 2026-09-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
