---
layout: default
title: 'CrowLLM (free models) free tier: limits, free models, verified 2026-11-26'
description: Free OpenAI-compatible Chat Completions with an account API key. The Free plan has a low request ceiling and no burst headroom while requests are queued. The model card gives this route no trial timer.
permalink: /providers/crowllm/
last_modified_at: 2026-11-26
crumb: CrowLLM (free models)
---

{% raw %}

# CrowLLM (free models) free tier

🧭 Aggregators (one key, many providers) · no card · provisional — added on 2026-11-23, a regular row from the first probe it passes on or after 2026-12-07 · **live** — last verified by a probe on 2026-11-26 · [crowllm.com](https://crowllm.com) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free OpenAI-compatible Chat Completions with an account API key

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The Free plan has a low request ceiling and no burst headroom while requests are queued. The model card gives this route no trial timer.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://crowllm.com/terms-of-service), read 2026-11-23).

## Connect

- Base URL: `https://crowllm.com/v1`
- Key: `CROWLLM_API_KEY` — get one at <https://crowllm.com/keys>
- Callable ids: `gemma-4-31b-it:free`

Try it from your terminal with your key in `CROWLLM_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://crowllm.com/v1/chat/completions \
  -H "Authorization: Bearer $CROWLLM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemma-4-31b-it:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://crowllm.com/models/gemma-4-31b-it%3Afree>, anchored on `gemma-4-31b-it:free from Google is free on CrowLLM`, `no card, no trial timer`, `$0 per 1M input tokens and $0 per 1M output tokens`, `/v1/chat/completions`; ids checked in <https://crowllm.com/v1/models>
- Source: <https://crowllm.com/models/gemma-4-31b-it%3Afree>
- Source: <https://crowllm.com/pricing>
- Source: <https://crowllm.com/v1/models>
- Source: <https://crowllm.com/docs/authentication>
- Source: <https://crowllm.com/terms-of-service>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-23` — Added: Free OpenAI-compatible Chat Completions with an account API key

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
