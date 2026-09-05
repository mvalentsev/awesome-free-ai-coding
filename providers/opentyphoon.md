---
layout: default
title: 'OpenTyphoon (SCB 10X) free tier: limits, free models, verified 2026-09-05'
description: Thai-tuned open models from SCB 10X, the venture arm of Siam Commercial Bank, behind an OpenAI-compatible API whose FAQ calls it a research showcase and free to use. Rate limits are the published ceiling — 5 requests per second and 200 per minute on typhoon-v2.5-30b-a3b-instruct, 2 and 20 on…
permalink: /providers/opentyphoon/
---

{% raw %}

# OpenTyphoon (SCB 10X)

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-05 · [opentyphoon.ai](https://opentyphoon.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Thai-tuned open models from SCB 10X, the venture arm of Siam Commercial Bank, behind an OpenAI-compatible API whose FAQ calls it a research showcase and free to use

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Rate limits are the published ceiling — 5 requests per second and 200 per minute on typhoon-v2.5-30b-a3b-instruct, 2 and 20 on typhoon-ocr — with no token, daily or monthly cap stated; higher limits are by email "with details about your use case, expected volume, and requirements". The FAQ answers the price in one sentence, "The Typhoon API is a research showcase and free to use", and names the trade in the next: "Yes, we are collecting usage data from the Typhoon API", used "to improve the model and the API" and, it says, never shared with third parties. Production use is pointed elsewhere — "please support us by using the API through Together AI" — and the paid API Pro that ran there sunset on 2025-12-31 with an AWS successor announced for Q1 2026 that had not appeared by this read (2026-09-05). A key is minted in the playground after signing up; no card is mentioned on any page read

## Connect

- Base URL: `https://api.opentyphoon.ai/v1`
- Key: `OPENTYPHOON_API_KEY` — get one at <https://playground.opentyphoon.ai/api-key>
- Callable ids: `typhoon-v2.5-30b-a3b-instruct`
- Note: the one chat id in the keyless catalog on 2026-09-05; the other five rows are OCR (typhoon-ocr, typhoon-ocr-v1.5, typhoon-ocr-preview) and speech (typhoon-asr-realtime, typhoon-isan-asr-realtime). typhoon-v2.1-12b-instruct keeps a line in the rate-limit table but has left the catalog. Typhoon 2.5 is a Qwen3-30B-A3B fine-tune for Thai, so it is a Qwen-class coder that also reads Thai; the Free models column stays empty because the FAQ the probe reads names no model

## Evidence

- Probe: the page at <https://docs.opentyphoon.ai/en/faq/>, anchored on `the typhoon api is a research showcase and`, `free to use`; ids checked in <https://api.opentyphoon.ai/v1/models>
- Source: <https://docs.opentyphoon.ai/en/faq/>
- Source: <https://docs.opentyphoon.ai/en/rate-limits/>
- Source: <https://api.opentyphoon.ai/v1/models>

## History

No recorded event yet — the first scheduled run after a row lands writes its `added` line.

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
