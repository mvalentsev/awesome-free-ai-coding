---
layout: default
title: 'ernie-5.5-flash-preview free: 3 providers, limits and ids, provider probes 2026-11-26'
description: ernie-5.5-flash-preview is served free by OpenRouter (free models), Kilo Code and AIHubMix (free models). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/ernie-5.5-flash-preview/
last_modified_at: 2026-11-26
crumb: ernie-5.5-flash-preview
---

{% raw %}

# Where ernie-5.5-flash-preview is free

**3 rows on the list serve `ernie-5.5-flash-preview` free:** OpenRouter (free models), Kilo Code and AIHubMix (free models). None asks for a card; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-11-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-26 · listed since 2026-11-26

One API key for a rotating set of :free model variants, open-weight and stealth models among them

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 50 requests/day; 20 requests/minute per account

1,000 requests/day per account (after 10 credits purchased all-time)

OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", and its limits page warns that a negative credit balance can produce errors "including for free models" and that a 429 can come from the upstream provider rather than the platform (read 2026-09-27). The docs define the daily counter as "Free-model requests recorded so far in the current UTC day". The higher daily ceiling is granted "starting one credit below the table’s threshold" to absorb rounding and top-up fees.

</details>

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free -m baidu/ernie-5.5-flash-preview:free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `baidu/ernie-5.5-flash-preview:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-11-26 · listed since 2026-11-26

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code -m baidu/ernie-5.5-flash-preview:free`
- Callable ids: `baidu/ernie-5.5-flash-preview:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-26 · listed since 2026-11-26

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; LiquidAI advises against agentic coding with the listed LFM models.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m ernie-5.5-flash-preview-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `ernie-5.5-flash-preview-free`

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-11-13 to 2026-11-17

---

Generated from `registry.yaml` and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
