---
layout: default
title: 'qwen3.8-flash free: 2 providers, limits and ids, verified 2026-09-24'
description: qwen3.8-flash is served free by Alibaba Cloud Model Studio (DashScope, international) and Yolo-Auto. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/qwen3.8-flash/
last_modified_at: 2026-09-26
crumb: qwen3.8-flash
---

{% raw %}

# Where qwen3.8-flash is free

**2 rows on the list serve `qwen3.8-flash` free:** Alibaba Cloud Model Studio (DashScope, international) and Yolo-Auto. None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-8-flash-next).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-09-24 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.8-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Yolo-Auto](https://mvalentsev.github.io/awesome-free-ai-coding/providers/yolo-auto/)

🔌 LLM APIs with free tier · no card · provisional since 2026-09-14 · verified 2026-09-24 · listed since 2026-09-16

One open-weight Qwen model served on the vendor's own flat-rate API for coding agents; the free plan is 15 requests a week with no card

- Limits, in the vendor's words: "15 free requests a week. No card required. Resets Monday at 00:00 UTC." on the home page and "No card required, free forever" on the Free plan card, at 128K context, against $19/mo Builder and $39/mo Pro — a handful of agent turns a week. The model is Qwen3.8 Flash, id qwen3.8-flash, charted with Artificial Analysis scores for Qwen3.8-Flash-Next, the mixture-of-experts Qwen published open-weight on 2026-08-24 (about 180B parameters, 10 of 512 experts active). Yolo-Auto "runs the model-serving stack rather than reselling a third-party model API". The FAQ calls the free tier "for testing" where the plan card says "free forever", and the terms forbid using "multiple accounts ... to combine capacity". Sign-in is through Google, GitHub or Discord, and prompt and response bodies are "not stored or retained". Read 2026-09-25
- Base URL: `https://yolo-auto.com/v1`
- Key: `YOLO_AUTO_API_KEY` — get one at <https://yolo-auto.com/app>
- Callable ids: `qwen3.8-flash`
- What you send is not used to train models ([the vendor's words](https://yolo-auto.com/pricing)).

## Related models

- [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/) — free at Groq, LLM Tech, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints
- [`qwen3.8-2.4t-a95b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-2.4t-a95b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.8-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-max/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
