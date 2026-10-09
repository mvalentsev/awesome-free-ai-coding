---
layout: default
title: 'Cohere (trial keys) free tier: limits, free models, verified 2026-10-08'
description: 'Cohere''s Command models via free trial API keys that never expire, plus a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type. Free models: command-a-plus, command-a-reasoning, north-mini-code, command-a, command-a-vision, command-r-plus, command-r, command-r7b. Trial keys are…'
permalink: /providers/cohere/
last_modified_at: 2026-10-08
crumb: Cohere (trial keys)
---

{% raw %}

# Cohere (trial keys) free tier

🔌 LLM APIs with free tier · no card · not offered in mainland China, Russia, Hong Kong and 5 more places · **live** — last verified by a probe on 2026-10-08 · [cohere.com](https://cohere.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cohere's Command models via free trial API keys that never expire, plus a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type

## Free models

[`command-a-plus`](https://mvalentsev.github.io/awesome-free-ai-coding/models/command-a-plus/), `command-a-reasoning`, [`north-mini-code`](https://mvalentsev.github.io/awesome-free-ai-coding/models/north-mini-code/), `command-a`, `command-a-vision`, `command-r-plus`, `command-r`, `command-r7b`

## Limits, in the vendor's words

Trial keys: 1,000 requests/month per key

Trial Chat models: 20 requests/minute per key per model

North Mini Code on production keys: 500 requests/minute per key per model

Trial keys are for evaluation, not production or commercial use; new accounts start with Trial keys. Chat limits differ from those for reranking, embeddings, tokenization and audio. North Mini Code is free on both Trial and production keys until the corresponding rate limit is reached. The trial monthly request allowance applies alongside its per-model rate caps.

## Where it is offered

Not offered in mainland China, Russia, Hong Kong, Iran, Belarus, Syria, Macao and North Korea ([source](https://cohere.com/saas-agreement), read 2026-09-26). That leaves out 10.4% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “means Belarus, China (including Hong Kong and Macau), Iran, North Korea, Russia and Syria”.

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

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
