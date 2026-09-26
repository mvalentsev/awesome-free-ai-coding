---
layout: default
title: 'laguna-s-2.1 free: 5 providers, limits and ids, verified 2026-09-24'
description: laguna-s-2.1 is served free by OpenRouter (free models), Kilo Code, AIHubMix (free models), Vercel AI Gateway and Nous Portal (Hermes Agent). Vercel AI Gateway asks for a card on file, the rest for none; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids…
permalink: /models/laguna-s-2.1/
last_modified_at: 2026-09-25
---

{% raw %}

# Where laguna-s-2.1 is free

**5 rows on the list serve `laguna-s-2.1` free:** OpenRouter (free models), Kilo Code, AIHubMix (free models), Vercel AI Gateway and Nous Portal (Hermes Agent). Vercel AI Gateway asks for a card on file, the rest for none; Kilo Code answers with no account at all. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One API key for a rotating set of :free model variants, open-weight and stealth models among them

- Limits, in the vendor's words: 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM, FREE_MODEL_NO_CREDITS_RPD, FREE_MODEL_HAS_CREDITS_RPD and FREE_MODEL_CREDITS_THRESHOLD — and the table that should show them serves empty cells to anything reading the HTML. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", warns that a negative credit balance can produce errors "including for free models", and notes a 429 may come from the upstream provider rather than the platform (read 2026-08-14)
- Call it: `poolside/laguna-s-2.1:free` at `https://openrouter.ai/api/v1`, with a key in `OPENROUTER_API_KEY` from <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · verified 2026-09-24 · listed since 2026-08-11

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

- Limits, in the vendor's words: $0 a month, and no account for the free lane: "The gateway allows unauthenticated access for free models only. Anonymous requests are identified by IP address and are subject to rate limiting (200 requests per hour per IP)". The lane is whatever the gateway marks isFree — 21 ids on 2026-09-24, Nemotron 3 Ultra, Step 3.7 Flash and Laguna S 2.1 among them — and it rotates within days, so an id waits two weeks before it joins the Models column. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21
- Call it: `poolside/laguna-s-2.1:free` at `https://api.kilo.ai/api/gateway`, with no key
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Call it: `laguna-s-2.1-free` at `https://aihubmix.com/v1`, with a key in `AIHUBMIX_API_KEY` from <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · verified 2026-09-24 · listed since 2026-08-14

One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits every month once the team has a payment method on file, and three language models priced at zero that never touch the credit

- Limits, in the vendor's words: Vercel's FAQ, in its error table: "The team must add a valid payment method before using free credits" (`403` `customer_verification_required`). $5 of gateway credit a month at provider list rates, renewed monthly, with lower per-model rate limits and no BYOK; buying credits ends the monthly free credit. A handful of language models are priced 0 in and 0 out and never draw on the credit — Laguna S 2.1 Free and the Ling 3.0 Flash Fin and Sante rows, each with and without its -free suffix, on 2026-09-23. Mind the suffix: poolside/laguna-s-2.1 without it costs $0.10/$0.20 per 1M tokens
- Call it: `poolside/laguna-s-2.1-free` at `https://ai-gateway.vercel.sh/v1`, with a key in `VERCEL_AI_GATEWAY_API_KEY` from <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

### [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/)

🧭 Aggregators (one key, many providers) · no card · provisional since 2026-09-16 · verified 2026-09-24 · listed since 2026-09-16

Nous Research's inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — seven on 2026-09-18, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API

- Limits, in the vendor's words: The portal's plan table reads "Free $0 Free models only Standard rate limits $0 monthly credits Try Hermes", and the Hermes Agent guide has you "create a Nous Portal account (or sign in), choose the Free plan, and authorize Hermes" — "The :free tag is what keeps it on the no-cost plan". No rate-limit figure is published and no page read mentions a card. The keyless catalog prices seven rows at zero; a call without a key answers HTTP 402 with a payment offer, so the free models want the portal's key. Read 2026-09-18
- Call it: `poolside/laguna-s-2.1:free` at `https://inference-api.nousresearch.com/v1`, with a key in `NOUS_PORTAL_API_KEY` from <https://portal.nousresearch.com>
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://portal.nousresearch.com/privacy)).

## Related models

- [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/) — free at OpenRouter (free models), Kilo Code, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and LLMTR

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
