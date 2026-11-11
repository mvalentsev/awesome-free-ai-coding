---
layout: default
title: 'agents-a1 free: 1 provider, limits and ids, provider probes 2026-11-09'
description: agents-a1 is served free by AIHubMix (free models). It asks for no card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/agents-a1/
last_modified_at: 2026-11-09
crumb: agents-a1
---

{% raw %}

# Where agents-a1 is free

**One row on the list serves `agents-a1` free:** AIHubMix (free models). It asks for no card. The provider's last scheduled probe was on 2026-11-09; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-10-01

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: Other free routes: Usage allowance: amount not published (period not published); scope not published; for `agents-a1-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m agents-a1-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `agents-a1-free`

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-23 to 2026-10-31

---

Generated from `registry.yaml` on 2026-11-11 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
