---
layout: default
title: 'Vercel AI Gateway free tier: limits, free models, verified 2026-09-21'
description: One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits included every month and five language models that never touch the credit. $5 of gateway credit a month at provider list rates, renewed monthly, with lower per-model rate limits and no BYOK; buying credits ends the…
permalink: /providers/vercel-ai-gateway/
---

{% raw %}

# Vercel AI Gateway

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-21 · [vercel.com](https://vercel.com/ai-gateway) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits included every month and five language models that never touch the credit

## Free models

`laguna-s-2.1`, `ling-3.0-flash-fin`, `ling-3.0-flash-sante`

## Limits, in the vendor's words

$5 of gateway credit a month at provider list rates, renewed monthly, with lower per-model rate limits and no BYOK; buying credits ends the monthly free credit. A handful of language models are priced 0 in and 0 out and never draw on the credit — Laguna S 2.1 Free and the Ling 3.0 Flash Fin, Sante and VL rows, each with and without its -free suffix, on 2026-09-12. Mind the suffix: poolside/laguna-s-2.1 without it costs $0.10/$0.20 per 1M tokens

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “By default, AI Gateway does not route based on the training data policy of providers. If we do not know a provider's training data stance or have not yet established an agreement with them, we assume that they train on your data.” ([source](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Connect

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Callable ids: `poolside/laguna-s-2.1-free`, `inclusionai/ling-3.0-flash-fin`, `inclusionai/ling-3.0-flash-fin-free`, `inclusionai/ling-3.0-flash-sante`, `inclusionai/ling-3.0-flash-sante-free`, `inclusionai/ling-3.0-flash-vl`, `inclusionai/ling-3.0-flash-vl-free`
- Note: every id listed is priced 0 in and 0 out and draws nothing from the $5 credit; any other Free-Tier-eligible model spends it. Zero-priced ids come and go within days, so a new one waits two weeks for the Models column. spacexai/grok-stt also shows a zero but is speech-to-text billed per second of audio. The same key serves the Anthropic Messages format at https://ai-gateway.vercel.sh, which Vercel's docs give as Claude Code's ANTHROPIC_BASE_URL with ANTHROPIC_API_KEY empty

## Evidence

- Probe: the models catalog at <https://ai-gateway.vercel.sh/v1/models>, every listed family required at a zero price
- Source: <https://vercel.com/docs/ai-gateway/pricing>
- Source: <https://vercel.com/docs/ai-gateway/openai-compat>
- Source: <https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-messages-api>

## History

- `2026-09-21` — Free models changed: added ling-3.0-flash-fin, ling-3.0-flash-sante
- `2026-08-20` — Free models changed: dropped glm-4.6v-flash
- `2026-08-17` — Free models changed: added laguna-s-2.1; dropped laguna-s-2.1-free
- `2026-08-14` — Free models changed: added glm-4.6v-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash-free
- `2026-08-03` — Added to the list: One OpenAI-compatible endpoint for 300+ models, with $5 of gateway credits included every month

---

Generated from `registry.yaml` on 2026-09-22 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
