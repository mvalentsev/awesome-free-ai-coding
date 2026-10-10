---
layout: default
title: 'The Grid free tier: limits, free models, verified 2026-10-08'
description: OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time. The signup grant is a limited-time offer with no payment step. A first deposit…
permalink: /providers/the-grid/
last_modified_at: 2026-10-08
crumb: The Grid
---

{% raw %}

# The Grid free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-08 · [thegrid.ai](https://thegrid.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

Promotional signup credit: $25 once per account

Before first deposit: 100 requests/day; 3 requests at once per account

The signup grant is a limited-time offer with no payment step. A first deposit lifts the daily free cap; concurrency counts deposits, excluding signup bonus. Free-tier prompts and completions are stored and stay stored after upgrade; zero retention is paid-only. Model names buy specifications, and the underlying model can change between calls. Historical catalog deliveries do not guarantee the next call's model.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://thegrid.ai/terms-of-use), read 2026-09-26).

## Connect

- Base URL: `https://api.thegrid.ai/v1`
- Key: `THE_GRID_API_KEY` — get one at <https://app.thegrid.ai/profile>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://messages-beta.api.thegrid.ai`
- Callable ids: `agent-prime`, `code-prime`, `agent-max`
- Note: the ids are instruments from the keyless catalog at api.thegrid.ai/v1/models, where each carries the models it delivered; the Claude Code guide sets ANTHROPIC_BASE_URL=https://messages-beta.api.thegrid.ai, the Messages API in beta

Try it from your terminal with your key in `THE_GRID_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.thegrid.ai/v1/chat/completions \
  -H "Authorization: Bearer $THE_GRID_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"agent-prime","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://thegrid.ai/docs/start-here/quickstart.md>, anchored on `New accounts get a $25 signup credit`; ids checked in <https://api.thegrid.ai/v1/models>
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

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
