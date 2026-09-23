---
layout: default
title: 'Mistral AI Studio free tier: limits, free models, verified 2026-09-21'
description: Mistral's Free plan — API keys with $10 a month of included usage, shared by the API, Studio and the Vibe coding CLI, no card. The Free card on mistral.ai/pricing lists "Limited coding sessions", "Test Mistral models in Studio" and "$10 /mo in API credits", where Pro's card says $30. The docs…
permalink: /providers/mistral-free/
---

{% raw %}

# Mistral AI Studio

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-21 · [mistral.ai](https://mistral.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Mistral's Free plan — API keys with $10 a month of included usage, shared by the API, Studio and the Vibe coding CLI, no card

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The Free card on mistral.ai/pricing lists "Limited coding sessions", "Test Mistral models in Studio" and "$10 /mo in API credits", where Pro's card says $30. The docs say where the allowance goes: "Mistral plans are global: the same plan applies across Vibe, Studio, and API usage", "Free mode is the default state for new accounts", and "Each Mistral plan includes monthly usage that is shared across Studio, the API, and Vibe Code. Usage consumes this monthly allowance first" — past it, usage "can stop until the next billing period" unless pay-as-you-go is switched on. The quickstart asks for nothing more: "Free mode: API access is enabled by default with no credit card required." What $10 buys is on the same page: "For example, Mistral Large costs $0.5 /M tokens in and $1.5 /M tokens out." Free mode also has the lowest rate limits — requests per second, tokens per minute and tokens per month, shown only inside the account — and API calls may be used to improve Mistral's services unless the Admin panel's `Anonymous improvement data` toggle is off.

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “As stated during subscription, we may use your data (input and output) to train our artificial intelligence models. … You have the right to opt out of this program at any time.” ([source](https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models)).

## Connect

- Base URL: `https://api.mistral.ai/v1`
- Key: `MISTRAL_API_KEY` — get one at <https://console.mistral.ai/api-keys>
- Note: Free mode is on by default for a new account; create the key under Studio › API Keys. A key made under Code › Vibe CLI is a plan key that spends the plan's Vibe budget, which Mistral tells API users to avoid

## Evidence

- Probe: the page at <https://mistral.ai/pricing>, anchored on `$10 /mo in API credits`, `Test Mistral models in Studio`
- Source: <https://mistral.ai/pricing>
- Source: <https://docs.mistral.ai/admin/billing-usage/subscriptions>
- Source: <https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key>
- Source: <https://docs.mistral.ai/admin/billing-usage/usage-limits>

## History

- `2026-08-17` — Free models changed: dropped mistral-medium
- `2026-07-19` — Added to the list: Free experiment tier on La Plateforme

---

Generated from `registry.yaml` on 2026-09-23 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
