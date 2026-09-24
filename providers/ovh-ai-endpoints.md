---
layout: default
title: 'OVHcloud AI Endpoints free tier: limits, free models, verified 2026-09-24'
description: 'EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller. OVHcloud documents the anonymous lane: "Anonymous: 2 requests per minute, per IP and per model. Authenticated…'
permalink: /providers/ovh-ai-endpoints/
---

{% raw %}

# OVHcloud AI Endpoints

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [ovhcloud.com](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

## Free models

`gpt-oss`, `qwen3.6`, `qwen3.8-27b`, `qwen3-coder`

## Limits, in the vendor's words

OVHcloud documents the anonymous lane: "Anonymous: 2 requests per minute, per IP and per model. Authenticated with an API access key: 400 requests per minute, per PCI project and per model", and its product page says "Test all our models for free in a sandbox or via the API". It is not counted per IP in practice: on 2026-09-24 one call a minute to Qwen3.8-27B from an address nothing else used answered twice in five, and each answer left `ratelimit-remaining: 0`, another caller having spent the minute's other request; the first call of a minute on six ids, and every call from a GitHub runner that morning, answered 429. The two requests a minute per model are shared by every anonymous caller. A key bills every chat model per token, Qwen3.8-27B at "0.4 € / Mtoken(input)" and "2.7 € / Mtoken(output)". Read 2026-09-24

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Your data will never be used to train or improve our AI models” ([source](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)).

## Connect

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `Qwen3.8-27B`, `gpt-oss-120b`, `Qwen3.6-27B`, `Qwen3-Coder-30B-A3B-Instruct`
- Note: no key at all on the anonymous lane, where 2 requests per minute per model are shared by every anonymous caller (measured 2026-09-24) — a 429 means the minute's quota is gone, not the offer. An API access key from a Public Cloud project raises that to 400 per minute and bills per token from then on

## Evidence

- Probe: the models catalog at <https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models>
- Source: <https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models>
- Source: <https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started>
- Source: <https://www.ovhcloud.com/en/public-cloud/ai-endpoints/>
- Source: <https://endpoints.ai.cloud.ovh.net/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Free models changed: added qwen3.8-27b; dropped qwen3.8
- `2026-09-07` — Free models changed: added qwen3.8
- `2026-08-19` — Free models changed: added qwen3-coder, qwen3.6; dropped qwen3
- `2026-07-19` — Added: EU-hosted serverless open-model API; anonymous tier needs no signup or API key (OpenAI-compatible)

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
