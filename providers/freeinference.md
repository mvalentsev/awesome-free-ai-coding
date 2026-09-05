---
layout: default
title: 'FreeInference (Harvard SEAS) free tier: limits, free models, verified 2026-09-05'
description: 'Harvard SEAS''s MadSys Lab serving frontier open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup. No quota figure is published: the landing page…'
permalink: /providers/freeinference/
---

{% raw %}

# FreeInference (Harvard SEAS)

🔌 LLM APIs with free tier · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-05 · [freeinference.org](https://freeinference.org) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Harvard SEAS's MadSys Lab serving frontier open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup

## Free models

`deepseek-v4-flash`, `glm-5.1`, `glm-5.3-flash`, `minimax-m3`, `qwen3.6`

## Limits, in the vendor's words

No quota figure is published: the landing page says "Free to use. No credit card required. Generous quota for research and prototyping", and the terms (last updated 2026-06-20) say "Quotas, rate limits, model access, and usage limits may change based on usage, demand, infrastructure capacity, abuse prevention, operational needs, and individual or aggregate activity"; a 429 is the rate limit and a 503 means "The upstream pool is temporarily exhausted". The framing is the restriction: "FreeInference for open-source, research and education ... free for the research community", and the terms call it "an experimental research service that provides access to hosted and routed large language model inference for experimentation and related development work". Prompts are not private — "All prompts and responses may be logged for research purposes" and "sanitized prompts and responses, usage statistics, and routing metrics — may be published or open-sourced". The models page splits the catalog in two: "Free accounts can use models marked Free. Models marked Pro require a Pro-enabled key" — seven chat ids Free (glm-5.1, glm-5.3-flash, deepseek-v4-flash, minimax-m3, minimax-m2.5, qwen3.6-35b, diffusiongemma) and three Pro (glm-5.2, glm-5.3, kimi-k2.7-code), read 2026-09-05

## Connect

- Base URL: `https://freeinference.org/v1`
- Key: `FREEINFERENCE_API_KEY` — get one at <https://freeinference.org>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://freeinference.org/anthropic`
- Callable ids: `deepseek-v4-flash`, `qwen3.6-35b`, `diffusiongemma`
- Note: the three ids are the chat rows the keyless catalog at freeinference.org/v1/models returned on 2026-09-05 (bge-m3, the fourth, is an embedding model); the docs mark four more chat ids Free — glm-5.1, glm-5.3-flash, minimax-m3, minimax-m2.5 — and say the full list is what an authenticated GET /v1/models returns, so those stay out of the generated configs until a keyed read confirms them. The catalog prints upstream reference prices beside every row ($0.44/$1.32 per 1M on deepseek-v4-flash), which the docs describe as accounting, "not fees charged by FreeInference to users". The same key serves an Anthropic-format endpoint at https://freeinference.org/anthropic — the docs set ANTHROPIC_BASE_URL to it for Claude Code, with deepseek-v4-flash behind the Opus and Sonnet aliases and qwen3.6-35b behind Haiku. The terms say requests "may route across local inference servers and remote model providers": by the catalog's owned_by field the listed ids run on the lab's own sglang and vllm servers, while DeepSeek calls are accounted at DeepSeek's upstream rate

## Evidence

- Probe: the page at <https://doc.freeinference.org/models>, anchored on `free accounts can use models marked`; ids checked in <https://freeinference.org/v1/models>
- Source: <https://doc.freeinference.org/models>
- Source: <https://doc.freeinference.org/claude-code.html>
- Source: <https://freeinference.org/terms>
- Source: <https://freeinference.org/v1/models>

## History

No recorded event yet — the first scheduled run after a row lands writes its `added` line.

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
