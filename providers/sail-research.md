---
layout: default
title: 'Sail Research free tier: limits, free models, verified 2026-09-24'
description: 'Open-weight models for long-running agents — Kimi K3, GLM-5.3, DeepSeek V4 Pro — behind OpenAI- and Anthropic-compatible APIs, with $5 of free credit every month once a payment method is on the account. The home page: "$5 in free credits every month when you attach a payment method", and its FAQ…'
permalink: /providers/sail-research/
last_modified_at: 2026-09-26
crumb: Sail Research
---

{% raw %}

# Sail Research free tier

🔌 LLM APIs with free tier · card required · not offered in Russia, Iran, Syria and 2 more places · provisional — added on 2026-09-21, a regular row from the first probe it passes on or after 2026-10-05 · **live** — last verified by a probe on 2026-09-24 · [sailresearch.com](https://www.sailresearch.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-weight models for long-running agents — Kimi K3, GLM-5.3, DeepSeek V4 Pro — behind OpenAI- and Anthropic-compatible APIs, with $5 of free credit every month once a payment method is on the account

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

The home page: "$5 in free credits every month when you attach a payment method", and its FAQ "with $5 in free credits refreshed every month". The credit spends at the per-token prices, which fall with the completion window a request asks for: GLM-5.3 is $0.98 in / $3.08 out per 1M tokens as soon as possible and $0.40 / $1.80 on flex, DeepSeek V4 Flash 0731 $0.09 / $0.18 and $0.05 / $0.09. "No strict rate limits", and request and response data is "not used to train models without written consent". Read 2026-09-21

## Where it is offered

Not offered in Russia, Iran, Syria, Cuba and North Korea ([source](https://www.sailresearch.com/terms), read 2026-09-26). That leaves out 2.4% of the developers GitHub counts, beyond the embargoed countries most offers leave out ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “access or use the Services in or for the benefit of any embargoed or sanctioned country, region, or person (including Cuba, Iran, North Korea, Syria, the Crimea, Donetsk, and Luhansk regions, and Russia)”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “We do not use inference request or response data to train, fine-tune, or improve models without your written consent.” ([source](https://docs.sailresearch.com/security)).

## Connect

- Base URL: `https://api.sailresearch.com/v1`
- Key: `SAIL_RESEARCH_API_KEY` — get one at <https://app.sailresearch.com>
- Callable ids: `moonshotai/Kimi-K3`, `zai-org/GLM-5.3`, `deepseek-ai/DeepSeek-V4-Pro-0813`, `zai-org/GLM-5.3-Flash`, `deepseek-ai/DeepSeek-V4-Flash-0731`
- Note: ids are the models page's, 2026-09-21 — the catalog answers only a key. Sail's stable surface is the Responses API, and the FAQ says "Responses, Chat Completions, and Messages all work as expected"; a request may name a balanced or flex completion window to pay less and wait longer

Try it from your terminal with your key in `SAIL_RESEARCH_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.sailresearch.com/v1/chat/completions \
  -H "Authorization: Bearer $SAIL_RESEARCH_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"moonshotai/Kimi-K3","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.sailresearch.com/>, anchored on `$5 in free credits every month when you attach a payment method`
- Source: <https://www.sailresearch.com/>
- Source: <https://docs.sailresearch.com/pricing>
- Source: <https://docs.sailresearch.com/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped deepseek-v4-flash, deepseek-v4-pro, glm-5.3, glm-5.3-flash, kimi-k3
- `2026-09-21` — Added: Open-weight models for long-running agents — Kimi K3, GLM-5.3, DeepSeek V4 Pro — behind OpenAI- and Anthropic-compatible APIs, with $5 of free credit every month once a payment method is on the account

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
