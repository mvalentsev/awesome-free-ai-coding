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

Retired. The $10 no-card trial belonged to AI21 Studio, and Studio is gone: on 2026-09-05 every studio.ai21.com route landed on the www.ai21.com homepage, and the catalog route answered 410 `This API has been retired. The AI21 Gateway is available at https://app.ai21.com`. The vendor's notice named the day: "On August 9, 2026, we will officially deprecate and sunset the following APIs in our platform: Jamba API, AI21 Maestro API, File library". What stands at app.ai21.com is not a model API but a bring-your-own-key gateway in front of OpenAI and Anthropic, with nothing AI21-hosted or free to call

## Connect

- Base URL: `https://api.ai21.com/studio/v1` (not OpenAI-shaped)
- Key: `AI21_LABS_API_KEY` — get one at <https://studio.ai21.com/sign-up>
- Callable ids: `jamba-mini`, `jamba-large`
- Note: the Jamba API these ids belong to was sunset by the vendor on 2026-08-09; on 2026-09-05 /studio/v1/models answered 410 and the replacement at api.ai21.com/gateway/v1 is a bring-your-own-key proxy, not a Jamba endpoint. Never OpenAI-compatible, so it never entered the generated configs

## Evidence

- Probe: the page at <https://www.ai21.com/pricing/>, anchored on `$10 credits for 7 days`, `No credit card needed`, `Jamba Mini`
- Source: <https://www.ai21.com/pricing/>
- Source: <https://docs.ai21.com/august-deprecation-notice>
- Source: <https://docs.ai21.com/docs/jamba-foundation-models.md>
- Source: <https://docs.ai21.com/docs/create-api-key.md>
- Source: <https://docs.ai21.com/docs/usage-cost.md>
- Source: <https://app.ai21.com/>

## History

- `2026-09-07` — Archived: vendor-announced shutdown on 2026-08-09
- `2026-08-14` — Added to the list: AI21's Jamba models on a no-card trial credit — hybrid Mamba/attention models built for 256K-token context, so the trial is worth spending on a long file rather than on a chat

---

Generated from `registry.yaml` on 2026-09-17 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
