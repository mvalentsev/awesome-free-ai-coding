---
layout: default
title: 'qwen3.8-27b free: 8 providers, limits and ids, provider probes 2026-11-12'
description: qwen3.8-27b is served free by Groq, LLMTR, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), IteraCompute, Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints. None asks for a card; VLM Run Gateway and OVHcloud AI Endpoints answer with no account at all. Each one's…
permalink: /models/qwen3.8-27b/
last_modified_at: 2026-11-12
crumb: qwen3.8-27b
---

{% raw %}

# Where qwen3.8-27b is free

**8 rows on the list serve `qwen3.8-27b` free:** Groq, LLMTR, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), IteraCompute, Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints. None asks for a card; VLM Run Gateway and OVHcloud AI Endpoints answer with no account at all. The providers' last scheduled probes were on 2026-11-12; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-09-17

Fast inference against a free plan Groq publishes as a per-model rate table

- Limits, in the vendor's words: Coding models: 30 requests/minute; 1,000 requests/day; 8,000 tokens/minute; 200,000 tokens/day per organization per model; for `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: These are the Free Plan limits for the coding models, shared by keys in the same organization. Classifiers, guardrails, speech and voice models have separate limits; their API examples do not establish free coding-model eligibility. Groq calls the table "a high level summary and there may be exceptions"; the account limits page gives the exact values.

</details>

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `qwen/qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-12 · listed since 2026-10-05

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

- Limits, in the vendor's words: Nemotron Ultra and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `qwen/qwen3.8-27b-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free chat rows can be called on a new account with zero balance before any top-up. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model".

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `qwen/qwen3.8-27b-free`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/)).

### [Hetzner Inference API](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hetzner-inference/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-09-17

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

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-11-12 · listed since 2026-09-25

Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical model token grant: 1,000,000 tokens once per account per model (Where granted; valid for 90 days from activation, model release or approval, whichever is later)

Removed model-grant campaigns: Usage allowance: see your account for values (period not published) per account per model (only previously issued quotas, until expiry or exhaustion; no new grants)

Separate OAuth allowance: 2,000 requests/day; scope not published (separate from API-key token grants)

Free token grants apply in Singapore (international), independently per model and dated snapshot. Current pricing tables decide new-grant eligibility. Some older models and snapshots no longer receive new grants; previously issued quotas remain usable until expiry or exhaustion. Check the console for each model's remaining quota. Kimi and glm-5.2-fast-preview have no API-key grant. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default. OAuth has a separate allowance; its eligible models and reset time are not established here.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [IteraCompute](https://mvalentsev.github.io/awesome-free-ai-coding/providers/iteracompute/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-10-21

OpenAI-compatible API with recurring free usage on a self-hosted open model and an automatic router

- Limits, in the vendor's words: Shared free-model allowance: 30,000,000 tokens/month per account; for `qwen/qwen3.8-27b`, `Auto`. Allowances reset on the first of each month at 00:00 UTC (08:00 Beijing time); unused tokens do not roll over.

Shared free-model slot: 1 request at once per account

Register and verify an email, or sign in with Google. Input and output, including reasoning, count across all account keys and free routes. "Context includes input and requested output; output is capped at 8,192 tokens." Free total context is 128K. There is no RPM, TPM or daily token cap. Requests reserve maximum usage, then settle actual usage; exhausted quota returns 429 without automatic paid overage. No recharge is required. Optional cumulative $10/$50 top-ups unlock larger allowances; new external payments add an 8% fee. Thresholds use completed principal minus refunds, excluding grants and fees. Spending keeps the tier; refunds may lower it. Shared capacity may queue; honor Retry-After. No SLA. Zero data retention requires a separate signed agreement. The no-recharge promotion has a deadline; recharged users retain tier benefits while model names, weights and precision may change.
- Base URL: `https://api.iteracompute.com/v1`
- Key: `ITERACOMPUTE_API_KEY` — get one at <https://platform.iteracompute.com/api-keys>
- Callable ids: `qwen/qwen3.8-27b`
- `qwen/qwen3.8-27b`: free until 2026-11-24 00:00-08:00 ([conditions](https://iteracompute.com/free/))
- What you send is not used to train models ([the vendor's words](https://iteracompute.com/privacy.html)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · last probe 2026-11-12 · listed since 2026-09-17

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 30-day trial: 1,000,000 tokens/day per account

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. Brick v1 Beta is a lightweight prompt-complexity classifier for LLM routing pipelines and is excluded from coding configs.

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

### [VLM Run Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vlm-run-gateway/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-09-17

OpenAI-compatible gateway whose GPU-served vision and language models accept anonymous callers — no signup or key — in beta

> ⚠️ **Does not work as published since [2026-11-05](https://docs.vlm.run/gateway/authentication).** Anonymous requests to `qwen/qwen3.8-27b`, the listed tool-capable model, currently return HTTP 403 asking for an API key. Its anonymous coding-agent connection is unavailable in the current checks; the other listed IDs are ordinary-chat choices.

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Anonymous lane: 10 requests/minute; 30 requests/hour; 100 requests/day per IP

GPU-served models are public and anonymous; frontier models require paid access. All three IP windows apply together and are shared by callers behind the same NAT or proxy. The gateway is beta; anonymous access is intended for evaluation. The operator is Autonomi AI Inc.; its terms render in a browser.

</details>

- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `qwen/qwen3.8-27b`

### [OVHcloud AI Endpoints](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-09-17

EU-hosted serverless API for open models, with anonymous OpenAI-compatible access and no signup, key or card

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

- [LLM Tech](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtech/) — listed 2026-09-18 to 2026-11-01; the row itself is archived
- [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) — listed 2026-10-02 to 2026-10-06
- [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) — listed 2026-10-02 to 2026-10-05

## Related models

- [`qwen3.8-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-max/) — free at LLMTR (until 2026-11-13) and Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-flash/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.8-2.4t-a95b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-2.4t-a95b/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
