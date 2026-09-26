---
layout: default
title: 'deepseek-v4-flash free: 3 providers, limits and ids, verified 2026-09-24'
description: deepseek-v4-flash is served free by Routeway, Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/deepseek-v4-flash/
last_modified_at: 2026-09-26
crumb: deepseek-v4-flash
---

{% raw %}

# Where deepseek-v4-flash is free

**3 rows on the list serve `deepseek-v4-flash` free:** Routeway, Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v4-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-16

OpenAI-compatible gateway whose :free lane rotates — three zero-priced chat models on 2026-09-23, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 269 metered rows in the same catalog

- Limits, in the vendor's words: Free models — every id ending :free — are capped at 5 requests per minute and 200 per day and answer 429 past either; the pay-as-you-go ids beside them have no API-level rate limits, only edge DDoS protection (docs.routeway.ai, read 2026-08-30). The lane itself rotates, ids joining and leaving within days while their metered twins stay. The gateway publishes no legal entity or terms of service and is supported through Discord alone: a fallback lane, not a dependency
- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Callable ids: `deepseek-v4-flash:free`

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-09-24 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen3.8 Max, DeepSeek V4 Pro and V4.1 Flash, GLM-5.3 among them — valid 90 days from activation or the model's release; OpenAI-compatible

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `deepseek-v4-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

- Limits, in the vendor's words: No quota figure is published: the landing page says "Free to use", "No credit card required" and "Generous quota for research and prototyping", and the terms say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity". It is "an experimental research service", and prompts are not private: "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05
- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `deepseek-v4-flash`

## Rows that listed it before

- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25
- [Sail Research](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) — listed 2026-09-21 to 2026-09-25
- [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/) — listed 2026-09-18 to 2026-09-22
- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-02 to 2026-09-16
- [Sarvam AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sarvam/) — listed 2026-09-05 to 2026-09-16
- [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/) — listed 2026-07-19 to 2026-08-20
- [BazaarLink](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/) — listed 2026-08-03 to 2026-08-19

## Related models

- [`deepseek-v3.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v3.2/) — free at Kiro and Alibaba Cloud Model Studio (DashScope, international)
- [`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/) — free at Freebuff and Token Harbor
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
