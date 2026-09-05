---
layout: default
title: 'Hetzner Inference API free tier: limits, free models, verified 2026-09-03'
description: 'OpenAI-compatible API on Hetzner''s own EU hardware, free for as long as the experiment runs. Hetzner answers it in its own FAQ: "As long as the Inference API remains in experimental status, it is free of charge. Should this status change, we will notify you in advance via email with detailed…'
permalink: /providers/hetzner-inference/
---

{% raw %}

# Hetzner Inference API

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [docs.hetzner.com](https://docs.hetzner.com/general/company-and-policy/experiments/inference/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs

## Free models

`qwen3.6`, `qwen3.8`

## Limits, in the vendor's words

Hetzner answers it in its own FAQ: "As long as the Inference API remains in experimental status, it is free of charge. Should this status change, we will notify you in advance via email with detailed information." Published per API key: 4M input and 100k output tokens per 60s, plus 10 requests per 60s, HTTP 429 over either. No daily, monthly or lifetime cap is published and no end date is named — the same page calls the service experimental, "provided for experimental purposes only and offered as is", with performance and availability not guaranteed and no backups. A Hetzner account is needed to mint a token and the docs do not say whether a payment method is required; Hetzner's own fraud-prevention page offers a card charge as one of several verification routes (read 2026-08-30)

## Connect

- Base URL: `https://inference.hetzner.com/api/v1`
- Key: `HETZNER_INFERENCE_API_KEY` — get one at <https://experiments.hetzner.com/inference>
- Callable ids: `Qwen/Qwen3.6-35B-A3B-FP8`, `Qwen3.8-27B`
- Note: both ids are 262K-context and take text and images; /v1/models, /v1/completions and /v1/chat/completions are the whole surface. The key is minted in the Inference tab of experiments.hetzner.com, which is a client-rendered page behind a Hetzner login — the readable copy of the terms is the docs page this row probes

## Evidence

- Probe: the page at <https://docs.hetzner.com/general/company-and-policy/experiments/inference/>, anchored on `remains in experimental status, it is free of charge`, `https://inference.hetzner.com/api/v1`
- Source: <https://docs.hetzner.com/general/company-and-policy/experiments/inference/>
- Source: <https://experiments.hetzner.com/inference>
- Source: <https://inference.hetzner.com/api/v1/models>

## History

- `2026-08-31` — Added to the list: OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
