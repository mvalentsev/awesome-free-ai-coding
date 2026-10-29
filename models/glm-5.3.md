---
layout: default
title: 'glm-5.3 free: 3 providers, limits and ids, provider probes 2026-10-26'
description: glm-5.3 is served free by AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-5.3/
last_modified_at: 2026-10-29
crumb: glm-5.3
---

{% raw %}

# Where glm-5.3 is free

**3 rows on the list serve `glm-5.3` free:** AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai). None asks for a card. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-5-3), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-16

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 100/day coding routes: 5 requests/minute; 100 requests/day; 1,000,000 tokens/day per account per model; for `xiaomi-mimo-v2.6-pro-free`, `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `xiaomi-mimo-v2.6-flash-free`, `coding-glm-5.2-free`, `coding-kimi-k3-free`, `coding-glm-5.1-free`, `coding-minimax-m2.7-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-minimax-m2.5-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `coding-minimax-m3-free`, `glm-4.7-flash-free`, `coding-glm-4.7-free`, `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-glm-4.6-free`, `coding-minimax-m2-free`

Other free routes: Usage allowance: amount not published (period not published); scope not published; for `agents-a1-free`, `intern-s2-free`, `dots-3-note-preview-free`, `lfm-2.5-2.6b-free`, `nemotron-3.5-lightning-free`, `nemotron-3-super-120b-a12b-free`, `nemotron-3-nano-omni-30b-a3b-reasoning-free`, `nemotron-3-ultra-550b-a55b-free`, `north-mini-code-free`, `laguna-xs-2.1-free`, `laguna-s-2.1-free`, `mimo-v2-flash-free`

Gemma 4 free routes: Usage allowance: amount not published (period not published); scope not published; for `gemma-4-26b-a4b-it-free`, `gemma-4-31b-it-free`

Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m coding-glm-5.3-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `coding-glm-5.3-free`

### [Alibaba Cloud Model Studio (DashScope, international)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/)

🔌 LLM APIs with free tier · no card · not offered in mainland China · last probe 2026-10-26 · listed since 2026-09-30

Model-specific free token grants in Singapore, typically one million tokens valid for 90 days; some models retain only previously issued allowances; OpenAI-compatible

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Typical model token grant: 1,000,000 tokens once per account per model (Where granted; valid for 90 days from activation, model release or approval, whichever is later)

Removed model-grant campaigns: Usage allowance: see your account for values (period not published) per account per model (only previously issued quotas, until expiry or exhaustion; no new grants)

Separate OAuth allowance: 2,000 requests/day; scope not published (separate from API-key token grants)

Free token grants apply in Singapore (international), independently per model and dated snapshot. Current pricing tables decide new-grant eligibility. Some older models and snapshots no longer receive new grants; previously issued quotas remain usable until expiry or exhaustion. Check the console for each model's remaining quota. Kimi and glm-5.2-fast-preview have no API-key grant. Account information must be completed before activation. After the grant, usage is automatically billed pay-as-you-go unless Free Quota Only is enabled separately for the model; that switch is disabled by default. OAuth has a separate allowance; its eligible models and reset time are not established here.

</details>

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Callable ids: `glm-5.3`
- What you send is not used to train models ([the vendor's words](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

### [ZCode (Z.ai)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zcode/)

🎁 Trials (no card when possible) · no card · last probe 2026-10-26 · listed since 2026-09-26

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

## Rows that listed it before

- [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/) — listed 2026-09-29 to 2026-10-15, 2026-10-15 to 2026-10-28
- [Sail Research](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) — listed 2026-09-21 to 2026-09-25

## Related models

- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM) and MegaNova (requires $1 top-up)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
