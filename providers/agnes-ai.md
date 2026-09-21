---
layout: default
title: 'Agnes AI free tier: limits, free models, verified 2026-09-21'
description: 'Agnes AI''s own models behind an OpenAI-compatible API, with its Flash text models charged at zero today and image generation free beside them. "Is the API free to use? Yes. Our core AI models are free to use indefinitely", the FAQ says, and the pricing page shows the mechanism: agnes-2.5-flash…'
permalink: /providers/agnes-ai/
---

{% raw %}

# Agnes AI

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [agnes-ai.com](https://agnes-ai.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Agnes AI's own models behind an OpenAI-compatible API, with its Flash text models charged at zero today and image generation free beside them

## Free models

`agnes-3.0-flash`, `agnes-2.5-flash`

## Limits, in the vendor's words

"Is the API free to use? Yes. Our core AI models are free to use indefinitely", the FAQ says, and the pricing page shows the mechanism: agnes-2.5-flash and agnes-3.0-flash list at $0.05 in / $0.15 out per 1M and are charged $0 — "Cached input, input tokens, and output tokens are currently free for agnes-2.5-flash and agnes-3.0-flash" — while agnes-2.5-pro bills $0.45/$0.90 and the pro beta $0.10/$0.30. The page is candid that the zero is a current price rather than a contract: "Promotional end dates are subject to Agnes AI platform announcements and your account bill". The ceiling is a rate, not a quota: a key that is neither on a paid Token Plan nor enterprise-verified gets 30 requests a minute allowed and 20 effective on text models (Token Plan FAQ, effective 2026-06-22), and no daily figure is published. Image models are free at every resolution too. The terms are governed by Singapore law. The docs live on wiki.agnes-ai.com. Read 2026-09-14

## Connect

- Base URL: `https://apihub.agnes-ai.com/v1`
- Key: `AGNES_AI_API_KEY` — get one at <https://platform.agnes-ai.com>
- Callable ids: `agnes-3.0-flash`, `agnes-2.5-flash`
- Note: the quickstart sends its chat completion to apihub.agnes-ai.com/v1/chat/completions with a Bearer key from the Agnes AI Platform dashboard; free and Token Plan keys draw on separate limit pools, and creating more keys of one type does not stack RPM. Agnes AI's China station (agnes-ai.cn) prices the same two Flash models at ¥0 (当前均免费, all currently free) and serves them from api.agnes-ai.cn/v1

## Evidence

- Probe: the page at <https://wiki.agnes-ai.com/en/docs/pricing>, anchored on `Cached input, input tokens, and output tokens are currently free for`, `agnes-3.0-flash`
- Source: <https://wiki.agnes-ai.com/en/docs/pricing>
- Source: <https://wiki.agnes-ai.com/en/docs/faqs>
- Source: <https://wiki.agnes-ai.com/en/docs/tokenplan>
- Source: <https://wiki.agnes-ai.cn/zh-Hans/docs/pricing>

## History

- `2026-09-14` — Added to the list: Agnes AI's own models behind an OpenAI-compatible API, with its Flash text models charged at zero today and image generation free beside them

---

Generated from `registry.yaml` on 2026-09-21 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
