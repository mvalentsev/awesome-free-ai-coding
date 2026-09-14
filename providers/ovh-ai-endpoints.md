---
layout: default
title: 'OVHcloud AI Endpoints free tier: limits, free models, verified 2026-09-14'
description: 'EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible). OVHcloud documents the anonymous lane rather than leaving it to be inferred: "Anonymous: 2 requests per minute, per IP and per model. Authenticated with an API access key: 400…'
permalink: /providers/ovh-ai-endpoints/
---

{% raw %}

# OVHcloud AI Endpoints

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-14 · [ovhcloud.com](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible)

## Free models

`gpt-oss`, `qwen3.6`, `qwen3.8`, `qwen3-coder`

## Limits, in the vendor's words

OVHcloud documents the anonymous lane rather than leaving it to be inferred: "Anonymous: 2 requests per minute, per IP and per model. Authenticated with an API access key: 400 requests per minute, per PCI project and per model" (docs.ovhcloud.com, read 2026-09-14), and its product page says "Test all our models for free in a sandbox or via the API". The keyless calls really do answer, and every probe run now makes one itself: gpt-oss-120b, gpt-oss-20b, Qwen3.6-27B, Qwen3-Coder-30B and Qwen3.8-27B all returned 200 with no Authorization header on 2026-09-14. The limit is tighter in practice than that sentence reads: at one call a minute per model from a single address, Qwen3.8-27B answered five times out of six and the gpt-oss and older Qwen ids once or twice, the rest 429 — so a 429 here is the quota, not a refusal, and Qwen3.8-27B leads the ids for that reason. It is also the one coding model the catalog prices at 0 on both sides: 15 of its 25 models carry a price, gpt-oss-120b at $0.00000047 per completion token, and the other zeros are the two Qwen3Guard safety classifiers, the two whisper models, four TTS voices and stable-diffusion-xl (read 2026-09-14). None of those is a coding model, which is why this row names what the anonymous lane serves instead of what the price column zeroes

## Connect

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `Qwen3.8-27B`, `gpt-oss-120b`, `Qwen3.6-27B`, `Qwen3-Coder-30B-A3B-Instruct`
- Note: no key at all on the anonymous lane, which OVHcloud rate-limits at 2 requests per minute per IP per model — a 429 means wait about half a minute, not that the offer is gone. An API access key from a Public Cloud project raises that to 400 per minute and bills per token from then on, except on Qwen3.8-27B, which the catalog prices at zero

## Evidence

- Probe: the models catalog at <https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models>
- Source: <https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models>
- Source: <https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started>
- Source: <https://www.ovhcloud.com/en/public-cloud/ai-endpoints/>

## History

- `2026-09-10` — Free models changed: added qwen3.8
- `2026-08-20` — Free models changed: added qwen3-coder, qwen3.6; dropped qwen3
- `2026-07-19` — Added to the list: EU-hosted serverless open-model API; anonymous tier needs no signup or API key (OpenAI-compatible)

---

Generated from `registry.yaml` on 2026-09-14 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
