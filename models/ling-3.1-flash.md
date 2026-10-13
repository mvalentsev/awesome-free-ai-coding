---
layout: default
title: 'ling-3.1-flash free: 1 provider, limits and ids, provider probes 2026-10-13'
description: ling-3.1-flash is served free by Vercel AI Gateway. It asks for a card on file. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/ling-3.1-flash/
last_modified_at: 2026-10-13
crumb: ling-3.1-flash
---

{% raw %}

# Where ling-3.1-flash is free

**One row on the list serves `ling-3.1-flash` free:** Vercel AI Gateway. It asks for a card on file. The provider's last scheduled probe was on 2026-10-13; its offer is rechecked twice a week. It measures **strong**: within 25 points of the top of the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/ling-3-1-flash).

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · last probe 2026-10-13 · listed since 2026-10-13

One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits every month once the team has a payment method on file, and language models priced at zero that never touch the credit

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Gateway credit: $5/month per team

Zero-priced model routes: Usage allowance: amount not published (period not published) per team

A team must add a valid payment method before using free credit; otherwise requests return `403 customer_verification_required`. Credit spends at provider list rates, has lower per-model rate limits and excludes BYOK. Buying credit ends the monthly free credit. Zero-priced model routes remain a separate free mode and do not spend that balance. Use their exact free IDs: a similarly named route without its free suffix can be metered.

</details>

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Codex CLI: [`configs/codex/vercel-ai-gateway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/vercel-ai-gateway.config.toml) — copy it to `~/.codex/`, then `codex -p vercel-ai-gateway`; Codex's base is `https://ai-gateway.vercel.sh/codex/v1`; set up on the lane by the vendor's own page, <https://vercel.com/docs/ai-gateway/coding-agents/openai-codex>: "Point Codex at its own compatibility endpoint"
- Callable ids: `inclusionai/ling-3.1-flash`, `inclusionai/ling-3.1-flash-free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-01 to 2026-10-13

## Related models

- [`ling-3.0-flash-fin`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-fin/) — free at opencode and Nous Portal (Hermes Agent)
- [`ling-3.0-tiny`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-tiny/) — free at Requesty and AIHubMix (free models)
- [`ling-3.0-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash/) — free at AIHubMix (free models)
- [`ling-3.0-flash-sante`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-sante/) — free at Nous Portal (Hermes Agent)

---

Generated from `registry.yaml` on 2026-10-13 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
