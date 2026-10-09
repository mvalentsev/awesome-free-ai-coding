---
layout: default
title: 'mimo-v2.5 free: 2 providers, limits and ids, verified 2026-10-08'
description: mimo-v2.5 is served free by opencode and AIHubMix (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/mimo-v2.5/
last_modified_at: 2026-10-08
crumb: mimo-v2.5
---

{% raw %}

# Where mimo-v2.5 is free

**2 rows on the list serve `mimo-v2.5` free:** opencode and AIHubMix (free models). None asks for a card. The published offers were checked on 2026-10-08 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/mimo-v2-5-0424), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · verified 2026-10-08 · listed since 2026-07-19

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant; plain muse-spark-1.3 is paid. Offers rotate and each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Muse Spark Contributor permits training on prompts and completions; max effort belongs to the paid Standard variant.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/docs/zen/)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-08-14

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
- Callable ids: `xiaomi-mimo-v2.5-free`

## Rows that listed it before

- [Freebuff](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) — listed 2026-09-02 to 2026-09-22
- [Token Harbor](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/) — listed 2026-09-16 to 2026-09-22
- [MiMo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mimo-code/) — listed 2026-07-20 to 2026-07-27; the row itself is archived

## Related models

- [`mimo-v2.6-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.6-flash/) — free at opencode, Freebuff, Cline, AIHubMix (free models) and Token Harbor
- [`mimo-v2-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2-flash/) — free at AIHubMix (free models)
- [`mimo-v2-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2-omni/) — free at AIHubMix (free models)
- [`mimo-v2-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2-pro/) — free at AIHubMix (free models)
- [`mimo-v2.5-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.5-pro/) — free at AIHubMix (free models)
- [`mimo-v2.6-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/mimo-v2.6-pro/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
