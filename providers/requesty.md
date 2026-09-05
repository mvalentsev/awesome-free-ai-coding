---
layout: default
title: 'Requesty free tier: limits, free models, verified 2026-09-03'
description: OpenAI-compatible router over a 690+ model catalog with routing, caching and fallbacks; twelve rows in it are priced 0 and the free plan is the same gateway restricted to those. Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend…
permalink: /providers/requesty/
---

{% raw %}

# Requesty

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [requesty.ai](https://www.requesty.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible router over a 690+ model catalog with routing, caching and fallbacks; twelve rows in it are priced 0 and the free plan is the same gateway restricted to those

## Free models

`nemotron-3-ultra`, `nemotron-3-super`, `gemma-4`, `ling-3.0-tiny`

## Limits, in the vendor's words

Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend tracking and EU data residency included; past that the same key moves to pay-as-you-go

## Connect

- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-nano-30b-a3b`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, `nvidia/nemotron-3.5-content-safety`, `novita/inclusionai/ling-3.0-tiny`, `google/gemma-4-31b-it`, `poolside/laguna-xs.2`, `poolside/laguna-m.1`, `mistral/leanstral-1-5`, `nvidia/muse-glimmer-30b`, `nvidia/nemotron-3.5-lightning-30b-a3b`
- Note: the twelve ids listed are every row the catalog prices at 0, and the free plan serves those alone — ten on 2026-08-11, twelve on 2026-09-02 after nvidia/muse-glimmer-30b and nvidia/nemotron-3.5-lightning-30b-a3b joined (both updated 2026-08-23). Ids here carry no :free suffix, so the price is the only thing separating them from the 686 metered rows beside them. Nine of the twelve — every NVIDIA row and both Poolside ones — are marked data_used_for_training with 30-day retention; nemotron-3.5-content-safety is a guardrail classifier rather than a coding model The Claude Code guide sets ANTHROPIC_BASE_URL to https://router.requesty.ai (router.eu.requesty.ai for EU residency) and recommends ANTHROPIC_MODEL over the /model directive; the SDK page's /anthropic/v1/messages path answers 404, the base above answers 401 keyless (2026-09-05)

## Evidence

- Probe: the models catalog at <https://router.requesty.ai/v1/models>, every listed family required at a zero price
- Source: <https://www.requesty.ai/pricing>
- Source: <https://docs.requesty.ai/quickstart>
- Source: <https://router.requesty.ai/v1/models>
- Source: <https://docs.requesty.ai/integrations/claude-code>

## History

- `2026-08-11` — Added to the list: OpenAI-compatible router over a 500+ model catalog with routing, caching and fallbacks; ten rows in it are priced 0 and the free plan is the same gateway restricted to those

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
