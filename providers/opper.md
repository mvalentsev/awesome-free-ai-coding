---
layout: default
title: 'Opper free tier: limits, free models, verified 2026-10-01'
description: 'EU-hosted model gateway advertising a free route before adding a card; current documentation conflicts on its availability. Free models: gemma-4-31b. The signup guide and llms.txt still say "gemini/gemma-4-31b is a free model, so this call works before you add a card. It runs on a US-hosted…'
permalink: /providers/opper/
last_modified_at: 2026-10-01
crumb: Opper
---

{% raw %}

# Opper free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-01 · [opper.ai](https://opper.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU-hosted model gateway advertising a free route before adding a card; current documentation conflicts on its availability

## Free models

[`gemma-4-31b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-31b/)

## Limits, in the vendor's words

The signup guide and llms.txt still say "gemini/gemma-4-31b is a free model, so this call works before you add a card. It runs on a US-hosted route." The 2026-10-01 directory lists no free routes and omits that id; the Gemma page lists premium routes from other providers. The API catalog retains the Gemini id but states no price or availability. Free access on the advertised route remains unconfirmed. No free quota or rate is published. Paid usage adds "a 3% fee on credit purchases". Opper Technology AB operates in Sweden on AWS Stockholm. Read 2026-10-01

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://opper.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Opper never trains on your data. Per-provider data policies are listed in the models directory.” ([source](https://opper.ai/pricing)).

## Connect

- Base URL: `https://api.opper.ai/v3/compat`
- Key: `OPPER_API_KEY` — get one at <https://platform.opper.ai/settings/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.opper.ai/v3/compat`
- Codex CLI: [`configs/codex/opper.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/opper.config.toml) — copy it to `~/.codex/`, then `codex -p opper`; set up on the lane by the vendor's own page, <https://docs.opper.ai/integrations/coding-agents/codex>: "Run OpenAI's Codex CLI on any model in the Opper catalog"
- Callable ids: `gemini/gemma-4-31b`
- Note: The signup guide advertises gemini/gemma-4-31b as free before adding a card, but the model directory omits that route; availability is uncertain. For Claude Code, use ANTHROPIC_BASE_URL=https://api.opper.ai/v3/compat; the client appends /v1/messages.

Try it from your terminal with your key in `OPPER_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.opper.ai/v3/compat/chat/completions \
  -H "Authorization: Bearer $OPPER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemini/gemma-4-31b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://opper.ai/llms.txt>, anchored on `gemini/gemma-4-31b is a free model`, `the free models work in the playground and the API`; ids checked in <https://api.opper.ai/v3/models?limit=0>
- Source: <https://opper.ai/pricing.md>
- Source: <https://opper.ai/llms.txt>
- Source: <https://docs.opper.ai/guides/claude-code-router.md>
- Source: <https://opper.ai/sign-up/free.md>
- Source: <https://opper.ai/models>
- Source: <https://opper.ai/google/gemma-4-31b-it.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: EU-hosted gateway over 700+ models whose free models — Gemma 4 31B and Gemma 4 26B on Google's route, Laguna S 2.1 and XS 2.1 through Poolside — answer an account with no card on file; every other model needs a card and credits

---

Generated from `registry.yaml` on 2026-10-02 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
