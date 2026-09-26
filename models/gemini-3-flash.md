---
layout: default
title: 'gemini-3-flash free: 2 providers, limits and ids, verified 2026-09-24'
description: gemini-3-flash is served free by Google AI Studio (Gemini API) and Gemini Enterprise Agent Platform express mode (formerly Vertex AI). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/gemini-3-flash/
last_modified_at: 2026-09-25
---

{% raw %}

# Where gemini-3-flash is free

**2 rows on the list serve `gemini-3-flash` free:** Google AI Studio (Gemini API) and Gemini Enterprise Agent Platform express mode (formerly Vertex AI). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Google AI Studio (Gemini API)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/google-ai-studio/)

🔌 LLM APIs with free tier · no card · verified 2026-09-24 · listed since 2026-09-25

Free tier on the Gemini API, priced model by model rather than as one account quota

- Limits, in the vendor's words: Google prices the free tier per model: its pricing page reads "Free of charge" for input, output and context caching on Gemini 3.8 Flash, "our most intelligent Flash model, engineered for long-horizon software engineering", in the same column that prices it at $0.75/$3.75 per 1M on the paid tier, and on 3.7, 3.6 and 3.5 Flash, 3.5 and 3.1 Flash-Lite, 3 Flash Preview and Gemma 4, with "Not available" there for Gemini 3.1 Pro Preview and Omni Flash. The 2.5 models keep a free column, but since 2026-09-18 the changelog says Google is "limiting access to the 2.5 models to users who have actively used them in the past": "For any new projects, use our latest models: 3.5 Flash-Lite or 3.8 Flash". What the free tier costs instead is one row lower in each table: "Used to improve our products" is Yes on the free tier and No on the paid one. Per-model RPM/TPM/RPD figures sit behind a sign-in at aistudio.google.com/rate-limit; the public rate-limits page keeps only the usage-tier table, whose free row reads "Active project or free trial". Read 2026-09-25
- Call it: `gemini-3-flash-preview` at `https://generativelanguage.googleapis.com/v1beta/openai/`, with a key in `GOOGLE_AI_STUDIO_API_KEY` from <https://aistudio.google.com/apikey>
- What you send may be used to train or improve models ([the vendor's words](https://ai.google.dev/gemini-api/terms)).

### [Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vertex-ai-express/)

🎁 Trials (no card when possible) · no card · provisional since 2026-09-23 · verified 2026-09-24 · listed since 2026-09-23

Google Cloud's express mode: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account

- Limits, in the vendor's words: The express mode overview: "New users to Google Cloud can sign up for an express mode account in a free tier to try Agent Platform for free for up to 90 days, within the specified quotas", and "You don't need to provide billing information to sign up in the free tier". Its model table gives gemini-3.1-pro-preview, gemini-3-pro-preview and gemini-3-flash-preview a dynamic rate limit and gemini-2.5-pro, gemini-2.5-flash and the Flash-Lite and 2.0 Flash rows 10 requests a minute. The FAQ: "If you don't enable billing, you won't be able to use express mode after 90 days". An existing Google Cloud user gets no free tier, and the separate $300 Free Trial asks for "a credit card or other payment method". Express mode is a Preview, and its terms add "Customer will not use the Express Mode Offerings to process personal data". Read 2026-09-23
- Call it: `gemini-3-flash-preview` at `https://aiplatform.googleapis.com/v1` (not OpenAI-shaped), with a key in `VERTEX_AI_EXPRESS_API_KEY` from <https://console.cloud.google.com/expressmode>
- What you send is not used to train models ([the vendor's words](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention)).

## Related models

- [`gemini-3.1-pro`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.1-pro/) — free at Google Antigravity and Gemini Enterprise Agent Platform express mode (formerly Vertex AI)
- [`gemini-3.6-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.6-flash/) — free at Google AI Studio (Gemini API) and Google Antigravity
- [`gemini-3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.7-flash/) — free at Google AI Studio (Gemini API) and Google Antigravity
- [`gemini-3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.8-flash/) — free at Google AI Studio (Gemini API) and Google Antigravity

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
