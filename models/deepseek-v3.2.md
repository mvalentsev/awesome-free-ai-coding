---
layout: default
title: 'deepseek-v3.2 free: 2 providers, limits and ids, verified 2026-09-24'
description: deepseek-v3.2 is served free by Kiro and Alibaba Cloud Model Studio (DashScope, international). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/deepseek-v3.2/
last_modified_at: 2026-09-26
crumb: deepseek-v3.2
---

{% raw %}

# Where deepseek-v3.2 is free

**2 rows on the list serve `deepseek-v3.2` free:** Kiro and Alibaba Cloud Model Studio (DashScope, international). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v3-2), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kiro](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kiro/)

🎁 Trials (no card when possible) · no card · verified 2026-09-24 · listed since 2026-08-20

Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models

- Limits, in the vendor's words: 50 credits/month; requires social login or AWS Builder ID; credits do not roll over; not available in AWS GovCloud, and free-tier requests are always served from the US. Kiro's docs settle what those credits reach, in a table with a Free column: ticked for Claude Sonnet 4.5 and 4.0, Auto, GLM-5, Qwen3 Coder Next, DeepSeek 3.2 and MiniMax M2.5 and M2.1; blank for Claude Sonnet 4.6 and 5, every Opus, Haiku 4.5 and all three GPT-5.6 tiers. The pricing page contradicts itself on exactly that point — its plan card and footnote both say Sonnet 4.5, its FAQ prose says the free tier includes Sonnet 4.6 — so read the docs table, not the FAQ (checked 2026-09-25)
- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://kiro.dev/docs/privacy-and-security/data-protection/)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-09-24 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen3.8 Max, DeepSeek V4 Pro and V4.1 Flash, GLM-5.3 among them — valid 90 days from activation or the model's release; OpenAI-compatible

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `deepseek-v3.2`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

## Related models

- [`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/) — free at Routeway, Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS)
- [`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/) — free at Freebuff and Token Harbor
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
