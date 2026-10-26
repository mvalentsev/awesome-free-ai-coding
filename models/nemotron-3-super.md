---
layout: default
title: 'nemotron-3-super free: 4 providers, limits and ids, provider probes 2026-10-26'
description: nemotron-3-super is served free by OpenRouter (free models), Kilo Code, Requesty and LLMTR. None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/nemotron-3-super/
last_modified_at: 2026-10-26
crumb: nemotron-3-super
---

{% raw %}

# Where nemotron-3-super is free

**4 rows on the list serve `nemotron-3-super` free:** OpenRouter (free models), Kilo Code, Requesty and LLMTR. None asks for a card; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

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
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free -m nvidia/nemotron-3-super-120b-a12b:free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `nvidia/nemotron-3-super-120b-a12b:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-10-26 · listed since 2026-08-11

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code -m nvidia/nemotron-3-super-120b-a12b:free`
- Callable ids: `nvidia/nemotron-3-super-120b-a12b:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-08-11

OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks

- Limits, in the vendor's words: 200 requests/day per account

No credit card for the Free plan, which serves free models only. Routing, caching, fallbacks, spend tracking and EU data residency are included. Past the free allowance the same key moves to pay-as-you-go.
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/nemotron-3-super-120b-a12b`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-09-24

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra/Super and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `qwen/qwen3.8-27b-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Nemotron3.5 Super VL: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3.5-super-vl-free`

Jais 3 MoVA: 200,000 tokens/day per account per model (Input and output count together; lower first-day allowance for new accounts); for `ifm/jais-3-mova-36b-a4b`. 00:00'da (TSİ)

K2 Horizon: 200,000 tokens/day per account per model (Input, output and reasoning count together; lower first-day allowance for new accounts); for `ifm/k2-horizon-375b-a23b`. 00:00'da (TSİ)

MiniMax M3.1 Flash: 5,000,000 tokens/day per account per model; for `minimax/minimax-m3.1-flash-free`. 00:00’da (TSİ)

Vast-10M Flash: 10,000,000 tokens/day per person; for `voltropy/vast-10m-flash-free`

Shanghai AI Lab models: 500,000 tokens/day sharing scope disputed (Per model; model pages say per person, the guide says per account. Input, output and reasoning count; new accounts have a lower first-day allowance.); for `internlm/intern-s2-free`, `internlm/atria-dawn-free`, `internlm/atria-dawn-preview-free`, `internlm/agents-a1-free`, `internlm/sage-a1.5-free`. 00:00'da (TSİ)

Free chat rows can be called on a new account with zero balance before any top-up. Laguna XS 2.1 follows Poolside's free inference offer, without a token allowance to track. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model". Shanghai AI Lab prompts and completions may be logged by the provider and used to improve models.

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3-super-120b-a12b`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

## Rows that listed it before

- [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/) — listed 2026-09-24 to 2026-10-26
- [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/) — listed 2026-09-22 to 2026-10-20
- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-16; the row itself is archived

## Related models

- [`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and LLMTR
- [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/) — free at OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and TokenRouter (PaleBlueDot)
- [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com) and AIHubMix (free models)
- [`nemotron-3-nano-30b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-30b/) — free at Requesty

---

Generated from `registry.yaml` on 2026-10-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
