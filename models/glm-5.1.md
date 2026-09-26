---
layout: default
title: 'glm-5.1 free: 3 providers, limits and ids, verified 2026-09-24'
description: glm-5.1 is served free by AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/glm-5.1/
last_modified_at: 2026-09-25
---

{% raw %}

# Where glm-5.1 is free

**3 rows on the list serve `glm-5.1` free:** AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-25

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Call it: `coding-glm-5.1-free` at `https://aihubmix.com/v1`, with a key in `AIHUBMIX_API_KEY` from <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen3.8 Max, DeepSeek V4 Pro and V4.1 Flash, GLM-5.3 among them — valid 90 days from activation or the model's release; OpenAI-compatible

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)
- Call it: `glm-5.1` at `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`, with a key in `ALIBABA_MODEL_STUDIO_API_KEY` from <https://modelstudio.console.alibabacloud.com>
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

- Limits, in the vendor's words: No quota figure is published: the landing page says "Free to use", "No credit card required" and "Generous quota for research and prototyping", and the terms say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity". It is "an experimental research service", and prompts are not private: "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05
- Call it at `https://freeinference.org/v1`, with a key in `FREEINFERENCE_API_KEY` from <https://freeinference.org> — the row lists no id for this model
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`

## Related models

- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models) and Z.ai (Zhipu GLM)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models) and Regolo AI
- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
