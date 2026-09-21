---
layout: default
title: 'Mixlayer free tier: limits, free models, verified 2026-09-21'
description: Serverless open models priced per token, with one of them at $0 — Qwen3.5 4B as qwen/qwen3.5-4b-free, at 131K context — callable without prepaid credit. The pricing page says "Free models stay free; pay-as-you-go for everything else." and prices its one free row, qwen/qwen3.5-4b-free, at $0.00…
permalink: /providers/mixlayer/
---

{% raw %}

# Mixlayer

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [mixlayer.com](https://www.mixlayer.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Serverless open models priced per token, with one of them at $0 — Qwen3.5 4B as qwen/qwen3.5-4b-free, at 131K context — callable without prepaid credit

## Free models

`qwen3.5-4b`

## Limits, in the vendor's words

The pricing page says "Free models stay free; pay-as-you-go for everything else." and prices its one free row, qwen/qwen3.5-4b-free, at $0.00 in and out, 131K context, vision and text. The billing docs: "Free models do not require prepaid credit." — a paid model on an empty prepaid balance answers `402`. Rate limits are set per organization and per model, and "Mixlayer does not publish fixed limit values because limits can differ by organization and model". The docs' introduction sends its first request to the free model. The operator is Mixlayer Labs Inc. Read 2026-09-17

## What happens to what you send

What you send is not used to train models. In the vendor's words: “By default, Mixlayer does not use Customer Content (Inputs/Outputs) to train or improve models for general availability” ([source](https://www.mixlayer.com/privacy-policy)).

## Connect

- Base URL: `https://models.mixlayer.ai/v1`
- Key: `MIXLAYER_API_KEY` — get one at <https://console.mixlayer.com/app/api-keys>
- Callable ids: `qwen/qwen3.5-4b-free`
- Note: the id is the pricing page's and the docs' own example; /v1/models answers 401 without a key, so it is not read off a catalog

## Evidence

- Probe: the page at <https://www.mixlayer.com/pricing>, anchored on `qwen/qwen3.5-4b-free`, `Free models stay free`
- Source: <https://www.mixlayer.com/pricing>
- Source: <https://docs.mixlayer.com/credits-and-limits.md>
- Source: <https://docs.mixlayer.com/introduction.md>

## History

- `2026-09-21` — Added to the list: Serverless open models priced per token, with one of them at $0 — Qwen3.5 4B as qwen/qwen3.5-4b-free, at 131K context — callable without prepaid credit

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
