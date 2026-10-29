---
layout: default
title: 'qwen3.5-122b-a10b free: 2 providers, limits and ids, provider probes 2026-10-26'
description: qwen3.5-122b-a10b is served free by Alibaba Cloud Model Studio (DashScope, international) and Regolo AI. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/qwen3.5-122b-a10b/
last_modified_at: 2026-10-29
crumb: qwen3.5-122b-a10b
---

{% raw %}

# Where qwen3.5-122b-a10b is free

**2 rows on the list serve `qwen3.5-122b-a10b` free:** Alibaba Cloud Model Studio (DashScope, international) and Regolo AI. None asks for a card. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-10-26 · listed since 2026-09-25

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
- Callable ids: `qwen3.5-122b-a10b`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · last probe 2026-10-26 · listed since 2026-09-27

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 30-day trial: 1,000,000 tokens/day per account

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. One model is priced at €0.00 in and out outside any trial, brick-v1-beta, and it is not one to code with: its own page calls it "a lightweight prompt-complexity classifier designed for LLM routing pipelines", a Qwen3.5-0.8B LoRA that labels a prompt easy, medium or hard for Regolo's Brick router (read 2026-09-21)

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `qwen3.5-122b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

## Related models

- [`qwen3.5-4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-4b/) — free at Mixlayer and SiliconFlow (China)
- [`qwen3.5-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-27b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-35b-a3b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-35b-a3b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-397b-a17b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-397b-a17b/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`qwen3.5-9b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-9b/) — free at Regolo AI

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
