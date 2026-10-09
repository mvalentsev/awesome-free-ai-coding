---
layout: default
title: 'Yolo-Auto free tier: limits, free models, verified 2026-10-08'
description: 'One open-weight Qwen model served on the vendor''s own flat-rate API for coding agents; the free plan is 15 requests a week with no card. Free models: qwen3.8-flash. No card. The vendor calls the Free tier both free forever and for testing. It runs the model-serving stack rather than reselling…'
permalink: /providers/yolo-auto/
last_modified_at: 2026-10-08
crumb: Yolo-Auto
---

{% raw %}

# Yolo-Auto free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [yolo-auto.com](https://yolo-auto.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One open-weight Qwen model served on the vendor's own flat-rate API for coding agents; the free plan is 15 requests a week with no card

## Free models

[`qwen3.8-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-flash/)

## Limits, in the vendor's words

15 requests/week per account. Resets Monday at 00:00 UTC.

No card. The vendor calls the Free tier both free forever and for testing. It runs the model-serving stack rather than reselling another API. Sign in through Google, GitHub or Discord; multiple accounts may not combine capacity. Prompt and response bodies are not stored or retained.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://yolo-auto.com/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Your prompts and responses are not used for model training.” ([source](https://yolo-auto.com/pricing)).

## Connect

- Base URL: `https://yolo-auto.com/v1`
- Key: `YOLO_AUTO_API_KEY` — get one at <https://yolo-auto.com/app>
- Callable ids: `qwen3.8-flash`
- Note: qwen3.8-flash is the Free plan's model; qwen3.8-27b remains accepted for existing client configurations. The yolo route is paid-only and its target can change. /v1/models and /v1/usage require a key. Free context is 128K tokens, versus Pro's 256K.

Try it from your terminal with your key in `YOLO_AUTO_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://yolo-auto.com/v1/chat/completions \
  -H "Authorization: Bearer $YOLO_AUTO_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3.8-flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://yolo-auto.com/>, anchored on `15 free requests a week`, `No card required, free forever`
- Source: <https://yolo-auto.com/>
- Source: <https://yolo-auto.com/pricing>
- Source: <https://yolo-auto.com/models>
- Source: <https://yolo-auto.com/docs>
- Source: <https://yolo-auto.com/free-llm-api>
- Source: <https://yolo-auto.com/about>
- Source: <https://yolo-auto.com/terms>
- Source: <https://huggingface.co/Qwen/Qwen3.8-Flash-Next>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-16` — Free models changed: added qwen3.8-flash; dropped qwen3.8
- `2026-09-14` — Added: One model, Qwen3.8-27B in FP8, served on the vendor's own flat-rate API for coding agents; the free plan is a small daily allowance with no card

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
