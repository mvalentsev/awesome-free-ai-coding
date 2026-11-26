---
layout: default
title: 'deepseek-v4.1-flash free: 7 providers, limits and ids, provider probes 2026-11-26'
description: deepseek-v4.1-flash is served free by opencode, NVIDIA NIM (build.nvidia.com), Alibaba Cloud Model Studio (DashScope, international), Token Harbor, Zro (MoonMath), OrcaRouter (free models) and BeatAPI (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and…
permalink: /models/deepseek-v4.1-flash/
last_modified_at: 2026-11-26
crumb: deepseek-v4.1-flash
---

{% raw %}

# Where deepseek-v4.1-flash is free

**7 rows on the list serve `deepseek-v4.1-flash` free:** opencode, NVIDIA NIM (build.nvidia.com), Alibaba Cloud Model Studio (DashScope, international), Token Harbor, Zro (MoonMath), OrcaRouter (free models) and BeatAPI (free models). None asks for a card. The providers' last scheduled probes were on 2026-11-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-11-26 · listed since 2026-10-29

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Flint 40B Free allows training and retains data for 30 days. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia. Hy4 flash Free's provider states zero retention and no training on your data.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In opencode's own model list: `DeepSeek V4.1 Flash Free`
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-11-26 · listed since 2026-10-02

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

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-11-26 · listed since 2026-09-28

Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical model token grant: 1,000,000 tokens once per account per model (Where granted; valid for 90 days from activation, model release or approval, whichever is later)

Separate OAuth allowance: 2,000 requests/day; scope not published (separate from API-key token grants)

Free token grants apply in Singapore (international), independently per model and dated snapshot. Current pricing tables decide new-grant eligibility. New grants exclude Qwen3.8 Max 0902, DeepSeek V4.1 Flash 1017, DeepSeek V4 Pro and Kimi K3. Previously issued quotas remain usable until expiry or exhaustion. Check the console for each model's remaining quota. Kimi and glm-5.2-fast-preview have no API-key grant. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default. OAuth has a separate allowance; its eligible models and reset time are not established here.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `deepseek-v4.1-flash`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-26 · listed since 2026-09-16

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

### [Zro (MoonMath)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zro/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-26 · listed since 2026-11-15

OpenAI-compatible inference for coding agents from MoonMath, with a recurring Free plan on selected Flash models

- Limits, in the vendor's words: Free plan: Daily usage allowance: amount not published; scope not published

Reset time and rate limits are not published. An account and API key are required. The pricing page offers Free separately from paid plans and usage packs. Inference passes through an EU gateway and runs in Europe or the US. Zro says it retains no request bodies and uses no requests or logs for training without separate explicit consent; account, billing and operational metadata are retained. Inference providers follow their own operational logging terms. Optional agent tools have separate prices.
- Base URL: `https://zro.moonmath.ai/v1`
- Key: `ZRO_API_KEY` — get one at <https://zro.moonmath.ai/get-started?plan=free>
- Callable ids: `deepseek-v4.1-flash`
- What you send is not used to train models ([the vendor's words](https://zro.moonmath.ai/privacy)).

### [OrcaRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/orcarouter/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-26 · listed since 2026-11-22

Free model APIs for accounts with established GitHub linkage

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 10 requests/minute; 50 requests/day per workspace (before any top-up)

20 requests/minute; 800 requests/day per workspace ($20 lifetime spend)

The workspace owner must link a GitHub account registered for some time, unless lifetime spend exempts the workspace. The lowest tier also has a small unpublished per-request prompt cap. Day buckets reset at 00:00 UTC. Free models never fall back to a paid model; availability and limits can change. Requests are routed to upstream providers under their own policies. The rate-limit guide states "OrcaRouter rate-limits at the workspace level, not per API key."

</details>

- Base URL: `https://api.orcarouter.ai/v1`
- Key: `ORCAROUTER_API_KEY` — get one at <https://www.orcarouter.ai>
- Callable ids: `deepseek/deepseek-v4.1-flash-free`

### [BeatAPI (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/beatapi/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-26 · listed since 2026-11-22

A no-top-up API for free text-model variants

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 1 request/minute per account (before the first top-up)

10 requests/minute per account (after any top-up)

Free calls are counted separately from paid rate limits, but can also be refused when the ordinary account limit is exhausted. Availability can change without notice and no daily allowance is promised. Free model contexts, output limits and reasoning settings are not those of the paid siblings.

</details>

- Base URL: `https://api.beatapi.io/v1`
- Key: `BEATAPI_API_KEY` — get one at <https://beatapi.io/dashboard/apikeys>
- Callable ids: `deepseek-v4.1-flash-free`

## Rows that listed it before

- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-16 to 2026-10-06, 2026-10-06 to 2026-11-08
- [Haimaker](https://mvalentsev.github.io/awesome-free-ai-coding/providers/haimaker/) — listed 2026-10-30 to 2026-11-01; the row itself is archived
- [Qoder](https://mvalentsev.github.io/awesome-free-ai-coding/providers/qoder/) — listed 2026-10-28 to 2026-10-31
- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-12 to 2026-10-16
- [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/) — listed 2026-09-28 to 2026-10-05

## Related models

- [`deepseek-v4.1-flash-1017`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4.1-flash-1017/) — free at Freebuff and cheapllm.shop
- [`deepseek-v4-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-pro/) — free at Alibaba Cloud Model Studio (DashScope, international)
- [`deepseek-v3.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v3.2/) — free at Kiro
- [`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/) — free at Alibaba Cloud Model Studio (DashScope, international), BazaarLink, AtomCode, FreeInference (Harvard SEAS) and OrcaRouter (free models)

---

Generated from `registry.yaml` and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
