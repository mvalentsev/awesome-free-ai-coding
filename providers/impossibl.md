---
layout: default
title: 'Impossibl free tier: limits, free models, verified 2026-09-21'
description: 'Prepaid gateway at provider list prices over 128 models, Claude, GPT, Gemini, DeepSeek and GLM among them, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card. An account is one POST with no key, and the llms.txt says what it carries: "an…'
permalink: /providers/impossibl/
---

{% raw %}

# Impossibl

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [impossibl.com](https://impossibl.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Prepaid gateway at provider list prices over 128 models, Claude, GPT, Gemini, DeepSeek and GLM among them, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

An account is one POST with no key, and the llms.txt says what it carries: "an agent-created account has $0.05; claiming adds an extra $1" — the claim is an email sign-in, the dollar "granted once per human". The billing page narrows it: "Some models require a completed credit purchase and return 403 billing_required without one. Saving a card or having promotional credits does not satisfy that requirement." Which models those are is not published. What the credit buys is list price — "Provider usage is billed at provider list prices with no usage markup" — GLM-5.3-Flash at $0.15 in and $0.50 out per million tokens, Claude Opus 5 at $5 and $25 — and a top-up starts at $5 plus a 5% platform fee. Read 2026-09-17

## Connect

- Base URL: `https://api.impossibl.com/v1`
- Key: `IMPOSSIBL_API_KEY` — get one at <https://impossibl.com/dashboard>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.impossibl.com`
- Callable ids: `zai/glm-5.3-flash`, `deepseek/deepseek-v4.1-flash`, `qwen/qwen3.8-27b`
- Note: ids are the keyless catalog's at api.impossibl.com/v1/models, 2026-09-17; which of them the promotional credit can call is not published. The Claude Code guide sets ANTHROPIC_BASE_URL=https://api.impossibl.com and clears ANTHROPIC_API_KEY so the bearer token is used

## Evidence

- Probe: the page at <https://impossibl.com/llms.txt>, anchored on `claiming adds an extra $1`, `a $0.05 signup bonus`; ids checked in <https://api.impossibl.com/v1/models>
- Source: <https://impossibl.com/llms.txt>
- Source: <https://api.impossibl.com/auth.md>
- Source: <https://impossibl.com/docs/billing>
- Source: <https://impossibl.com/docs/integrations>

## History

- `2026-09-21` — Added to the list: Prepaid gateway at provider list prices over 128 models, Claude, GPT, Gemini, DeepSeek and GLM among them, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
