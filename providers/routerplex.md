---
layout: default
title: 'RouterPlex free tier: limits, free models, verified 2026-09-11'
description: A one-time $1 of test credit on a prepaid reseller that bills 54 chat models at vendor list prices with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is. "$1 test credit for your first integration after email…
permalink: /providers/routerplex/
---

{% raw %}

# RouterPlex

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-11 · [routerplex.com](https://routerplex.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A one-time $1 of test credit on a prepaid reseller that bills 54 chat models at vendor list prices with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

"$1 test credit for your first integration after email verification. No card required" on the home page, and the docs quickstart: "Eligible verified accounts receive $1 in test credit once" — read 2026-09-11. What the dollar buys is the list price of whatever it is spent on: the catalog page states "vendor list prices with 0% markup, pulled from the live catalog on 11 September 2026", so at deepseek-v4-flash it is an afternoon of work and at claude-opus-5 a handful of turns. The terms (last updated July 13, 2026) narrow it: "Until an account makes its first paid top-up, promotional credit may be usable only with a subset of models and at reduced rate limits", "no promotional credit is guaranteed", and one account per person. Which models the subset holds is on no page. Continuing costs a top-up "from $5 by card or $12 by crypto"; purchased credit does not expire. No legal entity is named on /terms or /about — the terms speak of "upstream providers" whose "own usage policies" apply — and /v1/models answers 403 without a key, so nothing here is read off the catalog. A connection test with a little work in it, one step above the smallest trial on this list

## Connect

- Base URL: `https://api.routerplex.com/v1`
- Key: `ROUTERPLEX_API_KEY` — get one at <https://routerplex.com/sign-up>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.routerplex.com`
- Callable ids: `deepseek-v4-flash`, `glm-5.3-flash`, `claude-opus-4-8`
- Note: ids are the catalog page's own spellings (routerplex.com/models, 54 chat ids on 2026-09-11); the vendor's Claude Code page sets ANTHROPIC_BASE_URL=https://api.routerplex.com and ANTHROPIC_MODEL=claude-opus-4-8, the Anthropic SDK appending /v1/messages itself. /v1/models is keyed, so none of these ids is checked against a catalog, and which of them the promotional credit can call is not published

## Evidence

- Probe: the page at <https://routerplex.com/>, anchored on `$1 test credit`, `No card required`
- Source: <https://routerplex.com/>
- Source: <https://docs.routerplex.com/>
- Source: <https://routerplex.com/terms>
- Source: <https://docs.routerplex.com/claude-code>

## History

No recorded event yet — the first scheduled run after a row lands writes its `added` line.

---

Generated from `registry.yaml` on 2026-09-11 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
