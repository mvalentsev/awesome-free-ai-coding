---
layout: default
title: 'flint-v1.0 free: 2 providers, limits and ids, provider probes 2026-11-09'
description: flint-v1.0 is served free by opencode and AIHubMix (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/flint-v1.0/
last_modified_at: 2026-11-10
crumb: flint-v1.0
---

{% raw %}

# Where flint-v1.0 is free

**2 rows on the list serve `flint-v1.0` free:** opencode and AIHubMix (free models). None asks for a card. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-11-09 · listed since 2026-11-10

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Flint 40B Free allows training and retains data for 30 days. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia. Inkling 2 Small Free permits training. It has model-specific territorial exclusions, including Russia. LongCat 2.5 Free is hosted in China; its provider does not train on inputs or retain them.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In opencode's own model list: `Flint 40B Free`
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-09

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m flint-v1.0-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `flint-v1.0-free`

---

Generated from `registry.yaml` on 2026-11-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
