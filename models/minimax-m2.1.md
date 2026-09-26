---
layout: default
title: 'minimax-m2.1 free: 2 providers, limits and ids, verified 2026-09-24'
description: minimax-m2.1 is served free by Kiro and AIHubMix (free models). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/minimax-m2.1/
last_modified_at: 2026-09-25
crumb: minimax-m2.1
---

{% raw %}

# Where minimax-m2.1 is free

**2 rows on the list serve `minimax-m2.1` free:** Kiro and AIHubMix (free models). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kiro](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kiro/)

🎁 Trials (no card when possible) · no card · verified 2026-09-24 · listed since 2026-09-24

Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models

- Limits, in the vendor's words: 50 credits/month; requires social login or AWS Builder ID; credits do not roll over; not available in AWS GovCloud, and free-tier requests are always served from the US. Kiro's docs settle what those credits reach, in a table with a Free column: ticked for Claude Sonnet 4.5 and 4.0, Auto, GLM-5, Qwen3 Coder Next, DeepSeek 3.2 and MiniMax M2.5 and M2.1; blank for Claude Sonnet 4.6 and 5, every Opus, Haiku 4.5 and all three GPT-5.6 tiers. The pricing page contradicts itself on exactly that point — its plan card and footnote both say Sonnet 4.5, its FAQ prose says the free tier includes Sonnet 4.6 — so read the docs table, not the FAQ (checked 2026-09-25)
- No API endpoint to paste: this row is a tool you install or sign in to.
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://kiro.dev/docs/privacy-and-security/data-protection/)).

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-24 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code

- Limits, in the vendor's words: per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates
- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Callable ids: `coding-minimax-m2.1-free`

## Related models

- [`minimax-m2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.5/) — free at Kiro, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.7/) — free at AIHubMix (free models) and Routeway
- [`minimax-m3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3/) — free at AIHubMix (free models) and FreeInference (Harvard SEAS)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
