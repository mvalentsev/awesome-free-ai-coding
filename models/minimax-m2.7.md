---
layout: default
title: 'minimax-m2.7 free: 2 providers, limits and ids, verified 2026-09-24'
description: minimax-m2.7 is served free by AIHubMix (free models) and Routeway. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/minimax-m2.7/
last_modified_at: 2026-09-25
crumb: minimax-m2.7
---

{% raw %}

# Where minimax-m2.7 is free

**2 rows on the list serve `minimax-m2.7` free:** AIHubMix (free models) and Routeway. None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/minimax-m2-7), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `coding-minimax-m2.7-free`, `minimax-m2.7-free`

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-16

OpenAI-compatible gateway whose :free lane rotates — three zero-priced chat models on 2026-09-23, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 269 metered rows in the same catalog

- Limits, in the vendor's words: Free models — every id ending :free — are capped at 5 requests per minute and 200 per day and answer 429 past either; the pay-as-you-go ids beside them have no API-level rate limits, only edge DDoS protection (docs.routeway.ai, read 2026-08-30). The lane itself rotates, ids joining and leaving within days while their metered twins stay. The gateway publishes no legal entity or terms of service and is supported through Discord alone: a fallback lane, not a dependency
- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Callable ids: `minimax-m2.7:free`

## Rows that listed it before

- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25

## Related models

- [`minimax-m2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.5/) — free at Kiro, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.1/) — free at Kiro and AIHubMix (free models)
- [`minimax-m3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3/) — free at AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
