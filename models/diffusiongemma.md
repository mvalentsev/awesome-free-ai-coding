---
layout: default
title: 'diffusiongemma free: 1 provider, limits and ids, provider probes 2026-11-12'
description: diffusiongemma is served free by VLM Run Gateway. It asks for no card; it answers with no account at all. Each one's limits in the vendor's words, the ids to call and the provider's last probe date.
permalink: /models/diffusiongemma/
last_modified_at: 2026-11-12
crumb: diffusiongemma
---

{% raw %}

# Where diffusiongemma is free

**One row on the list serves `diffusiongemma` free:** VLM Run Gateway. It asks for no card; it answers with no account at all. The provider's last scheduled probe was on 2026-11-12; its offer is rechecked twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [VLM Run Gateway](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vlm-run-gateway/)

🔌 LLM APIs with free tier · no card · last probe 2026-11-12 · listed since 2026-10-09

OpenAI-compatible gateway whose GPU-served vision and language models accept anonymous callers — no signup or key — in beta

> ⚠️ **Does not work as published since [2026-11-05](https://docs.vlm.run/gateway/authentication).** Anonymous requests to `qwen/qwen3.8-27b`, the listed tool-capable model, currently return HTTP 403 asking for an API key. Its anonymous coding-agent connection is unavailable in the current checks; the other listed IDs are ordinary-chat choices.

<details markdown="block">
<summary>Provider-wide limits</summary>

- Limits, in the vendor's words: Anonymous lane: 10 requests/minute; 30 requests/hour; 100 requests/day per IP

GPU-served models are public and anonymous; frontier models require paid access. All three IP windows apply together and are shared by callers behind the same NAT or proxy. The gateway is beta; anonymous access is intended for evaluation. The operator is Autonomi AI Inc.; its terms render in a browser.

</details>

- Base URL: `https://gateway.vlm.run/v1/openai`
- Key: none — the lane is anonymous
- Callable ids: `google/diffusiongemma-26b-a4b-it`

## Rows that listed it before

- [NVIDIA NIM (build.nvidia.com)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/) — listed 2026-09-24 to 2026-11-12
- [FreeInference (Harvard SEAS)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/) — listed 2026-09-24 to 2026-10-26

---

Generated from `registry.yaml` on 2026-11-12 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
