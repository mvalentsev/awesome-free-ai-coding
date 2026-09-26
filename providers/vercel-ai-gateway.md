---
layout: default
title: 'Vercel AI Gateway free tier: limits, free models, verified 2026-09-24'
description: 'One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits every month once the team has a payment method on file, and three language models priced at zero that never touch the credit. Free models: laguna-s-2.1, ling-3.0-flash-sante. Vercel''s FAQ, in its error table: "The team…'
permalink: /providers/vercel-ai-gateway/
last_modified_at: 2026-09-26
crumb: Vercel AI Gateway
---

{% raw %}

# Vercel AI Gateway free tier

🧭 Aggregators (one key, many providers) · card required · **live** — last verified by a probe on 2026-09-24 · [vercel.com](https://vercel.com/ai-gateway) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits every month once the team has a payment method on file, and three language models priced at zero that never touch the credit

## Free models

[`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/), [`ling-3.0-flash-sante`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-sante/)

## Limits, in the vendor's words

Vercel's FAQ, in its error table: "The team must add a valid payment method before using free credits" (`403` `customer_verification_required`). $5 of gateway credit a month at provider list rates, renewed monthly, with lower per-model rate limits and no BYOK; buying credits ends the monthly free credit. A handful of language models are priced 0 in and 0 out and never draw on the credit — Laguna S 2.1 Free, Ling 3.0 Flash Sante with and without its -free suffix, and the anonymous stealth/pixel-canary, on 2026-09-26. Mind the suffix: poolside/laguna-s-2.1 without it costs $0.10/$0.20 per 1M tokens

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://vercel.com/legal/ai-product-terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “By default, AI Gateway does not route based on the training data policy of providers. If we do not know a provider's training data stance or have not yet established an agreement with them, we assume that they train on your data.” ([source](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Connect

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Callable ids: `poolside/laguna-s-2.1-free`, `inclusionai/ling-3.0-flash-sante`, `inclusionai/ling-3.0-flash-sante-free`, `stealth/pixel-canary`
- Note: every id listed is priced 0 in and 0 out and draws nothing from the $5 credit; any other Free-Tier-eligible model spends it. Zero-priced ids come and go within days, so a new one waits two weeks for the Models column; stealth/pixel-canary is a stealth codename that names no model, so it stays out of it. spacexai/grok-stt also shows a zero but is speech-to-text billed per second of audio. The same key serves the Anthropic Messages format at https://ai-gateway.vercel.sh, which Vercel's docs give as Claude Code's ANTHROPIC_BASE_URL with ANTHROPIC_API_KEY empty

Try it from your terminal with your key in `VERCEL_AI_GATEWAY_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://ai-gateway.vercel.sh/v1/chat/completions \
  -H "Authorization: Bearer $VERCEL_AI_GATEWAY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"poolside/laguna-s-2.1-free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://ai-gateway.vercel.sh/v1/models>, each listed family checked for a zero price
- Source: <https://vercel.com/docs/ai-gateway/pricing>
- Source: <https://vercel.com/docs/ai-gateway/faq>
- Source: <https://vercel.com/docs/ai-gateway/openai-compat>
- Source: <https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-messages-api>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-26` — Free models changed: dropped ling-3.0-flash-fin
- `2026-09-19` — Free models changed: added ling-3.0-flash-sante
- `2026-09-17` — Free models changed: added ling-3.0-flash-fin
- `2026-08-20` — Free models changed: dropped glm-4.6v-flash
- `2026-08-14` — Free models changed: added laguna-s-2.1; dropped laguna-s-2.1-free
- `2026-08-14` — Free models changed: added glm-4.6v-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash-free
- `2026-08-03` — Added: One OpenAI-compatible endpoint for 300+ models, with $5 of gateway credits included every month

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
