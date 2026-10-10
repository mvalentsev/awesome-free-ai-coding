---
layout: default
title: 'glm-4.7-flash free: 3 providers, limits and ids, verified 2026-10-08'
description: glm-4.7-flash is served free by AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova. Free usage is subject to the access conditions below. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/glm-4.7-flash/
last_modified_at: 2026-10-08
crumb: glm-4.7-flash
---

{% raw %}

# Where glm-4.7-flash is free

**3 rows on the list serve `glm-4.7-flash` free:** AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova. Free usage is subject to the access conditions below. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-4-7-flash), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-09-24

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
- Callable ids: `glm-4.7-flash-free`

### [Z.ai (Zhipu GLM)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zai-glm/)

🔌 LLM APIs with free tier · no card · verified 2026-10-08 · listed since 2026-07-27

GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free Flash models: Usage allowance: amount not published (period not published) per account

GLM-4.7-Flash, GLM-4.5-Flash and GLM-4.6V-Flash have free input and output prices. The flagship rows' limited-time-free cached-storage column does not make their input or output free. No numerical rate or usage allowance is published.

</details>

- Base URL: `https://api.z.ai/api/paas/v4`
- Key: `ZAI_GLM_API_KEY` — get one at <https://z.ai/manage-apikey/apikey-list>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.z.ai/api/anthropic`
- Callable ids: `glm-4.7-flash`
- What you send is not used to train models ([the vendor's words](https://docs.z.ai/legal-agreement/terms-of-use)).

### [MegaNova](https://mvalentsev.github.io/awesome-free-ai-coding/providers/meganova/)

🧭 Aggregators (one key, many providers) · not offered in Hong Kong, Venezuela, Azerbaijan and 40 more places · verified 2026-10-08 · listed since 2026-10-01

OpenAI-compatible gateway with daily free model quotas: no-card Tier 1, plus additional free access after a one-time deposit

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Tier 1: Manta Mini 1.0: 50 requests/day per account per model; for `meganova-ai/manta-mini-1.0`

Tier 1: Manta Flash 1.0: 50 requests/day per account per model; for `meganova-ai/manta-flash-1.0`

Tier 1: Mistral-Small-3.2-24B-Instruct-2506: 50 requests/day per account per model; for `mistralai/Mistral-Small-3.2-24B-Instruct-2506`

Tier 2: Manta Mini 1.0: 500 requests/day per account per model (After a $1 deposit); for `meganova-ai/manta-mini-1.0`

Tier 2: Manta Flash 1.0: 500 requests/day per account per model (After a $1 deposit); for `meganova-ai/manta-flash-1.0`

Tier 2: Mistral-Small-3.2-24B-Instruct-2506: 300 requests/day per account per model (After a $1 deposit); for `mistralai/Mistral-Small-3.2-24B-Instruct-2506`

Tier 2: Manta Pro 1.0: 50 requests/day per account per model (After a $1 deposit); for `meganova-ai/manta-pro-1.0`

Tier 2: GLM-4.7-Flash: 50 requests/day per account per model (After a $1 deposit); for `zai-org/GLM-4.7-Flash`

Tier 1: 60 requests/minute; 200,000 tokens/minute per account

Tier 1 registration needs no card. A $1 deposit unlocks Tier 2's separate per-model free allowances. Daily quotas reset at 00:00 UTC; they are per model, not one total budget to spend on any model. Free modules are for evaluation and interactive use, not production or unattended batches. The operator is Nebula Nova Inc. Audio and embedding quotas do not establish coding-model allowances.

</details>

- Base URL: `https://api.meganova.ai/v1`
- Key: `MEGANOVA_API_KEY` — get one at <https://www.meganova.ai/api-keys>
- Callable ids: `zai-org/GLM-4.7-Flash`
- `zai-org/GLM-4.7-Flash`: requires $1 one-time top-up ([conditions](https://docs.meganova.ai/tiers/tier-2.md))

## Rows that listed it before

- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-03; the row itself is archived

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at NVIDIA NIM (build.nvidia.com), AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and Regolo AI
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
