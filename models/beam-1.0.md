---
layout: default
title: 'beam-1.0 free: 4 providers, limits and ids, provider probes 2026-11-09'
description: beam-1.0 is served free by Kilo Code, Cline, Vercel AI Gateway and Nous Portal (Hermes Agent). Vercel AI Gateway asks for a card on file, the rest for none; Kilo Code answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/beam-1.0/
last_modified_at: 2026-11-09
crumb: beam-1.0
---

{% raw %}

# Where beam-1.0 is free

**4 rows on the list serve `beam-1.0` free:** Kilo Code, Cline, Vercel AI Gateway and Nous Portal (Hermes Agent). Vercel AI Gateway asks for a card on file, the rest for none; Kilo Code answers with no account at all. The providers' last scheduled probes were on 2026-11-09; their offers are rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Kilo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/)

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · last probe 2026-11-09 · listed since 2026-10-31

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

- Limits, in the vendor's words: 200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.
- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code -m reflection/beam-free`
- Callable ids: `reflection/beam-free`
- What you send may be used to train or improve models ([the vendor's words](https://api.kilo.ai/api/gateway/models)).

### [Cline](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/)

🤖 Coding agents & CLIs · no card · last probe 2026-11-09 · listed since 2026-11-05

Open-source coding agent for VS Code, JetBrains, the terminal and Cline Desktop; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free model promotions: Daily usage allowance: amount not published per account per model

Free promotions require a Cline account, with Google, GitHub or email signup and no card. The daily per-model scope is also reported by the client stop message: `You've reached today's free usage limit for this model`. The picker's free list rotates. Use these promotions in the IDE extensions, CLI or Cline Desktop; their free quotas do not cover the Cline API. Free usage may improve model performance and quality.

</details>

- No API endpoint to paste: this row is a tool you install or sign in to.
- In Cline's own model list: `reflection/beam-free`
- What you send may be used to train or improve models ([the vendor's words](https://docs.cline.bot/getting-started/free-models)).

### [Vercel AI Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/)

🧭 Aggregators (one key, many providers) · card required · last probe 2026-11-09 · listed since 2026-10-30

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

### [Nous Portal (Hermes Agent)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/)

🧭 Aggregators (one key, many providers) · no card · last probe 2026-11-09 · listed since 2026-11-02

Nous Research's inference portal with a $0 Free plan for :free models, accessible through an OpenAI-compatible API and Hermes Agent

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Free models: Usage allowance: amount not published (period not published) per account

Choose the Free plan and use exact :free IDs; they are zero-priced, while metered routes are outside it. Use a portal key with ordinary API clients; the catalog itself is public. The Free plan publishes no card requirement or numerical rate cap.

</details>

- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `reflection/beam-1.0-501b-a23b:free`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://portal.nousresearch.com/privacy)).

## Rows that listed it before

- [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) — listed 2026-10-17 to 2026-10-22

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
