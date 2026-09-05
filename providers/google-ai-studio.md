---
layout: default
title: 'Google AI Studio (Gemini API) free tier: limits, free models, verified 2026-09-03'
description: 'Free tier on the Gemini API, priced model by model rather than as one account quota. Google prices the free tier per model: its pricing page reads "Free of charge" for input, output and context caching on Gemini 3.7 Flash, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3 Flash Preview,…'
permalink: /providers/google-ai-studio/
---

{% raw %}

# Google AI Studio (Gemini API)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [aistudio.google.com](https://aistudio.google.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free tier on the Gemini API, priced model by model rather than as one account quota

## Free models

`gemini-3.7-flash`, `gemini-3.5-flash-lite`, `gemini-2.5-pro`

## Limits, in the vendor's words

Google prices the free tier per model: its pricing page reads "Free of charge" for input, output and context caching on Gemini 3.7 Flash, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3 Flash Preview, 2.5 Pro and 2.5 Flash, and "Not available" in the same column for Gemini 3.1 Pro Preview, Omni Flash Preview and the Live previews. What the free tier costs instead is one row lower in each table: "Used to improve our products" is Yes on the free tier and No on the paid one. The per-model RPM/TPM/RPD figures are no longer published anywhere a probe can read — as of its own "Last updated 2026-08-13" the rate-limits page keeps only the usage-tier table ("Free — Active project or free trial") and sends you to aistudio.google.com/rate-limit, which needs a sign-in (read 2026-08-14)

## Connect

- Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Key: `GOOGLE_AI_STUDIO_API_KEY` — get one at <https://aistudio.google.com/apikey>
- Note: pass the key as Bearer

## Evidence

- Probe: the page at <https://ai.google.dev/gemini-api/docs/pricing>, anchored on `gemini-2.5-flash`, `free of charge`
- Source: <https://ai.google.dev/gemini-api/docs/pricing>
- Source: <https://ai.google.dev/gemini-api/docs/rate-limits>

## History

- `2026-08-17` — Free models changed: added gemini-2.5-pro, gemini-3.5-flash-lite, gemini-3.7-flash; dropped gemini-2.5
- `2026-07-19` — Added to the list: Free tier for Gemini 2.5 Flash/Pro API

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
