---
layout: default
title: 'SEA-LION (AI Singapore) free tier: limits, free models, verified 2026-09-03'
description: AI Singapore's open Southeast-Asian model family behind a first-party OpenAI-compatible API — the vendor hosting its own weights rather than a gateway reselling somebody else's. Free API meant for prototyping — rate limited at 10 calls/min per user, with no credit or token budget published and…
permalink: /providers/sea-lion/
---

{% raw %}

# SEA-LION (AI Singapore)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [sea-lion.ai](https://sea-lion.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

AI Singapore's open Southeast-Asian model family behind a first-party OpenAI-compatible API — the vendor hosting its own weights rather than a gateway reselling somebody else's

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Free API meant for prototyping — rate limited at 10 calls/min per user, with no credit or token budget published and no expiry stated; production use is pointed at cloud partners (AWS, Cloudflare, GCP, IBM, NVIDIA, Qualcomm) instead. The two surfaces do not overlap — the page that calls the API free names no model, and the docs page that names aisingapore/Qwen-SEA-LION-v4.5-27B-IT — and dates the 10 RPM limit to 04 Jun 2026 — never says free

## Connect

- Base URL: `https://api.sea-lion.ai/v1`
- Key: `SEA_LION_API_KEY` — get one at <https://playground.sea-lion.ai/key-manager>
- Callable ids: `aisingapore/Qwen-SEA-LION-v4.5-27B-IT`, `aisingapore/Llama-SEA-LION-v3.5-70B-R`
- Note: the key manager calls it a Trial API Key but publishes no expiry and no credit balance — the documented ceiling is the 10 calls/min rate limit. /v1/models needs the key, so the probe reads the offer page

## Evidence

- Probe: the page at <https://sea-lion.ai/try-sea-lion/>, anchored on `10 calls/min`, `prototype and test with our free api`
- Source: <https://sea-lion.ai/try-sea-lion/>
- Source: <https://docs.sea-lion.ai/guides/inferencing/api>

## History

- `2026-08-17` — Free models changed: dropped llama-sea-lion-v3.5, qwen-sea-lion-v4.5
- `2026-08-11` — Added to the list: AI Singapore's open Southeast-Asian model family behind a first-party OpenAI-compatible API — the vendor hosting its own weights rather than a gateway reselling somebody else's

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
