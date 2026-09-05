---
layout: default
title: 'NVIDIA NIM (build.nvidia.com) free tier: limits, free models, verified 2026-09-03'
description: 'Free hosted NIM endpoints for 100+ models via the free NVIDIA Developer Program (OpenAI-compatible at integrate.api.nvidia.com/v1). Free to start with no card — the account is gated by phone/business-email verification, and access is metered in API credits rather than left open: NVIDIA staff…'
permalink: /providers/nvidia-nim/
---

{% raw %}

# NVIDIA NIM (build.nvidia.com)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [build.nvidia.com](https://build.nvidia.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free hosted NIM endpoints for 100+ models via the free NVIDIA Developer Program (OpenAI-compatible at integrate.api.nvidia.com/v1)

## Free models

`nemotron`

## Limits, in the vendor's words

Free to start with no card — the account is gated by phone/business-email verification, and access is metered in API credits rather than left open: NVIDIA staff describe the catalog as "a trial experience of NVIDIA NIM limited to 5000 free API credits", 1000 granted on sign-up. That answer is from 2024 and NVIDIA publishes no current figure; reports since put the ceiling at a ~40 req/min rate limit instead. Production use needs NVIDIA AI Enterprise either way. The ids move under the row without the offer changing: deepseek-v4-flash was re-dated deepseek-v4-flash-0731 and meta/llama-4-maverick-17b-128e-instruct left with every other Llama 4 (read 2026-08-28 — muse-glimmer-30b is the open Meta row hosted in their place), and on 2026-09-02 nemotron-3-nano-30b-a3b had become nemotron-nano-3-30b-a3b, the same model with the version moved into the middle of its name rather than the nemotron-3-nano-omni-30b-a3b-reasoning the catalog carries beside it

## Connect

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `deepseek-ai/deepseek-v4-flash-0731`, `nvidia/nemotron-nano-3-30b-a3b`, `meta/muse-glimmer-30b`
- Note: the catalog endpoint answers unauthenticated, which is what the probe reads — it confirms NVIDIA still hosts these models, not that your account still has credits to call them with, and it publishes no price field at all, so hosting is the only question it can answer

## Evidence

- Probe: the models catalog at <https://integrate.api.nvidia.com/v1/models>
- Source: <https://build.nvidia.com/explore/discover>
- Source: <https://forums.developer.nvidia.com/t/api-credits-for-build-nvidia-com/306633>

## History

- `2026-07-27` — Free models changed: dropped llama-4
- `2026-07-19` — Added to the list: Free hosted NIM endpoints for 100+ models via the free NVIDIA Developer Program (OpenAI-compatible at integrate.api.nvidia.com/v1)

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
