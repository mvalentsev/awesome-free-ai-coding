---
layout: default
title: 'glm-4.7-flash free: 4 providers, limits and ids, provider probes 2026-11-09'
description: glm-4.7-flash is served free by AIHubMix (free models), Z.ai (Zhipu GLM), NovAI and MegaNova. Free usage is subject to the access conditions below. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-4.7-flash/
last_modified_at: 2026-11-09
crumb: glm-4.7-flash
---

{% raw %}

# Where glm-4.7-flash is free

**4 rows on the list serve `glm-4.7-flash` free:** AIHubMix (free models), Z.ai (Zhipu GLM), NovAI and MegaNova. Free usage is subject to the access conditions below. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-09-24

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: 500/day coding routes: 5 requests/minute; 500 requests/day per account per model; for `coding-minimax-m3-free`, `coding-glm-4.7-free`, `coding-glm-4.6-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `glm-4.7-flash-free`

500/day coding routes: 5 requests/minute per account per model; for `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-minimax-m2-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m glm-4.7-flash-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `glm-4.7-flash-free`

### [Z.ai (Zhipu GLM)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zai-glm/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-09 · listed since 2026-07-27

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

### [NovAI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/novai/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-05

Hong Kong OpenAI-compatible gateway with a recurring free allowance on selected text and vision models, separate from its signup credit

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Shared free-model calls: 10 requests/day per account (before the first completed top-up). 00:00 UTC+8

5 requests/minute per account (before the first completed top-up)

Separate signup credit: $2 once per account (valid for 14 days)

Free chat calls: Unmetered requests per account (after any completed top-up; upstream provider limits still apply)

The daily allowance is shared across free chat, image and video models; media keep separate caps after a top-up. Calls at a cap return 429 until reset. An email account and API key are required. Signup accepts selected email providers and is screened for abuse. Paid models and top-ups are optional. The gateway says it does not store or train on prompts; upstream providers apply their own policies. Users must be at least 18.

</details>

- Base URL: `https://aiapi-pro.com/v1`
- Key: `NOVAI_API_KEY` — get one at <https://aiapi-pro.com/register.html>
- Callable ids: `glm-4.7-flash`

### [MegaNova](https://mvalentsev.github.io/awesome-free-ai-coding/providers/meganova/)

🧭 Aggregators (one key, many providers) · not offered in Hong Kong, Venezuela, Azerbaijan and 40 more places · last probe 2026-11-09 · listed since 2026-10-01

OpenAI-compatible gateway with daily free model quotas: no-card Tier 1, plus additional free access after a one-time deposit

- Limits, in the vendor's words: Tier 2: GLM-4.7-Flash: 50 requests/day per account per model (After a $1 deposit); for `zai-org/GLM-4.7-Flash`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Tier 1: 60 requests/minute; 200,000 tokens/minute per account

Tier 1 registration needs no card. A $1 deposit unlocks Tier 2's separate per-model free allowances. Daily quotas reset at 00:00 UTC; they are per model, not one total budget to spend on any model. Free modules are for evaluation and interactive use, not production or unattended batches. The operator is Nebula Nova Inc. Audio and embedding quotas do not establish coding-model allowances.

</details>

- Base URL: `https://api.meganova.ai/v1`
- Key: `MEGANOVA_API_KEY` — get one at <https://www.meganova.ai/api-keys>
- Callable ids: `zai-org/GLM-4.7-Flash`
- `zai-org/GLM-4.7-Flash`: requires $1 one-time top-up ([conditions](https://docs.meganova.ai/tiers/tier-2.md))

## Rows that listed it before

- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-03; the row itself is archived

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at opencode, NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.6v-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6v-flash/) — free at Z.ai (Zhipu GLM) and NovAI
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
