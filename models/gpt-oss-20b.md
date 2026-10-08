---
layout: default
title: 'gpt-oss-20b free: 4 providers, limits and ids, verified 2026-10-08'
description: gpt-oss-20b is served free by Groq, NVIDIA NIM (build.nvidia.com), Regolo AI and Pollinations.AI. None asks for a card; Pollinations.AI answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/gpt-oss-20b/
last_modified_at: 2026-10-08
crumb: gpt-oss-20b
---

{% raw %}

# Where gpt-oss-20b is free

**4 rows on the list serve `gpt-oss-20b` free:** Groq, NVIDIA NIM (build.nvidia.com), Regolo AI and Pollinations.AI. None asks for a card; Pollinations.AI answers with no account at all. The published offers were checked on 2026-10-08 and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-25

Fast inference against a free plan Groq publishes as a per-model rate table

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Coding models: 30 requests/minute; 1,000 requests/day; 8,000 tokens/minute; 200,000 tokens/day per organization per model; for `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`

These are the Free Plan limits for the coding models, shared by keys in the same organization. Classifiers, guardrails, speech and voice models have separate limits; their API examples do not establish free coding-model eligibility. Groq calls the table "a high level summary and there may be exceptions"; the account limits page gives the exact values.

</details>

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `openai/gpt-oss-20b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-10-08 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `openai/gpt-oss-20b`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-08 · listed since 2026-09-27

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 30-day trial: 1,000,000 tokens/day per account

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `gpt-oss-20b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

### [Pollinations.AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/pollinations/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-25

Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model

- Limits, in the vendor's words: Legacy anonymous lane: Usage allowance: amount not published (period not published); scope not published

The legacy keyless host lists openai-fast, GPT-OSS 20B on OVH, in the anonymous tier; the configured gpt-oss-20b alias completed a keyless POST on 2026-10-07. The current gen.pollinations.ai API requires a key and bills Pollen credits; without a key it returns 401. The former anonymous rate came from retired docs and is no longer a current published limit.
- Base URL: `https://text.pollinations.ai/openai`
- Key: none — the lane is anonymous
- Callable ids: `gpt-oss-20b`

## Related models

- [`gpt-oss-120b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-120b/) — free at Groq, Google Antigravity, Regolo AI and OVHcloud AI Endpoints

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
