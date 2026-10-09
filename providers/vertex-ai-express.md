---
layout: default
title: 'Gemini Enterprise Agent Platform express mode (formerly Vertex AI) free tier: limits, free models, verified 2026-10-08'
description: 'Google Cloud''s express mode: an API key and 90 days of Gemini models within the free tier''s quotas, with no billing information, for a new Google Cloud user on a @gmail.com account. Free models: gemini-3.1-pro, gemini-3-flash, gemini-2.5-pro, gemini-2.5-flash. The free express trial is for new…'
permalink: /providers/vertex-ai-express/
last_modified_at: 2026-10-08
crumb: Gemini Enterprise Agent Platform express mode (formerly Vertex AI)
---

{% raw %}

# Gemini Enterprise Agent Platform express mode (formerly Vertex AI) free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-08 · [docs.cloud.google.com](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Google Cloud's express mode: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account

## Free models

[`gemini-3.1-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.1-pro/), [`gemini-3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3-flash/), [`gemini-2.5-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-2.5-pro/), `gemini-2.5-flash`

## Limits, in the vendor's words

Preview models: Per-minute requests allowance: amount varies per project per model

Stable Gemini models: 10 requests/minute per project per model (Free express trial lasts up to 90 days); for `gemini-2.5-pro`, `gemini-2.5-flash`

Preview Gemini models: Per-minute requests allowance: amount varies per project per model (Free express trial lasts up to 90 days); for `gemini-3.1-pro-preview`, `gemini-3-flash-preview`

The free express trial is for new Google Cloud users and requires no billing information. Stable and Preview model rate policies differ; enabling billing is necessary after the trial. Existing Google Cloud accounts do not get this offer. The separate $300 Cloud Free Trial needs a payment method. Express is Preview and may not process personal data.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://cloud.google.com/terms/google-cloud-express), read 2026-09-26).

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

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-23` — Added: Google Cloud's express mode for the Gemini Enterprise Agent Platform, formerly Vertex AI: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
