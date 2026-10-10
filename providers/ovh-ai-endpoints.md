---
layout: default
title: 'OVHcloud AI Endpoints free tier: limits, free models, verified 2026-10-08'
description: 'EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller. Free models: gpt-oss-120b, qwen3.6, qwen3.8-27b, qwen3-coder. The documentation attributes the anonymous cap to IP…'
permalink: /providers/ovh-ai-endpoints/
last_modified_at: 2026-10-08
crumb: OVHcloud AI Endpoints
---

{% raw %}

# OVHcloud AI Endpoints free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [ovhcloud.com](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible), at two requests a minute per model shared by every anonymous caller

## Free models

[`gpt-oss-120b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-120b/), [`qwen3.6`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.6/), [`qwen3.8-27b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.8-27b/), `qwen3-coder`

## Limits, in the vendor's words

Anonymous lane: 2 requests/minute sharing scope disputed

The documentation attributes the anonymous cap to IP and model. Tests on 2026-09-24 instead observed callers sharing a model's anonymous capacity, so its effective sharing scope remains disputed. Anonymous requests can receive 429 before a caller has spent the documented cap. Authenticated API keys are metered per token and use the paid project/model limits; they do not create a larger free allowance.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://contract.eu.ovhapis.com/1.0/pdf/contrat_genServices-we.pdf), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Your data is never used to train our models, and we only keep what is strictly necessary for billing.” ([source](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)).

## Connect

- Base URL: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`
- Key: none — the lane is anonymous
- Callable ids: `Qwen3.6-27B`, `Qwen3.8-27B`, `gpt-oss-120b`, `Qwen3-Coder-30B-A3B-Instruct`
- Note: no key at all on the anonymous lane, where 2 requests per minute per model are shared by every anonymous caller (measured 2026-09-24) — a 429 means the minute's quota is gone, not the offer. An API access key from a Public Cloud project raises that to 400 per minute and bills per token from then on

Try it from your terminal — the lane takes no key:

```sh
curl -s https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen3.6-27B","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models>
- Source: <https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models>
- Source: <https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started>
- Source: <https://www.ovhcloud.com/en/public-cloud/ai-endpoints/>
- Source: <https://endpoints.ai.cloud.ovh.net/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added gpt-oss-120b; dropped gpt-oss
- `2026-09-17` — Free models changed: added qwen3.8-27b; dropped qwen3.8
- `2026-09-07` — Free models changed: added qwen3.8
- `2026-08-19` — Free models changed: added qwen3-coder, qwen3.6; dropped qwen3
- `2026-07-19` — Added: EU-hosted serverless open-model API; anonymous tier needs no signup or API key (OpenAI-compatible)

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
