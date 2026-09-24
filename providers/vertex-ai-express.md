---
layout: default
title: 'Gemini Enterprise Agent Platform express mode (formerly Vertex AI) free tier: limits, free models, verified 2026-09-24'
description: 'Google Cloud''s express mode: an API key and 90 days of Gemini models within the free tier''s quotas, with no billing information, for a new Google Cloud user on a @gmail.com account. The express mode overview: "New users to Google Cloud can sign up for an express mode account in a free tier to…'
permalink: /providers/vertex-ai-express/
---

{% raw %}

# Gemini Enterprise Agent Platform express mode (formerly Vertex AI)

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-23, a regular row from the first probe it passes on or after 2026-10-07 · **live** — last verified by a probe on 2026-09-24 · [docs.cloud.google.com](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Google Cloud's express mode: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account

## Free models

`gemini-3.1-pro`, `gemini-3-flash`, `gemini-2.5-pro`, `gemini-2.5-flash`

## Limits, in the vendor's words

The express mode overview: "New users to Google Cloud can sign up for an express mode account in a free tier to try Agent Platform for free for up to 90 days, within the specified quotas", and "You don't need to provide billing information to sign up in the free tier". Its model table gives gemini-3.1-pro-preview, gemini-3-pro-preview and gemini-3-flash-preview a dynamic rate limit and gemini-2.5-pro, gemini-2.5-flash and the Flash-Lite and 2.0 Flash rows 10 requests a minute. The FAQ: "If you don't enable billing, you won't be able to use express mode after 90 days". An existing Google Cloud user gets no free tier, and the separate $300 Free Trial asks for "a credit card or other payment method". Express mode is a Preview, and its terms add "Customer will not use the Express Mode Offerings to process personal data". Read 2026-09-23

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Google won't use your data to train or fine-tune any AI/ML models without your prior permission or instruction. This applies to all managed models on Gemini Enterprise Agent Platform, including GA and pre-GA models” ([source](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention)).

## Connect

- Base URL: `https://aiplatform.googleapis.com/v1` (not OpenAI-shaped)
- Key: `VERTEX_AI_EXPRESS_API_KEY` — get one at <https://console.cloud.google.com/expressmode>
- Callable ids: `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-pro`, `gemini-2.5-flash`
- Note: the key stands in for a project and a location: `https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:streamGenerateContent?key={API_KEY}`, Gemini's own API rather than an OpenAI-compatible one. Clients kept the old name: the Google Gen AI SDK takes the key with vertexai=True, and Gemini CLI reads it from GOOGLE_API_KEY "if using express mode", with Vertex AI as the auth method

## Evidence

- Probe: the page at <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview>, anchored on `try Agent Platform for free for up to 90 days`, `need to provide billing information to sign up in the free tier`
- Source: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview>
- Source: <https://cloud.google.com/terms/google-cloud-express>
- Source: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/vertex-ai-name-changes>
- Source: <https://cloud.google.com/resources/cloud-express-faqs>
- Source: <https://cloud.google.com/free/docs/free-cloud-features>
- Source: <https://raw.githubusercontent.com/google-gemini/gemini-cli/HEAD/packages/cli/src/config/auth.ts>

## History

Each line is a change to what this page publishes, dated the day the list recorded it, in UTC.

- `2026-09-23` — Added: Google Cloud's express mode for the Gemini Enterprise Agent Platform, formerly Vertex AI: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
