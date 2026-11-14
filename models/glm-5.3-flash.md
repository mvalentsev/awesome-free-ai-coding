---
layout: default
title: 'glm-5.3-flash free: 5 providers, limits and ids, provider probes 2026-11-12'
description: glm-5.3-flash is served free by opencode, NVIDIA NIM (build.nvidia.com), AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-5.3-flash/
last_modified_at: 2026-11-14
crumb: glm-5.3-flash
---

{% raw %}

# Where glm-5.3-flash is free

**5 rows on the list serve `glm-5.3-flash` free:** opencode, NVIDIA NIM (build.nvidia.com), AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS). None asks for a card. The providers' last scheduled probes were on 2026-11-12; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-11-12 · listed since 2026-11-02

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Flint 40B Free allows training and retains data for 30 days. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia. Inkling 2 Small Free permits training. It has model-specific territorial exclusions, including Russia. LongCat 2.5 Free is hosted in China; its provider does not train on inputs or retain them.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In opencode's own model list: `GLM-5.3-Flash Free`
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-11-12 · listed since 2026-09-29

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

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-12 · listed since 2026-09-25

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: 100/day coding routes: 5 requests/minute; 100 requests/day per account per model; for `xiaomi-mimo-v2.6-pro-free`, `xiaomi-mimo-v2.6-flash-free`, `coding-glm-5.2-free`, `coding-kimi-k3-free`, `coding-glm-5.1-free`, `coding-minimax-m2.7-free`

100/day coding routes: 5 requests/minute; 100 requests/day; 1,000,000 tokens/day per account per model; for `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`

100/day coding routes: 5 requests/minute per account per model; for `coding-minimax-m2.5-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; LiquidAI advises against agentic coding with the listed LFM models.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m coding-glm-5.3-flash-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `coding-glm-5.3-flash-free`

### [ZCode (Z.ai)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zcode/)

🎁 Trials (no card when possible) · no card · last probe 2026-11-12 · listed since 2026-10-12

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

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-09-05

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

- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-02 to 2026-10-06, 2026-10-06 to 2026-11-14
- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25
- [Sail Research](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) — listed 2026-09-21 to 2026-09-25
- [Sarvam AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sarvam/) — listed 2026-09-05 to 2026-09-16

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.6v-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6v-flash/) — free at Z.ai (Zhipu GLM) and NovAI
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM), NovAI and MegaNova (requires $1 top-up)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode

---

Generated from `registry.yaml` on 2026-11-14 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
