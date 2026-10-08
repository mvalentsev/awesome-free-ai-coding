---
layout: default
title: 'SenseNova (SenseTime 商汤) free tier: limits, free models, verified 2026-10-08'
description: SenseTime's own SenseNova models behind an OpenAI-compatible url, free for everyone while the token plan is in public beta. Free during the public beta; paid tiers are planned. The Free card covers SenseNova 6.8 Flash Lite and SenseNova U1 Fast, with special-model exceptions. The page states a…
permalink: /providers/sensenova/
last_modified_at: 2026-10-08
crumb: SenseNova (SenseTime 商汤)
---

{% raw %}

# SenseNova (SenseTime 商汤) free tier

🔌 LLM APIs with free tier · no card · offered only in mainland China · **live** — last verified by a probe on 2026-10-08 · [sensenova.cn](https://www.sensenova.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

SenseTime's own SenseNova models behind an OpenAI-compatible url, free for everyone while the token plan is in public beta

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Public beta: 60,000 credits/5 hours per account

Free during the public beta; paid tiers are planned. The Free card covers SenseNova 6.8 Flash Lite and SenseNova U1 Fast, with special-model exceptions. The page states a five-hour allowance without specifying a rolling reset. Up to 20 API keys are supported. Signup requires a phone number; acceptance of non-mainland numbers is unverified.

## Where it is offered

Offered only in mainland China ([source](https://platform.sensenova.cn/login), read 2026-09-26). That leaves out 93.6% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1).

## Connect

- Base URL: `https://token.sensenova.cn/v1`
- Key: `SENSENOVA_API_KEY` — get one at <https://platform.sensenova.cn>
- Callable ids: `sensenova-6.8-flash-lite`
- Note: the base url and the id are the ones SenseTime's own API guide on GitHub (OpenSenseNova, API.md) prints; token.sensenova.cn/v1/models answers 401 `Authorization Not Found` in an OpenAI-shaped envelope, so no run reads the catalog, and the id of SenseNova U1 Fast, the plan's other free model, is printed on no page a probe here can read.

Try it from your terminal with your key in `SENSENOVA_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://token.sensenova.cn/v1/chat/completions \
  -H "Authorization: Bearer $SENSENOVA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"sensenova-6.8-flash-lite","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.sensenova.cn/token-plan>, anchored on `公测期完全免费开放，付费档位即将上线`, `60,000 积分 / 5 小时`
- Source: <https://www.sensenova.cn/token-plan>
- Source: <https://github.com/OpenSenseNova/SenseNova6.8/blob/main/API.md>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Added: SenseTime's own models plus DeepSeek and GLM behind an OpenAI-compatible url, free for everyone while the token plan is in public beta

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
