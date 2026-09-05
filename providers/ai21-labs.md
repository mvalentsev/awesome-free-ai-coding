---
layout: default
title: 'AI21 Labs (Jamba) free tier (archived): what it offered, and when it stopped verifying'
description: 'AI21''s Jamba models on a no-card trial credit — hybrid Mamba/attention models built for 256K-token context. The trial was AI21 Studio''s, and the vendor sunset Studio''s Jamba API on 2026-08-09. Retired. The $10 no-card trial belonged to AI21 Studio, and Studio is gone: on 2026-09-05 every…'
permalink: /providers/ai21-labs/
---

{% raw %}

# AI21 Labs (Jamba)

🎁 Trials (no card when possible) · no card · **archived** — vendor-announced shutdown on 2026-08-09 · [ai21.com](https://www.ai21.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

AI21's Jamba models on a no-card trial credit — hybrid Mamba/attention models built for 256K-token context. The trial was AI21 Studio's, and the vendor sunset Studio's Jamba API on 2026-08-09

## Free models

`jamba-mini`, `jamba-large`

## Limits, in the vendor's words

Retired. The $10 no-card trial belonged to AI21 Studio, and Studio is gone: on 2026-09-05 every studio.ai21.com route — the pricing page's own "Start Now for FREE" link to studio.ai21.com/sign-up, the login, the account pages the docs still point at — lands on the www.ai21.com homepage, and the catalog route answers 410 "This API has been retired. The AI21 Gateway is available at https://app.ai21.com". The vendor's notice named the day: "On August 9, 2026, we will officially deprecate and sunset the following APIs in our platform: Jamba API, AI21 Maestro API, File library". What stands at app.ai21.com is not a model API: its own env file names it ai21-intelligent-gateway-webapp with a base of api.ai21.com/gateway, its code snippets take "your own OpenAI key" or "your own Anthropic key", and its billing is a "Tokenwise" plan with a trial counted in days — nothing AI21-hosted, nothing free to call. The pricing page, last modified 2026-05-06, still prints "$10 credits for 7 days. No credit card needed" beside the Jamba prices, and docs.ai21.com/docs/usage-cost still says "New accounts are given a $10 credit good for three months": two figures for one trial whose sign-up no longer exists

## Connect

- Base URL: `https://api.ai21.com/studio/v1` (not OpenAI-shaped)
- Key: `AI21_LABS_API_KEY` — get one at <https://studio.ai21.com/sign-up>
- Callable ids: `jamba-mini`, `jamba-large`
- Note: The Jamba API these ids belong to was sunset by the vendor on 2026-08-09: /studio/v1/models answers 410 "This API has been retired", while /studio/v1/chat/completions still returns 400 "bad or missing authentication" to a keyless POST on 2026-09-05 — the route exists, which says nothing about whether a key still gets an answer. The replacement at api.ai21.com/gateway/v1 gives the same 400 keyless, and it is a bring-your-own-key proxy in front of OpenAI and Anthropic, not a Jamba endpoint. key_url is the one the vendor published and now redirects to the homepage. Never OpenAI-compatible, so it never entered the generated configs

## Evidence

- Probe: the page at <https://www.ai21.com/pricing/>, anchored on `$10 credits for 7 days`, `No credit card needed`, `Jamba Mini`
- Source: <https://www.ai21.com/pricing/>
- Source: <https://docs.ai21.com/august-deprecation-notice>
- Source: <https://docs.ai21.com/docs/jamba-foundation-models.md>
- Source: <https://docs.ai21.com/docs/create-api-key.md>
- Source: <https://docs.ai21.com/docs/usage-cost.md>
- Source: <https://app.ai21.com/>

## History

- `2026-08-14` — Added to the list: AI21's Jamba models on a no-card trial credit — hybrid Mamba/attention models built for 256K-token context, so the trial is worth spending on a long file rather than on a chat

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
