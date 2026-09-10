---
layout: default
title: 'Standard Compute free tier: limits, free models, verified 2026-09-10'
description: A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is. "Eligible new accounts receive $0.25 of trial compute after activation. This is a finite…
permalink: /providers/standardcompute/
---

{% raw %}

# Standard Compute

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-10 · [standardcompute.com](https://standardcompute.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

"Eligible new accounts receive $0.25 of trial compute after activation. This is a finite platform compute allowance. It is not a recurring free tier, a fixed token count, or a value measured at another provider's prices" — the sentence sits on the free-trial page and in the pricing FAQ, both dated "Updated September 5, 2026" by the vendor and read here 2026-09-07. It does not refill, no card is asked for, and it is discretionary: "Access is subject to eligibility and availability", with a support address for accounts whose dashboard does not offer it. What the quarter buys is on no page — a flat-rate router publishes no per-token price, and the only conversion the site offers is its own marketing arithmetic, a paid "$20 monthly compute budget" claimed to do "the work of up to $60/mo" at list prices. The vendor sets the expectation itself: "Start with one small request that lets you check the connection and response", while "a longer coding-quality comparison may need a paid allowance". It is the smallest offer on this list — a connection test, not a working allowance

## Connect

- Base URL: `https://api.stdcmpt.com/v1`
- Key: `STANDARDCOMPUTE_API_KEY` — get one at <https://standardcompute.com/signup>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.stdcmpt.com`
- Callable ids: `anthropic/claude-standardcompute`, `StandardCompute`
- Note: one key, two wires: https://api.stdcmpt.com/v1 for OpenAI-shaped clients and https://api.stdcmpt.com for Claude Code, which appends /v1/messages itself — the vendor spells the difference out, "For Claude Code, use https://api.stdcmpt.com without /v1". /v1/models is keyless and listed 40 ids on 2026-09-07, anthropic/claude-opus-5, openai/gpt-6-astra, x-ai/grok-4.3 and five :eu-suffixed EU-region variants among them, none of them priced; requests are smart-routed across that pool unless a call pins one id. The two ids here are the router's own, read off that catalog rather than off the Claude Code page, which sets the model through the vendor's launcher instead

## Evidence

- Probe: the page at <https://standardcompute.com/free-trial>, anchored on `$0.25 of trial compute`, `no card required`
- Source: <https://standardcompute.com/free-trial>
- Source: <https://standardcompute.com/pricing>
- Source: <https://standardcompute.com/integrations/claude-code>

## History

- `2026-09-10` — Added to the list: A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

---

Generated from `registry.yaml` on 2026-09-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
