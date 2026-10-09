---
layout: default
title: 'gpt-oss-120b free: 4 providers, limits and ids, verified 2026-10-08'
description: gpt-oss-120b is served free by Groq, Google Antigravity, Regolo AI and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/gpt-oss-120b/
last_modified_at: 2026-10-08
crumb: gpt-oss-120b
---

{% raw %}

# Where gpt-oss-120b is free

**4 rows on the list serve `gpt-oss-120b` free:** Groq, Google Antigravity, Regolo AI and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. The published offers were checked on 2026-10-08 and are rechecked twice a week.

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
- Callable ids: `openai/gpt-oss-120b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [Google Antigravity](https://mvalentsev.github.io/awesome-free-ai-coding/providers/antigravity/)

🤖 Coding agents & CLIs · no card · not offered in mainland China, Russia, Hong Kong and 21 more places · verified 2026-10-08 · listed since 2026-09-25

Google's agent-first IDE and CLI, with a $0 Individual plan serving Gemini and third-party agent models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Gemini agent allowance: Weekly usage allowance: amount not published per account

Claude and GPT agent allowance: Weekly usage allowance: amount not published per account

Tab: Unmetered completions per account

Command: Unmetered requests per account

The model table includes older third-party models under Free & Google AI Plus, with removal on November 2, 2026; Claude 5.5 requires a paid plan. The plans overview instead lists third-party access under Ultra, so those sources disagree. Gemini and third-party models have separate weekly allowances. Baseline limits depend on available capacity and abuse prevention; no numerical weekly budget is published.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://antigravity.google/terms)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-08 · listed since 2026-09-25

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 30-day trial: 1,000,000 tokens/day per account

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `gpt-oss-120b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

### [OVHcloud AI Endpoints](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-25

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Anonymous lane: 2 requests/minute sharing scope disputed

The documentation attributes the anonymous cap to IP and model. Tests on 2026-09-24 instead observed callers sharing a model's anonymous capacity, so its effective sharing scope remains disputed. Anonymous requests can receive 429 before a caller has spent the documented cap. Authenticated API keys are metered per token and use the paid project/model limits; they do not create a larger free allowance.

</details>

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `gpt-oss-120b`
- What you send is not used to train models ([the vendor's words](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)).

## Related models

- [`gpt-oss-20b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-20b/) — free at Groq, NVIDIA NIM (build.nvidia.com), Regolo AI and Pollinations.AI

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
