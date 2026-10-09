---
layout: default
title: 'OpenRouter (free models) free tier: limits, free models, verified 2026-10-08'
description: 'One API key for a rotating set of :free model variants, open-weight and stealth models among them. Free models: nemotron-3-ultra, gemma-4-31b, gemma-4-26b-a4b, nemotron-3-super, north-mini-code, laguna-s-2.1, laguna-xs-2.1, nemotron-3.5-lightning and 5 more. OpenRouter''s FAQ says its free models…'
permalink: /providers/openrouter-free/
last_modified_at: 2026-10-08
crumb: OpenRouter (free models)
---

{% raw %}

# OpenRouter (free models) free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-08 · [openrouter.ai](https://openrouter.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One API key for a rotating set of :free model variants, open-weight and stealth models among them

## Free models

[`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`gemma-4-31b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-31b/), [`gemma-4-26b-a4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-26b-a4b/), [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/), [`north-mini-code`](https://mvalentsev.github.io/awesome-free-ai-coding/models/north-mini-code/), [`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/), [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/), [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/), [`inkling`](https://mvalentsev.github.io/awesome-free-ai-coding/models/inkling/), [`inkling-small`](https://mvalentsev.github.io/awesome-free-ai-coding/models/inkling-small/), [`dots-3-note`](https://mvalentsev.github.io/awesome-free-ai-coding/models/dots-3-note/), [`ling-3.0-flash-sante`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-sante/), [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/)

## Limits, in the vendor's words

50 requests/day; 20 requests/minute per account

1,000 requests/day per account (after 10 credits purchased all-time)

OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", and its limits page warns that a negative credit balance can produce errors "including for free models" and that a 429 can come from the upstream provider rather than the platform (read 2026-09-27) The docs define the daily counter as "Free-model requests recorded so far in the current UTC day". The higher daily ceiling is granted "starting one credit below the table’s threshold" to absorb rounding and top-up fees.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://openrouter.ai/terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “Wherever possible, OpenRouter works with providers to ensure that prompts will not be trained on, but there are exceptions. If you opt out of training in your account settings, OpenRouter will not route to providers that train.” ([source](https://openrouter.ai/docs/guides/privacy/provider-logging)).

## Connect

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Codex CLI: [`configs/codex/openrouter-free.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/openrouter-free.config.toml) — copy it to `~/.codex/`, then `codex -p openrouter-free`; set up on the lane by the vendor's own page, <https://openrouter.ai/docs/cookbook/coding-agents/codex-cli>: "Configure Codex for OpenRouter"
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `google/gemma-4-31b-it:free`, `google/gemma-4-26b-a4b-it:free`, `cohere/north-mini-code:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `thinkingmachines/inkling:free`, `thinkingmachines/inkling-small:free`, `dots-studio/dots-3-note-preview:free`, `inclusionai/ling-3.0-flash-sante:free`, `liquid/lfm-2.5-2.6b:free`, `openrouter/free`, `apodex/apodex-1.1-mini:free`
- Note: Use IDs with the :free suffix; their input and output prices are zero. openrouter/free chooses a free model automatically. LiquidAI advises against agentic coding with lfm-2.5-2.6b. For Claude Code, set ANTHROPIC_BASE_URL=https://openrouter.ai/api, leave ANTHROPIC_API_KEY empty and use a :free ID as ANTHROPIC_MODEL.

Try it from your terminal with your key in `OPENROUTER_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://openrouter.ai/api/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://openrouter.ai/docs/faq>
- Source: <https://openrouter.ai/docs/api_reference/limits>
- Source: <https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-06` — Free models changed: dropped qwen3.8-27b
- `2026-10-02` — Free models changed: added qwen3.8-27b
- `2026-09-29` — Free models changed: dropped ling-3.0-flash-fin
- `2026-09-25` — Free models changed: added gemma-4-26b-a4b, gemma-4-31b; dropped gemma-4
- `2026-09-24` — Free models changed: added dots-3-note, inkling, inkling-small, laguna-s-2.1, laguna-xs-2.1, ling-3.0-flash-fin, ling-3.0-flash-sante, nemotron-3-nano-omni, nemotron-3-super, nemotron-3.5-lightning, north-mini-code
- `2026-08-28` — Free models changed: dropped gpt-oss
- `2026-07-19` — Free models changed: added gemma-4, gpt-oss, nemotron-3-ultra; dropped deepseek, glm-4.5, kimi-k2, qwen3-coder
- `2026-07-19` — Added: One API key for rotating :free variants of frontier models

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
