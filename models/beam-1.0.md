---
layout: default
title: 'beam-1.0 free: 2 providers, limits and ids, provider probes 2026-11-12'
description: beam-1.0 is served free by opencode and Vercel AI Gateway. Vercel AI Gateway asks for a card on file, the rest for none. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/beam-1.0/
last_modified_at: 2026-11-12
crumb: beam-1.0
---

{% raw %}

# Where beam-1.0 is free

**2 rows on the list serve `beam-1.0` free:** opencode and Vercel AI Gateway. Vercel AI Gateway asks for a card on file, the rest for none. The providers' last scheduled probes were on 2026-11-12; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [opencode](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/)

🤖 Coding agents & CLIs · no card · last probe 2026-11-12 · listed since 2026-11-10

Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — inside OpenCode only, no sign-in; any provider via BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model usage: Usage allowance: amount not published (period not published); scope not published

Free models work only inside OpenCode; other clients receive `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Use `opencode/<model-id>` and select the Free variant. Offers rotate; each named free offer is "available on OpenCode for a limited time". Collected free-model data may improve models; NVIDIA offers are trial-only and exclude personal or confidential data. Flint 40B Free allows training and retains data for 30 days. Beam Free's provider does not train on inputs and retains them for 30 days; its listed territorial exclusions include Russia. Inkling 2 Small Free permits training. It has model-specific territorial exclusions, including Russia. LongCat 2.5 Free is hosted in China; its provider does not train on inputs or retain them.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In opencode's own model list: `Beam Free`
- What you send may be used to train or improve models ([the vendor's words](https://opencode.ai/v2/docs/console/models/)).

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · last probe 2026-11-12 · listed since 2026-10-30

OpenAI-compatible model gateway with recurring free credit after adding a payment method, plus separate zero-priced model routes

- Limits, in the vendor's words: Beam launch offer: Usage allowance: amount not published (period not published); scope not published (The free route stops at the end of the launch offer; the end date and numerical allowance are unpublished.); for `reflection/beam-free`

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Gateway credit: $5/month per team

Free credit rate limits: Requests allowance: amount not published (period not published); scope not published (Limits apply per model.)

A team must add a valid payment method before using free credit; otherwise requests return `403 customer_verification_required`. Credit spends at provider list rates and excludes BYOK. Buying credit ends the monthly free credit. Zero-priced model routes remain a separate free mode and do not spend that balance. Use their exact free IDs: a similarly named route without its free suffix can be metered. Ampersand inputs and outputs may be used for model training under its provider privacy notice.

</details>

- Base URL: `https://ai-gateway.vercel.sh/v1`
- Key: `VERCEL_AI_GATEWAY_API_KEY` — get one at <https://vercel.com/dashboard/ai-gateway/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://ai-gateway.vercel.sh`
- Codex CLI: [`configs/codex/vercel-ai-gateway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/vercel-ai-gateway.config.toml) — copy it to `~/.codex/`, then `codex -p vercel-ai-gateway -m reflection/beam-free`; Codex's base is `https://ai-gateway.vercel.sh/codex/v1`; set up on the lane by the vendor's own page, <https://vercel.com/docs/ai-gateway/coding-agents/openai-codex>: "Point Codex at its own compatibility endpoint"
- Callable ids: `reflection/beam-free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)).

## Rows that listed it before

- [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/) — listed 2026-11-02 to 2026-11-12
- [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/) — listed 2026-11-05 to 2026-11-12
- [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) — listed 2026-10-31 to 2026-11-10
- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-17 to 2026-10-22

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
