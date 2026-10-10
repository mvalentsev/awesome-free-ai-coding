---
layout: default
title: 'north-mini-code free: 4 providers, limits and ids, verified 2026-10-08'
description: north-mini-code is served free by OpenRouter (free models), Kilo Code, AIHubMix (free models) and Cohere (trial keys). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/north-mini-code/
last_modified_at: 2026-10-08
crumb: north-mini-code
---

{% raw %}

# Where north-mini-code is free

**4 rows on the list serve `north-mini-code` free:** OpenRouter (free models), Kilo Code, AIHubMix (free models) and Cohere (trial keys). None asks for a card; Kilo Code answers with no account at all. The published offers were checked on 2026-10-08 and are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-08 · listed since 2026-09-24

One API key for a rotating set of :free model variants, open-weight and stealth models among them

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 50 requests/day; 20 requests/minute per account

1,000 requests/day per account (after 10 credits purchased all-time)

OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", and its limits page warns that a negative credit balance can produce errors "including for free models" and that a 429 can come from the upstream provider rather than the platform (read 2026-09-27) The docs define the daily counter as "Free-model requests recorded so far in the current UTC day". The higher daily ceiling is granted "starting one credit below the table’s threshold" to absorb rounding and top-up fees.

</details>

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `cohere/north-mini-code:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · verified 2026-10-08 · listed since 2026-08-05

Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 200 requests/hour per IP

$0 a month; no account for the free lane.  The lane is whatever the gateway marks isFree and the free-model lineup rotates. It costs something other than money: every free id carries mayTrainOnYourPrompts, which almost no metered id does. Auto Free routes over the free models the catalog's autoRouting list names. Everything else runs on pay-as-you-go credits or a Kilo Pass subscription. Read 2026-09-21

</details>

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code`
- Callable ids: `cohere/north-mini-code:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

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
- Callable ids: `north-mini-code-free`

### [Cohere (trial keys)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cohere/)

🔌 LLM APIs with free tier · no card · not offered in mainland China, Russia, Hong Kong and 5 more places · verified 2026-10-08 · listed since 2026-08-14

Cohere's Command models via free trial API keys that never expire, plus a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Trial keys: 1,000 requests/month per key

Trial Chat models: 20 requests/minute per key per model

North Mini Code on production keys: 500 requests/minute per key per model

Trial keys are for evaluation, not production or commercial use; new accounts start with Trial keys. Chat limits differ from those for reranking, embeddings, tokenization and audio. North Mini Code is free on both Trial and production keys until the corresponding rate limit is reached. The trial monthly request allowance applies alongside its per-model rate caps.

</details>

- Base URL: `https://api.cohere.com/compatibility/v1`
- Key: `COHERE_API_KEY` — get one at <https://dashboard.cohere.com/api-keys>
- Callable ids: `north-mini-code-1-0`
- What you send may be used to train or improve models ([the vendor's words](https://cohere.com/privacy)).

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
