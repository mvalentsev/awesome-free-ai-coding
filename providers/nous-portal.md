---
layout: default
title: 'Nous Portal (Hermes Agent) free tier: limits, free models, verified 2026-10-08'
description: 'Nous Research''s inference portal with a $0 Free plan for :free models, accessible through an OpenAI-compatible API and Hermes Agent. Free models: step-3.7-flash, laguna-s-2.1, laguna-xs-2.1, ling-3.0-flash-fin, ling-3.0-flash-sante, longcat-2.0. Choose the Free plan and use exact :free IDs; they…'
permalink: /providers/nous-portal/
last_modified_at: 2026-10-08
crumb: Nous Portal (Hermes Agent)
---

{% raw %}

# Nous Portal (Hermes Agent) free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-08 · [portal.nousresearch.com](https://portal.nousresearch.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Nous Research's inference portal with a $0 Free plan for :free models, accessible through an OpenAI-compatible API and Hermes Agent

## Free models

[`step-3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/step-3.7-flash/), [`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/), [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/), [`ling-3.0-flash-fin`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-fin/), [`ling-3.0-flash-sante`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-flash-sante/), [`longcat-2.0`](https://mvalentsev.github.io/awesome-free-ai-coding/models/longcat-2.0/)

## Limits, in the vendor's words

Free models: Usage allowance: amount not published (period not published) per account

Choose the Free plan and use exact :free IDs; they are zero-priced, while metered routes are outside it. A portal key is required: a keyless chat call returns 402 even though the public catalog is readable. No page read mentions a card or a numerical rate cap.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://portal.nousresearch.com/terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “When Privacy Mode is enabled, we will not store your inference payloads and will not use such inference payloads for training, product improvement, or support purposes” ([source](https://portal.nousresearch.com/privacy)).

## Connect

- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `stepfun/step-3.7-flash:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `meituan/longcat-2.0:free`, `meituan/longcat-2.5-preview:free`, `upstage/solar-mini4:free`
- Note: Select a :free model and use your Nous Portal key; paid variants are outside the free plan.

Try it from your terminal with your key in `NOUS_PORTAL_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://inference-api.nousresearch.com/v1/chat/completions \
  -H "Authorization: Bearer $NOUS_PORTAL_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"stepfun/step-3.7-flash:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://inference-api.nousresearch.com/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://portal.nousresearch.com/>
- Source: <https://hermes-agent.nousresearch.com/docs/guides/run-nemotron-3-ultra-free>
- Source: <https://inference-api.nousresearch.com/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-01` — Free models changed: dropped solar-pro-4
- `2026-09-30` — Free models changed: added laguna-xs-2.1, ling-3.0-flash-fin, ling-3.0-flash-sante, longcat-2.0, solar-pro-4
- `2026-09-16` — Added: Nous Research's inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — eight on 2026-09-16, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
