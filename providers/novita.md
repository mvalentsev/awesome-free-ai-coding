---
layout: default
title: 'Novita AI free tier: limits, free models, verified 2026-10-26'
description: Inference cloud with a zero-priced chat model through an OpenAI-compatible API, including tool calling and structured output. Apodex 1.1 Mini has zero input and output prices on its public model page, pricing table and API catalog. An account and API key are required. The general quickstart asks…
permalink: /providers/novita/
last_modified_at: 2026-10-26
crumb: Novita AI
---

{% raw %}

# Novita AI free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-26 · [novita.ai](https://novita.ai/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Inference cloud with a zero-priced chat model through an OpenAI-compatible API, including tool calling and structured output

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Zero-priced model: Requests allowance: amount not published (period not published); scope not published

Apodex 1.1 Mini has zero input and output prices on its public model page, pricing table and API catalog. An account and API key are required. The general quickstart asks users to check available credit and model access; it does not state a minimum payment for this zero-priced model. No numeric Free request allowance or offer deadline is published on these pages. Other models are metered.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://novita.ai/legal/terms-of-service), read 2026-10-26).

## Connect

- Base URL: `https://api.novita.ai/openai`
- Key: `NOVITA_API_KEY` — get one at <https://novita.ai/settings/key-management>
- Callable ids: `apodex/apodex-1.1-mini`

Try it from your terminal with your key in `NOVITA_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.novita.ai/openai/chat/completions \
  -H "Authorization: Bearer $NOVITA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"apodex/apodex-1.1-mini","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://novita.ai/models/model-detail/apodex-apodex-1.1-mini>, anchored on `apodex/apodex-1.1-mini`, `Input $0 / M Tokens`, `Output $0 / M Tokens`; ids checked in <https://api.novita.ai/openai/v1/models>
- Source: <https://novita.ai/pricing>
- Source: <https://novita.ai/models/model-detail/apodex-apodex-1.1-mini>
- Source: <https://novita.ai/docs/guides/quickstart>
- Source: <https://api.novita.ai/openai/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-26` — Restored: Inference cloud with a zero-priced chat model through an OpenAI-compatible API, including tool calling and structured output
- `2026-08-14` — Delisted
- `2026-07-19` — Added: Inference cloud for 200+ open models; selected models priced Free plus a small signup trial credit

---

Generated from `registry.yaml` on 2026-10-30 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
