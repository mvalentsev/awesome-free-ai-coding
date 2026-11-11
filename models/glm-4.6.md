---
layout: default
title: 'glm-4.6 free: 1 provider, limits and ids, provider probes 2026-11-09'
description: glm-4.6 is served free by AIHubMix (free models). It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/glm-4.6/
last_modified_at: 2026-11-09
crumb: glm-4.6
---

{% raw %}

# Where glm-4.6 is free

**One row on the list serves `glm-4.6` free:** AIHubMix (free models). It asks for no card. The provider's last scheduled probe was on 2026-11-09; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-09-24

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: 500/day coding routes: 5 requests/minute; 500 requests/day per account per model; for `coding-minimax-m3-free`, `glm-4.7-flash-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `coding-glm-4.7-free`, `coding-glm-4.6-free`

500/day coding routes: 5 requests/minute per account per model; for `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-minimax-m2-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m coding-glm-4.6-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `coding-glm-4.6-free`

## Related models

- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and ZCode (Z.ai)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at opencode, NVIDIA NIM (build.nvidia.com), Freebuff, AIHubMix (free models), ZCode (Z.ai) and FreeInference (Harvard SEAS)
- [`glm-4.6v-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6v-flash/) — free at Z.ai (Zhipu GLM) and NovAI
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models), Z.ai (Zhipu GLM), NovAI and MegaNova (requires $1 top-up)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models) and Alibaba Cloud Model Studio (DashScope, international)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international), Regolo AI and AtomCode

---

Generated from `registry.yaml` on 2026-11-11 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
