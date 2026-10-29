---
layout: default
title: 'deepseek-v4.1-flash free: 6 providers, limits and ids, provider probes 2026-10-26'
description: deepseek-v4.1-flash is served free by opencode, NVIDIA NIM (build.nvidia.com), Freebuff, Alibaba Cloud Model Studio (DashScope, international), Qoder and Token Harbor. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/deepseek-v4.1-flash/
last_modified_at: 2026-10-29
crumb: deepseek-v4.1-flash
---

{% raw %}

# Where deepseek-v4.1-flash is free

**6 rows on the list serve `deepseek-v4.1-flash` free:** opencode, NVIDIA NIM (build.nvidia.com), Freebuff, Alibaba Cloud Model Studio (DashScope, international), Qoder and Token Harbor. None asks for a card. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-10-26 · listed since 2026-10-29

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Flint 40B Free allows training and retains data for 30 days. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-10-26 · listed since 2026-10-02

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

🤖 Coding agents & CLIs · no card · last probe 2026-10-26 · listed since 2026-10-06

Ad-funded coding agent for CLI, desktop, web, cloud and chat, with daily regional allowances and conditional free-session access

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Session-based limited mode: 6 one-hour sessions per day per account

Available models depend on the app and access level. “Promotional prices are temporary, and any price may change.” “Freebuff collects prompts, messages, code, files, repository data, and agent traces when you use features that need them”. Check the balance and picker in your app.

Daily allowance — the United States, Canada, the United Kingdom, Australia, New Zealand, Ireland, Norway, Sweden, Denmark, Finland, the Netherlands, Austria, Luxembourg, Iceland, Germany, France, Spain, Italy, Portugal, Belgium, Switzerland, Liechtenstein, Malta, South Korea: 30 hours per day; Other countries: 5 hours per day; VPN or proxy: 4 hours per day.

Check your account's picker for current model hour prices. Solar Pro 4: shared daily hours; available in limited mode; Solar Mini 4: shared daily hours; available in limited mode; MiMo V2.6 Flash Fast: shared daily hours; available in limited mode; GLM 5.3 Flash: shared daily hours; available in limited mode; DeepSeek V4.1 Flash 10/17: shared daily hours; available in limited mode; GPT-6 Luna: shared daily hours; full access only; MiMo 2.6 Pro: shared daily hours; full access only; DeepSeek V4.1 Flash Fast 10/17: shared daily hours; full access only; GPT-6.1 Terra: shared daily hours; full access only; GPT-6.1 Sol: paid plan; Gemini 4 Argon: paid plan; Gemini 3.8 Flash: paid plan; Muse Spark 1.3: shared daily hours; full access only; Gemini 3.1 Flash Lite: specialist tasks only.

Your balance is measured in hours. Gemini 3.8 Flash: “PAID-ONLY row” (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-models.ts). GPT-6.1 Sol, Gemini 4 Argon: The public Free-plan comparison requires a paid plan; paid plans allow one one-hour session per day. (source: https://freebuff.com/plans). Gemini 3.1 Flash Lite handles specialist tasks such as file finding and research. Muse Spark 1.3: Credit-funded at full access; a paid plan is required at limited access. (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-models.ts). GPT-6.1 Terra: “Open on full access, a paid plan on limited access. One session a day on every plan.” (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-sol-promo.ts).

MiMo V2.6 Flash Fast is the default on CLI, Desktop, Web, and Cloud. Daily hours refill at midnight in your local timezone and unused daily hours do not carry over. Older app versions show the same balance as Freebucks, five to an hour. (source: https://freebuff.com/llms.txt).

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://freebuff.com/llms.txt)).

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-10-26 · listed since 2026-09-28

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

### [Qoder](https://mvalentsev.github.io/awesome-free-ai-coding/providers/qoder/)

🤖 Coding agents & CLIs · no card · free until 2026-11-01 00:00+08:00 · last probe 2026-10-26 · listed since 2026-10-28

Alibaba's coding apps with an ongoing Free basic-model allowance, separate free Qwen and DeepSeek promotions, a 300-credit Pro trial, and daily promotional credits to claim

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Pro trial: 300 credits once per account (Valid for 2 weeks)

Claimed promotional credit: 100 credits/day per account (Each claim valid for 30 days)

Pro trial completion and next edits: Unmetered completions per account (Valid for 2 weeks)

Qwen3.8-Flash promotion: Requests allowance: amount not published (period not published) per account per model; for `Qwen3.8-Flash`

DeepSeek-Flash promotion: Daily requests allowance: amount not published per account per model; for `DeepSeek-Flash`

The Free plan continues on unnamed basic models with unpublished daily and monthly limits after credits run out. Both model promotions include individual Free accounts with zero Credits, require no claim, and exclude Teams and Enterprise. The Qwen3.8-Flash promotion spends no Credits; its end will be announced in advance. DeepSeek-Flash has an unpublished daily free-use count; when it runs out, wait for the next day or continue with Credits. Paid accounts receive more uses. The separate 14-day Pro trial includes 300 credits and unmetered completions and next edits. Daily promotional credits require a manual claim in the international desktop app; "End time: To be announced". Efficient-tier promotional usage requires a paid plan.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In Qoder's own model list: `DeepSeek-Flash`

### [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-16

OpenAI- and Anthropic-compatible gateway with a standing $0 plan: a rotating lineup of :free ids on a value-based allowance per rolling 7-day period, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free routes: Rolling 7-day list-price value allowance: amount not published per account

Free accounts: 60 requests/minute; 1,800 requests/hour per account

Free accounts: 100 requests/minute; 3,000 requests/hour per IP

Enable explicit :free routes in the dashboard before calling them; the rotating model set is listed under Free. The dashboard shows usage as a percentage. Exhausted free routes stop instead of charging the wallet. Request-rate caps apply to Free accounts across models and API keys. "There is no limit on concurrent requests, on any plan." "Free accounts: up to 4 MB (4,000,000 bytes)." Oversized requests return `413 request_too_large`. Permanent free routes require data sharing: staff and third-party AI tools may analyze retained prompts and responses for diagnostics and model or product improvement. Token Harbor says it does not train models itself; upstream providers may train under their own terms. Limited-time campaigns may expressly use the paid-route data policy instead. The operator is Token Harbor PTE. LTD., Singapore.

</details>

- Base URL: `https://tokenharbor.ai/v1`
- Key: `TOKEN_HARBOR_API_KEY` — get one at <https://tokenharbor.ai/dashboard/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://tokenharbor.ai`
- Codex CLI: [`configs/codex/token-harbor.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/token-harbor.config.toml) — copy it to `~/.codex/`, then `codex -p token-harbor`; set up on the lane by the vendor's own page, <https://tokenharbor.ai/docs/integrations/codex>: "Point OpenAI Codex at Token Harbor manually"
- Callable ids: `deepseek-v4.1-flash:free`
- What you send may be used to train or improve models ([the vendor's words](https://tokenharbor.ai/terms)).

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-12 to 2026-10-16
- [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/) — listed 2026-09-28 to 2026-10-05

## Related models

- [`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/) — free at Routeway, Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode and FreeInference (Harvard SEAS)
- [`deepseek-v3.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v3.2/) — free at Kiro
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
