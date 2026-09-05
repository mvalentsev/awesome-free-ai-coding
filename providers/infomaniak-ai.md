---
layout: default
title: 'Infomaniak AI Services free tier: limits, free models, verified 2026-09-03'
description: Swiss sovereign-cloud API over open-weight models with a one-month trial wallet of one million credits, one credit per LLM token. "One million free credits allow you to test the service without commitment for one month" and "The API is billed on a credit basis. Each request consumes one credit…
permalink: /providers/infomaniak-ai/
---

{% raw %}

# Infomaniak AI Services

🎁 Trials (no card when possible) · card required · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-03 · [infomaniak.com](https://www.infomaniak.com/en/hosting/ai-services) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Swiss sovereign-cloud API over open-weight models with a one-month trial wallet of one million credits, one credit per LLM token

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

"One million free credits allow you to test the service without commitment for one month" and "The API is billed on a credit basis. Each request consumes one credit or LLM token" (support guide 2845, read 2026-09-02). The card is the gate: "A credit card is required to start using the API. An unpaid invoice will result in service suspension", and the sales FAQ adds that at account creation "we'll ask you to confirm your identity by registering a valid payment card". After the wallet, list rates in CHF per 1M tokens — Gemma 4 31B at CHF 0.20/0.40, Kimi K2.6 at CHF 0.60/3.00, Qwen3.5-122B at CHF 0.40/3.20 — billed at the end of the month, with a spending limit settable in the Manager. Models are hosted in Switzerland, and "We don't currently offer the option of training our AI Services using custom data"

## Connect

- Base URL: `https://api.infomaniak.com/2/ai/{product_id}/openai/v1`
- Key: `INFOMANIAK_AI_API_KEY` — get one at <https://manager.infomaniak.com>
- Note: {product_id} is the AI Services product id shown in the Infomaniak Manager, where the API token is created too; the million credits are a one-month trial rather than a standing lane, which is why the Free models column stays empty

## Evidence

- Probe: the page at <https://www.infomaniak.com/en/support/faq/2845/getting-started-guide-ai-services-sovereign-ai-services>, anchored on `One million free credits`, `A credit card is required to start using the API`
- Source: <https://www.infomaniak.com/en/support/faq/2845/getting-started-guide-ai-services-sovereign-ai-services>
- Source: <https://www.infomaniak.com/en/hosting/ai-services/prices>

## History

- `2026-09-03` — Added to the list: Swiss sovereign-cloud API over open-weight models with a one-month trial wallet of one million credits, one credit per LLM token

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
