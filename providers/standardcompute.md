---
layout: default
title: 'Standard Compute free tier: limits, free models, verified 2026-09-24'
description: A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is. "Eligible new accounts receive $0.25 of trial compute after activation. This is a finite…
permalink: /providers/standardcompute/
---

{% raw %}

# Standard Compute

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-24 · [standardcompute.com](https://standardcompute.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

"Eligible new accounts receive $0.25 of trial compute after activation. This is a finite platform compute allowance. It is not a recurring free tier, a fixed token count, or a value measured at another provider's prices" — the free-trial page, "Updated September 5, 2026", read here 2026-09-16; the pricing FAQ adds "with no card required". It does not refill, no card is asked for, and it is discretionary: "Access is subject to eligibility and availability", with a support address for accounts whose dashboard does not offer it. What the quarter buys is on no page — a flat-rate router publishes no per-token price, and the only conversion the site offers is its own marketing arithmetic, a $20 monthly compute budget on the paid Starter plan that its pricing table says does the work of up to $60 a month of direct API use. The vendor sets the expectation itself: "Start with one small request that lets you check the connection and response", while "a longer coding-quality comparison may need a paid allowance". It is the smallest offer on this list — a connection test, not a working allowance

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Your prompts are never used for training. By us, or by any provider we route to.” ([source](https://standardcompute.com)).

## Connect

- Base URL: `https://api.stdcmpt.com/v1`
- Key: `STANDARDCOMPUTE_API_KEY` — get one at <https://standardcompute.com/signup>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.stdcmpt.com`
- Callable ids: `anthropic/claude-standardcompute`, `StandardCompute`
- Note: one key, two wires: https://api.stdcmpt.com/v1 for OpenAI-shaped clients and https://api.stdcmpt.com for Claude Code — "For Claude Code, use https://api.stdcmpt.com without /v1". /v1/models is keyless and lists the pool the router picks from, 40 unpriced ids on 2026-09-07 with Claude, GPT and Grok among them; requests are smart-routed across it unless a call pins one id. The two ids here are the router's own

## Evidence

- Probe: the page at <https://standardcompute.com/free-trial>, anchored on `$0.25 of trial compute`, `no card required`
- Source: <https://standardcompute.com/free-trial>
- Source: <https://standardcompute.com/pricing>
- Source: <https://standardcompute.com/integrations/claude-code>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-07` — Added: A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

---

Generated from `registry.yaml` on 2026-09-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
