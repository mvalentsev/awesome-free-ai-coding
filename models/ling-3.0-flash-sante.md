---
layout: default
title: 'ling-3.0-flash-sante free: 3 providers, limits and ids, verified 2026-09-24'
description: ling-3.0-flash-sante is served free by OpenRouter (free models), Kilo Code and Vercel AI Gateway. Vercel AI Gateway asks for a card on file, the rest for none; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day a live probe last…
permalink: /models/ling-3.0-flash-sante/
last_modified_at: 2026-09-26
crumb: ling-3.0-flash-sante
---

{% raw %}

# Where ling-3.0-flash-sante is free

**3 rows on the list serve `ling-3.0-flash-sante` free:** OpenRouter (free models), Kilo Code and Vercel AI Gateway. Vercel AI Gateway asks for a card on file, the rest for none; Kilo Code answers with no account at all. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One API key for a rotating set of :free model variants, open-weight and stealth models among them

- Limits, in the vendor's words: 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM, FREE_MODEL_NO_CREDITS_RPD, FREE_MODEL_HAS_CREDITS_RPD and FREE_MODEL_CREDITS_THRESHOLD — and the table that should show them serves empty cells to anything reading the HTML. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", warns that a negative credit balance can produce errors "including for free models", and notes a 429 may come from the upstream provider rather than the platform (read 2026-08-14)
- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Callable ids: `inclusionai/ling-3.0-flash-sante:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · verified 2026-09-24 · listed since 2026-09-24

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

- Limits, in the vendor's words: $0 a month, and no account for the free lane: "The gateway allows unauthenticated access for free models only. Anonymous requests are identified by IP address and are subject to rate limiting (200 requests per hour per IP)". The lane is whatever the gateway marks isFree — 21 ids on 2026-09-24, Nemotron 3 Ultra, Step 3.7 Flash and Laguna S 2.1 among them — and it rotates within days, so an id waits two weeks before it joins the Models column. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Callable ids: `inclusionai/ling-3.0-flash-sante:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · verified 2026-09-24 · listed since 2026-09-19

One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits every month once the team has a payment method on file, and three language models priced at zero that never touch the credit

- Limits, in the vendor's words: Vercel's FAQ, in its error table: "The team must add a valid payment method before using free credits" (`403` `customer_verification_required`). $5 of gateway credit a month at provider list rates, renewed monthly, with lower per-model rate limits and no BYOK; buying credits ends the monthly free credit. A handful of language models are priced 0 in and 0 out and never draw on the credit — Laguna S 2.1 Free, Ling 3.0 Flash Sante with and without its -free suffix, and the anonymous stealth/pixel-canary, on 2026-09-26. Mind the suffix: poolside/laguna-s-2.1 without it costs $0.10/$0.20 per 1M tokens
- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Callable ids: `inclusionai/ling-3.0-flash-sante`, `inclusionai/ling-3.0-flash-sante-free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Related models

- [`ling-3.0-flash-fin`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-fin/) — free at opencode, OpenRouter (free models), Kilo Code and LLMTR
- [`ling-3.0-tiny`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-tiny/) — free at Requesty and AIHubMix (free models)
- [`ling-3.0-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
