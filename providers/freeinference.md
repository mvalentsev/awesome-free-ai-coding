---
layout: default
title: 'FreeInference (Harvard SEAS) free tier: limits, free models, verified 2026-09-24'
description: 'Harvard SEAS''s MadSys Lab serving open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup. No quota figure is published: the landing page says "Free…'
permalink: /providers/freeinference/
---

{% raw %}

# FreeInference (Harvard SEAS)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [freeinference.org](https://freeinference.org) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Harvard SEAS's MadSys Lab serving open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

## Free models

`deepseek-v4-flash`, `glm-5.1`, `glm-5.3-flash`, `minimax-m3`, `qwen3.6`, `minimax-m2.5`, `diffusiongemma`

## Limits, in the vendor's words

No quota figure is published: the landing page says "Free to use", "No credit card required" and "Generous quota for research and prototyping", and the terms say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity". It is "an experimental research service", and prompts are not private: "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05

## Connect

- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `deepseek-v4-flash`, `qwen3.6-35b`, `diffusiongemma`
- Note: the three ids are the chat rows the keyless catalog at freeinference.org/v1/models returned on 2026-09-05 (bge-m3, the fourth, is an embedding model); the docs mark four more chat ids Free, which stay out of the generated configs until a keyed read confirms them. The catalog's prices are upstream reference accounting, "not fees charged by FreeInference to users". The same key serves https://freeinference.org/anthropic, which the docs give as Claude Code's ANTHROPIC_BASE_URL

## Evidence

- Probe: the page at <https://doc.freeinference.org/models>, anchored on `free accounts can use models marked`; ids checked in <https://freeinference.org/v1/models>
- Source: <https://freeinference.org/>
- Source: <https://doc.freeinference.org/models>
- Source: <https://doc.freeinference.org/claude-code.html>
- Source: <https://freeinference.org/terms>
- Source: <https://freeinference.org/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-24` — Free models changed: added diffusiongemma, minimax-m2.5
- `2026-09-05` — Added: Harvard SEAS's MadSys Lab serving frontier open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

---

Generated from `registry.yaml` on 2026-09-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
