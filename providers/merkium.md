---
layout: default
title: 'Merkium free tier: limits, free models, verified 2026-11-09'
description: Independent model developer with a free OpenAI-compatible API and chat service; current API models have no per-request or per-token charge. Sign in and create a free API key in the Console; no card or billing step. Space requests at least two seconds apart, including each step of a tool-call round…
permalink: /providers/merkium/
last_modified_at: 2026-11-09
crumb: Merkium
---

{% raw %}

# Merkium free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-05, a regular row from the first probe it passes on or after 2026-11-19 · **live** — last verified by a probe on 2026-11-09 · [merkium.nl](https://www.merkium.nl) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Independent model developer with a free OpenAI-compatible API and chat service; current API models have no per-request or per-token charge

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

30 requests/minute per key

Sign in and create a free API key in the Console; no card or billing step. Space requests at least two seconds apart, including each step of a tool-call round trip, and honor Retry-After on HTTP 429. The current models are advertised as permanently free; later models may be paid. The public terms page is a review draft without an effective date.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.merkium.nl/docs/pricing), read 2026-11-05).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Your conversations are never used to train, fine-tune or evaluate Merkium models.” ([source](https://www.merkium.nl/privacy)).

## Connect

- Base URL: `https://chat.merkium.nl/api/v1`
- Key: `MERKIUM_API_KEY` — get one at <https://chat.merkium.nl>
- Callable ids: `ceres-1.0`, `ceres-1.0-pro`, `ganymede-1.1`, `pluto-1.1-flash`, `pluto-1.1-pro`, `pluto-1.2-flash`, `pluto-1.2-pro`
- Note: Create a key in the Console API tab. Set the OpenAI-compatible base URL verbatim; use /chat/completions for chat, streaming and tool calls. Model listing also requires the key.

Try it from your terminal with your key in `MERKIUM_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://chat.merkium.nl/api/v1/chat/completions \
  -H "Authorization: Bearer $MERKIUM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"ganymede-1.1","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.merkium.nl/docs/pricing>, anchored on `free to use through the API, permanently`, `not need a credit card or a billing account`
- Source: <https://www.merkium.nl/docs>
- Source: <https://www.merkium.nl/docs/pricing>
- Source: <https://www.merkium.nl/docs/authentication>
- Source: <https://www.merkium.nl/docs/models>
- Source: <https://www.merkium.nl/docs/rate-limits>
- Source: <https://www.merkium.nl/privacy>
- Source: <https://www.merkium.nl/legal>
- Source: <https://www.merkium.nl/research/ganymede-1-1-technical-report>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-05` — Added: Independent model developer with a free OpenAI-compatible API and chat service; current API models have no per-request or per-token charge

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
