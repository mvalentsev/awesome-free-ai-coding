---
layout: default
title: 'qwen3.8-27b free: 8 providers, limits and ids, verified 2026-10-08'
description: qwen3.8-27b is served free by Groq, LLMTR, LLM Tech, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints. None asks for a card; LLM Tech, VLM Run Gateway and OVHcloud AI Endpoints answer with no account at all. Each…
permalink: /models/qwen3.8-27b/
last_modified_at: 2026-10-09
crumb: qwen3.8-27b
---

{% raw %}

# Where qwen3.8-27b is free

**8 rows on the list serve `qwen3.8-27b` free:** Groq, LLMTR, LLM Tech, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints. None asks for a card; LLM Tech, VLM Run Gateway and OVHcloud AI Endpoints answer with no account at all. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-8-27b).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-17

Fast inference against a free plan Groq publishes as a per-model rate table

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Coding models: 30 requests/minute; 1,000 requests/day; 8,000 tokens/minute; 200,000 tokens/day per organization per model; for `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`

These are the Free Plan limits for the coding models, shared by keys in the same organization. Classifiers, guardrails, speech and voice models have separate limits; their API examples do not establish free coding-model eligibility. Groq calls the table "a high level summary and there may be exceptions"; the account limits page gives the exact values.

</details>

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `qwen/qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-10-05

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

Apodex 1.1 Mini: Daily usage allowance: amount not published per account per model; for `apodex/apodex-1.1-mini-free`

Free chat rows can be called on a new account with zero balance before any top-up. Laguna XS 2.1 follows Poolside's free inference offer, without a token allowance to track. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Apodex Mini can close before its recorded deadline if the promotion pool runs out.

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `qwen/qwen3.8-27b-free`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

### [LLM Tech](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtech/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-18

EU provider of one model whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 4 concurrent requests, tool calls included, no account

- Limits, in the vendor's words: 2,000,000 tokens/day per IP. reset at 00:00 UTC

Shared trial key: 4 requests at once per key

64 requests at once shared across the endpoint

The public trial key shares its concurrency among all callers; the daily token budget is per IP and counts both prompt and completion. Its context is 131,072 tokens; personal paid keys have the full 262,144 and share the endpoint's separate inflight ceiling. Paid keys are issued by email, per token without subscription or minimum. Prompts and completions are volatile and never persisted or trained on; metadata, including IP, is retained 13 months. The sole proprietor operates in Poland, with GPUs in Italy behind a German edge.
- Base URL: `https://api.llmtech.eu/v1`
- Key: `LLMTECH_API_KEY` — no account needed: the vendor prints one for anyone at <https://llmtech.eu/docs/>, `lt-trial-ba1ef28c6d32ed6980678d8d`
- Callable ids: `nvidia/Qwen3.8-27B-NVFP4`
- What you send is not used to train models ([the vendor's words](https://llmtech.eu/privacy)).

### [Hetzner Inference API](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hetzner-inference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-17

OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 4,000,000 input tokens/60 seconds; 100,000 output tokens/60 seconds; 10 requests/60 seconds per key

Free while the Inference API remains experimental; Hetzner says it will email advance notice of a change. Per-key request and token windows both apply, with HTTP 429 at a cap. No daily, monthly or lifetime cap or end date is published. The service is offered as is for experimental use, without guaranteed availability or backups. Minting a token needs a Hetzner account; payment verification can include a card charge or other routes.

</details>

- Base URL: `https://inference.hetzner.com/api/v1`
- Key: `HETZNER_INFERENCE_API_KEY` — get one at <https://experiments.hetzner.com/inference>
- Callable ids: `Qwen3.8-27B`
- What you send is not used to train models ([the vendor's words](https://www.hetzner.com/legal/privacy-policy/)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-08 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical signup grant: 1,000,000 tokens once per account per model (Valid for 90 days from activation, model release or approval, whichever is later)

Free grants apply in Singapore (international) only, independently per model and dated snapshot. The model pricing tables decide eligibility: Kimi has no free-quota column and glm-5.2-fast-preview has none. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-08 · listed since 2026-09-17

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 30-day trial: 1,000,000 tokens/day per account

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

### [VLM Run Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vlm-run-gateway/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-17

OpenAI-compatible gateway whose GPU-served vision and language models accept anonymous callers — no signup or key — in beta

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Anonymous lane: 10 requests/minute; 30 requests/hour; 100 requests/day per IP

GPU-served models are public and anonymous; frontier models require paid access. All three IP windows apply together and are shared by callers behind the same NAT or proxy. The gateway is beta; anonymous access is intended for evaluation. The operator is Autonomi AI Inc.; its terms render in a browser.

</details>

- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `qwen/qwen3.8-27b`

### [OVHcloud AI Endpoints](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-17

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Anonymous lane: 2 requests/minute sharing scope disputed

The documentation attributes the anonymous cap to IP and model. Tests on 2026-09-24 instead observed callers sharing a model's anonymous capacity, so its effective sharing scope remains disputed. Anonymous requests can receive 429 before a caller has spent the documented cap. Authenticated API keys are metered per token and use the paid project/model limits; they do not create a larger free allowance.

</details>

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `Qwen3.8-27B`
- What you send is not used to train models ([the vendor's words](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)).

## Rows that listed it before

- [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) — listed 2026-10-02 to 2026-10-06
- [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) — listed 2026-10-02 to 2026-10-05

## Related models

- [`qwen3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-flash/) — free at Alibaba Cloud Model Studio (DashScope, international) and Yolo-Auto
- [`qwen3.8-2.4t-a95b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-2.4t-a95b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.8-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-max/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
