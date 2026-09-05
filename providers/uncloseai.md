---
layout: default
title: 'uncloseai (unturf) free tier: limits, free models, verified 2026-09-03'
description: Keyless OpenAI-compatible chat endpoint — no signup, no key, no account. No quota is published anywhere on the site. The offer is a sentence — "we offer free AI services powered by multiple AI models and a TTS endpoint ... embodying the principles of both free as in beer & free as in freedom" —…
permalink: /providers/uncloseai/
---

{% raw %}

# uncloseai (unturf)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [uncloseai.com](https://uncloseai.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Keyless OpenAI-compatible chat endpoint — no signup, no key, no account

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

No quota is published anywhere on the site. The offer is a sentence — "we offer free AI services powered by multiple AI models and a TTS endpoint ... embodying the principles of both free as in beer & free as in freedom" — and the page names three endpoints, of which one serves text today: hermes.ai.unturf.com/v1 answered a keyless chat completion on 2026-08-30, while qwen.ai.unturf.com/v1 answers 403 "Access denied - This endpoint is closed". The served id is not the one the page's own examples call, and the vendor says so — "See our Model Discovery docs to query the current model IDs being hosted" — so the id lives in api.model_ids and the Free models column stays empty

## Connect

- Base URL: `https://hermes.ai.unturf.com/v1`
- Key: none — the lane is anonymous
- Callable ids: `Lorbus/Qwen3.6-27B-int4-AutoRound`
- Note: anonymous: the catalog and chat/completions both answer with no Authorization header at all. One id is served at a time and it rotates — the endpoint is named after Hermes and serves a Qwen build today — so treat the id as this week's, not the offer

## Evidence

- Probe: the models catalog at <https://hermes.ai.unturf.com/v1/models>
- Source: <https://hermes.ai.unturf.com/v1/models>

## History

- `2026-08-31` — Added to the list: Keyless OpenAI-compatible chat endpoint — no signup, no key, no account

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
