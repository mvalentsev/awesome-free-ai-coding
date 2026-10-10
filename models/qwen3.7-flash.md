---
layout: default
title: 'qwen3.7-flash free: 2 providers, limits and ids, verified 2026-10-08'
description: qwen3.7-flash is served free by Alibaba Cloud Model Studio (DashScope, international) and BazaarLink. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/qwen3.7-flash/
last_modified_at: 2026-10-08
crumb: qwen3.7-flash
---

{% raw %}

# Where qwen3.7-flash is free

**2 rows on the list serve `qwen3.7-flash` free:** Alibaba Cloud Model Studio (DashScope, international) and BazaarLink. None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week.

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
- Callable ids: `qwen3.7-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [BazaarLink](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-08-03

OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Without credit: 10 requests/minute; 60 weighted units/day per account

With credit: 20 requests/minute; 120 weighted units/day per account

Free models: 2 requests at once per account

Free models: 15 requests/minute shared across the endpoint

The free models share each account's daily weighted allowance, reset at 00:00 UTC. Longer inputs can consume more units. Account concurrency and the site-wide rate also apply. Paid fallback happens only when enabled and the account has sufficient credit. Free IDs and their metered twins are separate catalog routes.

</details>

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`

## Related models

- [`qwen3.7-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-max/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.7-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-plus/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
