---
layout: default
title: 'Vercel AI Gateway free tier: limits, free models, verified 2026-10-22'
description: 'OpenAI-compatible model gateway with $5 of monthly credit after adding a payment method, plus separate zero-priced model routes. Free models: laguna-s-2.1. A team must add a valid payment method before using free credit; otherwise requests return `403 customer_verification_required`. Credit spends…'
permalink: /providers/vercel-ai-gateway/
last_modified_at: 2026-10-24
crumb: Vercel AI Gateway
---

{% raw %}

# Vercel AI Gateway free tier

🧭 Aggregators (one key, many providers) · card required · **live** — last verified by a probe on 2026-10-22 · [vercel.com](https://vercel.com/ai-gateway) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible model gateway with $5 of monthly credit after adding a payment method, plus separate zero-priced model routes

## Free models

[`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/)

## Limits, in the vendor's words

Gateway credit: $5/month per team

Free credit rate limits: Requests allowance: amount not published (period not published); scope not published (Limits apply per model.)

Beam launch offer: Usage allowance: amount not published (period not published); scope not published (The free route stops at the end of the launch offer; the end date and numerical allowance are unpublished.); for `reflection/beam-free`

A team must add a valid payment method before using free credit; otherwise requests return `403 customer_verification_required`. Credit spends at provider list rates and excludes BYOK. Buying credit ends the monthly free credit. Zero-priced model routes remain a separate free mode and do not spend that balance. Use their exact free IDs: a similarly named route without its free suffix can be metered.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://vercel.com/legal/ai-product-terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “By default, AI Gateway does not route based on the training data policy of providers. If we do not know a provider's training data stance or have not yet established an agreement with them, we assume that they train on your data.” ([source](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Connect

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Codex CLI: [`configs/codex/vercel-ai-gateway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/vercel-ai-gateway.config.toml) — copy it to `~/.codex/`, then `codex -p vercel-ai-gateway`; Codex's base is `https://ai-gateway.vercel.sh/codex/v1`; set up on the lane by the vendor's own page, <https://vercel.com/docs/ai-gateway/coding-agents/openai-codex>: "Point Codex at its own compatibility endpoint"
- Callable ids: `poolside/laguna-s-2.1-free`, `stealth/glyph-cluster`, `nvidia/nemotron-3.5-lightning-free`, `reflection/beam-free`
- Note: Use the IDs listed here; a zero catalog price can depend on the provider and change after a promotion. For Beam, use reflection/beam-free: it stops when free access ends. The regular reflection/beam route can charge at provider rates. Reflection's terms and privacy policy apply. For Claude Code, set ANTHROPIC_BASE_URL=https://ai-gateway.vercel.sh and leave ANTHROPIC_API_KEY empty.

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
- Source: <https://vercel.com/docs/ai-gateway/rate-limits>
- Source: <https://vercel.com/docs/ai-gateway/faq>
- Source: <https://vercel.com/docs/ai-gateway/openai-compat>
- Source: <https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-messages-api>
- Source: <https://vercel.com/changelog/reflection-ai-beam-now-available-on-ai-gateway-for-free>
- Source: <https://vercel.com/ai-gateway/models/beam-free>
- Source: <https://vercel.com/ai-gateway/models/beam>
- Source: <https://reflection.ai/legal/terms-of-service>
- Source: <https://reflection.ai/legal/privacy-policy>
- Source: <https://vercel.com/changelog/minimax-m3-1-flash-now-available-on-ai-gateway-for-free>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-15` — Free models changed: dropped ling-3.1-flash
- `2026-10-13` — Free models changed: added ling-3.1-flash
- `2026-10-05` — Free models changed: dropped ling-3.0-flash-sante
- `2026-09-26` — Free models changed: dropped ling-3.0-flash-fin
- `2026-09-19` — Free models changed: added ling-3.0-flash-sante
- `2026-09-17` — Free models changed: added ling-3.0-flash-fin
- `2026-08-20` — Free models changed: dropped glm-4.6v-flash
- `2026-08-14` — Free models changed: added laguna-s-2.1; dropped laguna-s-2.1-free
- `2026-08-14` — Free models changed: added glm-4.6v-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash-free
- `2026-08-03` — Added: One OpenAI-compatible endpoint for 300+ models, with $5 of gateway credits included every month

---

Generated from `registry.yaml` on 2026-10-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
