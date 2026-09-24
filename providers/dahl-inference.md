---
layout: default
title: 'Dahl Inference free tier: limits, free models, verified 2026-09-21'
description: 'An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account. The docs: "100 million tokens as a gift at signup", paid…'
permalink: /providers/dahl-inference/
---

{% raw %}

# Dahl Inference

🎁 Trials (no card when possible) · no card · provisional — added on 2026-09-21, a regular row from the first probe it passes on or after 2026-10-05 · **live** — last verified by a probe on 2026-09-21 · [inference.dahl.global](https://inference.dahl.global) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account

## Free models

`glm-5.3-flash`, `deepseek-v4-flash`, `minimax-m2.7`

## Limits, in the vendor's words

The docs: "100 million tokens as a gift at signup", paid into the account's pool rather than onto a key — a new key holds nothing and answers 402 until tokens are allocated to it at /account. The account is a username and a 32-character fingerprint, "Save the fingerprint shown once — it is the password", and "There is no email recovery by design". "Creating extra keys does not grant more free tokens", the terms forbid automating account creation "to harvest promotional allocations" and keep the right to "end discretionary free access", and past the grant the only top-up is crypto, "priced around $0.03 per 1M tokens". Requests are routed to "independent operators within a decentralised network" under terms from FROMZERO OÜ, an Estonian company. Read 2026-09-21

## Connect

- Base URL: `https://inference.dahl.global/v1`
- Key: `DAHL_INFERENCE_API_KEY` — get one at <https://inference.dahl.global/account>
- Callable ids: `zai-org/GLM-5.3-Flash`, `deepseek-ai/DeepSeek-V4-Flash-0731`, `MiniMaxAI/MiniMax-M2.7`
- Note: ids are the keyless catalog's at inference.dahl.global/v1/models, 2026-09-21; they rotate with the network's capacity, and the models page already lists Kimi K2.6 and GLM-5.2 as retired. A key answers 402 until tokens are moved to it from the account pool

## Evidence

- Probe: the page at <https://inference.dahl.global/docs/tokens/>, anchored on `100 million tokens as a gift at signup`; ids checked in <https://inference.dahl.global/v1/models>
- Source: <https://inference.dahl.global/docs/tokens/>
- Source: <https://inference.dahl.global/docs/authentication/>
- Source: <https://inference.dahl.global/docs/models/>
- Source: <https://inference.dahl.global/terms/>

## History

- *next scheduled run* — Added to the list: An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
