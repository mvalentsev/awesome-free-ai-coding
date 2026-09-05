---
layout: default
title: 'SambaNova Cloud free tier: limits, free models, verified 2026-09-03'
description: Open models on SambaNova's RDU hardware, OpenAI-compatible; the free tier is the one that applies while no payment method is linked, so linking a card is what ends it. 20 req/min, 20 req/day and 200,000 tokens/day per model on the free tier; five models carry it (DeepSeek V3.1/V3.2, Llama 3.3…
permalink: /providers/sambanova-cloud/
---

{% raw %}

# SambaNova Cloud

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [cloud.sambanova.ai](https://cloud.sambanova.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open models on SambaNova's RDU hardware, OpenAI-compatible; the free tier is the one that applies while no payment method is linked, so linking a card is what ends it

## Free models

`deepseek`, `gpt-oss`, `gemma-4`

## Limits, in the vendor's words

20 req/min, 20 req/day and 200,000 tokens/day per model on the free tier; five models carry it (DeepSeek V3.1/V3.2, Llama 3.3 70B, gpt-oss-120b, Gemma 4)

## Connect

- Base URL: `https://api.sambanova.ai/v1`
- Key: `SAMBANOVA_CLOUD_API_KEY` — get one at <https://cloud.sambanova.ai/apis>
- Callable ids: `DeepSeek-V3.1`, `Meta-Llama-3.3-70B-Instruct`, `gpt-oss-120b`
- Note: model ids are case-sensitive; the catalog publishes list prices for every row, so the free tier is a quota rather than a zero-priced lane

## Evidence

- Probe: the page at <https://docs.sambanova.ai/docs/en/models/rate-limits>, anchored on `no payment method linked with your account`, `Meta-Llama-3.3-70B-Instruct`, `200000`; ids checked in <https://api.sambanova.ai/v1/models>
- Source: <https://docs.sambanova.ai/docs/en/models/rate-limits>

## History

- `2026-08-05` — Added to the list: Open models on SambaNova's RDU hardware, OpenAI-compatible; the free tier is the one that applies while no payment method is linked, so linking a card is what ends it

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
