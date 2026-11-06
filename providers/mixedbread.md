---
layout: default
title: 'Mixedbread free tier: limits, free models, verified 2026-11-05'
description: OpenAI-compatible API for the Toast 1 knowledge and search model, with $5 in one-time Starter credits and no card required. Create an account and an API key; a restricted key needs the Completions scope. Starter credits do not renew, and their expiry is not published. They fund usage at the…
permalink: /providers/mixedbread/
last_modified_at: 2026-11-05
crumb: Mixedbread
---

{% raw %}

# Mixedbread free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-11-04, a regular row from the first probe it passes on or after 2026-11-18 · **live** — last verified by a probe on 2026-11-05 · [mixedbread.com](https://www.mixedbread.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API for the Toast 1 knowledge and search model, with $5 in one-time Starter credits and no card required

## Free models

The free offer is a budget for model usage across the catalog. See Limits for its conditions and Connect for API details, where available.

## Limits, in the vendor's words

Starter credits: $5 once per service plan

Create an account and an API key; a restricted key needs the Completions scope. Starter credits do not renew, and their expiry is not published. They fund usage at the standard rates; hosted searches and data storage have separate charges against the balance. The published search and upload rate limits do not establish a Chat Completions allowance. The terms license use for internal business purposes. Privacy and security pages exclude model training, but the Free-tier terms permit it; this conflict is unresolved. Both legal policies specify indefinite retention of Free usage data. The API documents store=false for response-content retention, but its relationship to the Free-tier legal retention rule is not established.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.mixedbread.com/pages/terms), read 2026-11-04).

## What happens to what you send

Training policy not established. In the vendor's words: “Data collected under the Free Tier is retained indefinitely.” ([source](https://www.mixedbread.com/pages/terms)).

## Connect

- Base URL: `https://api.mixedbread.com/v1`
- Key: `MIXEDBREAD_API_KEY` — get one at <https://platform.mixedbread.com/platform?next=api-keys>
- Callable ids: `toast-1`
- Note: toast-1 is a specialized model for knowledge questions and repository investigations. The vendor documents using it as a primary model or subagent in OpenCode. It consumes the Starter credit rather than providing an individually free model.

Try it from your terminal with your key in `MIXEDBREAD_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.mixedbread.com/v1/chat/completions \
  -H "Authorization: Bearer $MIXEDBREAD_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"toast-1","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.mixedbread.com/docs/platform/billing>, anchored on `The Starter plan is free`, `$5 in one-time credits`, `no card required`
- Source: <https://www.mixedbread.com/pricing>
- Source: <https://www.mixedbread.com/docs/platform/billing>
- Source: <https://www.mixedbread.com/docs/agent/chat-completions>
- Source: <https://www.mixedbread.com/docs/agent/responses>
- Source: <https://www.mixedbread.com/docs/agent/models>
- Source: <https://www.mixedbread.com/docs/agent/integrations/opencode>
- Source: <https://www.mixedbread.com/docs/platform/api-keys>
- Source: <https://www.mixedbread.com/docs/production/security>
- Source: <https://www.mixedbread.com/pages/terms>
- Source: <https://www.mixedbread.com/pages/privacy>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-04` — Added: OpenAI-compatible API for the Toast 1 knowledge and search model, with $5 in one-time Starter credits and no card required

---

Generated from `registry.yaml` on 2026-11-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
