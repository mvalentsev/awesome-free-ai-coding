---
layout: default
title: 'Dahl Inference free tier: limits, free models, verified 2026-10-05'
description: An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account. Signup tokens enter the account pool; a new key starts…
permalink: /providers/dahl-inference/
last_modified_at: 2026-10-05
crumb: Dahl Inference
---

{% raw %}

# Dahl Inference free tier

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-10-05 · [inference.dahl.global](https://inference.dahl.global) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

100,000,000 tokens once per account

Signup tokens enter the account pool; a new key starts empty and returns 402 until tokens are allocated at /account. Extra keys do not grant extra tokens. Save the fingerprint shown once: it is the password, with no email recovery. Terms prohibit automated account creation to harvest grants and permit ending discretionary free access. Further top-ups are crypto. Requests go to independent decentralized operators under FROMZERO OÜ's terms.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://inference.dahl.global/terms/), read 2026-09-26).

## Connect

- Base URL: `https://inference.dahl.global/v1`
- Key: `DAHL_INFERENCE_API_KEY` — get one at <https://inference.dahl.global/account>
- Callable ids: `zai-org/GLM-5.3-Flash`, `deepseek-ai/DeepSeek-V4-Flash-0731`, `MiniMaxAI/MiniMax-M2.7`
- Note: Model IDs rotate with network capacity. Allocate tokens from the account pool to each key at /account; a key without allocated tokens answers `402`.

Try it from your terminal with your key in `DAHL_INFERENCE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://inference.dahl.global/v1/chat/completions \
  -H "Authorization: Bearer $DAHL_INFERENCE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"zai-org/GLM-5.3-Flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://inference.dahl.global/docs/tokens/>, anchored on `100 million tokens as a gift at signup`; ids checked in <https://inference.dahl.global/v1/models>
- Source: <https://inference.dahl.global/docs/tokens/>
- Source: <https://inference.dahl.global/docs/authentication/>
- Source: <https://inference.dahl.global/docs/models/>
- Source: <https://inference.dahl.global/terms/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: dropped deepseek-v4-flash, glm-5.3-flash, minimax-m2.7
- `2026-09-21` — Added: An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account

---

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
