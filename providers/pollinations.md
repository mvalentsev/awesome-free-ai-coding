---
layout: default
title: 'Pollinations.AI free tier: limits, free models, verified 2026-10-08'
description: 'Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model. Free models: gpt-oss-20b. The legacy keyless host lists openai-fast, GPT-OSS 20B on OVH, in the anonymous tier; the configured gpt-oss-20b alias completed a keyless POST on 2026-10-07. The current…'
permalink: /providers/pollinations/
last_modified_at: 2026-10-08
crumb: Pollinations.AI
---

{% raw %}

# Pollinations.AI free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [pollinations.ai](https://pollinations.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model

## Free models

[`gpt-oss-20b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/gpt-oss-20b/)

## Limits, in the vendor's words

Legacy anonymous lane: Usage allowance: amount not published (period not published); scope not published

The legacy keyless host lists openai-fast, GPT-OSS 20B on OVH, in the anonymous tier; the configured gpt-oss-20b alias completed a keyless POST on 2026-10-07. The current gen.pollinations.ai API requires a key and bills Pollen credits; without a key it returns 401. The former anonymous rate came from retired docs and is no longer a current published limit.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://pollinations.ai/legal/TERMS_OF_SERVICE.md), read 2026-09-26).

## Connect

- Base URL: `https://text.pollinations.ai/openai`
- Key: none — the lane is anonymous
- Callable ids: `gpt-oss-20b`
- Note: The legacy endpoint needs no key. Both bare requests and the dummy Bearer token used by LiteLLM completed on 2026-10-07; anonymous requests can also return HTTP 402, so availability varies. The replacement gen.pollinations.ai requires personal keys and Pollen credits, bought or earned from Quests.

Try it from your terminal — the lane takes no key:

```sh
curl -s https://text.pollinations.ai/openai/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-oss-20b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://text.pollinations.ai/models>, anchored on `"tier":"anonymous"`, `GPT-OSS 20B`
- Source: <https://text.pollinations.ai/models>
- Source: <https://raw.githubusercontent.com/pollinations/pollinations/HEAD/APIDOCS.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added gpt-oss-20b; dropped gpt-oss
- `2026-07-19` — Added: Open GenAI text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai)

---

Generated from `registry.yaml` on 2026-10-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
