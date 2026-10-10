---
layout: default
title: 'Cloudflare Workers AI free tier: limits, free models, verified 2026-10-08'
description: '10k neurons/day free. Past the free allowance "further operations will fail with an error". Some models require a paid billing method even if neurons remain: Kimi K2.6, Kimi K2.7 Code, GLM 5.2, GLM 5.3, GLM 5.3 Flash, DeepSeek V4 Flash 0731 and DeepSeek V4 Pro 0813. The free text-generation rate…'
permalink: /providers/cloudflare-workers-ai/
last_modified_at: 2026-10-08
crumb: Cloudflare Workers AI
---

{% raw %}

# Cloudflare Workers AI free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [cloudflare.com](https://www.cloudflare.com/products/workers-ai/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

10k neurons/day free

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

10,000 neurons/day per account. All limits reset daily at 00:00 UTC.

Free text generation: 300 requests/minute per account

Past the free allowance "further operations will fail with an error". Some models require a paid billing method even if neurons remain: Kimi K2.6, Kimi K2.7 Code, GLM 5.2, GLM 5.3, GLM 5.3 Flash, DeepSeek V4 Flash 0731 and DeepSeek V4 Pro 0813. The free text-generation rate does not apply to models requiring the Workers Paid plan.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.cloudflare.com/terms/), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Cloudflare does not use your Customer Content to (1) train any AI models made available on Workers AI or (2) improve any Cloudflare or third-party services” ([source](https://developers.cloudflare.com/workers-ai/platform/data-usage/)).

## Connect

- Base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1`
- Key: `CLOUDFLARE_WORKERS_AI_API_KEY` — get one at <https://dash.cloudflare.com/profile/api-tokens>
- Callable ids: `@cf/qwen/qwen3.8-27b`, `@cf/meta/llama-4-scout-17b-16e-instruct`
- Note: substitute {account_id} with your Cloudflare account ID

Try it from your terminal with your key in `CLOUDFLARE_WORKERS_AI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions \
  -H "Authorization: Bearer $CLOUDFLARE_WORKERS_AI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"@cf/qwen/qwen3.8-27b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://developers.cloudflare.com/workers-ai/platform/pricing/>, anchored on `10,000 neurons per day`, `free allocation`
- Source: <https://developers.cloudflare.com/workers-ai/platform/pricing/>
- Source: <https://developers.cloudflare.com/workers-ai/platform/limits/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped llama-4
- `2026-07-19` — Added: 10k neurons/day free

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
