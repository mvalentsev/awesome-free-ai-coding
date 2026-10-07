---
layout: default
title: 'Mistral Studio free tier: limits, free models, verified 2026-10-05'
description: Mistral's Free plan — API keys with $10 a month of included usage, shared by the API, Studio and the Vibe coding CLI, no card. The allowance is shared across Studio, API and Vibe usage in the organization. Free mode is the default for new accounts, with no credit card required. At the cap usage…
permalink: /providers/mistral-free/
last_modified_at: 2026-10-05
crumb: Mistral Studio
---

{% raw %}

# Mistral Studio free tier

🔌 LLM APIs with free tier · no card · not offered in Iran, Syria, Cuba and 1 more place · **live** — last verified by a probe on 2026-10-05 · [mistral.ai](https://mistral.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Mistral's Free plan — API keys with $10 a month of included usage, shared by the API, Studio and the Vibe coding CLI, no card

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Shared API, Studio and Vibe credit: $10/month per organization

API rate limits: Per-second requests allowance: see your account for values; Per-minute tokens allowance: see your account for values per organization per model

The allowance is shared across Studio, API and Vibe usage in the organization. Free mode is the default for new accounts, with no credit card required. At the cap usage can stop until the next billing period unless pay-as-you-go is enabled. API throughput values are visible inside the account. API calls may be used to improve Mistral services unless the Admin panel's `Anonymous improvement data` toggle is off.

## Where it is offered

Not offered in Iran, Syria, Cuba and North Korea ([source](https://legal.mistral.ai/terms/commercial-terms-of-service), read 2026-09-26). That leaves out under 0.1% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “including, as of the Effective Date, Cuba, Iran, North Korea, Syria, and the Crimea, Donetsk, and Luhansk regions of Ukraine”.

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “As stated during subscription, we may use your data (input and output) to train our artificial intelligence models. … You have the right to opt out of this program at any time.” ([source](https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models)).

## Connect

- Base URL: `https://api.mistral.ai/v1`
- Key: `MISTRAL_API_KEY` — get one at <https://console.mistral.ai/api-keys>
- Callable ids: `mistral-large-latest`, `mistral-medium-latest`
- Note: Free mode is on by default for a new account; create the key under Studio › API Keys. A key made under Code › Vibe CLI is a plan key that spends the plan's Vibe budget, which Mistral tells API users to avoid. The ids are the ones Mistral's own API quickstart and docs call

Try it from your terminal with your key in `MISTRAL_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mistral-large-latest","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://mistral.ai/pricing>, anchored on `$10 /mo in API credits`, `Test Mistral models in Studio`
- Source: <https://mistral.ai/pricing>
- Source: <https://docs.mistral.ai/admin/billing-usage/subscriptions>
- Source: <https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key>
- Source: <https://docs.mistral.ai/admin/billing-usage/usage-limits>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Free models changed: dropped mistral-medium
- `2026-07-19` — Added: Free experiment tier on La Plateforme

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
