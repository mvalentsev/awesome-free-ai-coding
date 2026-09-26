---
layout: default
title: 'qwen3-8b free: 2 providers, limits and ids, verified 2026-09-24'
description: qwen3-8b is served free by Alibaba Cloud Model Studio (DashScope, international) and SiliconFlow (China). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/qwen3-8b/
last_modified_at: 2026-09-26
crumb: qwen3-8b
---

{% raw %}

# Where qwen3-8b is free

**2 rows on the list serve `qwen3-8b` free:** Alibaba Cloud Model Studio (DashScope, international) and SiliconFlow (China). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-09-24 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3-8b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [SiliconFlow (China)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/)

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · provisional since 2026-09-19 · verified 2026-09-24 · listed since 2026-09-19

China's SiliconFlow prices eight small chat models at ¥0 for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

- Limits, in the vendor's words: The rate-limit FAQ: free models cost nothing ("免费模型调用免费", billed at 0), their limits are fixed per model ("免费模型的 Rate Limits 固定", shown in the client-rendered model square), and "实名认证后使用全部的免费模型" — they open only after real-name verification. That is an Alipay face scan taking a mainland ID card, a Hong Kong, Macau or Taiwan travel or residence permit, or China's permanent-residence card for foreigners; without one "暂时不支持线上个人认证", and the FAQ offers a form to the staff instead. Sign-in is by SMS or email. The free rows are in the price list's own data, each at ¥0 in and out: Qwen3-8B, GLM-4-9B-0414, GLM-Z1-9B-0414, Qwen2.5-7B-Instruct, Qwen3.5-4B, DeepSeek-R1-0528-Qwen3-8B, Hunyuan-MT-7B and Xing4.0-29B, the last two also marked 免费 in the table the page renders. Read 2026-09-18
- Base URL: `https://api.siliconflow.cn/v1`
- Key: `SILICONFLOW_CN_API_KEY` — get one at <https://cloud.siliconflow.cn/account/ak>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.siliconflow.cn`
- Callable ids: `Qwen/Qwen3-8B`, `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`
- What you send is not used to train models ([the vendor's words](https://docs.siliconflow.cn/docs/legals/privacy-policy)).

## Related models

- [`qwen3-coder-next`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3-coder-next/) — free at Kiro and Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3-max/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
