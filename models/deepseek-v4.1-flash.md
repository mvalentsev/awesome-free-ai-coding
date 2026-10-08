---
layout: default
title: 'deepseek-v4.1-flash free: 4 providers, limits and ids, verified 2026-10-08'
description: deepseek-v4.1-flash is served free by NVIDIA NIM (build.nvidia.com), Freebuff, Alibaba Cloud Model Studio (DashScope, international) and Token Harbor. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/deepseek-v4.1-flash/
last_modified_at: 2026-10-08
crumb: deepseek-v4.1-flash
---

{% raw %}

# Where deepseek-v4.1-flash is free

**4 rows on the list serve `deepseek-v4.1-flash` free:** NVIDIA NIM (build.nvidia.com), Freebuff, Alibaba Cloud Model Studio (DashScope, international) and Token Harbor. None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v4-1-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-10-08 · listed since 2026-10-02

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `deepseek-ai/deepseek-v4.1-flash`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/)

🤖 Coding agents & CLIs · no card · verified 2026-10-08 · listed since 2026-10-06

Ad-funded coding agent — CLI, desktop, web, cloud and chat — with daily regional credits and conditional free-session access. “No API key, no credit card.”

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Session-based limited mode: 6 one-hour sessions per day per account

“Freebuff is supported by text ads.” “Model prices and usage limits still apply.” Available models depend on the app and access level. “Freebuff collects prompts, messages, code, files, repository data, and agent traces when you use features that need them”. Check the balance and picker in your app.

Daily allowance — the United States, Canada, the United Kingdom, Australia, New Zealand, Ireland, Norway, Sweden, Denmark, Finland, the Netherlands, Austria, Luxembourg, Iceland, Germany, France, Spain, Italy, Portugal, Belgium, Switzerland, Liechtenstein, Malta, South Korea: amount not published (Freebucks per day); Other countries: 25 Freebucks per day; VPN or proxy: 20 Freebucks per day.

Current model hour prices are not published; check your account's picker. Solar Pro 4: shared daily credits; available in limited mode; Solar Mini 4: shared daily credits; available in limited mode; MiMo 2.6 Flash: shared daily credits; available in limited mode; GLM 5.3 Flash: shared daily credits; available in limited mode; DeepSeek V4.1 Flash: shared daily credits; available in limited mode; GPT-6 Luna: shared daily credits; full access only; MiMo 2.6 Pro: shared daily credits; full access only; DeepSeek V4.1 Flash Fast: shared daily credits; full access only; GPT-6.1 Sol: free session with conditions; Gemini 3.8 Flash: paid plan; Muse Spark 1.3: paid plan; Gemini 3.1 Flash Lite: specialist tasks only.

Freebucks buy one-hour model sessions. Gemini 3.8 Flash: “PAID-ONLY row” (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-models.ts). Muse Spark 1.3: “Muse Spark 1.3, on every paid plan.” (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-models.ts). GPT-6.1 Sol: “Free in the US, a paid plan elsewhere, until the promotion ends. One session a day on every plan.” (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-sol-promo.ts). Gemini 3.1 Flash Lite handles specialist tasks such as file finding and research.

MiMo 2.6 Flash is the default on CLI, Desktop, Web, and Cloud. Daily Freebucks refill at midnight in your reset timezone and unused daily Freebucks do not carry over. (source: https://freebuff.com/llms.txt).

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://freebuff.com/llms.txt)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · verified 2026-10-08 · listed since 2026-09-28

A million free tokens on each of its chat models in the Singapore region — Qwen, DeepSeek and GLM among them — valid 90 days from activation or the model's release; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical signup grant: 1,000,000 tokens once per account per model (Valid for 90 days from activation, model release or approval, whichever is later)

Free grants apply in Singapore (international) only, independently per model and dated snapshot. The model pricing tables decide eligibility: Kimi has no free-quota column and glm-5.2-fast-preview has none. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `deepseek-v4.1-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-09-16

OpenAI- and Anthropic-compatible gateway with a standing $0 plan: a rotating lineup of :free ids on a value-based allowance per rolling 7-day period, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free routes: Rolling 7-day list-price value allowance: amount not published per account

60 requests/minute; 1,800 requests/hour per account

"Models on permanent free routes carry an explicit :free model ID and are listed under Free on the Models page", and "That set changes as models are added or retired". "Your first free request starts a personal rolling 7×24-hour period; it is not tied to a calendar week or midnight UTC. The allowance is measured by the list-price value of the work rather than a fixed number of requests" — no figure is published, and the dashboard shows only a percentage. "Free routes stop accepting new requests when the period allowance is exhausted", and "Free routes never charge your balance". "No card required". "Free routes are disabled by default" until you consent to them, "Token Harbor may retain prompts and responses sent through explicit free routes after you opt in", and "Upstream providers separately process request content under their own terms". The operator is Token Harbor PTE. LTD., Singapore. Read 2026-10-04

</details>

- Base URL: `https://tokenharbor.ai/v1`
- Key: `TOKEN_HARBOR_API_KEY` — get one at <https://tokenharbor.ai/dashboard/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://tokenharbor.ai`
- Codex CLI: [`configs/codex/token-harbor.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/token-harbor.config.toml) — copy it to `~/.codex/`, then `codex -p token-harbor`; set up on the lane by the vendor's own page, <https://tokenharbor.ai/docs/integrations/codex>: "Point OpenAI Codex at Token Harbor manually"
- Callable ids: `deepseek-v4.1-flash:free`
- What you send may be used to train or improve models ([the vendor's words](https://tokenharbor.ai/terms)).

## Rows that listed it before

- [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/) — listed 2026-09-28 to 2026-10-05

## Related models

- [`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/) — free at Routeway, Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode and FreeInference (Harvard SEAS)
- [`deepseek-v3.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v3.2/) — free at Kiro and Alibaba Cloud Model Studio (DashScope, international)
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
