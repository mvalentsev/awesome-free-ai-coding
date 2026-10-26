---
layout: default
title: 'nemotron-3.5-lightning free: 6 providers, limits and ids, provider probes 2026-10-26'
description: nemotron-3.5-lightning is served free by opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com) and AIHubMix (free models). None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's…
permalink: /models/nemotron-3.5-lightning/
last_modified_at: 2026-10-26
crumb: nemotron-3.5-lightning
---

{% raw %}

# Where nemotron-3.5-lightning is free

**6 rows on the list serve `nemotron-3.5-lightning` free:** opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com) and AIHubMix (free models). None asks for a card; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-10-26 · listed since 2026-08-14

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Flint 40B Free allows training and retains data for 30 days. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-24

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
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free -m nvidia/nemotron-3.5-lightning:free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `nvidia/nemotron-3.5-lightning:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-10-26 · listed since 2026-09-24

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code -m nvidia/nemotron-3.5-lightning:free`
- Callable ids: `nvidia/nemotron-3.5-lightning:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-17

OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks

- Limits, in the vendor's words: 200 requests/day per account

No credit card for the Free plan, which serves free models only. Routing, caching, fallbacks, spend tracking and EU data residency are included. Past the free allowance the same key moves to pay-as-you-go.
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/nemotron-3.5-lightning-30b-a3b`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-10-26 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `nvidia/nemotron-3.5-lightning-30b-a3b`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-24

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 100/day coding routes: 5 requests/minute; 100 requests/day; 1,000,000 tokens/day per account per model; for `xiaomi-mimo-v2.6-pro-free`, `coding-glm-5.3-flash-free`, `coding-glm-5.3-free`, `xiaomi-mimo-v2.6-flash-free`, `coding-glm-5.2-free`, `coding-kimi-k3-free`, `coding-glm-5.1-free`, `coding-minimax-m2.7-free`, `coding-glm-5-free`, `coding-glm-5-turbo-free`, `coding-minimax-m2.5-free`

500/day coding routes: 5 requests/minute; 500 requests/day; 1,000,000 tokens/day per account per model; for `coding-minimax-m3-free`, `glm-4.7-flash-free`, `coding-glm-4.7-free`, `k2.6-code-preview-free`, `coding-minimax-m2.1-free`, `kimi-for-coding-free`, `coding-glm-4.6-free`, `coding-minimax-m2-free`

Other free routes: Usage allowance: amount not published (period not published); scope not published; for `agents-a1-free`, `intern-s2-free`, `dots-3-note-preview-free`, `lfm-2.5-2.6b-free`, `nemotron-3.5-lightning-free`, `nemotron-3-super-120b-a12b-free`, `nemotron-3-nano-omni-30b-a3b-reasoning-free`, `nemotron-3-ultra-550b-a55b-free`, `north-mini-code-free`, `laguna-xs-2.1-free`, `laguna-s-2.1-free`, `mimo-v2-flash-free`

Qwen3.8 Flash/Max GMI promotion: Usage allowance: amount not published (period not published) per account per model (30 days from launch or until campaign credits run out; launch date unconfirmed.); for `qwen3.8-flash-free`, `qwen3.8-max-free`

Gemma 4 free routes: Usage allowance: amount not published (period not published); scope not published; for `gemma-4-26b-a4b-it-free`, `gemma-4-31b-it-free`

Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m nemotron-3.5-lightning-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `nemotron-3.5-lightning-free`

## Related models

- [`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and LLMTR
- [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/) — free at OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and TokenRouter (PaleBlueDot)
- [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/) — free at OpenRouter (free models), Kilo Code, Requesty, AIHubMix (free models) and LLMTR
- [`nemotron-3-nano-30b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-30b/) — free at Requesty

---

Generated from `registry.yaml` on 2026-10-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
