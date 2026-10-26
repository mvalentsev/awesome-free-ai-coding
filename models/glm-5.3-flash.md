---
layout: default
title: 'glm-5.3-flash free: 5 providers, limits and ids, provider probes 2026-10-26'
description: glm-5.3-flash is served free by NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-5.3-flash/
last_modified_at: 2026-10-26
crumb: glm-5.3-flash
---

{% raw %}

# Where glm-5.3-flash is free

**5 rows on the list serve `glm-5.3-flash` free:** NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS). None asks for a card. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-5-3-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-10-26 · listed since 2026-09-29

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `z-ai/glm-5.3-flash`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/)

🤖 Coding agents & CLIs · no card · last probe 2026-10-26 · listed since 2026-10-06

Ad-funded coding agent for CLI, desktop, web, cloud and chat, with daily regional allowances and conditional free-session access

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Session-based limited mode: 6 one-hour sessions per day per account

Available models depend on the app and access level. “Promotional prices are temporary, and any price may change.” “Freebuff collects prompts, messages, code, files, repository data, and agent traces when you use features that need them”. Check the balance and picker in your app.

Daily allowance — the United States, Canada, the United Kingdom, Australia, New Zealand, Ireland, Norway, Sweden, Denmark, Finland, the Netherlands, Austria, Luxembourg, Iceland, Germany, France, Spain, Italy, Portugal, Belgium, Switzerland, Liechtenstein, Malta, South Korea: 30 hours per day; Other countries: 5 hours per day; VPN or proxy: 4 hours per day.

Check your account's picker for current model hour prices. Solar Pro 4: shared daily hours; available in limited mode; Solar Mini 4: shared daily hours; available in limited mode; MiMo V2.6 Flash Fast: shared daily hours; available in limited mode; GLM 5.3 Flash: shared daily hours; available in limited mode; DeepSeek V4.1 Flash 10/17: shared daily hours; available in limited mode; GPT-6 Luna: shared daily hours; full access only; MiMo 2.6 Pro: shared daily hours; full access only; DeepSeek V4.1 Flash Fast 10/17: shared daily hours; full access only; GPT-6.1 Sol: paid plan; Gemini 4 Argon: paid plan; Gemini 3.8 Flash: paid plan; Muse Spark 1.3: shared daily hours; full access only; Gemini 3.1 Flash Lite: specialist tasks only.

Your balance is measured in hours. Gemini 3.8 Flash: “PAID-ONLY row” (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-models.ts). GPT-6.1 Sol, Gemini 4 Argon: The public Free-plan comparison requires a paid plan; paid plans allow one one-hour session per day. (source: https://freebuff.com/plans). Gemini 3.1 Flash Lite handles specialist tasks such as file finding and research. Muse Spark 1.3: Credit-funded at full access; a paid plan is required at limited access. (source: https://raw.githubusercontent.com/CodebuffAI/codebuff/main/common/src/constants/freebuff-models.ts).

MiMo V2.6 Flash Fast is the default on CLI, Desktop, Web, and Cloud. Daily hours refill at midnight in your local timezone and unused daily hours do not carry over. Older app versions show the same balance as Freebucks, five to an hour. (source: https://freebuff.com/llms.txt).

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://freebuff.com/llms.txt)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-25

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 100/day coding routes: 5 requests/minute; 100 requests/day; 1,000,000 tokens/day per account per model; for `xiaomi-mimo-v2.6-pro-free`, `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `xiaomi-mimo-v2.6-flash-free`, `coding-glm-5.2-free`, `coding-kimi-k3-free`, `coding-glm-5.1-free`, `coding-minimax-m2.7-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-minimax-m2.5-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `coding-minimax-m3-free`, `glm-4.7-flash-free`, `coding-glm-4.7-free`, `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-glm-4.6-free`, `coding-minimax-m2-free`

Other free routes: Usage allowance: amount not published (period not published); scope not published; for `agents-a1-free`, `intern-s2-free`, `dots-3-note-preview-free`, `lfm-2.5-2.6b-free`, `nemotron-3.5-lightning-free`, `nemotron-3-super-120b-a12b-free`, `nemotron-3-nano-omni-30b-a3b-reasoning-free`, `nemotron-3-ultra-550b-a55b-free`, `north-mini-code-free`, `laguna-xs-2.1-free`, `laguna-s-2.1-free`, `mimo-v2-flash-free`

Qwen3.8 Flash/Max GMI promotion: Usage allowance: amount not published (period not published) per account per model (30 days from launch or until campaign credits run out; launch date unconfirmed.); for `qwen3.8-flash-free`, `qwen3.8-max-free`

Gemma 4 free routes: Usage allowance: amount not published (period not published); scope not published; for `gemma-4-26b-a4b-it-free`, `gemma-4-31b-it-free`

Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m coding-glm-5.3-flash-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `coding-glm-5.3-flash-free`

### [ZCode (Z.ai)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zcode/)

🎁 Trials (no card when possible) · no card · last probe 2026-10-26 · listed since 2026-10-12

Z.ai's desktop coding agent, free as an app, with five days of its GLM models for a new user and no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Global trial: GLM-5.3: 3,000,000 tokens/day per account per model (First 5 days only)

Global trial: GLM-5-turbo: 2,000,000 tokens/day per account per model (First 5 days only)

BigModel trial: GLM-5.3: 3,000,000 tokens/day per account per model (First 5 days only)

BigModel trial: GLM-5.3-Flash: 5,000,000 tokens/day per account per model (First 5 days only)

Global and mainland BigModel accounts have different per-model daily trial grants. The global trial covers GLM-5.3 and GLM-5-Turbo; BigModel covers GLM-5.3 and GLM-5.3-Flash in separate buckets. Both end after the first five days and do not create ongoing daily access. Afterwards the app needs a GLM Coding Plan or your own API key; the application itself remains free.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send is not used to train models ([the vendor's words](https://zcode.z.ai/en/privacy)).

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · last probe 2026-10-26 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Usage allowance: amount varies (period not published) per account

No card. This is an experimental research service with capacity-dependent limits. Prompts and responses may be logged for research; sanitized content, usage statistics and routing metrics may be published or open-sourced. Only models marked Free accept a Free key; Pro catalog rows need a Pro-enabled key.

</details>

- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `glm-5.3-flash`

## Rows that listed it before

- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25
- [Sail Research](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) — listed 2026-09-21 to 2026-09-25
- [Sarvam AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sarvam/) — listed 2026-09-05 to 2026-09-16

## Related models

- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode
- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at NVIDIA NIM (build.nvidia.com), AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova (requires $1 top-up)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
