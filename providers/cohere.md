---
layout: default
title: 'Cohere (trial keys) free tier: limits, free models, verified 2026-09-24'
description: 'Cohere''s Command models via free trial API keys that never expire, plus a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type. Free models: command-a-plus, command-a-reasoning, north-mini-code, command-a, command-a-vision, command-r-plus, command-r, command-r7b. Trial keys are…'
permalink: /providers/cohere/
last_modified_at: 2026-09-26
crumb: Cohere (trial keys)
---

{% raw %}

# Cohere (trial keys) free tier

🔌 LLM APIs with free tier · no card · not offered in mainland China, Russia, Hong Kong and 5 more places · **live** — last verified by a probe on 2026-09-24 · [cohere.com](https://cohere.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cohere's Command models via free trial API keys that never expire, plus a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type

## Free models

`command-a-plus`, `command-a-reasoning`, [`north-mini-code`](https://mvalentsev.github.io/awesome-free-ai-coding/models/north-mini-code/), `command-a`, `command-a-vision`, `command-r-plus`, `command-r`, `command-r7b`

## Limits, in the vendor's words

Trial keys are "limited to 1,000 API calls a month" and rate-limited per model — 20 req/min on every Chat model, Command A and North Mini Code included, with Rerank at 10/min, Tokenize at 100/min, Embed at 2,000 inputs/min and audio transcription at 5/min. Two things that page does not say. Cohere's pricing page states that trial keys "are not permitted to be used for production or commercial purposes", and that every account "begins as a personal account and only has access to Trial API keys" — so the 1,000 calls are for evaluation, not for a product. And the North Mini Code page states that "for both trial keys and production keys, North Mini Code is free until rate limits are reached", which makes the one model here built for agentic coding the one that stays free on a paid key too (read 2026-08-14)

## Where it is offered

Not offered in mainland China, Russia, Hong Kong, Iran, Belarus, Syria, Macao and North Korea ([source](https://cohere.com/saas-agreement), read 2026-09-26). That leaves out 10.4% of the developers GitHub counts, beyond the embargoed countries most offers leave out ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “means Belarus, China (including Hong Kong and Macau), Iran, North Korea, Russia and Syria”.

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Analyzing usage patterns and using Trial or Research User Inputs/Outputs to improve the performance and safety of our AI models.” ([source](https://cohere.com/privacy)).

## Connect

- Base URL: `https://api.cohere.com/compatibility/v1`
- Key: `COHERE_API_KEY` — get one at <https://dashboard.cohere.com/api-keys>
- Callable ids: `north-mini-code-1-0`, `command-a-plus-05-2026`, `command-a-reasoning-08-2025`, `command-a-03-2025`, `command-a-vision-07-2025`, `command-r-plus-08-2024`, `command-r-08-2024`, `command-r7b-12-2024`
- Note: OpenAI-compatible endpoint; native API lives at https://api.cohere.com/v2. Both ids are the Model ID Cohere's own model pages publish — north-mini-code-1-0 is the free-on-any-key one

Try it from your terminal with your key in `COHERE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.cohere.com/compatibility/v1/chat/completions \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"north-mini-code-1-0","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.cohere.com/docs/rate-limits>, anchored on `trial keys`, `1,000`
- Source: <https://docs.cohere.com/docs/rate-limits>
- Source: <https://cohere.com/pricing>
- Source: <https://docs.cohere.com/docs/north-mini-code-1.0>
- Source: <https://docs.cohere.com/docs/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added command-a-plus, command-a-reasoning, command-a-vision, command-r, command-r-plus, command-r7b
- `2026-08-14` — Free models changed: added north-mini-code
- `2026-07-22` — Added: Cohere Command models via free trial API keys that never expire

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
