---
layout: default
title: 'Blue Claw Network free tier: limits, free models, verified 2026-09-24'
description: 'OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start. The home page: "Every new account starts with a $5 welcome credit. After that, you run on prepaid USD…'
permalink: /providers/blue-claw/
---

{% raw %}

# Blue Claw Network

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [blueclaw.network](https://blueclaw.network) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The home page: "Every new account starts with a $5 welcome credit. After that, you run on prepaid USD credits — buy what you use, no subscriptions." and "No credit card required to start." Sign-in is a six-digit code sent by email. No public page names the models or their prices — "Live per-model pricing is on the Models page in the console" — and the quick start calls the model auto. Calls go to "a network of independent GPU operators", partners running Livepeer orchestrators among them; Blue Claw "does not log prompts, inputs, or outputs by default" and offers "No TEE, E2EE, or confidential-compute guarantee yet". No page gives the credit an expiry. Read 2026-09-17

## Connect

- Base URL: `https://openai.blueclaw.network/v1`
- Key: `BLUE_CLAW_API_KEY` — get one at <https://portal.blueclaw.network/>
- Callable ids: `auto`
- Note: auto is the quick start's model and keys start with bc_; /v1/models answers 401 without a key, and the models behind auto are listed only in the console

## Evidence

- Probe: the page at <https://blueclaw.network/>, anchored on `Every new account starts with a $5 welcome credit`, `No credit card required to start`
- Source: <https://blueclaw.network/>
- Source: <https://blueclaw.network/quickstart>
- Source: <https://blueclaw.network/how-it-works>
- Source: <https://blueclaw.network/operators>

## History

Each line is a change to what this page publishes, dated the day the list recorded it, in UTC.

- `2026-09-17` — Added: OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
