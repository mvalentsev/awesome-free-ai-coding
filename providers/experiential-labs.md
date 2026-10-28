---
layout: default
title: 'Experiential Labs free tier: limits, free models, verified 2026-10-26'
description: Open-source AI gateway backed by Y Combinator with recurring model-specific free quotas after a settled payment, separate from its paid credit wallet. The documented promotional free tiers require a saved card and one settled $1+ charge; adding a card alone is insufficient. The :free aliases stop…
permalink: /providers/experiential-labs/
last_modified_at: 2026-10-26
crumb: Experiential Labs
---

{% raw %}

# Experiential Labs free tier

🧭 Aggregators (one key, many providers) · card required · requires $1 one-time charge · **live** — last verified by a probe on 2026-10-26 · [experientiallabs.ai](https://www.experientiallabs.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source AI gateway backed by Y Combinator with recurring model-specific free quotas after a settled payment, separate from its paid credit wallet

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Astra promotional input: 500,000 tokens/day; 200,000 tokens/hour per organization per model; for `gpt-6-astra:free`

Astra promotional output: 100,000 tokens/day; 40,000 tokens/hour per organization per model; for `gpt-6-astra:free`

Fable 5.1 promotional input: 375,000 tokens/day; 100,000 tokens/hour per organization per model; for `claude-fable-5.1:free`

Fable 5.1 promotional output: 75,000 tokens/day; 30,000 tokens/hour per organization per model; for `claude-fable-5.1:free`

Free core models: 10 requests/minute; 250,000 tokens/minute; 1,000,000 tokens/day per service plan

The documented promotional free tiers require a saved card and one settled $1+ charge; adding a card alone is insufficient. The :free aliases stop at their quota instead of switching to paid credit. Cached input does not count toward these promotional quotas. The separate pricing-page Free core caps apply to its advertised DeepSeek V4.1 Flash and GPT-6 Luna routes, not these promotional aliases. That page has no general monthly credits; its Free card speed conflicts with its detailed table and FAQ, and its chat claims conflict with positive Free-selected catalog prices. Jev uses a decision API rather than chat. Free prompt and response storage cannot be disabled without a paid plan.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.experientiallabs.ai/terms), read 2026-09-26).

## Connect

- Base URL: `https://api.experientiallabs.ai/v1`
- Key: `EXPERIENTIAL_LABS_API_KEY` — get one at <https://platform.experientiallabs.ai>
- Callable ids: `gpt-6-astra:free`, `claude-fable-5.1:free`
- `gpt-6-astra:free`: requires $1 one-time charge ([conditions](https://platform.experientiallabs.ai/llms.txt))
- `claude-fable-5.1:free`: requires $1 one-time charge ([conditions](https://platform.experientiallabs.ai/llms.txt))
- Note: An API key is required. These documented promotional :free aliases stop without charging when their allowance is spent. Do not remove the suffix: plain model IDs can switch to paid credit. The separate pricing-page Luna and DeepSeek chat offers have conflicting Free catalog prices.

Try it from your terminal with your key in `EXPERIENTIAL_LABS_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.experientiallabs.ai/v1/chat/completions \
  -H "Authorization: Bearer $EXPERIENTIAL_LABS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-6-astra:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://platform.experientiallabs.ai/llms.txt>, anchored on `some platform-funded models carry a promotional free daily tier`
- Source: <https://www.experientiallabs.ai/pricing>
- Source: <https://www.experientiallabs.ai/>
- Source: <https://platform.experientiallabs.ai/models>
- Source: <https://platform.experientiallabs.ai/llms.txt>
- Source: <https://api.experientiallabs.ai/api/models/gpt-6-luna>
- Source: <https://api.experientiallabs.ai/api/models/deepseek-v4.1-flash>
- Source: <https://api.experientiallabs.ai/api/models/clef-flash>
- Source: <https://api.experientiallabs.ai/api/models/gpt-6-astra>
- Source: <https://api.experientiallabs.ai/api/models/claude-fable-5.1>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-26` — Restored: Open-source AI gateway backed by Y Combinator with recurring model-specific free quotas after a settled payment, separate from its paid credit wallet
- `2026-10-26` — Archived: delisted on 2026-10-26: no confirmed free chat allowance after the general monthly credit was withdrawn
- `2026-09-21` — Added: An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check

---

Generated from `registry.yaml` on 2026-10-28 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
