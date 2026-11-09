---
layout: default
title: 'qwen3.8-flash free: 2 providers, limits and ids, provider probes 2026-11-09'
description: qwen3.8-flash is served free by Alibaba Cloud Model Studio (DashScope, international) and Qoder CN (formerly Lingma). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/qwen3.8-flash/
last_modified_at: 2026-11-09
crumb: qwen3.8-flash
---

{% raw %}

# Where qwen3.8-flash is free

**2 rows on the list serve `qwen3.8-flash` free:** Alibaba Cloud Model Studio (DashScope, international) and Qoder CN (formerly Lingma). None asks for a card. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

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
- Callable ids: `qwen3.8-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Qoder CN (formerly Lingma)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/qoder-cn/)

🤖 Coding agents & CLIs · no card · last probe 2026-11-09 · listed since 2026-10-12

Alibaba Cloud's coding apps for China, formerly Tongyi Lingma, with a free personal-model promotion alongside a two-week 300-credit trial and 100 credits a day to claim in the desktop app

- Limits, in the vendor's words: Qwen3.8 Flash promotion: Daily requests allowance: amount not published per account per model; for `Qwen3.8-Flash`

Pro trial: 300 credits once per account (Valid for 2 weeks)

Claimed promotional credit: 100 credits/day per account (Each claim valid for 30 days)

Basic-model fallback: Completions allowance: amount not published (period not published) per account

The model promotion is open to personal users, including free accounts with zero credits; it needs no paid subscription or claim and works across the CN apps, including CLI. Daily free uses are limited, with more for paid accounts; after the allowance, wait until the next day or spend Credits. Its end is "结束时间将提前在本页公告" (to be announced in advance). The separate daily credit promotion must be claimed in the desktop app; its end is "结束时间：另行公告" (to be announced). Each claim window runs from 10:00 to the next day at 10:00 Beijing time (UTC+8); unclaimed credit does not accumulate. After trial credit runs out, a basic model still provides limited completion. Signup requires an Alibaba Cloud account bound to a phone number; real-name verification is needed for purchases. Qoder and Qoder CN are "separate product systems"; their accounts, tasks and data are not interoperable.
- No API endpoint to paste: this row is a tool you install or sign in to.
- In Qoder CN (formerly Lingma)'s own model list: `Qwen3.8-Flash`

## Rows that listed it before

- [Qoder](https://mvalentsev.github.io/awesome-free-ai-coding/providers/qoder/) — listed 2026-10-28 to 2026-11-08
- [Yolo-Auto](https://mvalentsev.github.io/awesome-free-ai-coding/providers/yolo-auto/) — listed 2026-09-16 to 2026-10-15; the row itself is archived

## Related models

- [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/) — free at Groq, LLMTR, Hetzner Inference API, Alibaba Cloud Model Studio (DashScope, international), IteraCompute (until 2026-11-24), Regolo AI, VLM Run Gateway and OVHcloud AI Endpoints
- [`qwen3.8-2.4t-a95b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-2.4t-a95b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.8-max`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-max/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
