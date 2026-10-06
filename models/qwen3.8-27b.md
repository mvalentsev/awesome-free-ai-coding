---
layout: default
title: 'qwen3.8-27b free: 8 providers, limits and ids, verified 2026-10-05'
description: qwen3.8-27b is served free by Groq, LLMTR, LLM Tech, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints. None asks for a card; LLM Tech, VLM Run Gateway and OVHcloud AI Endpoints answer with no account at all. Each…
permalink: /models/qwen3.8-27b/
last_modified_at: 2026-10-06
crumb: qwen3.8-27b
---

{% raw %}

# Where qwen3.8-27b is free

**8 rows on the list serve `qwen3.8-27b` free:** Groq, LLMTR, LLM Tech, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints. None asks for a card; LLM Tech, VLM Run Gateway and OVHcloud AI Endpoints answer with no account at all. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-8-27b).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Groq](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-17

Fast inference against a free plan Groq publishes as a per-model rate table

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Groq states the free plan as a table rather than one quota, in RPM / RPD / TPM / TPD: 30 / 1K / 8K / 200K on openai/gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b and qwen/qwen3.8-27b, 30 / 14.4K / 15K / 500K on the two meta-llama/llama-prompt-guard classifiers, 20 / 2K on the two whisper models and 10 / 100 / 1.2K / 3.6K on the two canopylabs/orpheus voices (read 2026-09-27). Those ten rows are the whole free plan, with no Llama among them — the Llama ids in the page's API samples are not on it. Groq calls the table "a high level summary and there may be exceptions", and points at the limits page in an account for the exact figures

</details>

- Base URL: `https://api.groq.com/openai/v1`
- Key: `GROQ_API_KEY` — get one at <https://console.groq.com/keys>
- Callable ids: `qwen/qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://console.groq.com/docs/legal/services-agreement)).

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-10-05

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published

A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak işaretlenen bir chat modelini seçin" (pick a free chat model), and "Bu adım, sıfır bakiye ile gateway ve kullanım kaydı akışının çalıştığını doğrular" (checks gateway use on a zero balance). Laguna XS 2.1 is free because "Poolside serves these models free on its own inference API", with "no extra token allowance to track". Paid use is prepaid credit: "An 8% platform margin is added on top of the requested top-up amount", and "The platform margin is not added to model prices; it is applied only once, at top-up". The privacy page says prompt and response bodies are not written permanently to its usage and billing database ("kalıcı olarak yazılmaz"). Apodex Mini has an unpublished daily per-account cap and may close before its deadline if the promotion pool runs out. Read 2026-10-06

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `qwen/qwen3.8-27b-free`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

### [LLM Tech](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtech/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-18

EU provider of one model whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 4 concurrent requests, tool calls included, no account

- Limits, in the vendor's words: The quickstart prints the key itself: "Shared and rate-limited: 4 concurrent requests and 2M tokens per day per address, counted across prompt and completion and reset at 00:00 UTC. Enough to evaluate, not enough to run on." A personal key "with no daily limit is issued the same day" by email, paid "Per token. No subscription, no minimums", and "it shares the endpoint's 64 requests in flight with other keys". The model is the NVFP4 build of Qwen3.8-27B — "the trial key allows 4 for everyone using it together and a context of 131,072 tokens. Other keys get the full 262,144." — with tool calling, structured outputs and image input. Prompts and completions are held in "volatile memory only — never persisted" and never trained on; metadata, the source IP among it, is kept 13 months as billing evidence. The operator is one person, Artem Burei, trading as a sole proprietorship in Poland, serving since 22 August 2026 from GPUs in Italy behind an edge in Germany. Read 2026-09-27
- Base URL: `https://api.llmtech.eu/v1`
- Key: `LLMTECH_API_KEY` — no account needed: the vendor prints one for anyone at <https://llmtech.eu/docs/>, `lt-trial-ba1ef28c6d32ed6980678d8d`
- Callable ids: `nvidia/Qwen3.8-27B-NVFP4`
- What you send is not used to train models ([the vendor's words](https://llmtech.eu/privacy)).

### [Hetzner Inference API](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hetzner-inference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-17

OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Hetzner answers it in its own FAQ: "As long as the Inference API remains in experimental status, it is free of charge. Should this status change, we will notify you in advance via email with detailed information." Published per API key: 4M input and 100k output tokens per 60s, plus 10 requests per 60s, HTTP 429 over either. No daily, monthly or lifetime cap is published and no end date is named — the same page calls the service experimental, "provided for experimental purposes only" and offered as is, with performance and availability not guaranteed and no backups. A Hetzner account is needed to mint a token and the docs do not say whether a payment method is required; Hetzner's own fraud-prevention page offers a card charge as one of several verification routes (read 2026-08-30)

</details>

- Base URL: `https://inference.hetzner.com/api/v1`
- Key: `HETZNER_INFERENCE_API_KEY` — get one at <https://experiments.hetzner.com/inference>
- Callable ids: `Qwen3.8-27B`
- What you send is not used to train models ([the vendor's words](https://www.hetzner.com/legal/privacy-policy/)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-05 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.8-27b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-05 · listed since 2026-09-17

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

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-17

OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha

- Limits, in the vendor's words: The authentication page says it plainly: "The VLM Run Gateway serves anonymous callers on a small free quota, keyed by client IP", and "Every GPU-served model is public and reachable anonymously", while "The frontier models carry the paid access tier". The rate-limit table gives the anonymous tier "10/min, 30/hr, 100/day" per client IP, the three windows stacking, against 240 a minute with a key. The FAQ calls the gateway alpha, with a model catalog kept intentionally small: its chat models on VLM Run GPUs are Qwen3.8 27B, Qwen3.5 0.8B and DiffusionGemma 26B, beside OCR, embedding and speech models. The published request schema has no tools field, yet a keyless call carrying one tool was answered with a tool call on 2026-09-17. The operator is Autonomi AI Inc.; its terms render only in a browser. Read 2026-09-23
- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `qwen/qwen3.8-27b`

### [OVHcloud AI Endpoints](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-17

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: OVHcloud documents the anonymous lane: "Anonymous: 2 requests per minute, per IP and per model. Authenticated with an API access key: 400 requests per minute, per PCI project and per model", and its product page says "Test all our models for free in a sandbox or via the API". It is not counted per IP in practice: on 2026-09-24 one call a minute to Qwen3.8-27B from an address nothing else used answered twice in five, and each answer left `ratelimit-remaining: 0`, another caller having spent the minute's other request; the first call of a minute on six ids, and every call from a GitHub runner that morning, answered 429. The two requests a minute per model are shared by every anonymous caller. A key bills every chat model per token, Qwen3.8-27B at "0.4 € / Mtoken(input)" and "2.7 € / Mtoken(output)". Read 2026-09-24

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

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
