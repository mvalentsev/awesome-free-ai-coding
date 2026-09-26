---
layout: default
title: 'Pollinations.AI free tier: limits, free models, verified 2026-09-24'
description: Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model — GPT-OSS 20B. The keyless catalog publishes exactly one model and tags it with the tier it belongs to — "openai-fast", described as "GPT-OSS 20B Reasoning LLM (OVH)", tier "anonymous", aliased to…
permalink: /providers/pollinations/
last_modified_at: 2026-09-25
---

{% raw %}

# Pollinations.AI

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [pollinations.ai](https://pollinations.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model — GPT-OSS 20B

## Free models

[`gpt-oss-20b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-20b/)

## Limits, in the vendor's words

The keyless catalog publishes exactly one model and tags it with the tier it belongs to — "openai-fast", described as "GPT-OSS 20B Reasoning LLM (OVH)", tier "anonymous", aliased to openai / gpt-oss / gpt-oss-20b — and a POST with no key answered it on 2026-09-21. It is the legacy host, and the only place the offer is stated now: the API docs on the vendor's working branch describe gen.pollinations.ai alone — "Get an API key" at enter.pollinations.ai, usage billed in Pollen credits — and a keyless call there answers 401. The 1 request per 15 seconds this row used to quote came from docs on a branch the vendor stopped updating on 2026-08-04, and no current page states an anonymous rate

## Connect

- Base URL: `https://text.pollinations.ai/openai`
- Key: none — the lane is anonymous
- Callable ids: `gpt-oss-20b`
- Note: no key and no account on the legacy host. The API that replaced it, gen.pollinations.ai, answers a keyless call with `401` `A valid API key is required. Get one at https://enter.pollinations.ai/keys` (2026-09-21); its keys spend Pollen, bought or earned from the site's Quests

## Evidence

- Probe: the page at <https://text.pollinations.ai/models>, anchored on `"tier":"anonymous"`, `GPT-OSS 20B`
- Source: <https://text.pollinations.ai/models>
- Source: <https://raw.githubusercontent.com/pollinations/pollinations/HEAD/APIDOCS.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added gpt-oss-20b; dropped gpt-oss
- `2026-07-19` — Added: Open GenAI text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai)

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
