---
layout: default
title: 'glm-4.7-flash free: 2 providers, limits and ids, verified 2026-09-24'
description: glm-4.7-flash is served free by AIHubMix (free models) and Z.ai (Zhipu GLM). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/glm-4.7-flash/
last_modified_at: 2026-09-25
crumb: glm-4.7-flash
---

{% raw %}

# Where glm-4.7-flash is free

**2 rows on the list serve `glm-4.7-flash` free:** AIHubMix (free models) and Z.ai (Zhipu GLM). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/glm-4-7-flash), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `glm-4.7-flash-free`

### [Z.ai (Zhipu GLM)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zai-glm/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-07-27

GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4)

- Limits, in the vendor's words: GLM-4.7-Flash, GLM-4.5-Flash and the GLM-4.6V-Flash vision model are the three rows z.ai's own price table reads Free on all four columns — every other model there says "Limited-time Free" instead, including the flagship GLM-5.x. Rate-limited
- Base URL: `https://api.z.ai/api/paas/v4`
- Key: `ZAI_GLM_API_KEY` — get one at <https://z.ai/manage-apikey/apikey-list>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.z.ai/api/anthropic`
- Callable ids: `glm-4.7-flash`
- What you send is not used to train models ([the vendor's words](https://docs.z.ai/legal-agreement/terms-of-use)).

## Rows that listed it before

- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-03; the row itself is archived

## Related models

- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`glm-5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5/) — free at Kiro and AIHubMix (free models)
- [`glm-5-turbo`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5-turbo/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models) and Regolo AI
- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models) and ZCode (Z.ai)
- [`glm-4.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.6/) — free at AIHubMix (free models)
- [`glm-4.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
