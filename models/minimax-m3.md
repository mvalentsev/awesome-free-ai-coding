---
layout: default
title: 'minimax-m3 free: 3 providers, limits and ids, provider probes 2026-10-26 or later'
description: minimax-m3 is served free by AIHubMix (free models), FreeInference (Harvard SEAS) and Haimaker. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/minimax-m3/
last_modified_at: 2026-10-30
crumb: minimax-m3
---

{% raw %}

# Where minimax-m3 is free

**3 rows on the list serve `minimax-m3` free:** AIHubMix (free models), FreeInference (Harvard SEAS) and Haimaker. None asks for a card. The providers' last scheduled probes were on 2026-10-26 or later; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-24

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
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m coding-minimax-m3-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `coding-minimax-m3-free`

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · last probe 2026-10-26 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Usage allowance: amount varies (period not published) per account

No card. This is an experimental research service with capacity-dependent limits. Prompts and responses may be logged for research; sanitized content, usage statistics and routing metrics may be published or open-sourced. Only models marked Free accept a Free key; Pro catalog rows need a Pro-enabled key.

</details>

- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `minimax-m3`

### [Haimaker](https://mvalentsev.github.io/awesome-free-ai-coding/providers/haimaker/)

🧭 Aggregators (one key, many providers) · no card · provisional since 2026-10-30 · last probe 2026-10-30 · listed since 2026-10-30

OpenAI-compatible API gateway with a limited-time free model promotion, no card required

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Usage allowance: amount not published (period not published); scope not published

Create an account and an API key. Free capacity is best effort and shared across the wave; paid requests have priority. No numerical allowance is published. After the promotion, the same IDs and key return to paid token pricing. Prompts and responses are logged by default; opt out in API key settings. Logged contents are deleted after 30 days. Haimaker says "We do not use the content of your API requests to train AI models." Upstream providers apply their own data policies; their training practices are not established here. Its terms restrict competing-product development and comparative benchmarking without permission.

</details>

- Base URL: `https://api.haimaker.ai/v1`
- Key: `HAIMAKER_API_KEY` — get one at <https://app.haimaker.ai/sign-up>
- Callable ids: `minimax/minimax-m3`
- `minimax/minimax-m3`: free until 2026-11-01 14:00+00:00 ([conditions](https://haimaker.ai/free/))
- Training policy not established ([the vendor's words](https://haimaker.ai/terms-and-conditions/)).

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-09-02 to 2026-09-07

## Related models

- [`minimax-m2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.1/) — free at Kiro and AIHubMix (free models)
- [`minimax-m2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.5/) — free at Kiro and AIHubMix (free models)
- [`minimax-m2.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.7/) — free at AIHubMix (free models) and Routeway
- [`minimax-m2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2/) — free at AIHubMix (free models)
- [`minimax-m3.1-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3.1-flash/) — free at LLMTR (until 2026-11-02)

---

Generated from `registry.yaml` on 2026-10-31 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
