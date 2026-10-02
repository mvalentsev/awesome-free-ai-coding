---
layout: default
title: 'Routeway free tier: limits, free models, verified 2026-10-01'
description: 'OpenAI-compatible gateway with a rotating :free chat-model lane beside metered models. Free models: deepseek-v4-flash, minimax-m2.7, muse-glimmer-30b. Free models — every id ending :free — cost nothing and "are rate-limited to 20 requests/minute and 200 requests/day", the FAQ says, where the…'
permalink: /providers/routeway/
last_modified_at: 2026-10-01
crumb: Routeway
---

{% raw %}

# Routeway free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-01 · [routeway.ai](https://routeway.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway with a rotating :free chat-model lane beside metered models

## Free models

[`deepseek-v4-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/deepseek-v4-flash/), [`minimax-m2.7`](https://mvalentsev.github.io/awesome-free-ai-coding/models/minimax-m2.7/), [`muse-glimmer-30b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/muse-glimmer-30b/)

## Limits, in the vendor's words

Free models — every id ending :free — cost nothing and "are rate-limited to 20 requests/minute and 200 requests/day", the FAQ says, where the rate-limits page gives "5 Requests Per Minute (RPM)" and "200 Requests Per Day (RPD)"; past either they answer 429, and the pay-as-you-go ids beside them "require a positive account balance". The lane itself rotates, ids joining and leaving within days while their metered twins stay, and free models "can be removed at any time". A key is sign-up and Create API Key with no payment step in the FAQ, while the terms, last updated 31.05.2025 behind a bot wall this list's client cannot pass, count a payment method among what any account needs. No legal entity is named, and support is by email and Discord. Read 2026-09-27

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://routeway.ai/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.routeway.ai/v1`
- Key: `ROUTEWAY_API_KEY` — get one at <https://routeway.ai/dashboard/keys>
- Codex CLI: [`configs/codex/routeway.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/routeway.config.toml) — copy it to `~/.codex/`, then `codex -p routeway`; set up on the lane by the vendor's own page, <https://docs.routeway.ai/integrations/agents/codex>: "Use OpenAI’s Codex with Routeway by adding a custom provider"
- Callable ids: `deepseek-v4-flash:free`, `muse-glimmer-30b:free`, `minimax-m2.7:free`
- Note: Only IDs ending :free are free; the same catalog meters Claude, GPT and other paid models. Some zero-priced community fine-tunes are intended for expressive writing and roleplay.

Try it from your terminal with your key in `ROUTEWAY_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.routeway.ai/v1/chat/completions \
  -H "Authorization: Bearer $ROUTEWAY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-flash:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.routeway.ai/v1/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://api.routeway.ai/v1/models>
- Source: <https://docs.routeway.ai/getting-started/rate-limits>
- Source: <https://docs.routeway.ai/getting-started/faq.md>
- Source: <https://docs.routeway.ai/getting-started/rate-limits.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-16` — Free models changed: added deepseek-v4-flash, minimax-m2.7
- `2026-09-14` — Free models changed: added muse-glimmer-30b
- `2026-09-05` — Free models changed: dropped gemma-4, gpt-oss
- `2026-08-30` — Free models changed: dropped llama-3.3, step-3.7-flash
- `2026-08-11` — Free models changed: dropped ling-3.0-flash
- `2026-08-05` — Free models changed: added gemma-4, llama-3.3
- `2026-08-05` — Added: OpenAI-compatible gateway whose catalog carries eleven live :free ids priced at zero — gpt-oss-120b, Ling 3.0 Flash, Step 3.7 Flash, Gemma 4 and the Llama 3.x line — beside a metered 100+ model catalog

---

Generated from `registry.yaml` on 2026-10-02 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
