---
layout: default
title: 'gemini-3.1-pro free: 2 providers, limits and ids, verified 2026-09-24'
description: gemini-3.1-pro is served free by Google Antigravity and Gemini Enterprise Agent Platform express mode (formerly Vertex AI). None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/gemini-3.1-pro/
last_modified_at: 2026-09-25
---

{% raw %}

# Where gemini-3.1-pro is free

**2 rows on the list serve `gemini-3.1-pro` free:** Google Antigravity and Gemini Enterprise Agent Platform express mode (formerly Vertex AI). None asks for a card. A live probe confirmed each one on 2026-09-24 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [Google Antigravity](https://mvalentsev.github.io/awesome-free-ai-coding/providers/antigravity/)

🤖 Coding agents & CLIs · no card · verified 2026-09-24 · listed since 2026-08-11

Google's agent-first IDE and CLI, and where the Gemini CLI free tier went — Gemini CLI and the Code Assist IDE extensions stopped serving free, AI Pro and Ultra users on 2026-06-18. The $0 Individual plan carries the same agent models the paid ones do

- Limits, in the vendor's words: $0/month, no subscription. The plan's own bullet reads "Agent model: access to Gemini 3.8 Flash, Gemini 3.7 Flash, Gemini 3.6 Flash, Gemini 3.1 Pro, Claude Sonnet & Opus 4.6, gpt-oss-120b" (read 2026-09-03; Gemini 3.5 Flash stood there until 2026-08-31 and three newer Flash generations have taken its place), with unlimited Tab completions, unlimited Command requests and "Basic weekly rate limits". The docs' availability table ticks all seven models in its Free column, and gives the Claude and GPT models a weekly allowance of their own, apart from the Gemini one. Google publishes no figure for either: "The baseline rate limits are primarily determined to the degree we have capacity, and exist to prevent abuse"
- Inside Google Antigravity itself: no API endpoint to paste
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://antigravity.google/terms)).

### [Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vertex-ai-express/)

🎁 Trials (no card when possible) · no card · provisional since 2026-09-23 · verified 2026-09-24 · listed since 2026-09-23

Google Cloud's express mode: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account

- Limits, in the vendor's words: The express mode overview: "New users to Google Cloud can sign up for an express mode account in a free tier to try Agent Platform for free for up to 90 days, within the specified quotas", and "You don't need to provide billing information to sign up in the free tier". Its model table gives gemini-3.1-pro-preview, gemini-3-pro-preview and gemini-3-flash-preview a dynamic rate limit and gemini-2.5-pro, gemini-2.5-flash and the Flash-Lite and 2.0 Flash rows 10 requests a minute. The FAQ: "If you don't enable billing, you won't be able to use express mode after 90 days". An existing Google Cloud user gets no free tier, and the separate $300 Free Trial asks for "a credit card or other payment method". Express mode is a Preview, and its terms add "Customer will not use the Express Mode Offerings to process personal data". Read 2026-09-23
- Call it: `gemini-3.1-pro-preview` at `https://aiplatform.googleapis.com/v1` (not OpenAI-shaped), with a key in `VERTEX_AI_EXPRESS_API_KEY` from <https://console.cloud.google.com/expressmode>
- What you send is not used to train models ([the vendor's words](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention)).

## Related models

- [`gemini-3-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3-flash/) — free at Google AI Studio (Gemini API) and Gemini Enterprise Agent Platform express mode (formerly Vertex AI)
- [`gemini-3.6-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.6-flash/) — free at Google AI Studio (Gemini API) and Google Antigravity
- [`gemini-3.7-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.7-flash/) — free at Google AI Studio (Gemini API) and Google Antigravity
- [`gemini-3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gemini-3.8-flash/) — free at Google AI Studio (Gemini API) and Google Antigravity

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
