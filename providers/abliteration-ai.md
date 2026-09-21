---
layout: default
title: 'abliteration.ai free tier: limits, free models, verified 2026-09-21'
description: 'OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card. The pricing FAQ: "You can start with a one-credit free preview and no credit card. Sign in to use the Playground or API, inspect…'
permalink: /providers/abliteration-ai/
---

{% raw %}

# abliteration.ai

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [abliteration.ai](https://abliteration.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The pricing FAQ: "You can start with a one-credit free preview and no credit card. Sign in to use the Playground or API, inspect the available models, and add prepaid credit or a monthly plan when you are ready." No page says what a credit is worth; the credits endpoint reports the balance as "Total credits available to the organization, in USD". Usage is billed per token — abliterated-model $1.00 in and $3.00 out per million, abliterated-model-large-v2 and abliterated-model-large $3.00 and $5.00 — and plans start at $20 a month. The models "think before answering by default", stream and call tools, and abliterated-model-large-v2 is "Derived from the open-weight GLM-5.3 model, further abliterated and fine-tuned by Abliteration AI". The operator is Abliteration AI, Inc. Read 2026-09-17

## Connect

- Base URL: `https://api.abliteration.ai/v1`
- Key: `ABLITERATION_AI_API_KEY` — get one at <https://abliteration.ai/console>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.abliteration.ai`
- Callable ids: `abliterated-model-large-v2`, `abliterated-model`
- Note: ids are the docs' models page, read 2026-09-17; /v1/models answers 401 without a key. The Claude Code guide sets ANTHROPIC_BASE_URL=https://api.abliteration.ai with an ak_ key as ANTHROPIC_AUTH_TOKEN, the client appending /v1/messages

## Evidence

- Probe: the page at <https://abliteration.ai/pricing>, anchored on `You can start with a one-credit free preview and no credit card`
- Source: <https://abliteration.ai/pricing>
- Source: <https://docs.abliteration.ai/models.md>
- Source: <https://docs.abliteration.ai/pricing.md>
- Source: <https://docs.abliteration.ai/api-reference/credits/get-the-credit-balance-for-the-api-keys-organization.md>
- Source: <https://docs.abliteration.ai/integrations/claude-code.md>

## History

- `2026-09-21` — Added to the list: OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
