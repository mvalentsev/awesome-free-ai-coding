---
layout: default
title: 'glm-4.7-flash free: 3 providers, limits and ids, verified 2026-10-05'
description: glm-4.7-flash is served free by AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova. Free usage is subject to the access conditions below. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/glm-4.7-flash/
last_modified_at: 2026-10-05
crumb: glm-4.7-flash
---

{% raw %}

# Where glm-4.7-flash is free

**3 rows on the list serve `glm-4.7-flash` free:** AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova. Free usage is subject to the access conditions below. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-4-7-flash), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself, with an Anthropic-format /v1/messages too, so a free id can back Claude Code

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex CLI"
- Callable ids: `glm-4.7-flash-free`

### [Z.ai (Zhipu GLM)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zai-glm/)

🔌 LLM APIs with free tier · no card · verified 2026-10-05 · listed since 2026-07-27

GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4)

- Limits, in the vendor's words: GLM-4.7-Flash, GLM-4.5-Flash and the GLM-4.6V-Flash vision model are the three rows z.ai's own price table reads Free on all four columns — every other model there says "Limited-time Free" instead, including the flagship GLM-5.x. Rate-limited
- Base URL: `https://api.z.ai/api/paas/v4`
- Key: `ZAI_GLM_API_KEY` — get one at <https://z.ai/manage-apikey/apikey-list>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.z.ai/api/anthropic`
- Callable ids: `glm-4.7-flash`
- What you send is not used to train models ([the vendor's words](https://docs.z.ai/legal-agreement/terms-of-use)).

### [MegaNova](https://mvalentsev.github.io/awesome-free-ai-coding/providers/meganova/)

🧭 Aggregators (one key, many providers) · not offered in Hong Kong, Venezuela, Azerbaijan and 40 more places · verified 2026-10-05 · listed since 2026-10-01

OpenAI-compatible gateway with daily free model quotas: no-card Tier 1, plus additional free access after a one-time deposit

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Tier 1 is "Free registration — no credit card required", with "Free Access Models (<100B), including Manta Mini". The Free Model Quota table gives a Tier 1 account 50 requests a day ("50 RPD (Requests Per Day)") on each of Mistral-Small-3.2-24B, Manta Mini and Manta Flash, and on several roleplay fine-tunes, an embedding model and a reranker — "Total Free Quota per day 550", with a "daily reset at 00:00 UTC" — and 0 on GLM-4.7-Flash and Manta Pro until a "$1 deposit" moves the account to Tier 2. The terms say "Free modules are for evaluation and interactive use only and are not designed for production or unattended batch workloads". The operator is Nebula Nova Inc., a Delaware corporation. Read 2026-09-16

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

Generated from `registry.yaml` on 2026-10-05 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
