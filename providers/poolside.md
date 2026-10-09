---
layout: default
title: 'Poolside Platform free tier: limits, free models, verified 2026-10-08'
description: Free self-serve developer access to Poolside's own Laguna coding models. The quickstart recommends free developer access; an organization's enterprise deployment is a separate access path. No quota, rate, or duration is published. The pricing page returns 404, which does not establish unlimited…
permalink: /providers/poolside/
last_modified_at: 2026-10-08
crumb: Poolside Platform
---

{% raw %}

# Poolside Platform free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [poolside.ai](https://poolside.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free self-serve developer access to Poolside's own Laguna coding models

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

Usage allowance: amount not published (period not published) per organization

The quickstart recommends free developer access; an organization's enterprise deployment is a separate access path. No quota, rate, or duration is published. The pricing page returns 404, which does not establish unlimited capacity or a withdrawn offer.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://poolside.ai/legal/eula), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “We may use your Content to provide, maintain, improve, and develop the Products and other Poolside offerings, including training our models, unless you opt-out. … you may opt-out of Poolside using your Content for training by selecting the Training Opt-Out under User Settings” ([source](https://poolside.ai/legal/eula)).

## Connect

- Base URL: `https://inference.poolside.ai/v1`
- Key: `POOLSIDE_API_KEY` — get one at <https://platform.poolside.ai>
- Callable ids: `poolside/laguna-s-2.1`, `poolside/laguna-xs-2.1`
- Note: Sign in to Poolside Platform to create a key. Public docs do not distinguish free and paid Platform models.

Try it from your terminal with your key in `POOLSIDE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://inference.poolside.ai/v1/chat/completions \
  -H "Authorization: Bearer $POOLSIDE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"poolside/laguna-s-2.1","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.poolside.ai/get-started/quickstart>, anchored on `Choose this option for fast, free developer access`, `fastest way to get a free Poolside API key`
- Source: <https://docs.poolside.ai/get-started/quickstart>
- Source: <https://docs.poolside.ai/api/overview>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Added: Free self-serve developer access to the Laguna coding models, direct from the vendor whose models this list already carries second-hand through OpenRouter and Kilo Gateway

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
