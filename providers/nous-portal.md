---
layout: default
title: 'Nous Portal (Hermes Agent) free tier: limits, free models, verified 2026-09-24'
description: 'Nous Research''s inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — seven on 2026-09-18, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API. The portal''s plan table reads "Free $0 Free models only Standard rate limits $0…'
permalink: /providers/nous-portal/
---

{% raw %}

# Nous Portal (Hermes Agent)

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-09-16, a regular row from the first probe it passes on or after 2026-09-30 · **live** — last verified by a probe on 2026-09-24 · [portal.nousresearch.com](https://portal.nousresearch.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Nous Research's inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — seven on 2026-09-18, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API

## Free models

`step-3.7-flash`, `laguna-s-2.1`

## Limits, in the vendor's words

The portal's plan table reads "Free $0 Free models only Standard rate limits $0 monthly credits Try Hermes", and the Hermes Agent guide has you "create a Nous Portal account (or sign in), choose the Free plan, and authorize Hermes" — "The :free tag is what keeps it on the no-cost plan". No rate-limit figure is published and no page read mentions a card. The keyless catalog prices seven rows at zero; a call without a key answers HTTP 402 with a payment offer, so the free models want the portal's key. Read 2026-09-18

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “When Privacy Mode is enabled, we will not store your inference payloads and will not use such inference payloads for training, product improvement, or support purposes” ([source](https://portal.nousresearch.com/privacy)).

## Connect

- Base URL: `https://inference-api.nousresearch.com/v1`
- Key: `NOUS_PORTAL_API_KEY` — get one at <https://portal.nousresearch.com>
- Callable ids: `stepfun/step-3.7-flash:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `inclusionai/ling-3.0-flash-fin:free`, `inclusionai/ling-3.0-flash-sante:free`, `upstage/solar-pro4:free`, `meituan/longcat-2.0:free`
- Note: every id the keyless catalog prices at 0 on 2026-09-18; solar-pro4 is a limited-time trial on other gateways

## Evidence

- Probe: the models catalog at <https://inference-api.nousresearch.com/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://portal.nousresearch.com/>
- Source: <https://hermes-agent.nousresearch.com/docs/guides/run-nemotron-3-ultra-free>
- Source: <https://inference-api.nousresearch.com/v1/models>

## History

Each line is a change to what this page publishes, dated the day the list recorded it, in UTC.

- `2026-09-16` — Added: Nous Research's inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — eight on 2026-09-16, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
