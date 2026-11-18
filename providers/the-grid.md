---
layout: default
title: 'The Grid free tier: limits, free models, verified 2026-11-18'
description: OpenAI- and Anthropic-compatible inference market with Free-account limits; signup-credit issuance is unconfirmed. An account and API key are required. Current onboarding requires a funded balance; signup-credit issuance and amount are unconfirmed. Rate-limit docs still describe Free accounts, and…
permalink: /providers/the-grid/
last_modified_at: 2026-11-18
crumb: The Grid
---

{% raw %}

# The Grid free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-11-18 · [thegrid.ai](https://thegrid.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible inference market with Free-account limits; signup-credit issuance is unconfirmed

## Free models

The vendor does not identify which models the free offer includes. See Limits for the published conditions.

## Limits, in the vendor's words

Signup credit: One-time USD allowance: see your account for values per account (current issuance and amount are unconfirmed; unused signup credits expire 14 days after signup)

Before first deposit: 100 requests/day; 3 requests at once per account

An account and API key are required. Current onboarding requires a funded balance; signup-credit issuance and amount are unconfirmed. Rate-limit docs still describe Free accounts, and Terms retain signup-credit expiry. A first deposit lifts the daily cap; concurrency counts deposits, excluding bonuses. Free-tier prompts and completions are stored and stay stored after upgrade; zero retention is paid-only. Instruments buy quality specifications, so the underlying model can change between calls.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://thegrid.ai/terms-of-use), read 2026-09-26).

## Connect

- Base URL: `https://api.thegrid.ai/v1`
- Key: `THE_GRID_API_KEY` — get one at <https://app.thegrid.ai/profile>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://messages-beta.api.thegrid.ai`
- Callable ids: `agent-max`, `agent-prime`, `code-prime`
- Note: the ids are instruments from the keyless catalog at api.thegrid.ai/v1/models, where each carries the models it delivered; the Claude Code guide sets ANTHROPIC_BASE_URL=https://messages-beta.api.thegrid.ai, the Messages API in beta

Try it from your terminal with your key in `THE_GRID_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.thegrid.ai/v1/chat/completions \
  -H "Authorization: Bearer $THE_GRID_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"agent-prime","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://thegrid.ai/docs/api-reference/errors-and-rate-limits.md>, anchored on `Free accounts have a daily request limit of 100 requests.`, `Make your first deposit to lift all daily request limits.`; ids checked in <https://api.thegrid.ai/v1/models>
- Source: <https://thegrid.ai/docs/start-here/quickstart.md>
- Source: <https://thegrid.ai/llms.txt>
- Source: <https://thegrid.ai/docs/api-reference/errors-and-rate-limits.md>
- Source: <https://thegrid.ai/docs/instrument-specifications/current-instruments.md>
- Source: <https://thegrid.ai/docs/integrations-and-best-practices/integrations/claude-code.md>
- Source: <https://thegrid.ai/docs/data-handling-and-privacy/data-handling-and-privacy.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
