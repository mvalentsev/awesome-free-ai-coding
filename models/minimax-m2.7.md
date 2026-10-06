---
layout: default
title: 'minimax-m2.7 free: 2 providers, limits and ids, verified 2026-10-05'
description: minimax-m2.7 is served free by AIHubMix (free models) and Routeway. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day the published offer was last checked.
permalink: /models/minimax-m2.7/
last_modified_at: 2026-10-06
crumb: minimax-m2.7
---

{% raw %}

# Where minimax-m2.7 is free

**2 rows on the list serve `minimax-m2.7` free:** AIHubMix (free models) and Routeway. None asks for a card. The published offers were checked on 2026-10-05 and are rechecked twice a week. It measures **notable**: in the upper half of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/minimax-m2-7), below its strong bar.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-24

One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself, with an Anthropic-format /v1/messages too, so a free id can back Claude Code

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: MiMo V2.6 Flash/Pro: 100 requests/day; 5 requests/minute; 1,000,000 tokens/day per account per model

per-model caps, spelled out in each model's catalog description: the newest coding routes — GLM-5.3, GLM-5.2, Kimi K3 and MiMo V2.5 among them — are "limited to 5 requests per minute, 100 requests per day, and 1 million tokens per day", others such as GLM-4.7, MiniMax M3 and kimi-for-coding allow 500 requests a day on the same caps, and the rest of the lane names no figure (read 2026-09-21); the vendor states the quotas reset daily with no trial expiry and no payment method on file. nemotron-3.5-content-safety-free is a guardrail classifier, and of lfm-2.5-2.6b-free the catalog says "the developer advises against using this model for agentic coding tasks". Every free id carries a -free suffix and the paid twin beside it is metered at list rates

</details>

- Base URL: `https://aihubmix.com/v1`
- Key: `AIHUBMIX_API_KEY` — get one at <https://aihubmix.com/token>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://aihubmix.com`
- Codex CLI: [`configs/codex/aihubmix.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/aihubmix.config.toml) — copy it to `~/.codex/`, then `codex -p aihubmix`; set up on the lane by the vendor's own page, <https://docs.aihubmix.com/en/api/Codex-CLI>: "Connect AIHubMix in Codex CLI"
- Callable ids: `coding-minimax-m2.7-free`, `minimax-m2.7-free`

### [Routeway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-10-05 · listed since 2026-09-16

OpenAI-compatible gateway with a rotating :free chat-model lane beside metered models

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free models — every id ending :free — cost nothing and "are rate-limited to 20 requests/minute and 200 requests/day", the FAQ says, where the rate-limits page gives "5 Requests Per Minute (RPM)" and "200 Requests Per Day (RPD)"; past either they answer 429, and the pay-as-you-go ids beside them "require a positive account balance". The lane itself rotates, ids joining and leaving within days while their metered twins stay, and free models "can be removed at any time". A key is sign-up and Create API Key with no payment step in the FAQ, while the terms, last updated 31.05.2025 behind a bot wall this list's client cannot pass, count a payment method among what any account needs. No legal entity is named, and support is by email and Discord. Read 2026-09-27

</details>

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Codex CLI: [`configs/codex/routeway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/routeway.config.toml) — copy it to `~/.codex/`, then `codex -p routeway`; set up on the lane by the vendor's own page, <https://docs.routeway.ai/integrations/agents/codex>: "Use OpenAI’s Codex with Routeway by adding a custom provider"
- Callable ids: `minimax-m2.7:free`

## Rows that listed it before

- [Dahl Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) — listed 2026-09-21 to 2026-09-25

## Related models

- [`minimax-m2.5`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.5/) — free at Kiro, AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.1/) — free at Kiro and AIHubMix (free models)
- [`minimax-m3`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m3/) — free at AIHubMix (free models) and FreeInference (Harvard SEAS)
- [`minimax-m2`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2/) — free at AIHubMix (free models)

---

Generated from `registry.yaml` on 2026-10-06 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
