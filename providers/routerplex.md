---
layout: default
title: 'RouterPlex free tier: limits, free models, verified 2026-09-24'
description: 'A one-time $1 of free credit on a prepaid reseller that bills 56 models at catalog rates with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is. The home page: "Get $1 in free credit", granted "once during key…'
permalink: /providers/routerplex/
last_modified_at: 2026-09-26
crumb: RouterPlex
---

{% raw %}

# RouterPlex free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-11, a regular row from the first probe it passes on or after 2026-09-25 · **live** — last verified by a probe on 2026-09-24 · [routerplex.com](https://routerplex.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A one-time $1 of free credit on a prepaid reseller that bills 56 models at catalog rates with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

The home page: "Get $1 in free credit", granted "once during key creation, not immediately after signup" to an account with "no previous paid top-up, no existing credit, and no previous setup-credit grant". "Trial traffic is limited to 10 requests per minute, 250,000 tokens per minute, and four concurrent requests", "Signup and guided setup have no payment step", and "The $1 credit does not expire". What the dollar buys is the catalog rate of whatever it is spent on, with "0% Token markup" on the pricing page, so at deepseek-v4-flash it is an afternoon of work and at claude-opus-5 a handful of turns. The terms narrow it: "Until an account makes its first paid top-up, promotional credit may be usable only with a subset of models and at reduced rate limits", "no promotional credit is guaranteed", and one account per person. Which models the subset holds is on no page. Continuing costs a top-up "from $5 by card or $12 by crypto". No legal entity is named on /terms or /about, and /v1/models answers 403 without a key, so nothing here is read off the catalog. A connection test with a little work in it, one step above the smallest trial on this list. Read 2026-09-18

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://routerplex.com/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “RouterPlex does not use your prompts or outputs to train models … Every other model in the catalog remains covered by the no-training rule above.” ([source](https://routerplex.com/privacy)).

## Connect

- Base URL: `https://api.routerplex.com/v1`
- Key: `ROUTERPLEX_API_KEY` — get one at <https://routerplex.com/sign-up>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.routerplex.com`
- Callable ids: `deepseek-v4-flash`, `glm-5.3-flash`, `claude-sonnet-4-6`
- Note: ids are the catalog page's own spellings (routerplex.com/models, 54 chat ids on 2026-09-11); the vendor's Claude Code page sets ANTHROPIC_BASE_URL=https://api.routerplex.com and ANTHROPIC_MODEL=claude-sonnet-4-6 (guide reviewed 2026-09-13), the Anthropic SDK appending /v1/messages itself. /v1/models is keyed, so none of these ids is checked against a catalog, and which of them the promotional credit can call is not published

Try it from your terminal with your key in `ROUTERPLEX_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.routerplex.com/v1/chat/completions \
  -H "Authorization: Bearer $ROUTERPLEX_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://routerplex.com/>, anchored on `Get $1 in free credit`, `Signup and guided setup have no payment step`
- Source: <https://routerplex.com/>
- Source: <https://routerplex.com/pricing>
- Source: <https://docs.routerplex.com/>
- Source: <https://routerplex.com/terms>
- Source: <https://docs.routerplex.com/claude-code>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-11` — Added: A one-time $1 of test credit on a prepaid reseller that bills 54 chat models at vendor list prices with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
