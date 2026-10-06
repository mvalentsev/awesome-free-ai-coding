---
layout: default
title: 'gemma-4-31b free: 5 providers, limits and ids, verified 2026-10-05'
description: gemma-4-31b is served free by OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com), Regolo AI and Opper. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/gemma-4-31b/
last_modified_at: 2026-10-06
crumb: gemma-4-31b
---

{% raw %}

# Where gemma-4-31b is free

**5 rows on the list serve `gemma-4-31b` free:** OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com), Regolo AI and Opper. None asks for a card. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/gemma-4-31b), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-25

One API key for a rotating set of :free model variants, open-weight and stealth models among them

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. The quota figures are published in the limits page's JavaScript data. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", and its limits page warns that a negative credit balance can produce errors "including for free models" and that a 429 can come from the upstream provider rather than the platform (read 2026-09-27)

</details>

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `google/gemma-4-31b-it:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-25

OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks

- Limits, in the vendor's words: Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend tracking and EU data residency included; past that the same key moves to pay-as-you-go
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `google/gemma-4-31b-it`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-10-05 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: No card; the API key needs a free NVIDIA Developer Program account verified by a code sent to your phone, and on 2026-09-25 build.nvidia.com's own list kept fourteen countries out of that step: Afghanistan, Bangladesh, Belarus, Cuba, Iran, Kazakhstan, Kyrgyzstan, North Korea, Pakistan, Russia, Syria, Tajikistan, Tanzania and Uzbekistan. The ceiling is a rate, not credits: NVIDIA's site puts it at "Up to 40 rpm" and "10,000 requests per day", adding that "Rate limits may vary by model and traffic from other users may cause throttling"; NVIDIA staff call 40 RPM "the published free-tier cap" that "is not adjustable on a per-account basis". A key can also be issued and still not answer: since June 2026 the vendor's forum has carried thread after thread of new personal keys that list the catalog and get 404 on every chat call, and NVIDIA's pinned note on account access says verification "has been challenging for both the community and NVIDIA", sending such cases to help@build.nvidia.com. Each model's page states whether its free endpoint is available or deprecated, and NVIDIA renames ids without notice, so copy them from the catalog. Read 2026-09-25

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `google/gemma-4-31b-it`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-05 · listed since 2026-09-27

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: "Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), "1M tokens per day" and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `gemma4-31b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

### [Opper](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opper/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-17

EU-hosted model gateway advertising a free route before adding a card; current documentation conflicts on its availability

- Limits, in the vendor's words: The signup guide and llms.txt still say "gemini/gemma-4-31b is a free model, so this call works before you add a card. It runs on a US-hosted route." The 2026-10-01 directory lists no free routes and omits that id; the Gemma page lists premium routes from other providers. The API catalog retains the Gemini id but states no price or availability. Free access on the advertised route remains unconfirmed. No free quota or rate is published. Paid usage adds "a 3% fee on credit purchases". Opper Technology AB operates in Sweden on AWS Stockholm. Read 2026-10-01
- Base URL: `https://api.opper.ai/v3/compat`
- Key: `OPPER_API_KEY` — get one at <https://platform.opper.ai/settings/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.opper.ai/v3/compat`
- Codex CLI: [`configs/codex/opper.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/opper.config.toml) — copy it to `~/.codex/`, then `codex -p opper`; set up on the lane by the vendor's own page, <https://docs.opper.ai/integrations/coding-agents/codex>: "Run OpenAI's Codex CLI on any model in the Opper catalog"
- Callable ids: `gemini/gemma-4-31b`
- What you send is not used to train models ([the vendor's words](https://opper.ai/pricing)).

## Related models

- [`gemma-4-26b-a4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-26b-a4b/) — free at OpenRouter (free models)

---

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
