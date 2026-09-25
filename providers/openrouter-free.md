---
layout: default
title: 'OpenRouter (free models) free tier: limits, free models, verified 2026-09-24'
description: One API key for a rotating set of :free model variants, open-weight and stealth models among them. 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants —…
permalink: /providers/openrouter-free/
---

{% raw %}

# OpenRouter (free models)

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-24 · [openrouter.ai](https://openrouter.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One API key for a rotating set of :free model variants, open-weight and stealth models among them

## Free models

`nemotron-3-ultra`, `gemma-4-31b`, `gemma-4-26b-a4b`, `nemotron-3-super`, `north-mini-code`, `laguna-s-2.1`, `laguna-xs-2.1`, `nemotron-3.5-lightning`, `inkling`, `inkling-small`, `dots-3-note`, `ling-3.0-flash-fin`, `ling-3.0-flash-sante`, `nemotron-3-nano-omni`

## Limits, in the vendor's words

20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM, FREE_MODEL_NO_CREDITS_RPD, FREE_MODEL_HAS_CREDITS_RPD and FREE_MODEL_CREDITS_THRESHOLD — and the table that should show them serves empty cells to anything reading the HTML. OpenRouter's FAQ says its free models "have low rate limits" and "are usually not suitable for production use", warns that a negative credit balance can produce errors "including for free models", and notes a 429 may come from the upstream provider rather than the platform (read 2026-08-14)

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “Wherever possible, OpenRouter works with providers to ensure that prompts will not be trained on, but there are exceptions. If you opt out of training in your account settings, OpenRouter will not route to providers that train.” ([source](https://openrouter.ai/docs/guides/privacy/provider-logging)).

## Connect

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `google/gemma-4-31b-it:free`, `google/gemma-4-26b-a4b-it:free`, `cohere/north-mini-code:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `thinkingmachines/inkling:free`, `thinkingmachines/inkling-small:free`, `dots-studio/dots-3-note-preview:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `liquid/lfm-2.5-2.6b:free`, `z-ai/glm-5.2:free`, `qwen/qwen3.8-27b:free`, `openrouter/free`
- Note: pick models with the :free suffix: every id carrying it is priced 0/0, 20 on 2026-09-24, and the lane rotates, so a new id waits two weeks for the Models column. Kept out of it: openrouter/free, the free-models router; lfm-2.5-2.6b, which LiquidAI advises against agentic coding; and nemotron-3.5-content-safety, a guardrail classifier. Nex-N2.5 Pro and Mini are ignored: the catalog dates their free ids to end 2026-09-25. For Claude Code, OpenRouter's cookbook sets ANTHROPIC_BASE_URL to https://openrouter.ai/api with ANTHROPIC_API_KEY empty and a :free id as ANTHROPIC_MODEL

## Evidence

- Probe: the models catalog at <https://openrouter.ai/api/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://openrouter.ai/docs/faq>
- Source: <https://openrouter.ai/docs/api_reference/limits>
- Source: <https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added gemma-4-26b-a4b, gemma-4-31b; dropped gemma-4
- `2026-09-24` — Free models changed: added dots-3-note, inkling, inkling-small, laguna-s-2.1, laguna-xs-2.1, ling-3.0-flash-fin, ling-3.0-flash-sante, nemotron-3-nano-omni, nemotron-3-super, nemotron-3.5-lightning, north-mini-code
- `2026-08-28` — Free models changed: dropped gpt-oss
- `2026-07-19` — Free models changed: added gemma-4, gpt-oss, nemotron-3-ultra; dropped deepseek, glm-4.5, kimi-k2, qwen3-coder
- `2026-07-19` — Added: One API key for rotating :free variants of frontier models

---

Generated from `registry.yaml` on 2026-09-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
