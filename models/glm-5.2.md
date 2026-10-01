---
layout: default
title: 'glm-5.2 free: 3 providers, limits and ids, verified 2026-10-01'
description: glm-5.2 is served free by AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and Regolo AI. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/glm-5.2/
last_modified_at: 2026-10-01
crumb: glm-5.2
---

{% raw %}

# Where glm-5.2 is free

**3 rows on the list serve `glm-5.2` free:** AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and Regolo AI. None asks for a card. A live probe confirmed each one on 2026-10-01 and reads them again twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-5-2).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-25

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself, with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex CLI"
- Callable ids: `coding-glm-5.2-free`

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-01 · listed since 2026-09-30

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `glm-5.2`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · verified 2026-10-01 · listed since 2026-09-22

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

- Limits, in the vendor's words: "Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), "1M tokens per day" and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)
- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `glm5.2`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

## Rows that listed it before

- [Scaleway Generative APIs](https://mvalentsev.github.io/awesome-free-ai-coding/providers/scaleway-generative/) — listed 2026-07-19 to 2026-08-14; the row itself is archived

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at NVIDIA NIM (build.nvidia.com), AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova (requires $1 one-time top-up)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-01 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
