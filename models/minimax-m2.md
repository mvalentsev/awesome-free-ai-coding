---
layout: default
title: 'minimax-m2 free: 1 provider, limits and ids, provider probes 2026-11-09'
description: minimax-m2 is served free by AIHubMix (free models). It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/minimax-m2/
last_modified_at: 2026-11-09
crumb: minimax-m2
---

{% raw %}

# Where minimax-m2 is free

**One row on the list serves `minimax-m2` free:** AIHubMix (free models). It asks for no card. The provider's last scheduled probe was on 2026-11-09; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-09-24

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: 500/day coding routes: 5 requests/minute per account per model; for `coding-minimax-m3-free`, `glm-4.7-flash-free`, `coding-glm-4.7-free`, `coding-glm-4.6-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-minimax-m2-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m coding-minimax-m2-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `coding-minimax-m2-free`

## Related models

- [`minimax-m3.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3.1-flash/) — free at NVIDIA NIM (build.nvidia.com)
- [`minimax-m3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3/) — free at AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.1/) — free at Kiro and AIHubMix (free models)
- [`minimax-m2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.5/) — free at Kiro and AIHubMix (free models)
- [`minimax-m2.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
