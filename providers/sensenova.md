---
layout: default
title: 'SenseNova (SenseTime 商汤) free tier: limits, free models, verified 2026-11-26'
description: 'SenseTime''s SenseNova API, with a $0 Free plan during public beta; registration and identity verification required. Free models: sensenova-6.8-flash-lite. The public beta plan names SenseNova 6.8 Flash and SenseNova U1.6 Lite. The separate API guide documents the Flash Lite preview with a free…'
permalink: /providers/sensenova/
last_modified_at: 2026-11-26
crumb: SenseNova (SenseTime 商汤)
---

{% raw %}

# SenseNova (SenseTime 商汤) free tier

🔌 LLM APIs with free tier · no card · offered only in mainland China · **live** — last verified by a probe on 2026-11-26 · [sensenova.cn](https://www.sensenova.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

SenseTime's SenseNova API, with a $0 Free plan during public beta; registration and identity verification required

## Free models

`sensenova-6.8-flash-lite`

## Limits, in the vendor's words

Public beta: Usage allowance: amount not published (period not published) per account

The public beta plan names SenseNova 6.8 Flash and SenseNova U1.6 Lite. The separate API guide documents the Flash Lite preview with a free token plan. Registration and identity verification are required. The plan does not publish a numerical allowance or reset time.

## Where it is offered

Offered only in mainland China ([source](https://platform.sensenova.cn/login), read 2026-09-26). That leaves out 93.6% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1).

## Connect

- Base URL: `https://token.sensenova.cn/v1`
- Key: `SENSENOVA_API_KEY` — get one at <https://platform.sensenova.cn>
- Callable ids: `sensenova-6.8-flash-lite`
- Note: The API guide uses this exact Flash Lite preview ID. It does not give callable IDs for the two models named on the current plan card.

Try it from your terminal with your key in `SENSENOVA_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"sensenova-6.8-flash-lite","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://raw.githubusercontent.com/OpenSenseNova/SenseNova6.8/main/API.md>, anchored on `free token plan available`, `sensenova-6.8-flash-lite`, `registration plus identity verification`
- Source: <https://www.sensenova.cn/token-plan>
- Source: <https://www.sensenova.cn/en/token-plan>
- Source: <https://raw.githubusercontent.com/OpenSenseNova/SenseNova6.8/main/API.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-12` — Free models changed: added sensenova-6.8-flash-lite
- `2026-08-14` — Added: SenseTime's own models plus DeepSeek and GLM behind an OpenAI-compatible url, free for everyone while the token plan is in public beta

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
