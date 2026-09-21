---
layout: default
title: 'The Grid free tier: limits, free models, verified 2026-09-21'
description: 'OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time. The quick start: "New accounts get a $25 signup credit (limited time), enough…'
permalink: /providers/the-grid/
---

{% raw %}

# The Grid

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [thegrid.ai](https://thegrid.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The quick start: "New accounts get a $25 signup credit (limited time), enough for millions of test calls on" text-prime, and its three steps from sign-up to a first call ask for no payment method — adding one is listed under what to do next. Concurrency counts deposits only, "a signup bonus of $25 and a deposit of $20 only counts as $20", and an account with $0 to $20 deposited gets 3 concurrent requests. A model name buys a specification: "The specific model behind any given call can change between calls." The keyless catalog publishes what each tier delivered over 30 days to 2026-09-03 — Agent Max Claude Opus 5, Agent Prime MiniMax-M3, Agent Standard gpt-oss-120b — at market prices per million tokens. Read 2026-09-17

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Neither we nor our suppliers retain the content of your requests or responses. Your data is not used for training, fine-tuning, or any purpose beyond serving the request in front of it.” ([source](https://thegrid.ai/docs/data-handling-and-privacy/data-handling-and-privacy)).

## Connect

- Base URL: `https://api.thegrid.ai/v1`
- Key: `THE_GRID_API_KEY` — get one at <https://app.thegrid.ai/profile>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://messages-beta.api.thegrid.ai`
- Callable ids: `agent-prime`, `code-prime`, `agent-max`
- Note: the ids are instruments from the keyless catalog at api.thegrid.ai/v1/models, where each carries the models it delivered; the Claude Code guide sets ANTHROPIC_BASE_URL=https://messages-beta.api.thegrid.ai, the Messages API in beta

## Evidence

- Probe: the page at <https://thegrid.ai/docs/start-here/quickstart.md>, anchored on `New accounts get a $25 signup credit`; ids checked in <https://api.thegrid.ai/v1/models>
- Source: <https://thegrid.ai/docs/start-here/quickstart.md>
- Source: <https://thegrid.ai/llms.txt>
- Source: <https://thegrid.ai/docs/api-reference/errors-and-rate-limits.md>
- Source: <https://thegrid.ai/docs/instrument-specifications/current-instruments.md>
- Source: <https://thegrid.ai/docs/integrations-and-best-practices/integrations/claude-code.md>

## History

- `2026-09-21` — Added to the list: OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
