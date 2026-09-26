---
layout: default
title: 'Google AI Studio (Gemini API) free tier: limits, free models, verified 2026-09-24'
description: 'Free tier on the Gemini API, priced model by model rather than as one account quota. Google prices the free tier per model: its pricing page reads "Free of charge" for input, output and context caching on Gemini 3.8 Flash, "our most intelligent Flash model, engineered for long-horizon software…'
permalink: /providers/google-ai-studio/
last_modified_at: 2026-09-26
crumb: Google AI Studio (Gemini API)
---

{% raw %}

# Google AI Studio (Gemini API) free tier

🔌 LLM APIs with free tier · no card · not offered in mainland China, Russia, Hong Kong and 13 more places · **live** — last verified by a probe on 2026-09-24 · [aistudio.google.com](https://aistudio.google.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free tier on the Gemini API, priced model by model rather than as one account quota

## Free models

[`gemini-3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.8-flash/), [`gemini-3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.7-flash/), [`gemini-3.6-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.6-flash/), [`gemini-3.5-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.5-flash/), [`gemini-3.5-flash-lite`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.5-flash-lite/), [`gemini-3.1-flash-lite`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.1-flash-lite/), [`gemini-3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3-flash/), `gemma-4`

## Limits, in the vendor's words

Google prices the free tier per model: its pricing page reads "Free of charge" for input, output and context caching on Gemini 3.8 Flash, "our most intelligent Flash model, engineered for long-horizon software engineering", in the same column that prices it at $0.75/$3.75 per 1M on the paid tier, and on 3.7, 3.6 and 3.5 Flash, 3.5 and 3.1 Flash-Lite, 3 Flash Preview and Gemma 4, with "Not available" there for Gemini 3.1 Pro Preview and Omni Flash. The 2.5 models keep a free column, but since 2026-09-18 the changelog says Google is "limiting access to the 2.5 models to users who have actively used them in the past": "For any new projects, use our latest models: 3.5 Flash-Lite or 3.8 Flash". What the free tier costs instead is one row lower in each table: "Used to improve our products" is Yes on the free tier and No on the paid one. Per-model RPM/TPM/RPD figures sit behind a sign-in at aistudio.google.com/rate-limit; the public rate-limits page keeps only the usage-tier table, whose free row reads "Active project or free trial". Read 2026-09-25

## Where it is offered

Offered in the 230 countries and territories its list names, not in mainland China, Russia, Hong Kong, Iran, Belarus, Myanmar, Syria, Afghanistan and 8 more places ([source](https://ai.google.dev/gemini-api/docs/available-regions), read 2026-09-26). That leaves out 10.5% of the developers GitHub counts, beyond the embargoed countries most offers leave out ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “The Gemini API and Google AI Studio are available in the following countries and territories”.

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “When you use Unpaid Services, including, for example, Google AI Studio and the unpaid quota on Gemini API, Google uses the content you submit to the Services and any generated responses to provide, improve, and develop Google products and services and machine learning technologies” ([source](https://ai.google.dev/gemini-api/terms)).

## Connect

- Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Key: `GOOGLE_AI_STUDIO_API_KEY` — get one at <https://aistudio.google.com/apikey>
- Callable ids: `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3-flash-preview`, `gemma-4-31b-it`, `gemma-4-26b-a4b-it`
- Note: pass the key as Bearer

## Evidence

- Probe: the page at <https://ai.google.dev/gemini-api/docs/pricing>, anchored on `gemini-3.8-flash`, `free of charge`
- Source: <https://ai.google.dev/gemini-api/docs/pricing>
- Source: <https://ai.google.dev/gemini-api/docs/rate-limits>
- Source: <https://ai.google.dev/gemini-api/docs/changelog>
- Source: <https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added gemini-3-flash, gemini-3.1-flash-lite, gemini-3.5-flash, gemini-3.6-flash, gemma-4
- `2026-09-23` — Free models changed: dropped gemini-2.5-pro
- `2026-09-07` — Free models changed: added gemini-3.8-flash
- `2026-08-14` — Free models changed: added gemini-2.5-pro, gemini-3.5-flash-lite, gemini-3.7-flash; dropped gemini-2.5
- `2026-07-19` — Added: Free tier for Gemini 2.5 Flash/Pro API

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
