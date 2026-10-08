---
layout: default
title: 'qwen3-8b free: 2 providers, limits and ids, verified 2026-10-08'
description: qwen3-8b is served free by Alibaba Cloud Model Studio (DashScope, international) and SiliconFlow (China). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/qwen3-8b/
last_modified_at: 2026-10-08
crumb: qwen3-8b
---

{% raw %}

# Where qwen3-8b is free

**2 rows on the list serve `qwen3-8b` free:** Alibaba Cloud Model Studio (DashScope, international) and SiliconFlow (China). None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

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
- Callable ids: `qwen3-8b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [SiliconFlow (China)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/)

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · verified 2026-10-08 · listed since 2026-09-19

China's SiliconFlow prices eight small chat models at ¥0 for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Verified free models: Usage allowance: see your account for values (period not published) per account per model

Free models are zero-priced but require real-name verification. Online verification uses an Alipay face scan and accepted mainland, Hong Kong, Macau, Taiwan or Chinese permanent-residence documents; other applicants must contact staff. Sign in by SMS or email. Per-model fixed rate values are shown in the client-rendered model square, rather than public docs.

</details>

- Base URL: `https://api.siliconflow.cn/v1`
- Key: `SILICONFLOW_CN_API_KEY` — get one at <https://cloud.siliconflow.cn/account/ak>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.siliconflow.cn`
- Callable ids: `Qwen/Qwen3-8B`
- What you send is not used to train models ([the vendor's words](https://docs.siliconflow.cn/docs/legals/privacy-policy)).

## Related models

- [`qwen3-coder-next`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3-coder-next/) — free at Kiro and Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3-max/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
