---
layout: default
title: 'glm-5.3-flash free: 6 providers, limits and ids, provider probes 2026-11-19 or later'
description: glm-5.3-flash is served free by NVIDIA NIM (build.nvidia.com), AIHubMix (free models), ZCode (Z.ai), FreeInference (Harvard SEAS), OrcaRouter (free models) and BeatAPI (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-5.3-flash/
last_modified_at: 2026-11-26
crumb: glm-5.3-flash
---

{% raw %}

# Where glm-5.3-flash is free

**6 rows on the list serve `glm-5.3-flash` free:** NVIDIA NIM (build.nvidia.com), AIHubMix (free models), ZCode (Z.ai), FreeInference (Harvard SEAS), OrcaRouter (free models) and BeatAPI (free models). None asks for a card. The providers' last scheduled probes were on 2026-11-19 or later; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-11-26 · listed since 2026-09-29

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

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-26 · listed since 2026-09-25

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: 100/day coding routes: 5 requests/minute; 100 requests/day per account per model; for `xiaomi-mimo-v2.6-pro-free`, `xiaomi-mimo-v2.6-flash-free`, `coding-glm-5.2-free`, `coding-kimi-k3-free`, `coding-glm-5.1-free`, `coding-minimax-m2.7-free`

100/day coding routes: 5 requests/minute; 100 requests/day; 1,000,000 tokens/day per account per model; for `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-glm-5.4-free`

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

🎁 Trials (no card when possible) · no card · last probe 2026-11-26 · listed since 2026-10-12

A desktop coding agent with a no-cost Start Plan that new users can claim after signing in.

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: BigModel trial: GLM-5.4: 3,000,000 tokens/day per account per model (First 5 days only)

BigModel trial: GLM-5.3-Flash: 5,000,000 tokens/day per account per model (First 5 days only)

Use the Start Plan in the official app. BigModel publishes separate daily model quotas. Global Z.ai also offers a Start Plan and shows the exact models and allowances after sign-in. Its former GLM-5.3 and GLM-5-Turbo trial allocations are unconfirmed. The app also supports separately funded coding plans and your own API keys.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send is not used to train models ([the vendor's words](https://zcode.z.ai/en/privacy)).

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-19 · listed since 2026-09-05

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
- Callable ids: `z-ai/glm-5.3-flash-free`

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
- Callable ids: `glm-5.3-flash-free`

## Rows that listed it before

- [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/) — listed 2026-11-02 to 2026-11-18
- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-02 to 2026-10-06, 2026-10-06 to 2026-11-14
- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25
- [Sail Research](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) — listed 2026-09-21 to 2026-09-25
- [Sarvam AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sarvam/) — listed 2026-09-05 to 2026-09-16

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.6v-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6v-flash/) — free at Z.ai (Zhipu GLM) and NovAI
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM), Kiosapi.id, NovAI and MegaNova (requires $1 top-up)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode

---

Generated from `registry.yaml` and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
