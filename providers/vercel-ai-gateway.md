---
layout: default
title: 'Vercel AI Gateway free tier: limits, free models, verified 2026-09-03'
description: One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits included every month and seven language models that never touch the credit. $5/month credit at provider list rates, renewed monthly; lower per-model rate limits, no BYOK. Seven of the 373 catalogued models are language…
permalink: /providers/vercel-ai-gateway/
---

{% raw %}

# Vercel AI Gateway

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [vercel.com](https://vercel.com/ai-gateway) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits included every month and seven language models that never touch the credit

## Free models

`laguna-s-2.1`

## Limits, in the vendor's words

$5/month credit at provider list rates, renewed monthly; lower per-model rate limits, no BYOK. Seven of the 373 catalogued models are language models priced 0 in and 0 out on 2026-09-05 — poolside's Laguna S 2.1 Free, MiniMax M3 (Free) and M2.7 (Free), and Ling 3.0 Flash Fin and Ling 3.0 Flash Sante each with and without its -free suffix — against five on 2026-09-02 and exactly one on 2026-08-20, and none of them draws the credit down; the only other zero row is spacexai/grok-stt, speech-to-text billed per second of audio. z.ai's GLM-4.6V-Flash, free here until it left the catalog by the 2026-08-20 read, is gone: the 14 GLM rows that remain are all priced. Mind the suffix, since the same catalog carries poolside/laguna-s-2.1 without it at $0.10/$0.20 per 1M tokens (read 2026-08-20). Buying credits ends the monthly free credit

## Connect

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Callable ids: `poolside/laguna-s-2.1-free`, `minimax/minimax-m3-free`, `minimax/minimax-m2.7-free`, `inclusionai/ling-3.0-flash-fin`, `inclusionai/ling-3.0-flash-fin-free`, `inclusionai/ling-3.0-flash-sante`, `inclusionai/ling-3.0-flash-sante-free`
- Note: every id listed is priced 0 in and 0 out and draws nothing from the $5 credit; any other Free-Tier-eligible model spends it. One such id on 2026-08-20, five on 2026-09-02, seven on 2026-09-05: MiniMax M3 (Free) and M2.7 (Free) arrived beside metered twins at $0.30/$1.20 per 1M, and Ling 3.0 Flash Fin and then its health-tuned sibling Ling 3.0 Flash Sante are priced 0 with and without the -free suffix. They stay out of the Models column until they have stood a while — zai/glm-4.6v-flash was free here from 2026-08-14 and gone by 2026-08-20. spacexai/grok-stt, the sixth row at 0 per token, is speech-to-text billed per second of audio, which the probe reads as a price The same key serves the Anthropic Messages format at https://ai-gateway.vercel.sh — the docs (updated 2026-08-11) set ANTHROPIC_BASE_URL to it for Claude Code with ANTHROPIC_API_KEY left empty, and the zero-priced ids here are what to name in ANTHROPIC_MODEL

## Evidence

- Probe: the models catalog at <https://ai-gateway.vercel.sh/v1/models>, every listed family required at a zero price
- Source: <https://vercel.com/docs/ai-gateway/pricing>
- Source: <https://vercel.com/docs/ai-gateway/openai-compat>
- Source: <https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-messages-api>

## History

- `2026-08-20` — Free models changed: dropped glm-4.6v-flash
- `2026-08-17` — Free models changed: added laguna-s-2.1; dropped laguna-s-2.1-free
- `2026-08-14` — Free models changed: added glm-4.6v-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash-free
- `2026-08-03` — Added to the list: One OpenAI-compatible endpoint for 300+ models, with $5 of gateway credits included every month

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
