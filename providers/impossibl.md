---
layout: default
title: 'Impossibl free tier: limits, free models, verified 2026-10-05'
description: Prepaid gateway at provider list prices, Claude, GPT, Gemini, DeepSeek and GLM among its models, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card. An account can be created by a keyless POST; email sign-in claims the additional grant once per…
permalink: /providers/impossibl/
last_modified_at: 2026-10-05
crumb: Impossibl
---

{% raw %}

# Impossibl free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-05 · [impossibl.com](https://impossibl.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Prepaid gateway at provider list prices, Claude, GPT, Gemini, DeepSeek and GLM among its models, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Signup credit: $0.05 (period not published) per account

Email-claim grant: $1 once per account

An account can be created by a keyless POST; email sign-in claims the additional grant once per person. Some models require a completed credit purchase and return `403 billing_required` without it; adding a card or holding promotional credit does not meet that condition. The eligible subset is unpublished. Usage bills at provider list prices without token markup; top-ups start at $5 plus a 5% fee.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://impossibl.com/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.impossibl.com/v1`
- Key: `IMPOSSIBL_API_KEY` — get one at <https://impossibl.com/dashboard>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.impossibl.com`
- Callable ids: `zai/glm-5.3-flash`, `deepseek/deepseek-v4.1-flash`, `qwen/qwen3.8-27b`
- Note: ids are the keyless catalog's at api.impossibl.com/v1/models, 2026-09-17; which of them the promotional credit can call is not published. The Claude Code guide sets ANTHROPIC_BASE_URL=https://api.impossibl.com and clears ANTHROPIC_API_KEY so the bearer token is used

Try it from your terminal with your key in `IMPOSSIBL_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.impossibl.com/v1/chat/completions \
  -H "Authorization: Bearer $IMPOSSIBL_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"zai/glm-5.3-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://impossibl.com/llms.txt>, anchored on `claiming adds an extra $1`, `a $0.05 signup bonus`; ids checked in <https://api.impossibl.com/v1/models>
- Source: <https://impossibl.com/llms.txt>
- Source: <https://api.impossibl.com/auth.md>
- Source: <https://impossibl.com/docs/billing>
- Source: <https://impossibl.com/docs/integrations>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: Prepaid gateway at provider list prices over 128 models, Claude, GPT, Gemini, DeepSeek and GLM among them, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
