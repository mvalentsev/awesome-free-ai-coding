---
layout: default
title: 'Cline free tier: limits, free models, verified 2026-09-24'
description: Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK. "Cline periodically offers free model promotions that let…
permalink: /providers/cline/
last_modified_at: 2026-09-26
crumb: Cline
---

{% raw %}

# Cline free tier

🤖 Coding agents & CLIs · no card · provisional — added on 2026-09-14, a regular row from the first probe it passes on or after 2026-09-28 · **live** — last verified by a probe on 2026-09-24 · [cline.bot](https://cline.bot) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK

## Free models

[`muse-spark-1.3-contributor`](https://mvalentsev.github.io/awesome-free-ai-coding/models/muse-spark-1.3-contributor/)

## Limits, in the vendor's words

"Cline periodically offers free model promotions that let you try select models at no cost, up to a limited usage quota", and "Free models are available to any user with a Cline account" — a sign-in with Google, GitHub or email, no card. No figure is published; the quota is counted per model and per day, which is how Cline's clients word the stop: `You've reached today's free usage limit for this model`. The lane is the free list the model picker reads, keyless at api.cline.bot, and it turns over "on a rotating, limited-time basis" — ids change within a day, so a model joins the Models column only after two weeks in the lane. The free-models page states two limits outright: "Free model usage is not supported through the Cline API. Free models are only available in the Cline IDE Extension and CLI", and "Free model usage may be used to help improve model performance and quality". Read 2026-09-14

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://cline.bot/tos), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Free model usage may be used to help improve model performance and quality.” ([source](https://docs.cline.bot/getting-started/free-models)).

## Connect

- No API endpoint to paste: this row is a tool you install or sign in to.
- In Cline's own model list: `stealth/pixel-canary`, `stealth/space-bunny-alpha`, `cline-free/mimo-v2.6-flash`, `cline-free/deepseek-v4.1-flash`, `cline-free/gemini-3.8-flash`, `cline-free/muse-spark-1.3-contributor`

## Evidence

- Probe: the `free` lane of the models document at <https://api.cline.bot/api/v1/ai/cline/recommended-models>, each listed family checked in that lane
- Source: <https://docs.cline.bot/getting-started/free-models>
- Source: <https://api.cline.bot/api/v1/ai/cline/recommended-models>
- Source: <https://docs.cline.bot/getting-started/cline-provider>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-24` — Free models changed: added muse-spark-1.3-contributor
- `2026-09-23` — Free models changed: dropped laguna-s-2.1
- `2026-09-14` — Free models changed: dropped deepseek-v4-flash
- `2026-09-14` — Added: Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK
- `2026-07-19` — Delisted
- `2026-07-19` — Added: Open-source (Apache-2.0) autonomous coding agent for VS Code, JetBrains and CLI; BYOK — pair with free-tier provider keys or local models for zero model cost

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
