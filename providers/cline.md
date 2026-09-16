---
layout: default
title: 'Cline free tier: limits, free models, verified 2026-09-14'
description: Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK. "Cline periodically offers free model promotions that let…
permalink: /providers/cline/
---

{% raw %}

# Cline

🤖 Coding agents & CLIs · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-14 · [cline.bot](https://cline.bot) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK

## Free models

`laguna-s-2.1`

## Limits, in the vendor's words

"Cline periodically offers free model promotions that let you try select models at no cost, up to a limited usage quota", and "Free models are available to any user with a Cline account" — a sign-in with Google, GitHub or email; the docs ask for no card. No figure is published for the quota. It is counted per model and per day, which is how Cline's own clients word the stop — "You've reached today's free usage limit for this model". The lane is the free list the model picker reads, keyless at api.cline.bot. Early on 2026-09-14 it held six ids: cline-free/muse-spark-1.3-contributor, deepseek/deepseek-v4-flash, z-ai/glm-5.3-flash, cline-free/solar-pro4, cline-free/longcat-2.0 and poolside/laguna-s-2.1:free; at 20:57 UTC the same day it held five, cline-free/deepseek-v4.1-flash standing where DeepSeek V4 Flash had been and LongCat 2.0 gone. It turns over, "on a rotating, limited-time basis": the screenshots Cline committed to its docs on 2026-07-29 show GLM-5.2, Laguna S 2.1, DeepSeek V4 Flash and Step 3.7 Flash, and its 2026-08-11 post put Nemotron 3.5 Lightning in the FREE dropdown, yet by the evening of 2026-09-14 Laguna S 2.1 was the only one of them still in the lane, and it is the only family in the Models column. Two limits the free-models page states outright: "Free model usage is not supported through the Cline API. Free models are only available in the Cline IDE Extension and CLI" — the API guide's own "Try a Free Model" example, minimax/minimax-m2.5, is a metered row in the provider's catalog — and "Free model usage may be used to help improve model performance and quality"

## Connect

No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the `free` lane of the models document at <https://api.cline.bot/api/v1/ai/cline/recommended-models>, every listed family required in that lane
- Source: <https://docs.cline.bot/getting-started/free-models>
- Source: <https://api.cline.bot/api/v1/ai/cline/recommended-models>
- Source: <https://docs.cline.bot/getting-started/cline-provider>

## History

- *next scheduled run* — Free models changed: dropped deepseek-v4-flash
- `2026-09-14` — Added to the list: Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK
- `2026-07-19` — Delisted
- `2026-07-19` — Added to the list: Open-source (Apache-2.0) autonomous coding agent for VS Code, JetBrains and CLI; BYOK — pair with free-tier provider keys or local models for zero model cost

---

Generated from `registry.yaml` on 2026-09-16 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
