---
layout: default
title: 'Yolo-Auto free tier: limits, free models, verified 2026-09-14'
description: One model, Qwen3.8-27B in FP8, served on the vendor's own flat-rate API for coding agents; the free plan is a small daily allowance with no card. "Start free → 15 requests/day · no card required" on the home page, and on the plan card "No card required, free forever" and "Free forever. No card…
permalink: /providers/yolo-auto/
---

{% raw %}

# Yolo-Auto

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-14 · [yolo-auto.com](https://yolo-auto.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

One model, Qwen3.8-27B in FP8, served on the vendor's own flat-rate API for coding agents; the free plan is a small daily allowance with no card

## Free models

`qwen3.8`

## Limits, in the vendor's words

"Start free → 15 requests/day · no card required" on the home page, and on the plan card "No card required, free forever" and "Free forever. No card required and no trial period" — at 128K context and "Designed for 1 coding agent", against $19/mo Builder and $39/mo Pro. Fifteen requests is a handful of agent turns, which is why this row sits at the bottom of its section: the same model answers keyless on OVHcloud and on Hetzner's free lane with more headroom. The terms (last updated 2026-08-22) close the obvious workaround — "You may not create, control, fund, coordinate, or use multiple accounts ... to combine capacity" — and sign-in is through Google, GitHub or Discord. Prompt and response bodies are "not routinely retained", the home page says. Read 2026-09-14

## Connect

- Base URL: `https://yolo-auto.com/v1`
- Key: `YOLO_AUTO_API_KEY` — get one at <https://yolo-auto.com/app>
- Callable ids: `qwen3.8-27b`
- Note: qwen3.8-27b is the only model id; /v1/models and /v1/usage answer 401 without a key, and the free plan's context is 128K where Pro's is 256K

## Evidence

- Probe: the page at <https://yolo-auto.com/>, anchored on `15 requests/day`, `No card required, free forever`
- Source: <https://yolo-auto.com/>
- Source: <https://yolo-auto.com/pricing>
- Source: <https://yolo-auto.com/terms>

## History

- *next scheduled run* — Added to the list: One model, Qwen3.8-27B in FP8, served on the vendor's own flat-rate API for coding agents; the free plan is a small daily allowance with no card

---

Generated from `registry.yaml` on 2026-09-14 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
