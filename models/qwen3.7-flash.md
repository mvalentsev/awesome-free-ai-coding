---
layout: default
title: 'qwen3.7-flash free: 2 providers, limits and ids, verified 2026-10-01'
description: qwen3.7-flash is served free by Alibaba Cloud Model Studio (DashScope, international) and BazaarLink. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/qwen3.7-flash/
last_modified_at: 2026-10-01
crumb: qwen3.7-flash
---

{% raw %}

# Where qwen3.7-flash is free

**2 rows on the list serve `qwen3.7-flash` free:** Alibaba Cloud Model Studio (DashScope, international) and BazaarLink. None asks for a card. The published offers were checked on 2026-10-01 and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-01 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.7-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [BazaarLink](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-08-03

OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: BazaarLink prints the figures on its free page, one allowance shared across the free models: "No credit: 10 RPM and 60 weighted units/day. With credit: 20 RPM and 120 weighted units/day." Where weighted limits are on, "Longer inputs consume more daily units"; the counter resets at 00:00 UTC, beside a "Site-wide free cap: 15 RPM" and "Concurrent free requests per account: 2". "After a limit, paid use is possible only when fallback is enabled and the account has sufficient credit"; everything else in the catalog is metered at list rates. The free ids are Qwen3.7 Flash and the 0731 revision of DeepSeek V4 Flash, under the catalog's own id deepseek/deepseek-v4-flash-0731free:free, described as "Rate-limited free tier." and listed on the free page as "Deepseek V4 Flash 0731free", priced $0 beside a metered deepseek-v4-flash-0731free twin at $0.20/$0.40. Read 2026-10-01

</details>

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`

## Related models

- [`qwen3.7-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-max/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.7-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-plus/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-02 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
