---
layout: default
title: 'Requesty free tier: limits, free models, verified 2026-10-08'
description: 'OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks. Free models: nemotron-3-ultra, nemotron-3-super, gemma-4-31b, ling-3.0-tiny, muse-glimmer-30b, nemotron-3.5-lightning, leanstral-1.5, nemotron-3-nano-30b and 1 more. No credit card for the Free…'
permalink: /providers/requesty/
last_modified_at: 2026-10-08
crumb: Requesty
---

{% raw %}

# Requesty free tier

🧭 Aggregators (one key, many providers) · no card · **live** — last verified by a probe on 2026-10-08 · [requesty.ai](https://www.requesty.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible router with free models beside a metered catalog, routing, caching and fallbacks

## Free models

[`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/), [`gemma-4-31b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemma-4-31b/), [`ling-3.0-tiny`](https://mvalentsev.github.io/awesome-free-ai-coding/models/ling-3.0-tiny/), [`muse-glimmer-30b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/muse-glimmer-30b/), [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/), `leanstral-1.5`, [`nemotron-3-nano-30b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-30b/), [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/)

## Limits, in the vendor's words

200 requests/day per account

No credit card for the Free plan, which serves free models only. Routing, caching, fallbacks, spend tracking and EU data residency are included. Past the free allowance the same key moves to pay-as-you-go.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.requesty.ai/terms), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Where a Model Provider trains on prompts, we label that model a Training Permitted Model so you can see exactly which ones they are, and every model we label that way is offered free of charge. Requesty's own use of content for training is limited to free plan accounts.” ([source](https://www.requesty.ai/privacy)).

## Connect

- Base URL: `https://router.requesty.ai/v1`
- Key: `REQUESTY_API_KEY` — get one at <https://app.requesty.ai/api-keys>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://router.requesty.ai`
- Callable ids: `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-nano-30b-a3b`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, `novita/inclusionai/ling-3.0-tiny`, `google/gemma-4-31b-it`, `mistral/leanstral-1-5`, `nvidia/muse-glimmer-30b`, `nvidia/nemotron-3.5-lightning-30b-a3b`, `novita/ling-3.1-flash`
- Note: Free-plan IDs are priced zero and have no expired retirement date; they carry no :free suffix. NVIDIA rows disclose training use and 30-day retention. For Claude Code, set ANTHROPIC_BASE_URL=https://router.requesty.ai, or https://router.eu.requesty.ai for EU residency.

Try it from your terminal with your key in `REQUESTY_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://router.requesty.ai/v1/chat/completions \
  -H "Authorization: Bearer $REQUESTY_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://router.requesty.ai/v1/models>, each listed family checked for a zero price
- Source: <https://www.requesty.ai/pricing>
- Source: <https://docs.requesty.ai/quickstart>
- Source: <https://router.requesty.ai/v1/models>
- Source: <https://docs.requesty.ai/integrations/claude-code>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-27` — Free models changed: dropped laguna-m.1, laguna-xs.2
- `2026-09-25` — Free models changed: added gemma-4-31b; dropped gemma-4
- `2026-09-24` — Free models changed: added laguna-m.1, laguna-xs.2, leanstral-1.5, nemotron-3-nano-30b, nemotron-3-nano-omni
- `2026-09-17` — Free models changed: added muse-glimmer-30b, nemotron-3.5-lightning
- `2026-08-11` — Added: OpenAI-compatible router over a 500+ model catalog with routing, caching and fallbacks; ten rows in it are priced 0 and the free plan is the same gateway restricted to those

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
