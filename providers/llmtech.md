---
layout: default
title: 'LLM Tech free tier: limits, free models, verified 2026-09-21'
description: 'EU provider of one model, Qwen3.8 27B, whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 2 concurrent requests, tool calls included, no account. The quickstart prints the key itself: "Shared and rate-limited: 2 concurrent requests and 2M tokens per day per…'
permalink: /providers/llmtech/
---

{% raw %}

# LLM Tech

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-21 · [llmtech.eu](https://llmtech.eu) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU provider of one model, Qwen3.8 27B, whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 2 concurrent requests, tool calls included, no account

## Free models

`qwen3.8-27b`

## Limits, in the vendor's words

The quickstart prints the key itself: "Shared and rate-limited: 2 concurrent requests and 2M tokens per day per address, counted across prompt and completion and reset at 00:00 UTC. Enough to evaluate, not enough to run on." A personal key — "64 concurrent and no daily limit" — is paid per token and asked for by email. The model is the NVFP4 build of Qwen3.8-27B with a 262,144-token context, tool calling, structured outputs and image input. Prompts and completions are held in "volatile memory only — never persisted" and never trained on; metadata, the source IP among it, is kept 13 months as billing evidence. The operator is one person, Artem Burei, trading as a sole proprietorship in Poland, serving since 22 August 2026 from GPUs in Italy behind an edge in Germany. Read 2026-09-18

## What happens to what you send

What you send is not used to train models. In the vendor's words: “We do not use your inputs or outputs to train, fine-tune, or evaluate any model, and we do not provide them to third parties for that purpose.” ([source](https://llmtech.eu/privacy)).

## Connect

- Base URL: `https://api.llmtech.eu/v1`
- Key: `LLMTECH_API_KEY` — no account needed: the vendor prints one for anyone at <https://llmtech.eu/docs/>, `lt-trial-ba1ef28c6d32ed6980678d8d`
- Callable ids: `nvidia/Qwen3.8-27B-NVFP4`
- Note: reasoning is adaptive: `chat_template_kwargs: {"enable_thinking": false}` turns it off, and `reasoning_effort` takes low, medium or xhigh. Cline lists LLM Tech among its built-in providers; Claude Code "needs a translating proxy", LiteLLM in the vendor's own example

## Evidence

- Probe: the page at <https://llmtech.eu/docs/>, anchored on `2 concurrent requests and 2M tokens per day per address`; ids checked in <https://api.llmtech.eu/v1/models>
- Source: <https://llmtech.eu/docs/>
- Source: <https://llmtech.eu/agents/>
- Source: <https://llmtech.eu/security/>
- Source: <https://llmtech.eu/about/>
- Source: <https://api.llmtech.eu/v1/models>

## History

- `2026-09-21` — Added to the list: EU provider of one model, Qwen3.8 27B, whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 2 concurrent requests, tool calls included, no account

---

Generated from `registry.yaml` on 2026-09-23 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
