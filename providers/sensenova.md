---
layout: default
title: 'SenseNova (SenseTime 商汤) free tier: limits, free models, verified 2026-09-24'
description: 'SenseTime''s own SenseNova models behind an OpenAI-compatible url, free for everyone while the token plan is in public beta. The plan page says 公测期完全免费开放，付费档位即将上线 — free during the public beta, paid tiers coming — at ¥0/month: 60,000 积分 / 5 小时, a rolling 60,000 credits per five hours, 特殊模型除外,…'
permalink: /providers/sensenova/
---

{% raw %}

# SenseNova (SenseTime 商汤)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [sensenova.cn](https://www.sensenova.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

SenseTime's own SenseNova models behind an OpenAI-compatible url, free for everyone while the token plan is in public beta

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The plan page says 公测期完全免费开放，付费档位即将上线 — free during the public beta, paid tiers coming — at ¥0/month: 60,000 积分 / 5 小时, a rolling 60,000 credits per five hours, 特殊模型除外, with 最多 20 个 API Key and the tier marked 限时放量. The Free card names the two models it covers, SenseNova 6.8 Flash Lite and SenseNova U1 Fast. Signup needs a phone number; whether a non-mainland one is accepted could not be verified from any served page

## Connect

- Base URL: `https://token.sensenova.cn/v1`
- Key: `SENSENOVA_API_KEY` — get one at <https://platform.sensenova.cn>
- Note: the base url is not printed on any server-rendered page — it is taken from the vendor's console docs and corroborated directly, since token.sensenova.cn/v1/models answers 401 `Authorization Not Found` in an OpenAI-shaped envelope. The callable ids live only in that JavaScript console, which no probe here can read, so none are published; the plan page names "SenseNova 6.8 Flash Lite" in prose alone.

## Evidence

- Probe: the page at <https://www.sensenova.cn/token-plan>, anchored on `公测期完全免费开放，付费档位即将上线`, `60,000 积分 / 5 小时`
- Source: <https://www.sensenova.cn/token-plan>

## History

Each line is a change to what this page publishes, dated the day the list recorded it, in UTC.

- `2026-08-17` — Added: SenseTime's own models plus DeepSeek and GLM behind an OpenAI-compatible url, free for everyone while the token plan is in public beta

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
