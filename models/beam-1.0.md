---
layout: default
title: 'beam-1.0 free: 1 provider, limits and ids, provider probes 2026-10-26'
description: beam-1.0 is served free by Vercel AI Gateway. It asks for a card on file. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/beam-1.0/
last_modified_at: 2026-10-30
crumb: beam-1.0
---

{% raw %}

# Where beam-1.0 is free

**One row on the list serves `beam-1.0` free:** Vercel AI Gateway. It asks for a card on file. The provider's last scheduled probe was on 2026-10-26; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · last probe 2026-10-26 · listed since 2026-10-30

OpenAI-compatible model gateway with $5 of monthly credit after adding a payment method, plus separate zero-priced model routes

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Gateway credit: $5/month per team

Free credit rate limits: Requests allowance: amount not published (period not published); scope not published (Limits apply per model.)

Beam launch offer: Usage allowance: amount not published (period not published); scope not published (The free route stops at the end of the launch offer; the end date and numerical allowance are unpublished.); for `reflection/beam-free`

A team must add a valid payment method before using free credit; otherwise requests return `403 customer_verification_required`. Credit spends at provider list rates and excludes BYOK. Buying credit ends the monthly free credit. Zero-priced model routes remain a separate free mode and do not spend that balance. Use their exact free IDs: a similarly named route without its free suffix can be metered.

</details>

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Codex CLI: [`configs/codex/vercel-ai-gateway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/vercel-ai-gateway.config.toml) — copy it to `~/.codex/`, then `codex -p vercel-ai-gateway -m reflection/beam-free`; Codex's base is `https://ai-gateway.vercel.sh/codex/v1`; set up on the lane by the vendor's own page, <https://vercel.com/docs/ai-gateway/coding-agents/openai-codex>: "Point Codex at its own compatibility endpoint"
- Callable ids: `reflection/beam-free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-17 to 2026-10-22

---

Generated from `registry.yaml` on 2026-10-30 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
