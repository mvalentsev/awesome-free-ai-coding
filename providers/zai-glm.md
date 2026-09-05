---
layout: default
title: 'Z.ai (Zhipu GLM) free tier: limits, free models, verified 2026-09-03'
description: GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4). GLM-4.7-Flash, GLM-4.5-Flash and the GLM-4.6V-Flash vision model are the three rows z.ai's own price table reads Free on all four columns — every other model there says "Limited-time Free" instead,…
permalink: /providers/zai-glm/
---

{% raw %}

# Z.ai (Zhipu GLM)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [z.ai](https://z.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4)

## Free models

`glm-4.7-flash`, `glm-4.5-flash`, `glm-4.6v-flash`

## Limits, in the vendor's words

GLM-4.7-Flash, GLM-4.5-Flash and the GLM-4.6V-Flash vision model are the three rows z.ai's own price table reads Free on all four columns — every other model there says "Limited-time Free" instead, including the flagship GLM-5.x. Rate-limited

## Connect

- Base URL: `https://api.z.ai/api/paas/v4`
- Key: `ZAI_GLM_API_KEY` — get one at <https://z.ai/manage-apikey/apikey-list>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.z.ai/api/anthropic`
- Note: Coding-Plan keys use https://api.z.ai/api/coding/paas/v4 instead. The Claude Code guide sets ANTHROPIC_BASE_URL to https://api.z.ai/api/anthropic with "your_zai_api_key" as the token and names Coding-Plan ids (glm-5.3, glm-5.3-flash); whether the free Flash ids answer on that route is not stated, and the route answers 401 keyless (2026-09-05)

## Evidence

- Probe: the page at <https://docs.z.ai/guides/overview/pricing>, anchored on `GLM-4.7-Flash</td><td style="text-align:left">Free</td>`, `GLM-4.5-Flash</td><td style="text-align:left">Free</td>`, `GLM-4.6V-Flash</td><td style="text-align:left">Free</td>`
- Source: <https://docs.z.ai/guides/overview/pricing>
- Source: <https://docs.z.ai/devpack/tool/claude>

## History

- `2026-08-14` — Free models changed: added glm-4.5-flash, glm-4.6v-flash
- `2026-07-27` — Free models changed: added glm-4.7-flash; dropped glm-4.5
- `2026-07-19` — Added to the list: GLM Flash models free on the API (OpenAI-compatible at api.z.ai/api/paas/v4)

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
