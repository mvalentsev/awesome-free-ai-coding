---
layout: default
title: 'Fireworks AI free tier: limits, free models, verified 2026-09-24'
description: Serverless inference on open-weight models — Kimi K3, GLM 5.3, DeepSeek V4.1 Flash among them — with a one-time $1 of credit that is spent without a card, at 10 requests a minute until a payment method is added. The pricing page offers "Get started with $1 in free credits", and the billing FAQ…
permalink: /providers/fireworks-ai/
last_modified_at: 2026-09-26
crumb: Fireworks AI
---

{% raw %}

# Fireworks AI free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [fireworks.ai](https://fireworks.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Serverless inference on open-weight models — Kimi K3, GLM 5.3, DeepSeek V4.1 Flash among them — with a one-time $1 of credit that is spent without a card, at 10 requests a minute until a payment method is added

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

The pricing page offers "Get started with $1 in free credits", and the billing FAQ says what happens to an account "Without payment method" when the dollar runs out: "Your account will be suspended until you add a payment method". Until then the account quotas put "No payment method or no credits" at 10 RPM, against 6,000 RPM with a payment method and credits. No page gives the dollar an expiry or makes it recur, and beyond it Fireworks "operates on a pre-paid credits billing system". The dollar buys list prices, per 1M input and output tokens: DeepSeek V4.1 Flash $0.22 and $0.66, GLM 5.3 Flash $0.15 and $0.50, MiniMax M3 $0.30 and $1.20, Kimi K3 $3.00 and $15.00 — about 4.5M input tokens on DeepSeek V4.1 Flash, about 330K on Kimi K3. Read 2026-09-17

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://fireworks.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “No AI Training on Your Data: We do not use your prompts, training data, or API inputs to train or improve our AI models without your explicit opt-in.” ([source](https://fireworks.ai/privacy-policy)).

## Connect

- Base URL: `https://api.fireworks.ai/inference/v1`
- Key: `FIREWORKS_AI_API_KEY` — get one at <https://app.fireworks.ai/settings/users/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.fireworks.ai/inference`
- Callable ids: `accounts/fireworks/models/deepseek-v4p1-flash`, `accounts/fireworks/models/glm-5p3-flash`, `accounts/fireworks/models/minimax-m3`, `accounts/fireworks/models/glm-5p3`, `accounts/fireworks/models/kimi-k3`
- Note: ids are accounts/fireworks/models/ plus the slug the serverless pricing page links, read 2026-09-17; /inference/v1/models answers 401 without a key, so none is read off a catalog. The quickstart gives the Anthropic SDK base_url https://api.fireworks.ai/inference, which is Claude Code's ANTHROPIC_BASE_URL, the client appending /v1/messages

## Evidence

- Probe: the page at <https://fireworks.ai/pricing>, anchored on `Get started with $1 in free credits`
- Source: <https://fireworks.ai/pricing>
- Source: <https://docs.fireworks.ai/faq-new/billing-pricing/what-happens-when-i-finish-my-1-dollar-credit>
- Source: <https://docs.fireworks.ai/guides/quotas_usage/account-quotas>
- Source: <https://docs.fireworks.ai/serverless/pricing>
- Source: <https://docs.fireworks.ai/getting-started/quickstart>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: Serverless inference on open-weight models — Kimi K3, GLM 5.3, DeepSeek V4.1 Flash among them — with a one-time $1 of credit that is spent without a card, at 10 requests a minute until a payment method is added

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
