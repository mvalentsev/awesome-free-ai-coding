---
layout: default
title: 'abliteration.ai free tier: limits, free models, verified 2026-09-24'
description: 'OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card. The pricing FAQ: "You can start with a one-credit free preview and no credit card. Sign in to use the Playground or API, inspect…'
permalink: /providers/abliteration-ai/
last_modified_at: 2026-09-24
crumb: abliteration.ai
---

{% raw %}

# abliteration.ai free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [abliteration.ai](https://abliteration.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

The pricing FAQ: "You can start with a one-credit free preview and no credit card. Sign in to use the Playground or API, inspect the available models, and add prepaid credit or a monthly plan when you are ready." No page says what a credit is worth; the credits endpoint reports the balance as "Total credits available to the organization, in USD". Usage is billed per token — abliterated-model $1.00 in and $3.00 out per million, abliterated-model-large-v2 and abliterated-model-large $3.00 and $5.00 — and plans start at $20 a month. The models "think before answering by default", stream and call tools, and abliterated-model-large-v2 is "Derived from the open-weight GLM-5.3 model, further abliterated and fine-tuned by Abliteration AI". The operator is Abliteration AI, Inc. Read 2026-09-17

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Prompts, completions, and images are processed in memory and never stored by default. They are never used to train or fine-tune any model.” ([source](https://abliteration.ai/data-handling)).

## Connect

- Base URL: `https://api.abliteration.ai/v1`
- Key: `ABLITERATION_AI_API_KEY` — get one at <https://abliteration.ai/console>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.abliteration.ai`
- Callable ids: `abliterated-model-large-v2`, `abliterated-model`, `abliterated-model-large`
- Note: ids are the three the docs' models page serves, read 2026-09-23 — abliterated-model-large the previous large model, from GLM-5.2; /v1/models answers 401 without a key. The Claude Code guide sets ANTHROPIC_BASE_URL=https://api.abliteration.ai with an ak_ key as ANTHROPIC_AUTH_TOKEN, the client appending /v1/messages

## Evidence

- Probe: the page at <https://abliteration.ai/pricing>, anchored on `You can start with a one-credit free preview and no credit card`
- Source: <https://abliteration.ai/pricing>
- Source: <https://docs.abliteration.ai/models.md>
- Source: <https://docs.abliteration.ai/pricing.md>
- Source: <https://docs.abliteration.ai/api-reference/credits/get-the-credit-balance-for-the-api-keys-organization.md>
- Source: <https://docs.abliteration.ai/integrations/claude-code.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
