---
layout: default
title: 'deepseek-v4-flash free: 5 providers, limits and ids, verified 2026-10-01'
description: deepseek-v4-flash is served free by Routeway, Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/deepseek-v4-flash/
last_modified_at: 2026-10-01
crumb: deepseek-v4-flash
---

{% raw %}

# Where deepseek-v4-flash is free

**5 rows on the list serve `deepseek-v4-flash` free:** Routeway, Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode and FreeInference (Harvard SEAS). None asks for a card. The published offers were checked on 2026-10-01 and are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v4-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-16

OpenAI-compatible gateway with a rotating :free chat-model lane beside metered models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free models — every id ending :free — cost nothing and "are rate-limited to 20 requests/minute and 200 requests/day", the FAQ says, where the rate-limits page gives "5 Requests Per Minute (RPM)" and "200 Requests Per Day (RPD)"; past either they answer 429, and the pay-as-you-go ids beside them "require a positive account balance". The lane itself rotates, ids joining and leaving within days while their metered twins stay, and free models "can be removed at any time". A key is sign-up and Create API Key with no payment step in the FAQ, while the terms, last updated 31.05.2025 behind a bot wall this list's client cannot pass, count a payment method among what any account needs. No legal entity is named, and support is by email and Discord. Read 2026-09-27

</details>

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Codex CLI: [`configs/codex/routeway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/routeway.config.toml) — copy it to `~/.codex/`, then `codex -p routeway`; set up on the lane by the vendor's own page, <https://docs.routeway.ai/integrations/agents/codex>: "Use OpenAI’s Codex with Routeway by adding a custom provider"
- Callable ids: `deepseek-v4-flash:free`

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-01 · listed since 2026-09-25

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions", and the quota "is independent per model and cannot be shared across models", a dated snapshot counting as a model of its own. The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later". The last column of each Singapore table, "Free quota", gives it to every Qwen text model from Qwen3.8 Max down to Qwen3 8B, the Coder and VL lines among them, to DeepSeek V4.1 Flash, V4 Pro, V4 Flash and V3.2, and to GLM-5.3, 5.2 and 5.1; the Kimi table has no such column, glm-5.2-fast-preview reads "None", and its translation, OCR, omni and realtime models are not ones to code with (read 2026-09-25). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `deepseek-v4-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [BazaarLink](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-01 · listed since 2026-09-28

OpenAI-compatible gateway with a shared free allowance on selected models and an auto:free router

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: BazaarLink prints the figures on its free page, one allowance shared across the free models: "No credit: 10 RPM and 60 weighted units/day. With credit: 20 RPM and 120 weighted units/day." Where weighted limits are on, "Longer inputs consume more daily units"; the counter resets at 00:00 UTC, beside a "Site-wide free cap: 15 RPM" and "Concurrent free requests per account: 2". "After a limit, paid use is possible only when fallback is enabled and the account has sufficient credit"; everything else in the catalog is metered at list rates. The free ids are Qwen3.7 Flash and the 0731 revision of DeepSeek V4 Flash, under the catalog's own id deepseek/deepseek-v4-flash-0731free:free, described as "Rate-limited free tier." and listed on the free page as "Deepseek V4 Flash 0731free", priced $0 beside a metered deepseek-v4-flash-0731free twin at $0.20/$0.40. Read 2026-10-01

</details>

- Base URL: `https://api.bazaarlink.ai/v1`
- Key: `BAZAARLINK_API_KEY` — get one at <https://bazaarlink.ai/keys>
- Callable ids: `deepseek/deepseek-v4-flash-0731free:free`

### [AtomCode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/atomcode/)

🎁 Trials (no card when possible) · no card · provisional since 2026-09-27 · verified 2026-10-01 · listed since 2026-09-27

Open-source terminal coding agent from AtomGit, the code host run by CSDN and the Open Atom Foundation, whose sign-in claims a free 30-day coding plan, its quota counted in five-hour windows and its claims capped at a thousand a day

- Limits, in the vendor's words: CodingPlan "offers three tiers" and "Quota is measured on a rolling 5-hour window": Lite, "30 days" on a "Free claim, 1,000 slots/day"; a 7-day Pro Trial on "100 slots/day at 10:00" and a 30-day Pro for a PR merged in its activity repository add GLM-5.2. The plan is served inside AtomCode, which signs in through an AtomGit account (WeChat, SMS or password); other providers take your own key. Lite also carries Qwen3-VL-8B, a vision model. Read 2026-09-27
- No API endpoint to paste: this row is a tool you install or sign in to.

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-01 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: No quota figure is published: the landing page says "Free to use", "No credit card required" and "Generous quota for research and prototyping", and the terms say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity". It is "an experimental research service", and prompts are not private: "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05

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

- [`deepseek-v4.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash/) — free at NVIDIA NIM (build.nvidia.com), Freebuff, Cline, Alibaba Cloud Model Studio (DashScope, international) and Token Harbor
- [`deepseek-v3.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v3.2/) — free at Kiro and Alibaba Cloud Model Studio (DashScope, international)
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-02 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
