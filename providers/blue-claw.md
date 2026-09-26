---
layout: default
title: 'Blue Claw Network free tier: limits, free models, verified 2026-09-24'
description: 'OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start. The home page: "Every new account starts with a $5 welcome credit. After that, you run on prepaid USD…'
permalink: /providers/blue-claw/
last_modified_at: 2026-09-26
crumb: Blue Claw Network
---

{% raw %}

# Blue Claw Network free tier

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-17, a regular row from the first probe it passes on or after 2026-10-01 · **live** — last verified by a probe on 2026-09-24 · [blueclaw.network](https://blueclaw.network) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

The home page: "Every new account starts with a $5 welcome credit. After that, you run on prepaid USD credits — buy what you use, no subscriptions." and "No credit card required to start." Sign-in is a six-digit code sent by email. No public page names the models or their prices — "Live per-model pricing is on the Models page in the console" — and the quick start calls the model auto. Calls go to "a network of independent GPU operators", partners running Livepeer orchestrators among them; Blue Claw "does not log prompts, inputs, or outputs by default" and offers "No TEE, E2EE, or confidential-compute guarantee yet". No page gives the credit an expiry. Read 2026-09-17

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://blueclaw.network/terms), read 2026-09-26).

## Connect

- Base URL: `https://openai.blueclaw.network/v1`
- Key: `BLUE_CLAW_API_KEY` — get one at <https://portal.blueclaw.network/>
- Callable ids: `auto`
- Note: auto is the quick start's model and keys start with bc_; /v1/models answers 401 without a key, and the models behind auto are listed only in the console

Try it from your terminal with your key in `BLUE_CLAW_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://openai.blueclaw.network/v1/chat/completions \
  -H "Authorization: Bearer $BLUE_CLAW_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"auto","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://blueclaw.network/>, anchored on `Every new account starts with a $5 welcome credit`, `No credit card required to start`
- Source: <https://blueclaw.network/>
- Source: <https://blueclaw.network/quickstart>
- Source: <https://blueclaw.network/how-it-works>
- Source: <https://blueclaw.network/operators>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
