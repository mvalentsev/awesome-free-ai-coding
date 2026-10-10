---
layout: default
title: 'glm-5.3-flash free: 4 providers, limits and ids, verified 2026-10-08'
description: glm-5.3-flash is served free by NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/glm-5.3-flash/
last_modified_at: 2026-10-08
crumb: glm-5.3-flash
---

{% raw %}

# Where glm-5.3-flash is free

**4 rows on the list serve `glm-5.3-flash` free:** NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS). None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-5-3-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · verified 2026-10-08 · listed since 2026-09-29

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

🤖 Coding agents & CLIs · no card · verified 2026-10-08 · listed since 2026-10-06

Ad-funded coding agent — CLI, desktop, web, cloud and chat — with daily regional credits and conditional free-session access. “No card required.”

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

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-09-25

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself, with an Anthropic-format /v1/messages too, so a free id can back Claude Code

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 100/day coding routes: 5 requests/minute; 100 requests/day; 1,000,000 tokens/day per account per model; for `xiaomi-mimo-v2.6-pro-free`, `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `xiaomi-mimo-v2.6-flash-free`, `coding-glm-5.2-free`, `coding-kimi-k3-free`, `xiaomi-mimo-v2-omni-free`, `xiaomi-mimo-v2.5-free`, `xiaomi-mimo-v2.5-pro-free`, `coding-glm-5.1-free`, `coding-minimax-m2.7-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-minimax-m2.5-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `coding-minimax-m3-free`, `xiaomi-mimo-v2-pro-free`, `glm-4.7-flash-free`, `coding-glm-4.7-free`, `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-glm-4.6-free`, `coding-minimax-m2-free`

Other free routes: Usage allowance: amount not published (period not published); scope not published; for `agents-a1-free`, `union-alpha-free`, `intern-s2-free`, `dots-3-note-preview-free`, `hy3-free`, `minimax-m2.7-free`, `lfm-2.5-2.6b-free`, `ling-3.0-tiny-free`, `nemotron-3.5-lightning-free`, `ling-3.0-flash-free`, `nemotron-nano-9b-v2-free`, `nemotron-nano-12b-v2-vl-free`, `nemotron-3-super-120b-a12b-free`, `nemotron-3-nano-omni-30b-a3b-reasoning-free`, `nemotron-3-ultra-550b-a55b-free`, `north-mini-code-free`, `laguna-xs-2.1-free`, `laguna-s-2.1-free`, `nemotron-3-nano-30b-a3b-free`, `mimo-v2-flash-free`

Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Exact IDs for each published cap appear above; the remaining routes have no numerical budget published. Daily quotas have no trial expiry or payment-method requirement. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex CLI"
- Callable ids: `coding-glm-5.3-flash-free`

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-09-05

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

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at NVIDIA NIM (build.nvidia.com), AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova (requires $1 top-up)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and Regolo AI
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
