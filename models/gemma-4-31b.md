---
layout: default
title: 'gemma-4-31b free: 4 providers, limits and ids, verified 2026-09-24'
description: gemma-4-31b is served free by OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com) and Opper. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/gemma-4-31b/
last_modified_at: 2026-09-25
---

{% raw %}

# Where gemma-4-31b is free

**4 rows on the list serve `gemma-4-31b` free:** OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com) and Opper. None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-25

One API key for a rotating set of :free model variants, open-weight and stealth models among them

- Limits, in the vendor's words: 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM, FREE_MODEL_NO_CREDITS_RPD, FREE_MODEL_HAS_CREDITS_RPD and FREE_MODEL_CREDITS_THRESHOLD — and the table that should show them serves empty cells to anything reading the HTML. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", warns that a negative credit balance can produce errors "including for free models", and notes a 429 may come from the upstream provider rather than the platform (read 2026-08-14)
- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Callable ids: `google/gemma-4-31b-it:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-25

OpenAI-compatible router over a 690+ model catalog with routing, caching and fallbacks; twelve rows in it are priced 0 and the free plan is the same gateway restricted to those

- Limits, in the vendor's words: Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend tracking and EU data residency included; past that the same key moves to pay-as-you-go
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `google/gemma-4-31b-it`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

- Limits, in the vendor's words: No card; the API key needs a free NVIDIA Developer Program account verified by a code sent to your phone, and on 2026-09-25 build.nvidia.com's own list kept fourteen countries out of that step: Afghanistan, Bangladesh, Belarus, Cuba, Iran, Kazakhstan, Kyrgyzstan, North Korea, Pakistan, Russia, Syria, Tajikistan, Tanzania and Uzbekistan. The ceiling is a rate, not credits: NVIDIA's site puts it at "Up to 40 rpm" and "10,000 requests per day", adding that "Rate limits may vary by model and traffic from other users may cause throttling"; NVIDIA staff call 40 RPM "the published free-tier cap" that "is not adjustable on a per-account basis". A key can also be issued and still not answer: since June 2026 the vendor's forum has carried thread after thread of new personal keys that list the catalog and get 404 on every chat call, and NVIDIA's pinned note on account access says verification "has been challenging for both the community and NVIDIA", sending such cases to help@build.nvidia.com. Each model's page states whether its free endpoint is available or deprecated, and NVIDIA renames ids without notice, so copy them from the catalog. Read 2026-09-25
- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `google/gemma-4-31b-it`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Opper](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opper/)

🧭 Aggregators (one key, many providers) · no card · provisional since 2026-09-17 · verified 2026-09-24 · listed since 2026-09-17

EU-hosted gateway over 700+ models whose free models — Gemma 4 31B and Gemma 4 26B on Google's route, Laguna S 2.1 and XS 2.1 through Poolside — answer an account with no card on file; every other model needs a card and credits

- Limits, in the vendor's words: The pricing FAQ: "Sign up needs no credit card: you get an API key straight away and the free models work in the playground and the API. Add a card to use premium models, pay-as-you-go with no minimum." The llms.txt names one of them — "gemini/gemma-4-31b is a free model, so this call works before you add a card. It runs on a US-hosted route." — and the model directory at opper.ai/models flags five rows free: gemini/gemma-4-31b, gemini/gemma-4-26b-moe, poolside/laguna-s-2.1, poolside/laguna-xs-2.1 and Talkie 1930, a 13B model trained on pre-1931 text. The keyless catalog publishes no price for them, and no page gives the free models a quota or a rate limit. Paid usage is billed at provider rates with "a 3% fee on credit purchases". The operator is Opper Technology AB, in Sweden, on AWS Stockholm. Read 2026-09-17
- Base URL: `https://api.opper.ai/v3/compat`
- Key: `OPPER_API_KEY` — get one at <https://platform.opper.ai/settings/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.opper.ai/v3/compat`
- Callable ids: `gemini/gemma-4-31b`
- What you send is not used to train models ([the vendor's words](https://opper.ai/pricing)).

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
