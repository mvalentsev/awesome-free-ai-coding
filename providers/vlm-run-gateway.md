---
layout: default
title: 'VLM Run Gateway free tier: limits, free models, verified 2026-09-17'
description: 'OpenAI-compatible gateway for vision and language models whose models on VLM Run''s own GPUs, Qwen3.8 27B among them, answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha. The authentication page says it plainly: "The VLM Run Gateway serves anonymous callers on a…'
permalink: /providers/vlm-run-gateway/
---

{% raw %}

# VLM Run Gateway

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-17 · [vlm.run](https://vlm.run) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs, Qwen3.8 27B among them, answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha

## Free models

`qwen3.8-27b`

## Limits, in the vendor's words

The authentication page says it plainly: "The VLM Run Gateway serves anonymous callers on a small free quota, keyed by client IP", and "Every GPU-served model is public and reachable anonymously", while "The routed models carry the paid access tier". The rate-limit table gives the anonymous tier "10/min, 30/hr, 100/day" per client IP, the three windows stacking, against 240 a minute with a key. The FAQ calls the gateway alpha, with a model catalog kept intentionally small: its chat models on VLM Run GPUs are Qwen3.8 27B and Qwen3.5 0.8B, beside OCR, embedding and speech models. The published request schema has no tools field, yet a keyless call carrying one tool was answered with a tool call on 2026-09-17. The operator is Autonomi AI Inc.; its terms render only in a browser. Read 2026-09-17

## Connect

- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `qwen/qwen3.8-27b`
- Note: no key: a call with no Authorization header is anonymous, and `Bearer vlmrun` is the explicit anonymous form for a client that needs a non-empty key; 10 a minute, 30 an hour and 100 a day per IP. qwen/qwen3.5-0.8b is the other chat model on VLM Run's GPUs, and the routed ids in the same catalog, Kimi K3 among them, answer `403 model_not_entitled` without a paid organization

## Evidence

- Probe: the page at <https://docs.vlm.run/gateway/models>, anchored on `qwen/qwen3.8-27b`; ids checked in <https://gateway.vlm.run/v1/openai/models>
- Source: <https://docs.vlm.run/gateway/authentication>
- Source: <https://docs.vlm.run/gateway/rate-limits.md>
- Source: <https://docs.vlm.run/gateway/faq.md>
- Source: <https://docs.vlm.run/gateway/models>
- Source: <https://docs.vlm.run/gateway/introduction>

## History

- *next scheduled run* — Added to the list: OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs, Qwen3.8 27B among them, answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha

---

Generated from `registry.yaml` on 2026-09-19 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
