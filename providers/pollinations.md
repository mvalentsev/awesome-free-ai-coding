---
layout: default
title: 'Pollinations.AI free tier: limits, free models, verified 2026-09-03'
description: Open GenAI text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai). Anonymous 1 req/15s (no signup). The keyless catalog publishes exactly one model and tags it with the tier it belongs to — "openai-fast", described as "GPT-OSS 20B Reasoning LLM (OVH)", tier "anonymous",…
permalink: /providers/pollinations/
---

{% raw %}

# Pollinations.AI

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [pollinations.ai](https://pollinations.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open GenAI text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai)

## Free models

`gpt-oss`

## Limits, in the vendor's words

Anonymous 1 req/15s (no signup). The keyless catalog publishes exactly one model and tags it with the tier it belongs to — "openai-fast", described as "GPT-OSS 20B Reasoning LLM (OVH)", tier "anonymous", aliased to openai / gpt-oss / gpt-oss-20b. The documented free registration that lifts the rate to 1 req/5s is unreachable — its host stopped resolving on 2026-08-14

## Connect

- Base URL: `https://text.pollinations.ai/openai`
- Key: none — the lane is anonymous
- Note: anonymous works and needs no key. The optional token that raises the rate limit has no working signup — auth.pollinations.ai, the host the vendor's own APIDOCS still sends you to, stopped resolving (NXDOMAIN from both Cloudflare and Google resolvers, 2026-08-14)

## Evidence

- Probe: the page at <https://text.pollinations.ai/models>, anchored on `"tier":"anonymous"`, `GPT-OSS 20B`
- Source: <https://text.pollinations.ai/models>
- Source: <https://raw.githubusercontent.com/pollinations/pollinations/master/APIDOCS.md>

## History

- `2026-07-19` — Added to the list: Open GenAI text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai)

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
