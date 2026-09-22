---
layout: default
title: 'NVIDIA NIM (build.nvidia.com) free tier: limits, free models, verified 2026-09-21'
description: Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible). No card; the API key needs a free NVIDIA Developer Program account verified…
permalink: /providers/nvidia-nim/
---

{% raw %}

# NVIDIA NIM (build.nvidia.com)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-21 · [build.nvidia.com](https://build.nvidia.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible)

## Free models

`kimi-k3`, `nemotron-3-ultra`, `nemotron-3-super`, `laguna-xs-2.1`

## Limits, in the vendor's words

No card; the API key needs a free NVIDIA Developer Program account verified by a code sent to your phone, and the phone step does not take every country. The ceiling is a rate, not credits: NVIDIA's site puts it at "Up to 40 rpm" and "10,000 requests per day", adding that "Rate limits may vary by model and traffic from other users may cause throttling". NVIDIA staff call 40 RPM "the published free-tier cap" that "is not adjustable on a per-account basis"; more throughput takes "an NVIDIA AI Enterprise license or self-hosting the model via the corresponding NIM container". Each model's page states whether its free endpoint is available or deprecated, and NVIDIA renames ids without notice, so copy them from the catalog. Read 2026-09-22

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Your input and output will be recorded to provide you with this trial experience and to improve NVIDIA products and services, including AI models” ([source](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)).

## Connect

- Base URL: `https://integrate.api.nvidia.com/v1`
- Key: `NVIDIA_NIM_API_KEY` — get one at <https://build.nvidia.com>
- Callable ids: `moonshotai/kimi-k3`, `z-ai/glm-5.3`, `z-ai/glm-5.3-flash`, `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3-super-120b-a12b`, `poolside/laguna-xs-2.1`, `google/gemma-4-31b-it`, `meta/muse-glimmer-30b`, `nvidia/nemotron-3.5-lightning-30b-a3b`, `openai/gpt-oss-20b`
- Note: model_ids are chat models whose build.nvidia.com page marks the free endpoint available; the catalog also answers with older ids that have no page and no such mark, and those are left out. The catalog endpoint answers unauthenticated, which is what the probe reads — it confirms NVIDIA still hosts these models, not that your key may call them, and it publishes no price field, so the free mark lives only on each model's page

## Evidence

- Probe: the models catalog at <https://integrate.api.nvidia.com/v1/models>
- Source: <https://build.nvidia.com/explore/discover>
- Source: <https://build.nvidia.com/moonshotai/kimi-k3>
- Source: <https://forums.developer.nvidia.com/t/request-for-nvidia-nim-api-rate-limit-increase-40-200-rpm/369798>

## History

- *next scheduled run* — Free models changed: added kimi-k3, laguna-xs-2.1, nemotron-3-super, nemotron-3-ultra; dropped nemotron
- `2026-07-27` — Free models changed: dropped llama-4
- `2026-07-19` — Added to the list: Free hosted NIM endpoints for 100+ models via the free NVIDIA Developer Program (OpenAI-compatible at integrate.api.nvidia.com/v1)

---

Generated from `registry.yaml` on 2026-09-22 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
