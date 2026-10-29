---
layout: default
title: 'NovAI free tier: limits, free models, verified 2026-10-26'
description: Hong Kong OpenAI-compatible gateway with a recurring free allowance on selected text and vision models, separate from its signup credit. The daily allowance is shared across free chat, image and video models; media keep separate caps after a top-up. Calls at a cap return 429 until reset. An email…
permalink: /providers/novai/
last_modified_at: 2026-10-29
crumb: NovAI
---

{% raw %}

# NovAI free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-10-22, a regular row from the first probe it passes on or after 2026-11-05 · **live** — last verified by a probe on 2026-10-26 · [aiapi-pro.com](https://aiapi-pro.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Hong Kong OpenAI-compatible gateway with a recurring free allowance on selected text and vision models, separate from its signup credit

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Shared free-model calls: 10 requests/day per account (before the first completed top-up). 00:00 UTC+8

5 requests/minute per account (before the first completed top-up)

Separate signup credit: $2 once per account (valid for 14 days)

Free chat calls: Unmetered requests per account (after any completed top-up; upstream provider limits still apply)

The daily allowance is shared across free chat, image and video models; media keep separate caps after a top-up. Calls at a cap return 429 until reset. An email account and API key are required. Signup accepts selected email providers and is screened for abuse. Paid models and top-ups are optional. The gateway says it does not store or train on prompts; upstream providers apply their own policies. Users must be at least 18.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://aiapi-pro.com/terms.html), read 2026-10-22).

## Connect

- Base URL: `https://aiapi-pro.com/v1`
- Key: `NOVAI_API_KEY` — get one at <https://aiapi-pro.com/register.html>
- Callable ids: `glm-4.7-flash`, `glm-4.6v-flash`, `glm-4.1v-thinking-flash`
- Note: Use a NovAI API key and an exact chat model ID. GLM-4.7-Flash documents OpenAI-compatible function calling and coding-agent setup. CogView and CogVideo are media generators, separate from the chat configurations.

Try it from your terminal with your key in `NOVAI_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://aiapi-pro.com/v1/chat/completions \
  -H "Authorization: Bearer $NOVAI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"glm-4.7-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://aiapi-pro.com/v1/models>, each listed family checked for a zero price
- Source: <https://aiapi-pro.com/free/index.html>
- Source: <https://aiapi-pro.com/transparency.html>
- Source: <https://aiapi-pro.com/register.html>
- Source: <https://aiapi-pro.com/models/glm-4.7-flash.html>
- Source: <https://aiapi-pro.com/blog/free-ai-coding-api-cline-continue-aider-cursor>
- Source: <https://aiapi-pro.com/docs.md>
- Source: <https://aiapi-pro.com/terms.html>
- Source: <https://aiapi-pro.com/privacy.html>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-22` — Added: Hong Kong OpenAI-compatible gateway with a recurring free allowance on selected text and vision models, separate from its signup credit

---

Generated from `registry.yaml` on 2026-10-29 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
