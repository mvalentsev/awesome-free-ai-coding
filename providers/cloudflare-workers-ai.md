---
layout: default
title: 'Cloudflare Workers AI free tier: limits, free models, verified 2026-09-03'
description: 10k neurons/day free. Cloudflare's free allocation "allows anyone to use a total of 10,000 Neurons per day at no charge", which at its own $0.011 per 1,000 Neurons is about $0.11 of inference a day. "All limits reset daily at 00:00 UTC", and past the cap "further operations will fail with an…
permalink: /providers/cloudflare-workers-ai/
---

{% raw %}

# Cloudflare Workers AI

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [workers.cloudflare.com](https://workers.cloudflare.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

10k neurons/day free

## Free models

`llama-4`

## Limits, in the vendor's words

Cloudflare's free allocation "allows anyone to use a total of 10,000 Neurons per day at no charge", which at its own $0.011 per 1,000 Neurons is about $0.11 of inference a day. "All limits reset daily at 00:00 UTC", and past the cap "further operations will fail with an error" rather than being billed. Rate limits are per task type — 300 requests per minute for Text Generation. Three catalog models sit outside the free lane whatever the neuron count: the same page notes that @cf/moonshotai/kimi-k2.6, @cf/moonshotai/kimi-k2.7-code and @cf/zai-org/glm-5.2 "require a paid billing method" (read 2026-08-14)

## Connect

- Base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1`
- Key: `CLOUDFLARE_WORKERS_AI_API_KEY` — get one at <https://dash.cloudflare.com/profile/api-tokens>
- Note: substitute {account_id} with your Cloudflare account ID

## Evidence

- Probe: the page at <https://developers.cloudflare.com/workers-ai/platform/pricing/>, anchored on `10,000 neurons per day`, `free allocation`
- Source: <https://developers.cloudflare.com/workers-ai/platform/pricing/>
- Source: <https://developers.cloudflare.com/workers-ai/platform/limits/>

## History

- `2026-07-19` — Added to the list: 10k neurons/day free

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
