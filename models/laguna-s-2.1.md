---
layout: default
title: 'laguna-s-2.1 free: 1 provider, limits and ids, provider probes 2026-11-09'
description: laguna-s-2.1 is served free by Vercel AI Gateway. It asks for a card on file. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/laguna-s-2.1/
last_modified_at: 2026-11-09
crumb: laguna-s-2.1
---

{% raw %}

# Where laguna-s-2.1 is free

**One row on the list serves `laguna-s-2.1` free:** Vercel AI Gateway. It asks for a card on file. The provider's last scheduled probe was on 2026-11-09; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · last probe 2026-11-09 · listed since 2026-08-14

OpenAI-compatible model gateway with recurring free credit after adding a payment method, plus separate zero-priced model routes

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Gateway credit: $5/month per team

Free credit rate limits: Requests allowance: amount not published (period not published); scope not published (Limits apply per model.)

A team must add a valid payment method before using free credit; otherwise requests return `403 customer_verification_required`. Credit spends at provider list rates and excludes BYOK. Buying credit ends the monthly free credit. Zero-priced model routes remain a separate free mode and do not spend that balance. Use their exact free IDs: a similarly named route without its free suffix can be metered. Ampersand inputs and outputs may be used for model training under its provider privacy notice.

</details>

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Codex CLI: [`configs/codex/vercel-ai-gateway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/vercel-ai-gateway.config.toml) — copy it to `~/.codex/`, then `codex -p vercel-ai-gateway`; Codex's base is `https://ai-gateway.vercel.sh/codex/v1`; set up on the lane by the vendor's own page, <https://vercel.com/docs/ai-gateway/coding-agents/openai-codex>: "Point Codex at its own compatibility endpoint"
- Callable ids: `poolside/laguna-s-2.1-free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Rows that listed it before

- [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) — listed 2026-08-11 to 2026-11-01
- [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/) — listed 2026-09-16 to 2026-11-01
- [AIHubMix (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/) — listed 2026-09-24 to 2026-11-01
- [OpenRouter (free models)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) — listed 2026-09-24 to 2026-11-01
- [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/) — listed 2026-09-14 to 2026-09-23
- [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) — listed 2026-09-02 to 2026-09-16; the row itself is archived
- [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/) — listed 2026-08-14 to 2026-08-20

## Related models

- [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/) — free at NVIDIA NIM (build.nvidia.com)

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
