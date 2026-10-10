---
layout: default
title: 'Wallaby free tier: limits, free models, verified 2026-10-08'
description: OpenAI-compatible Kimi K3 API from an Australian open-weight inference gateway, with $0.50 of signup credit and no card or initial payment. One trial per person or organisation, with a verified email and human check. The trial credit does not expire; requests stop when it is exhausted. Optional…
permalink: /providers/wallaby/
last_modified_at: 2026-10-08
crumb: Wallaby
---

{% raw %}

# Wallaby free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-10-08, a regular row from the first probe it passes on or after 2026-10-22 · **live** — last verified by a probe on 2026-10-08 · [wallabytoken.com](https://wallabytoken.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible Kimi K3 API from an Australian open-weight inference gateway, with $0.50 of signup credit and no card or initial payment

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Signup trial credit: $0.5 once per account (No card or top-up required)

Trial rate limit: Requests allowance: amount not published (period not published) per account

One trial per person or organisation, with a verified email and human check. The trial credit does not expire; requests stop when it is exhausted. Optional paid top-ups start at $20. Trial access may have lower rate limits or model restrictions; the vendor publishes no numeric trial rate. Wallaby says it does not log or train on prompts, but its privacy policy does not establish the upstream providers' retention or training rules. Users must be at least 18.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://wallabytoken.com/aup), read 2026-10-08).

## Connect

- Base URL: `https://api.wallabytoken.com/v1`
- Key: `WALLABY_API_KEY` — get one at <https://api.wallabytoken.com/register>
- Callable ids: `kimi-k3`
- Note: Create an account, verify your email and create a token under Tokens → Add token. The official API docs name kimi-k3, support streaming, function tools and structured outputs. The catalog requires a key; the signup credit is a spending balance, not an individually free model.

Try it from your terminal with your key in `WALLABY_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.wallabytoken.com/v1/chat/completions \
  -H "Authorization: Bearer $WALLABY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"kimi-k3","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://wallabytoken.com/docs>, anchored on `$0.50 of free trial credit`
- Source: <https://wallabytoken.com/docs>
- Source: <https://wallabytoken.com/blog/p/kimi-k3-free-trial>
- Source: <https://wallabytoken.com/pricing.json>
- Source: <https://wallabytoken.com/about>
- Source: <https://wallabytoken.com/terms>
- Source: <https://wallabytoken.com/privacy>
- Source: <https://wallabytoken.com/aup>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-08` — Added: OpenAI-compatible Kimi K3 API from an Australian open-weight inference gateway, with $0.50 of signup credit and no card or initial payment

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
