---
layout: default
title: 'Alibaba Cloud Model Studio (DashScope, international) free tier: limits, free models, verified 2026-10-26'
description: 'Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible. Free models: qwen3.8-max, qwen3.8-flash, qwen3.8-2.4t-a95b, qwen3.8-27b, deepseek-v4-pro, deepseek-v4-flash, deepseek-v4.1-flash…'
permalink: /providers/alibaba-model-studio/
last_modified_at: 2026-10-29
crumb: Alibaba Cloud Model Studio (DashScope, international)
---

{% raw %}

# Alibaba Cloud Model Studio (DashScope, international) free tier

🔌 LLM APIs with free tier · no card · not offered in mainland China · **live** — last verified by a probe on 2026-10-26 · [alibabacloud.com](https://www.alibabacloud.com/en/product/modelstudio) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible

## Free models

[`qwen3.8-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-max/), [`qwen3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-flash/), [`qwen3.8-2.4t-a95b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-2.4t-a95b/), [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/), [`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/), [`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/), [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/), [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/), [`qwen3.7-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-max/), [`qwen3.7-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-plus/), [`qwen3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.7-flash/), [`qwen3.6-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-plus/), `qwen3.6-flash`, [`qwen3.6-35b-a3b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-35b-a3b/), [`qwen3.6-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6-27b/), `qwen3.5-plus`, `qwen3.5-flash`, [`qwen3.5-397b-a17b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-397b-a17b/), [`qwen3.5-122b-a10b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-122b-a10b/), [`qwen3.5-35b-a3b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-35b-a3b/), [`qwen3.5-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-27b/), `qwen3-coder-flash`, `qwen-max`, `qwen-plus`, `qwen-flash`, `qwen3-vl-plus`, [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/)

## Limits, in the vendor's words

Typical model token grant: 1,000,000 tokens once per account per model (Where granted; valid for 90 days from activation, model release or approval, whichever is later)

Removed model-grant campaigns: Usage allowance: see your account for values (period not published) per account per model (only previously issued quotas, until expiry or exhaustion; no new grants)

Separate OAuth allowance: 2,000 requests/day; scope not published (separate from API-key token grants)

Free token grants apply in Singapore (international), independently per model and dated snapshot. Current pricing tables decide new-grant eligibility. Some older models and snapshots no longer receive new grants; previously issued quotas remain usable until expiry or exhaustion. Check the console for each model's remaining quota. Kimi and glm-5.2-fast-preview have no API-key grant. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default. OAuth has a separate allowance; its eligible models and reset time are not established here.

## Where it is offered

Not offered in mainland China ([source](https://www.alibabacloud.com/help/en/account/step-1-register-an-alibaba-cloud-account), read 2026-09-26). That leaves out 5.9% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “The Alibaba Cloud international site does not support selecting the Chinese mainland as the registration region, and does not support binding a mobile number of the Chinese mainland”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Alibaba Cloud strictly protects your data privacy and will never use your data for model training.” ([source](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

## Connect

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `qwen3.8-max`, `qwen3.8-flash`, `qwen3.8-2.4t-a95b`, `qwen3.8-27b`, `deepseek-v4-pro`, `deepseek-v4-flash-0731`, `deepseek-v4.1-flash`, `glm-5.3`, `glm-5.2`, `qwen3.7-max`, `qwen3.7-plus`, `qwen3.7-flash`, `qwen3.6-plus`, `qwen3.6-flash`, `qwen3.6-35b-a3b`, `qwen3.6-27b`, `qwen3.5-plus`, `qwen3.5-flash`, `qwen3.5-397b-a17b`, `qwen3.5-122b-a10b`, `qwen3.5-35b-a3b`, `qwen3.5-27b`, `qwen3-coder-flash`, `qwen-max`, `qwen-plus`, `qwen-flash`, `qwen3-vl-plus`, `glm-5.1`
- Note: Singapore (international) endpoint; use a region-specific general-purpose pay-as-you-go key, not a Token Plan or Coding Plan key. Call the exact IDs listed here. Enable Free Quota Only per model and wait for the setting to take effect before calling. Check each ID's remaining free token quota before use; removed grants survive only for existing recipients. These API-key profiles do not use the separate OAuth allowance.

Try it from your terminal with your key in `ALIBABA_MODEL_STUDIO_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $ALIBABA_MODEL_STUDIO_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3.8-max","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.alibabacloud.com/help/en/model-studio/model-pricing>, anchored on `free quota`, `valid for 90 days`
- Source: <https://www.alibabacloud.com/help/en/model-studio/model-pricing>
- Source: <https://www.alibabacloud.com/help/en/model-studio/new-free-quota>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-12` — Free models changed: dropped deepseek-v3.2, qvq-max, qwen-turbo, qwen-vl-max, qwen-vl-plus, qwen3-14b, qwen3-235b-a22b, qwen3-235b-a22b-instruct-2507, qwen3-235b-a22b-thinking-2507, qwen3-30b-a3b, qwen3-30b-a3b-instruct-2507, qwen3-30b-a3b-thinking-2507, qwen3-32b, qwen3-8b, qwen3-coder-30b-a3b, qwen3-coder-480b-a35b, qwen3-coder-next, qwen3-coder-plus, qwen3-max, qwen3-next-80b-a3b-instruct, qwen3-next-80b-a3b-thinking, qwen3-vl-235b-a22b-instruct, qwen3-vl-235b-a22b-thinking, qwen3-vl-30b-a3b-instruct, qwen3-vl-30b-a3b-thinking, qwen3-vl-32b-instruct, qwen3-vl-32b-thinking, qwen3-vl-8b-instruct, qwen3-vl-8b-thinking, qwen3-vl-flash, qwen3.6-max, qwq-plus
- `2026-09-30` — Free models changed: added glm-5.2, glm-5.3
- `2026-09-28` — Free models changed: added deepseek-v4.1-flash
- `2026-09-25` — Free models changed: added deepseek-v3.2, deepseek-v4-flash, deepseek-v4-pro, glm-5.1, qvq-max, qwen-flash, qwen-max, qwen-plus, qwen-turbo, qwen-vl-max, qwen-vl-plus, qwen3-14b, qwen3-235b-a22b, qwen3-235b-a22b-instruct-2507, qwen3-235b-a22b-thinking-2507, qwen3-30b-a3b, qwen3-30b-a3b-instruct-2507, qwen3-30b-a3b-thinking-2507, qwen3-32b, qwen3-8b, qwen3-coder-30b-a3b, qwen3-coder-480b-a35b, qwen3-coder-flash, qwen3-coder-next, qwen3-coder-plus, qwen3-next-80b-a3b-instruct, qwen3-next-80b-a3b-thinking, qwen3-vl-235b-a22b-instruct, qwen3-vl-235b-a22b-thinking, qwen3-vl-30b-a3b-instruct, qwen3-vl-30b-a3b-thinking, qwen3-vl-32b-instruct, qwen3-vl-32b-thinking, qwen3-vl-8b-instruct, qwen3-vl-8b-thinking, qwen3-vl-flash, qwen3-vl-plus, qwen3.5-122b-a10b, qwen3.5-27b, qwen3.5-35b-a3b, qwen3.5-397b-a17b, qwen3.5-flash, qwen3.5-plus, qwen3.6-27b, qwen3.6-35b-a3b, qwen3.6-flash, qwen3.6-max, qwen3.6-plus, qwen3.7-flash, qwen3.7-max, qwen3.7-plus, qwen3.8-2.4t-a95b, qwen3.8-27b, qwen3.8-flash, qwq-plus; dropped qwen3-coder
- `2026-09-10` — Free models changed: added qwen3.8-max
- `2026-07-19` — Added: Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
