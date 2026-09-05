---
layout: default
title: 'OpenRouter (free models) free tier: limits, free models, verified 2026-09-03'
description: One API key for rotating :free variants of frontier models. 20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM,…
permalink: /providers/openrouter-free/
---

{% raw %}

# OpenRouter (free models)

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-09-03 · [openrouter.ai](https://openrouter.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One API key for rotating :free variants of frontier models

## Free models

`nemotron-3-ultra`, `gemma-4`

## Limits, in the vendor's words

20 requests per minute on any :free id, 50 requests per day, and 1,000 per day once the account has purchased at least 10 credits all-time. Those four figures are in the page only as JS constants — FREE_MODEL_RATE_LIMIT_RPM, FREE_MODEL_NO_CREDITS_RPD, FREE_MODEL_HAS_CREDITS_RPD and FREE_MODEL_CREDITS_THRESHOLD — and the table that should show them serves empty cells to anything reading the HTML. OpenRouter describes :free as "always provided for free and has low rate limits", warns that a negative credit balance can produce errors "including for free models", and notes a 429 may come from the upstream provider rather than the platform (read 2026-08-14)

## Connect

- Base URL: `https://openrouter.ai/api/v1`
- Key: `OPENROUTER_API_KEY` — get one at <https://openrouter.ai/settings/keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://openrouter.ai/api`
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `nvidia/nemotron-3.5-content-safety:free`, `google/gemma-4-31b-it:free`, `google/gemma-4-26b-a4b-it:free`, `cohere/north-mini-code:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `z-ai/glm-5.2:free`, `minimax/minimax-m3:free`, `minimax/minimax-m2.7:free`, `thinkingmachines/inkling:free`, `thinkingmachines/inkling-small:free`, `dots-studio/dots-3-note-preview:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `liquid/lfm-2.5-2.6b:free`, `openrouter/free`
- Note: pick models with the :free suffix; all nineteen ids carrying it are priced 0/0 and the other 409 rows are metered, bar Google's two Lyria 3 music previews at 0 without the suffix (read 2026-09-05; eighteen :free ids and 354 metered on 2026-08-28, inclusionai/ling-3.0-flash-sante:free the arrival since). openai/gpt-oss-20b:free left that set between the 2026-08-20 and 2026-08-24 probes, leaving its metered twin behind and taking gpt-oss out of the column. Six are not coding models: openrouter/free is the Free Models Router, priced 0/0, picking whichever free model is up and the id that survives this lane rotating; nemotron-3.5-content-safety is a guardrail, ling-3.0-flash-fin finance-tuned and ling-3.0-flash-sante health-tuned, nemotron-3-nano-omni a perception sub-agent, and LiquidAI warns lfm-2.5-2.6b off agentic coding The Claude Code cookbook sets ANTHROPIC_BASE_URL to https://openrouter.ai/api — the "Anthropic Skin", which "behaves exactly like the Anthropic API" and maps model names — with ANTHROPIC_API_KEY explicitly empty; a :free id in ANTHROPIC_MODEL keeps the session on the free lane, and the page warns Claude Code "may not work correctly with other providers" openrouter/free is the vendor's own router over the :free set rather than a model, so it sits last: the first id is the one the generated Claude Code function leads with, and a router can land on a free model without tool use

## Evidence

- Probe: the models catalog at <https://openrouter.ai/api/v1/models>, free rows carrying `:free`, every listed family required at a zero price
- Source: <https://openrouter.ai/docs/faq>
- Source: <https://openrouter.ai/docs/api_reference/limits>
- Source: <https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration>

## History

- `2026-08-27` — Free models changed: dropped gpt-oss
- `2026-07-19` — Free models changed: added gemma-4, gpt-oss, nemotron-3-ultra; dropped deepseek, glm-4.5, kimi-k2, qwen3-coder
- `2026-07-19` — Added to the list: One API key for rotating :free variants of frontier models

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
