---
layout: default
title: 'qwen3.6-35b-a3b free: 2 providers, limits and ids, provider probes 2026-11-19'
description: qwen3.6-35b-a3b is served free by LLMTR and Alibaba Cloud Model Studio (DashScope, international). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/qwen3.6-35b-a3b/
last_modified_at: 2026-11-19
crumb: qwen3.6-35b-a3b
---

{% raw %}

# Where qwen3.6-35b-a3b is free

**2 rows on the list serve `qwen3.6-35b-a3b` free:** LLMTR and Alibaba Cloud Model Studio (DashScope, international). None asks for a card. The providers' last scheduled probes were on 2026-11-19; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-19 · listed since 2026-11-17

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

- Limits, in the vendor's words: Creekside Free models: Usage allowance: amount not published (period not published); scope not published (quantized builds; provider states no request/response storage or training); for `creekside/qwen3.8-27b-creekside-free`, `creekside/qwen3.6-35b-a3b-creekside-free`, `creekside/gemma-4-31b-it-creekside-free`, `creekside/muse-glimmer-30b-creekside-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free chat rows can be called on a new account with zero balance before any top-up. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model".

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `creekside/qwen3.6-35b-a3b-creekside-free`
- `creekside/qwen3.6-35b-a3b-creekside-free`: free until 2026-11-24 00:00+03:00 ([conditions](https://llmtr.com/docs/en/gateway/creekside/))
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-11-19 · listed since 2026-09-25

Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical model token grant: 1,000,000 tokens once per account per model (Where granted; valid for 90 days from activation, model release or approval, whichever is later)

Separate OAuth allowance: 2,000 requests/day; scope not published (separate from API-key token grants)

Free token grants apply in Singapore (international), independently per model and dated snapshot. Current pricing tables decide new-grant eligibility. New grants exclude Qwen3.8 Max 0902, DeepSeek V4.1 Flash 1017, DeepSeek V4 Pro and Kimi K3. Previously issued quotas remain usable until expiry or exhaustion. Check the console for each model's remaining quota. Kimi and glm-5.2-fast-preview have no API-key grant. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default. OAuth has a separate allowance; its eligible models and reset time are not established here.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.6-35b-a3b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

## Related models

- [`qwen3.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6/) — free at Hetzner Inference API, FreeInference (Harvard SEAS) and OVHcloud AI Endpoints
- [`qwen3.6-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-27b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.6-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-plus/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
