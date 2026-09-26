---
layout: default
title: 'nemotron-3-nano-30b free: 2 providers, limits and ids, verified 2026-09-24'
description: nemotron-3-nano-30b is served free by Requesty and AIHubMix (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/nemotron-3-nano-30b/
last_modified_at: 2026-09-26
crumb: nemotron-3-nano-30b
---

{% raw %}

# Where nemotron-3-nano-30b is free

**2 rows on the list serve `nemotron-3-nano-30b` free:** Requesty and AIHubMix (free models). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Requesty](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

OpenAI-compatible router over a 690+ model catalog with routing, caching and fallbacks; twelve rows in it are priced 0 and the free plan is the same gateway restricted to those

- Limits, in the vendor's words: Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend tracking and EU data residency included; past that the same key moves to pay-as-you-go
- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/nemotron-3-nano-30b-a3b`
- What you send may be used to train or improve models ([the vendor's words](https://www.requesty.ai/privacy)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `nemotron-3-nano-30b-a3b-free`

## Related models

- [`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and LLMTR
- [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/) — free at OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and TokenRouter (PaleBlueDot)
- [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/) — free at OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com), AIHubMix (free models) and LLMTR
- [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/) — free at opencode, OpenRouter (free models), Kilo Code, Requesty, NVIDIA NIM (build.nvidia.com) and AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
