---
layout: default
title: 'minimax-m3 free: 2 providers, limits and ids, verified 2026-09-24'
description: minimax-m3 is served free by AIHubMix (free models) and FreeInference (Harvard SEAS). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/minimax-m3/
last_modified_at: 2026-09-25
crumb: minimax-m3
---

{% raw %}

# Where minimax-m3 is free

**2 rows on the list serve `minimax-m3` free:** AIHubMix (free models) and FreeInference (Harvard SEAS). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `coding-minimax-m3-free`

### [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-05

Harvard SEAS's MadSys Lab serving open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

- Limits, in the vendor's words: No quota figure is published: the landing page says "Free to use", "No credit card required" and "Generous quota for research and prototyping", and the terms say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity". It is "an experimental research service", and prompts are not private: "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05
- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: the row lists none for this model

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-09-02 to 2026-09-07

## Related models

- [`minimax-m2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.5/) — free at Kiro, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.1/) — free at Kiro and AIHubMix (free models)
- [`minimax-m2.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.7/) — free at AIHubMix (free models) and Routeway

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
