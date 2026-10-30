---
layout: default
title: 'nemotron-3.5-super-vl-120b-a12b free: 5 providers, limits and ids, provider probes 2026-10-26'
description: nemotron-3.5-super-vl-120b-a12b is served free by OpenRouter (free models), Kilo Code, NVIDIA NIM (build.nvidia.com), Cline and LLMTR. None asks for a card; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/nemotron-3.5-super-vl-120b-a12b/
last_modified_at: 2026-10-29
crumb: nemotron-3.5-super-vl-120b-a12b
---

{% raw %}

# Where nemotron-3.5-super-vl-120b-a12b is free

**5 rows on the list serve `nemotron-3.5-super-vl-120b-a12b` free:** OpenRouter (free models), Kilo Code, NVIDIA NIM (build.nvidia.com), Cline and LLMTR. None asks for a card; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-10-26; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-10-29

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
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free -m nvidia/nemotron-3.5-super-vl:free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `nvidia/nemotron-3.5-super-vl:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-10-26 · listed since 2026-10-29

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code -m nvidia/nemotron-3.5-super-vl:free`
- Callable ids: `nvidia/nemotron-3.5-super-vl:free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-10-26 · listed since 2026-10-29

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `nvidia/nemotron-3.5-super-vl-120b-a12b`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/)

🤖 Coding agents & CLIs · no card · last probe 2026-10-26 · listed since 2026-10-29

Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model promotions: Daily usage allowance: amount not published per account per model

Free promotions require a Cline account, with Google, GitHub or email signup and no card. The daily per-model scope is also reported by the client stop message: `You've reached today's free usage limit for this model`. The picker's free list rotates. These models work only in the Cline IDE extension and CLI, not through the Cline API. Free usage may improve model performance and quality.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In Cline's own model list: `cline-free/nemotron-3.5-super-vl`
- What you send may be used to train or improve models ([the vendor's words](https://docs.cline.bot/getting-started/free-models)).

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-10-26 · listed since 2026-10-29

Turkish OpenAI-compatible gateway with free models on a zero balance and dated previews; some previews require a previous top-up

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Nemotron Ultra and Qwen3.8 27B: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3-ultra-550b-a55b`, `qwen/qwen3.8-27b-free`

Heabsy Qwen3.8 27B: Daily usage allowance: amount not published per account; for `heabsy/qwen3.8-27b-heabsy-free`

Nemotron3.5 Super VL: Daily usage allowance: amount not published; scope not published; for `nvidia/nemotron-3.5-super-vl-free`

Jais 3 MoVA: 200,000 tokens/day per account per model (Input and output count together; lower first-day allowance for new accounts); for `ifm/jais-3-mova-36b-a4b`. 00:00'da (TSİ)

K2 Horizon: 200,000 tokens/day per account per model (Input, output and reasoning count together; lower first-day allowance for new accounts); for `ifm/k2-horizon-375b-a23b`. 00:00'da (TSİ)

MiniMax M3.1 Flash: 5,000,000 tokens/day per account per model; for `minimax/minimax-m3.1-flash-free`. 00:00’da (TSİ)

Shanghai AI Lab models: 500,000 tokens/day sharing scope disputed (Per model; model pages say per person, the guide says per account. Input, output and reasoning count; new accounts have a lower first-day allowance.); for `internlm/intern-s2-free`, `internlm/atria-dawn-free`, `internlm/atria-dawn-preview-free`, `internlm/agents-a1-free`, `internlm/sage-a1.5-free`. 00:00'da (TSİ)

Free chat rows can be called on a new account with zero balance before any top-up. Paid use is prepaid; an 8% margin applies once at top-up, not to model prices. Prompt and response bodies are not permanently written to the usage and billing database. Heabsy requires provider-specific data-transfer consent: "Heabsy models cannot be called until your account has granted the data-transfer consent for Heabsy". Its stream is buffered until completion, and reasoning_effort is unsupported. For free Nemotron3.5 Super VL, inputs "may be retained by the provider and used to improve the model". Shanghai AI Lab prompts and completions may be logged by the provider and used to improve models.

</details>

- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `nvidia/nemotron-3.5-super-vl-free`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/nemotron-3-5-super-vl/)).

## Related models

- [`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and LLMTR
- [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and Vercel AI Gateway
- [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/) — free at OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and TokenRouter (PaleBlueDot)
- [`nemotron-3-nano-30b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-30b/) — free at Requesty
- [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/) — free at Requesty

---

Generated from `registry.yaml` on 2026-10-31 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
