---
layout: default
title: 'Arli AI free tier: limits, free models, verified 2026-09-24'
description: OpenAI-compatible inference on open models and their fine-tunes, whose Free plan tries each model five times every two days at 12K tokens of context, one request at a time. The pricing page's Free plan, "Test out the Arli platform" at $0, lists only what it withholds — "Delayed Response",…
permalink: /providers/arli-ai/
last_modified_at: 2026-09-26
crumb: Arli AI
---

{% raw %}

# Arli AI free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [arliai.com](https://www.arliai.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible inference on open models and their fine-tunes, whose Free plan tries each model five times every two days at 12K tokens of context, one request at a time

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The pricing page's Free plan, "Test out the Arli platform" at $0, lists only what it withholds — "Delayed Response", "Slower with more requests", "Max 12K context tokens", "1 request at a time" — and the text generation docs state the allowance: "Free accounts are able to use each model for a maximum of 5 requests every 2 days for testing purposes". The keyless catalog at api.arliai.com/model/all listed 92 models on 2026-09-17 — DeepSeek-V4-Flash-0731, MiMo-V2.5, GLM-4.7 and Gemma-4-31B-it among them, most of the rest Qwen3.5 27B and Gemma 4 31B fine-tunes recommended for writing and roleplay. Past the trial the Personal Starter plan is $10 a month. Read 2026-09-25

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.arliai.com/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “By submitting prompts or other inputs to the Services, you grant us a worldwide, non-exclusive, royalty-free license to use, process, and transmit your inputs solely for the purpose of generating and returning a response to you, and only for the duration necessary to complete that request.” ([source](https://www.arliai.com/terms)).

## Connect

- Base URL: `https://api.arliai.com/v1`
- Key: `ARLI_AI_API_KEY` — get one at <https://www.arliai.com/account>
- Note: the quick-start calls it a drop-in OpenAI-API compatible endpoint and uses a placeholder model id; the catalog's names are the models page's, and the coding quick-start connects Roo Code and Kilo Code with a context window set to the model picked. /v1/chat/completions answers 401 without a key. The Models column stays empty: the docs page the probe reads names no model, and the trial covers every catalog row alike

## Evidence

- Probe: the page at <https://www.arliai.com/docs/textgen>, anchored on `Free accounts are able to use each model for a maximum of 5 requests every 2 days`
- Source: <https://www.arliai.com/pricing>
- Source: <https://www.arliai.com/docs/textgen>
- Source: <https://www.arliai.com/quick-start>
- Source: <https://api.arliai.com/model/all>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI-compatible inference on open models and their fine-tunes, whose Free plan tries each model five times every two days at 12K tokens of context, one request at a time

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
