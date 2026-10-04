---
layout: default
title: 'laguna-xs-2.1 free: 6 providers, limits and ids, verified 2026-10-01'
description: laguna-xs-2.1 is served free by OpenRouter (free models), Kilo Code, NVIDIA NIM (build.nvidia.com), AIHubMix (free models), LLMTR and Nous Portal (Hermes Agent). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the…
permalink: /models/laguna-xs-2.1/
last_modified_at: 2026-10-04
crumb: laguna-xs-2.1
---

{% raw %}

# Where laguna-xs-2.1 is free

**6 rows on the list serve `laguna-xs-2.1` free:** OpenRouter (free models), Kilo Code, NVIDIA NIM (build.nvidia.com), AIHubMix (free models), LLMTR and Nous Portal (Hermes Agent). None asks for a card; Kilo Code answers with no account at all. The published offers were checked on 2026-10-01 and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-24

One API key for a rotating set of :free model variants, open-weight and stealth models among them

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. The quota figures are published in the limits page's JavaScript data. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", and its limits page warns that a negative credit balance can produce errors "including for free models" and that a 429 can come from the upstream provider rather than the platform (read 2026-09-27)

</details>

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `poolside/laguna-xs-2.1:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · verified 2026-10-01 · listed since 2026-08-11

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: $0 a month, and no account for the free lane: "The gateway allows unauthenticated access for free models only. Anonymous requests are identified by IP address and are subject to rate limiting (200 requests per hour per IP)". The lane is whatever the gateway marks isFree and the free-model lineup rotates. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21

</details>

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code`
- Callable ids: `poolside/laguna-xs-2.1:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-10-01 · listed since 2026-09-22

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: No card; the API key needs a free NVIDIA Developer Program account verified by a code sent to your phone, and on 2026-09-25 build.nvidia.com's own list kept fourteen countries out of that step: Afghanistan, Bangladesh, Belarus, Cuba, Iran, Kazakhstan, Kyrgyzstan, North Korea, Pakistan, Russia, Syria, Tajikistan, Tanzania and Uzbekistan. The ceiling is a rate, not credits: NVIDIA's site puts it at "Up to 40 rpm" and "10,000 requests per day", adding that "Rate limits may vary by model and traffic from other users may cause throttling"; NVIDIA staff call 40 RPM "the published free-tier cap" that "is not adjustable on a per-account basis". A key can also be issued and still not answer: since June 2026 the vendor's forum has carried thread after thread of new personal keys that list the catalog and get 404 on every chat call, and NVIDIA's pinned note on account access says verification "has been challenging for both the community and NVIDIA", sending such cases to help@build.nvidia.com. Each model's page states whether its free endpoint is available or deprecated, and NVIDIA renames ids without notice, so copy them from the catalog. Read 2026-09-25

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `poolside/laguna-xs-2.1`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself, with an Anthropic-format /v1/messages too, so a free id can back Claude Code

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex CLI"
- Callable ids: `laguna-xs-2.1-free`

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-24

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak işaretlenen bir chat modelini seçin" (pick a free chat model), and "Bu adım, sıfır bakiye ile gateway ve kullanım kaydı akışının çalıştığını doğrular" (checks gateway use on a zero balance). Three free rows carry a daily quota whose figure is published nowhere (Nemotron 3 Ultra and Super, Qwen3.8 27B); Laguna XS 2.1 is free because "Poolside serves these models free on its own inference API", with "no extra token allowance to track". Paid use is prepaid credit: "An 8% platform margin is added on top of the requested top-up amount", and "The platform margin is not added to model prices; it is applied only once, at top-up". The privacy page says prompt and response bodies are not written permanently to its usage and billing database ("kalıcı olarak yazılmaz"). Ling 3.1 Flash is a short promotion: "13 Ekim 2026 19:00'a kadar ucretsiz" (free until October 13, 19:00). MiniMax M3.1 Flash Preview requires a top-up: "6 Ekim 2026 23:59'a kadar ücretsiz, en az bir kez bakiye yüklemiş hesaplara açık" (until October 6, 23:59, only for accounts that have topped up). Read 2026-10-04

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `poolside/laguna-xs-2.1`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

### [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-30

Nous Research's inference portal with a $0 Free plan for :free models, accessible through an OpenAI-compatible API and Hermes Agent

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: The portal's plan table reads "Free $0 Free models only Standard rate limits $0 monthly credits Try Hermes", and the Hermes Agent guide has you "create a Nous Portal account (or sign in), choose the Free plan, and authorize Hermes" — "The :free tag is what keeps it on the no-cost plan". No rate-limit figure is published and no page read mentions a card. The keyless catalog prices seven qualifying :free chat rows at zero; a call without a key answers HTTP 402 with a payment offer, so the free models want the portal's key. Read 2026-10-01

</details>

- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `poolside/laguna-xs-2.1:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://portal.nousresearch.com/privacy)).

## Related models

- [`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/) — free at OpenRouter (free models), Kilo Code, AIHubMix (free models), Vercel AI Gateway and Nous Portal (Hermes Agent)

---

Generated from `registry.yaml` on 2026-10-02 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
