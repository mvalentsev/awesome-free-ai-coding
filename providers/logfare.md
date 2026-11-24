---
layout: default
title: 'Logfare (Standard models) free tier: limits, free models, verified 2026-11-23'
description: Free OpenAI-compatible model gateway operated by Solexsis Research LLC, with a Standard tier and optional data-consent tiers. One account per person; Discord verification and continued server membership are required. New-account limits apply for the first 24 hours. Account limits are shared across…
permalink: /providers/logfare/
last_modified_at: 2026-11-24
crumb: Logfare (Standard models)
---

{% raw %}

# Logfare (Standard models) free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-11, a regular row from the first probe it passes on or after 2026-11-25 · **live** — last verified by a probe on 2026-11-23 · [logfare.ai](https://logfare.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free OpenAI-compatible model gateway operated by Solexsis Research LLC, with a Standard tier and optional data-consent tiers

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Regular account: 2,500 requests/day; 3 requests at once per account

Premium account: 5,000 requests/day; 6 requests at once per account

Pro account: 10,000 requests/day; 12 requests at once per account

New account: 500 requests/day; 1 request at once per account

Shared network / IP: 40,000 requests/day per IP (a window bypasses the network counter when the account's own allowance is higher or unlimited)

One account per person; Discord verification and continued server membership are required. New-account limits apply for the first 24 hours. Account limits are shared across models, keys and apps; minute/hour, network and provider caps also apply. Some Standard models bypass request allowances, while concurrency and provider caps remain. Automation is allowed; honor Retry-After on 429/503. Standard traffic is logged for internal evaluation, with an evaluation opt-out. Optional Premium requires training consent; Pro additionally requires data-sale consent. Raw prompts reach changing upstream providers under their own policies. The privacy policy says API keys are stored in plain text, while current docs describe fingerprints only.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://logfare.ai/tos), read 2026-11-11).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “If — and only if — you opt in at /consent, your post-scrub request and response content may also be used to train and fine-tune the models we operate.” ([source](https://logfare.ai/privacy)).

## Connect

- Base URL: `https://logfare.ai/v1`
- Key: `LOGFARE_API_KEY` — get one at <https://logfare.ai/register>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://logfare.ai`
- Callable ids: `glm-5.3-flash`
- Note: Check the public catalog before using the configured GLM ID; account availability is unconfirmed. Standard requires no training or data-sale opt-in. Register, link Discord and keep server membership; each key is shown once. Chat, tools and streaming use /chat/completions; Messages use /v1/messages. Premium and Pro require separate data consents.

Try it from your terminal with your key in `LOGFARE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://logfare.ai/v1/chat/completions \
  -H "Authorization: Bearer $LOGFARE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://logfare.ai/docs>, anchored on `There are three tiers, and every one is free`, `New accounts use the new-account budget for their first 24 hours`; ids checked in <https://logfare.ai/v1/models>
- Source: <https://logfare.ai/>
- Source: <https://logfare.ai/docs>
- Source: <https://logfare.ai/v1/models>
- Source: <https://logfare.ai/tos>
- Source: <https://logfare.ai/privacy>
- Source: <https://logfare.ai/register>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-11` — Added: Free OpenAI-compatible model gateway operated by Solexsis Research LLC, with a Standard tier and optional data-consent tiers

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
