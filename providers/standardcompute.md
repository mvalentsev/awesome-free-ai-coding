---
layout: default
title: 'Standard Compute free tier: limits, free models, verified 2026-10-08'
description: A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is. A finite platform-compute trial, not a recurring budget or fixed token count. No card is…
permalink: /providers/standardcompute/
last_modified_at: 2026-10-08
crumb: Standard Compute
---

{% raw %}

# Standard Compute free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-08 · [standardcompute.com](https://standardcompute.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Platform compute: $0.25 once per account

A finite platform-compute trial, not a recurring budget or fixed token count. No card is required, but eligibility and availability are discretionary; contact support if activation offers no grant. No expiry or per-token conversion is published. The vendor recommends a small connection test and warns that a longer coding comparison may need paid allowance.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://standardcompute.com/free-trial), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Your prompts are never used for training. By us, or by any provider we route to.” ([source](https://standardcompute.com)).

## Connect

- Base URL: `https://api.stdcmpt.com/v1`
- Key: `STANDARDCOMPUTE_API_KEY` — get one at <https://standardcompute.com/signup>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.stdcmpt.com`
- Callable ids: `anthropic/claude-standardcompute`, `StandardCompute`
- Note: one key, two wires: https://api.stdcmpt.com/v1 for OpenAI-shaped clients and https://api.stdcmpt.com for Claude Code — "For Claude Code, use https://api.stdcmpt.com without /v1". /v1/models is keyless and lists the pool the router picks from, 40 unpriced ids on 2026-09-07 with Claude, GPT and Grok among them; requests are smart-routed across it unless a call pins one id. The two ids here are the router's own

Try it from your terminal with your key in `STANDARDCOMPUTE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.stdcmpt.com/v1/chat/completions \
  -H "Authorization: Bearer $STANDARDCOMPUTE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"anthropic/claude-standardcompute","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://standardcompute.com/free-trial>, anchored on `$0.25 of trial compute`, `no card required`
- Source: <https://standardcompute.com/free-trial>
- Source: <https://standardcompute.com/pricing>
- Source: <https://standardcompute.com/integrations/claude-code>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-07` — Added: A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
