---
layout: default
title: 'mimo-v2-flash free: 1 provider, limits and ids, provider probes 2026-11-12'
description: mimo-v2-flash is served free by AIHubMix (free models). It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/mimo-v2-flash/
last_modified_at: 2026-11-14
crumb: mimo-v2-flash
---

{% raw %}

# Where mimo-v2-flash is free

**One row on the list serves `mimo-v2-flash` free:** AIHubMix (free models). It asks for no card. The provider's last scheduled probe was on 2026-11-12; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-12 · listed since 2026-09-24

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: Other free routes: Usage allowance: amount not published (period not published); scope not published; for `mimo-v2-flash-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; LiquidAI advises against agentic coding with the listed LFM models.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m mimo-v2-flash-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `mimo-v2-flash-free`

## Related models

- [`mimo-v2.6-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.6-pro/) — free at AIHubMix (free models)
- [`mimo-v2.6-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.6-flash/) — free at opencode, Freebuff (MiMo v2.6 Flash Fast remains admitted for saved selections, but no picker lists it.), AIHubMix (free models) and Token Harbor

---

Generated from `registry.yaml` on 2026-11-14 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
