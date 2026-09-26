---
layout: default
title: 'glm-5 free: 2 providers, limits and ids, verified 2026-09-24'
description: glm-5 is served free by Kiro and AIHubMix (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/glm-5/
last_modified_at: 2026-09-25
crumb: glm-5
---

{% raw %}

# Where glm-5 is free

**2 rows on the list serve `glm-5` free:** Kiro and AIHubMix (free models). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kiro](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kiro/)

🎁 Trials (no card when possible) · no card · verified 2026-09-24 · listed since 2026-09-25

Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models

- Limits, in the vendor's words: 50 credits/month; requires social login or AWS Builder ID; credits do not roll over; not available in AWS GovCloud, and free-tier requests are always served from the US. Kiro's docs settle what those credits reach, in a table with a Free column: ticked for Claude Sonnet 4.5 and 4.0, Auto, GLM-5, Qwen3 Coder Next, DeepSeek 3.2 and MiniMax M2.5 and M2.1; blank for Claude Sonnet 4.6 and 5, every Opus, Haiku 4.5 and all three GPT-5.6 tiers. The pricing page contradicts itself on exactly that point — its plan card and footnote both say Sonnet 4.5, its FAQ prose says the free tier includes Sonnet 4.6 — so read the docs table, not the FAQ (checked 2026-09-25)
- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://kiro.dev/docs/privacy-and-security/data-protection/)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-08-14

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `coding-glm-5-free`

## Rows that listed it before

- [Regolo AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/) — listed 2026-08-30 to 2026-09-22

## Related models

- [`glm-5.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.1/) — free at AIHubMix (free models), Alibaba Cloud Model Studio (DashScope, international) and FreeInference (Harvard SEAS)
- [`glm-5.3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3-flash/) — free at Freebuff, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`glm-4.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-4.7-flash/) — free at AIHubMix (free models) and Z.ai (Zhipu GLM)
- [`glm-5.2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.2/) — free at AIHubMix (free models) and Regolo AI
- [`glm-5.3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/glm-5.3/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
