---
layout: default
title: 'qwen3.8-max free: 2 providers, limits and ids, provider probes 2026-11-09'
description: qwen3.8-max is served free by LLMTR and Alibaba Cloud Model Studio (DashScope, international). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/qwen3.8-max/
last_modified_at: 2026-11-09
crumb: qwen3.8-max
---

{% raw %}

# Where qwen3.8-max is free

**2 rows on the list serve `qwen3.8-max` free:** LLMTR and Alibaba Cloud Model Studio (DashScope, international). None asks for a card. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/qwen3-8-max), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-09

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

- Limits, in the vendor's words: Qwen3.8 Max promotion: 3,000,000 tokens (period not published) per account per model; for `qwen/qwen3.8-max-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free chat rows can be called on a new account with zero balance before any top-up. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model".

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `qwen/qwen3.8-max-free`
- `qwen/qwen3.8-max-free`: free until 2026-11-13 03:00+03:00 ([conditions](https://llmtr.com/models/qwen/qwen3.8-max-free))
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-11-09 · listed since 2026-09-10

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
- Callable ids: `qwen3.8-max`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

## Related models

- [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/) — free at Groq, LLMTR, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), IteraCompute (until 2026-11-24), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints
- [`qwen3.8-2.4t-a95b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-2.4t-a95b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-flash/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-11-11 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
