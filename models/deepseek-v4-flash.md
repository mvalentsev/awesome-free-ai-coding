---
layout: default
title: 'deepseek-v4-flash free: 5 providers, limits and ids, verified 2026-10-05'
description: deepseek-v4-flash is served free by Routeway, Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/deepseek-v4-flash/
last_modified_at: 2026-10-05
crumb: deepseek-v4-flash
---

{% raw %}

# Where deepseek-v4-flash is free

**5 rows on the list serve `deepseek-v4-flash` free:** Routeway, Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode and FreeInference (Harvard SEAS). None asks for a card. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v4-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-16

OpenAI-compatible gateway with a rotating :free chat-model lane beside metered models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Rate-limits documentation: 5 requests/minute (published sources disagree) per account

FAQ: 20 requests/minute (published sources disagree) per account

Free models: 200 requests/day per account

The FAQ and rate-limit docs disagree on the per-minute cap; both publish the same daily cap. Free IDs end in :free, rotate and may be removed at any time. At a cap they return 429; paid twins require a positive balance. The FAQ describes signup and key creation without payment, but the older terms list a payment method and are behind a bot wall. No legal entity is named; support is email and Discord.

</details>

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Codex CLI: [`configs/codex/routeway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/routeway.config.toml) — copy it to `~/.codex/`, then `codex -p routeway`; set up on the lane by the vendor's own page, <https://docs.routeway.ai/integrations/agents/codex>: "Use OpenAI’s Codex with Routeway by adding a custom provider"
- Callable ids: `deepseek-v4-flash:free`

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-05 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical signup grant: 1,000,000 tokens once per account per model (Valid for 90 days from activation, model release or approval, whichever is later)

Free grants apply in Singapore (international) only, independently per model and dated snapshot. The model pricing tables decide eligibility: Kimi has no free-quota column and glm-5.2-fast-preview has none. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `deepseek-v4-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [BazaarLink](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-28

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
- Callable ids: `deepseek/deepseek-v4-flash-0731free:free`

### [AtomCode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/atomcode/)

🎁 Trials (no card when possible) · no card · provisional since 2026-09-27 · verified 2026-10-05 · listed since 2026-09-27

Open-source terminal coding agent from AtomGit, the code host run by CSDN and the Open Atom Foundation, whose sign-in claims a free 30-day coding plan, its quota counted in five-hour windows and its claims capped at a thousand a day

- Limits, in the vendor's words: Claimed Lite plan: Rolling 5-hour usage allowance: amount not published per account (Valid for 30 days)

Claimed Lite lasts 30 days; claims have a platform-wide pool of 1,000 slots per day, not a per-user inference cap. A seven-day Pro trial has 100 claim slots at 10:00; a merged activity-repository PR can grant 30 days of Pro and access to GLM-5.2. All plan usage is measured in rolling five-hour windows without published numerical budgets. CodingPlan works inside AtomCode via AtomGit sign-in; other providers use your own key.
- No API endpoint to paste: this row is a tool you install or sign in to.

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Usage allowance: amount varies (period not published) per account

No card. This is an experimental research service with capacity-dependent limits. Prompts and responses may be logged for research; sanitized content, usage statistics and routing metrics may be published or open-sourced. Only models marked Free accept a Free key; Pro catalog rows need a Pro-enabled key.

</details>

- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `deepseek-v4-flash`

## Rows that listed it before

- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25
- [Sail Research](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) — listed 2026-09-21 to 2026-09-25
- [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/) — listed 2026-09-18 to 2026-09-22
- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-02 to 2026-09-16
- [Sarvam AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sarvam/) — listed 2026-09-05 to 2026-09-16
- [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/) — listed 2026-07-19 to 2026-08-20

## Related models

- [`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/) — free at NVIDIA NIM (build.nvidia.com), Freebuff, Alibaba Cloud Model Studio (DashScope, international) and Token Harbor
- [`deepseek-v3.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v3.2/) — free at Kiro and Alibaba Cloud Model Studio (DashScope, international)
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
