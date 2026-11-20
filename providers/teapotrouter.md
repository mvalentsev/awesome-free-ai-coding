---
layout: default
title: 'Teapot Router free tier: limits, free models, verified 2026-11-19'
description: Independent prepaid API gateway with discretionary signup credit. Email verification and an account key are required. The vendor says signup credit is usually unavailable and advertises it on the homepage when offered. The vendor says balances do not expire. Top-ups start at $3. Models and…
permalink: /providers/teapotrouter/
last_modified_at: 2026-11-20
crumb: Teapot Router
---

{% raw %}

# Teapot Router free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-11-17, a regular row from the first probe it passes on or after 2026-12-01 · **live** — last verified by a probe on 2026-11-19 · [teapotrouter.com](https://teapotrouter.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Independent prepaid API gateway with discretionary signup credit

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

Discretionary signup credit: One-time credits allowance: amount not published per account

Email verification and an account key are required. The vendor says signup credit is usually unavailable and advertises it on the homepage when offered. The vendor says balances do not expire. Top-ups start at $3. Models and channels depend on account access. Requests go to configured upstream providers; usage, billing and audit records are retained for operational, accounting, security and legal needs. Upstream retention and training rules are not established.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://teapotrouter.com/en/terms), read 2026-11-17).

## Connect

- Base URL: `https://api.teapotrouter.com/v1`
- Key: `TEAPOTROUTER_API_KEY` — get one at <https://teapotrouter.com/en/register>
- Callable ids: `gpt-6.1-sol`
- Note: Check your balance in the workspace before making requests. Create a key there and use a GPT ID enabled for it with the OpenAI endpoint. The separately documented Messages mode uses the gateway root and Claude IDs; a GPT ID is not its model default. Demo keys and balances cannot make real requests. Credit is a shared spending balance.

Try it from your terminal with your key in `TEAPOTROUTER_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.teapotrouter.com/v1/chat/completions \
  -H "Authorization: Bearer $TEAPOTROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-6.1-sol","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://teapotrouter.com>, anchored on `Sign-up includes a small amount of trial credit`
- Source: <https://teapotrouter.com/en/about>
- Source: <https://teapotrouter.com/en/docs/getting-started>
- Source: <https://teapotrouter.com/en/docs/billing>
- Source: <https://teapotrouter.com/en/docs/api-keys>
- Source: <https://teapotrouter.com/en/docs/client-setup>
- Source: <https://teapotrouter.com/api/pricing>
- Source: <https://teapotrouter.com/en/pricing>
- Source: <https://teapotrouter.com/en/terms>
- Source: <https://teapotrouter.com/en/privacy>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-17` — Added: Independent API gateway advertising signup trial credit before optional prepaid use

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
