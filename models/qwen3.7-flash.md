---
layout: default
title: 'qwen3.7-flash free: 2 providers, limits and ids, provider probes 2026-11-09'
description: qwen3.7-flash is served free by Alibaba Cloud Model Studio (DashScope, international) and BazaarLink. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/qwen3.7-flash/
last_modified_at: 2026-11-10
crumb: qwen3.7-flash
---

{% raw %}

# Where qwen3.7-flash is free

**2 rows on the list serve `qwen3.7-flash` free:** Alibaba Cloud Model Studio (DashScope, international) and BazaarLink. None asks for a card. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-11-09 · listed since 2026-09-25

Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical model token grant: 1,000,000 tokens once per account per model (Where granted; valid for 90 days from activation, model release or approval, whichever is later)

Removed model-grant campaigns: Usage allowance: see your account for values (period not published) per account per model (only previously issued quotas, until expiry or exhaustion; no new grants)

Separate OAuth allowance: 2,000 requests/day; scope not published (separate from API-key token grants)

Free token grants apply in Singapore (international), independently per model and dated snapshot. Current pricing tables decide new-grant eligibility. Some older models and snapshots no longer receive new grants; previously issued quotas remain usable until expiry or exhaustion. Check the console for each model's remaining quota. Kimi and glm-5.2-fast-preview have no API-key grant. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default. OAuth has a separate allowance; its eligible models and reset time are not established here.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.7-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [BazaarLink](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-10

OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Without credit: 10 requests/rolling minute; 60 weighted units/day per account

With credit: 20 requests/rolling minute; 120 weighted units/day per account

Free models: 2 requests at once per account

Free models: 20 requests/minute shared across the endpoint

Additional IP guard: Requests allowance: amount not published (period not published) per IP

The free models share each account's daily weighted allowance, reset at 00:00 UTC. Longer inputs can consume more units. Account concurrency and the site-wide rate also apply. The platform grants free eligibility per model; a regular ID can have a free quota alongside its paid price. After the free quota, paid fallback needs an enabled setting and sufficient account credit.

</details>

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `qwen/qwen3.7-flash:free`

## Related models

- [`qwen3.7-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-max/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.7-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-plus/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
