---
layout: default
title: 'Cloudflare Workers AI free tier: limits, free models, verified 2026-09-24'
description: 10k neurons/day free. Cloudflare's free allocation "allows anyone to use a total of 10,000 Neurons per day at no charge", which at its own $0.011 per 1,000 Neurons is about $0.11 of inference a day. "All limits reset daily at 00:00 UTC", and past the cap "further operations will fail with an…
permalink: /providers/cloudflare-workers-ai/
last_modified_at: 2026-09-26
crumb: Cloudflare Workers AI
---

{% raw %}

# Cloudflare Workers AI free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [cloudflare.com](https://www.cloudflare.com/products/workers-ai/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

10k neurons/day free

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Cloudflare's free allocation "allows anyone to use a total of 10,000 Neurons per day at no charge", which at its own $0.011 per 1,000 Neurons is about $0.11 of inference a day. "All limits reset daily at 00:00 UTC", and past the cap "further operations will fail with an error" rather than being billed. Rate limits are per task type — 300 requests per minute for Text Generation. Three catalog models sit outside the free lane whatever the neuron count: the same page notes that @cf/moonshotai/kimi-k2.6, @cf/moonshotai/kimi-k2.7-code and @cf/zai-org/glm-5.2 "require a paid billing method" (read 2026-08-14)

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.cloudflare.com/terms/), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Cloudflare does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services” ([source](https://developers.cloudflare.com/workers-ai/platform/data-usage/)).

## Connect

- Base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1`
- Key: `CLOUDFLARE_WORKERS_AI_API_KEY` — get one at <https://dash.cloudflare.com/profile/api-tokens>
- Callable ids: `@cf/zai-org/glm-5.3-flash`, `@cf/qwen/qwen3.8-27b`, `@cf/meta/llama-4-scout-17b-16e-instruct`
- Note: substitute {account_id} with your Cloudflare account ID

## Evidence

- Probe: the page at <https://developers.cloudflare.com/workers-ai/platform/pricing/>, anchored on `10,000 neurons per day`, `free allocation`
- Source: <https://developers.cloudflare.com/workers-ai/platform/pricing/>
- Source: <https://developers.cloudflare.com/workers-ai/platform/limits/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped llama-4
- `2026-07-19` — Added: 10k neurons/day free

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
