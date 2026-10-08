---
layout: default
title: 'RouterPlex free tier: limits, free models, verified 2026-10-08'
description: A one-time $1 of free credit on a prepaid reseller that bills its catalog at vendor list prices with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is. The key-creation grant is for an account with no earlier…
permalink: /providers/routerplex/
last_modified_at: 2026-10-08
crumb: RouterPlex
---

{% raw %}

# RouterPlex free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-08 · [routerplex.com](https://routerplex.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

A one-time $1 of free credit on a prepaid reseller that bills its catalog at vendor list prices with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

Key-creation grant: $1 once per account

Trial traffic: 10 requests/minute; 250,000 tokens/minute; 4 requests at once per account

The key-creation grant is for an account with no earlier paid top-up, existing credit or setup grant; signup has no payment step and the grant does not expire. It spends at catalog prices with no token markup. Before a first paid top-up, only an unpublished subset of models may accept promotional credit, at reduced rates. Terms do not guarantee a grant and allow one account per person. Continuing requires at least $5 by card or $15 by crypto. No legal entity is named; the catalog needs a key.

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

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
