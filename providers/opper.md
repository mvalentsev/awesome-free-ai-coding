---
layout: default
title: 'Opper free tier: limits, free models, verified 2026-09-24'
description: 'EU-hosted gateway over 700+ models whose free models — Gemma 4 31B and Gemma 4 26B on Google''s route, Laguna S 2.1 and XS 2.1 through Poolside — answer an account with no card on file; every other model needs a card and credits. The pricing FAQ: "Sign up needs no credit card: you get an API key…'
permalink: /providers/opper/
last_modified_at: 2026-09-26
crumb: Opper
---

{% raw %}

# Opper free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [opper.ai](https://opper.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU-hosted gateway over 700+ models whose free models — Gemma 4 31B and Gemma 4 26B on Google's route, Laguna S 2.1 and XS 2.1 through Poolside — answer an account with no card on file; every other model needs a card and credits

## Free models

[`gemma-4-31b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-31b/)

## Limits, in the vendor's words

The pricing FAQ: "Sign up needs no credit card: you get an API key straight away and the free models work in the playground and the API. Add a card to use premium models, pay-as-you-go with no minimum." The llms.txt names one of them — "gemini/gemma-4-31b is a free model, so this call works before you add a card. It runs on a US-hosted route." — and the model directory at opper.ai/models flags five rows free: gemini/gemma-4-31b, gemini/gemma-4-26b-moe, poolside/laguna-s-2.1, poolside/laguna-xs-2.1 and Talkie 1930, a 13B model trained on pre-1931 text. The keyless catalog publishes no price for them, and no page gives the free models a quota or a rate limit. Paid usage is billed at provider rates with "a 3% fee on credit purchases". The operator is Opper Technology AB, in Sweden, on AWS Stockholm. Read 2026-09-17

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://opper.ai/terms-of-service), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Opper never trains on your data. Per-provider data policies are listed in the models directory.” ([source](https://opper.ai/pricing)).

## Connect

- Base URL: `https://api.opper.ai/v3/compat`
- Key: `OPPER_API_KEY` — get one at <https://platform.opper.ai/settings/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.opper.ai/v3/compat`
- Callable ids: `gemini/gemma-4-31b`, `gemini/gemma-4-26b-moe`, `poolside/laguna-s-2.1`, `poolside/laguna-xs-2.1`
- Note: ids are four of the five rows the model directory flags free on 2026-09-17, checked against the keyless catalog at api.opper.ai/v3/models; opper/talkie-1930, an 8K-context period piece, is left out. The Claude Code guide sets ANTHROPIC_BASE_URL=https://api.opper.ai/v3/compat, the client appending /v1/messages

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

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: EU-hosted gateway over 700+ models whose free models — Gemma 4 31B and Gemma 4 26B on Google's route, Laguna S 2.1 and XS 2.1 through Poolside — answer an account with no card on file; every other model needs a card and credits

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
