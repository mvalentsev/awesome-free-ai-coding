---
layout: default
title: 'gemma-4-31b free: 6 providers, limits and ids, provider probes 2026-11-09'
description: gemma-4-31b is served free by OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models), Regolo AI and Opper. None asks for a card. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/gemma-4-31b/
last_modified_at: 2026-11-10
crumb: gemma-4-31b
---

{% raw %}

# Where gemma-4-31b is free

**6 rows on the list serve `gemma-4-31b` free:** OpenRouter (free models), Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models), Regolo AI and Opper. None asks for a card. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-09-25

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
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free -m google/gemma-4-31b-it:free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `google/gemma-4-31b-it:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://openrouter.ai/docs/guides/privacy/provider-logging)).

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-09-25

OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks

- Limits, in the vendor's words: 200 requests/day per account

No credit card for the Free plan, which serves free models only. Routing, caching, fallbacks, spend tracking and EU data residency are included. Past the free allowance the same key moves to pay-as-you-go.
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `google/gemma-4-31b-it`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/)

🔌 LLM APIs with free tier · no card · not offered in Russia, Pakistan, Bangladesh and 11 more places · last probe 2026-11-09 · listed since 2026-09-24

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Published ceiling: 40 requests/minute; 10,000 requests/day per account

No card, but an API key requires an NVIDIA Developer Program account and phone verification in a supported country. Published ceilings can vary by model and traffic can cause throttling. Vendor forum reports describe new personal keys that can list models but receive 404 on chat calls; an issued key alone does not establish working inference. Model pages identify available and deprecated endpoints; copy current IDs from the catalog.

</details>

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `google/gemma-4-31b-it`
- What you send may be used to train or improve models ([the vendor's words](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-06

OpenAI-compatible model gateway with zero-priced routes and an Anthropic-format endpoint for coding clients

- Limits, in the vendor's words: Gemma 4 free routes: Usage allowance: amount not published (period not published); scope not published; for `gemma-4-31b-it-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free IDs end in -free; paid twins are metered at list prices. The daily request and token caps are independent per account and model, rather than a pool to split across models. Published caps apply to their named model IDs; the remaining routes have no numerical budget published. Request limits and campaign durations apply to their named IDs. nemotron-3.5-content-safety-free is a classifier; the lfm-2.5-2.6b-free developer advises against agentic coding use.

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://console.aihubmix.com/workspaces/default/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix -m gemma-4-31b-it-free`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex (CLI and desktop app)"
- Callable ids: `gemma-4-31b-it-free`

### [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/)

🎁 Trials (no card when possible) · no card · last probe 2026-11-09 · listed since 2026-09-27

EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: 30-day trial: 1,000,000 tokens/day per account

"Start your 30-day free trial ... No credit card required, no commitment": the trial card names "1 month duration" ("Full access for 30 days, then choose a plan"), and "Stricter rate limits" with "Fair usage throttling applies", against "All Core Models", which on the same page is every chat model in the library table (each marked Included under Core). Nothing survives the 30 days — the page names no grant after it, only paid plans — and the daily figure is the only number the trial publishes. Brick v1 Beta is a lightweight prompt-complexity classifier for LLM routing pipelines and is excluded from coding configs.

</details>

- Base URL: `https://api.regolo.ai/v1`
- Key: `REGOLO_API_KEY` — get one at <https://dashboard.regolo.ai>
- Callable ids: `gemma4-31b`
- What you send is not used to train models ([the vendor's words](https://regolo.ai/faq/)).

### [Opper](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opper/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-09-17

EU-hosted model gateway advertising a free route before adding a card; current documentation conflicts on its availability

- Limits, in the vendor's words: Advertised route; free access unconfirmed: Usage allowance: published sources disagree (period not published); scope not published

The signup guide advertises a free US-hosted Gemma route before adding a card, but the current directory has no free routes and its Gemma page lists paid alternatives. The API catalog retains the ID without a price or availability claim. Free access remains unconfirmed. Paid credit purchases add a 3% fee. Opper Technology AB operates in Sweden on AWS Stockholm.
- Base URL: `https://api.opper.ai/v3/compat`
- Key: `OPPER_API_KEY` — get one at <https://platform.opper.ai/settings/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.opper.ai/v3/compat`
- Codex CLI: [`configs/codex/opper.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/opper.config.toml) — copy it to `~/.codex/`, then `codex -p opper`; set up on the lane by the vendor's own page, <https://docs.opper.ai/integrations/coding-agents/codex>: "Run OpenAI's Codex CLI on any model in the Opper catalog"
- Callable ids: `gemini/gemma-4-31b`
- What you send is not used to train models ([the vendor's words](https://opper.ai/pricing)).

## Related models

- [`gemma-4-26b-a4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-26b-a4b/) — free at OpenRouter (free models) and AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-11-11 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
