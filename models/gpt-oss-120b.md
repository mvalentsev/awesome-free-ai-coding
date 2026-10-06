---
layout: default
title: 'gpt-oss-120b free: 4 providers, limits and ids, verified 2026-10-01 or later'
description: gpt-oss-120b is served free by Groq, Google Antigravity, Regolo AI and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/gpt-oss-120b/
last_modified_at: 2026-10-05
crumb: gpt-oss-120b
---

{% raw %}

# Where gpt-oss-120b is free

**4 rows on the list serve `gpt-oss-120b` free:** Groq, Google Antigravity, Regolo AI and OVHcloud AI Endpoints. None asks for a card; OVHcloud AI Endpoints answers with no account at all. The published offers were checked on 2026-10-01 or later and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-25

Fast inference against a free plan Groq publishes as a per-model rate table

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 1K / 8K / 200K on openai/gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b and qwen/qwen3.8-27b, 30 / 14.4K / 15K / 500K on the two meta-llama/llama-prompt-guard classifiers, 20 / 2K on the two whisper models and 10 / 100 / 1.2K / 3.6K on the two canopylabs/orpheus voices (read 2026-09-27). Those ten rows are the whole free plan, with no Llama among them — the Llama ids in the page's API samples are not on it. Groq calls the table "a high level summary and there may be exceptions", and points at the limits page in an account for the exact figures

</details>

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `openai/gpt-oss-120b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [Google Antigravity](https://mvalentsev.github.io/awesome-free-ai-coding/providers/antigravity/)

🤖 Coding agents & CLIs · no card · not offered in mainland China, Russia, Hong Kong and 21 more places · verified 2026-10-01 · listed since 2026-09-25

Google's agent-first IDE and CLI, with a $0 Individual plan serving Gemini and third-party agent models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: The $0 Individual plan has unlimited Tab completions and Command requests, with "Basic weekly rate limits". The model table marks the listed models available under "Free & Google AI Plus"; Claude Sonnet 4.6, Claude Opus 4.6 and GPT-OSS-120b carry its notice "Will be removed on November 2, 2026". Claude 5.5 models require paid plans. Gemini and third-party models have separate weekly allowances. No quota figure is published: "The baseline rate limits are primarily determined by available capacity and exist to prevent abuse." The plans overview lists third-party access under Ultra, while the specific model table still includes these older models on Free. Read 2026-10-05

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://antigravity.google/terms)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-05 · listed since 2026-09-25

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

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-25

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: OVHcloud documents the anonymous lane: "Anonymous: 2 requests per minute, per IP and per model. Authenticated with an API access key: 400 requests per minute, per PCI project and per model", and its product page says "Test all our models for free in a sandbox or via the API". It is not counted per IP in practice: on 2026-09-24 one call a minute to Qwen3.8-27B from an address nothing else used answered twice in five, and each answer left `ratelimit-remaining: 0`, another caller having spent the minute's other request; the first call of a minute on six ids, and every call from a GitHub runner that morning, answered 429. The two requests a minute per model are shared by every anonymous caller. A key bills every chat model per token, Qwen3.8-27B at "0.4 € / Mtoken(input)" and "2.7 € / Mtoken(output)". Read 2026-09-24

</details>

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `gpt-oss-120b`
- What you send is not used to train models ([the vendor's words](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)).

## Related models

- [`gpt-oss-20b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-20b/) — free at Groq, NVIDIA NIM (build.nvidia.com), Regolo AI and Pollinations.AI
- [`gpt-6-luna`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-6-luna/) — free at Zed

---

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
