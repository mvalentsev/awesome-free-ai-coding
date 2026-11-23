---
layout: default
title: 'iFlytek Spark Lite (讯飞星火) free tier: limits, free models, verified 2026-11-23'
description: Free Spark Lite HTTP API. Claim the Spark API allowance and create an APIPassword in the developer console. Personal verification asks for identity and phone details. Hong Kong, Macao, Taiwan and overseas applicants can submit valid ID for manual review. The HTTP documentation describes Lite as…
permalink: /providers/iflytek-spark/
last_modified_at: 2026-11-23
crumb: iFlytek Spark Lite (讯飞星火)
---

{% raw %}

# iFlytek Spark Lite (讯飞星火) free tier

🔌 LLM APIs with free tier · no card · provisional — added on 2026-11-19, a regular row from the first probe it passes on or after 2026-12-03 · **live** — last verified by a probe on 2026-11-23 · [xinghuo.xfyun.cn](https://xinghuo.xfyun.cn/sparkapi) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free Spark Lite HTTP API

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Tokens allowance: amount not published (period not published) per account per model

Claim the Spark API allowance and create an APIPassword in the developer console. Personal verification asks for identity and phone details. Hong Kong, Macao, Taiwan and overseas applicants can submit valid ID for manual review. The HTTP documentation describes Lite as free but leaves its account quota unpublished.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://www.xfyun.cn/doc/authentication/personal.html), read 2026-11-19). In the vendor's words: “港澳台及海外地区用户请填写有效证件信息，进入人工审核”.

## Connect

- Base URL: `https://spark-api-open.xf-yun.com/v1`
- Key: `IFLYTEK_SPARK_API_KEY` — get one at <https://console.xfyun.cn/>
- Callable ids: `lite`
- Note: Use the APIPassword issued for your Spark app and the exact model ID lite.

Try it from your terminal with your key in `IFLYTEK_SPARK_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://spark-api-open.xf-yun.com/v1/chat/completions \
  -H "Authorization: Bearer $IFLYTEK_SPARK_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"lite","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html>, anchored on `具有更高的响应速度,支持 免费使用`, `lite指向Lite版本`, `https://spark-api-open.xf-yun.com/v1`
- Source: <https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html>
- Source: <https://www.xfyun.cn/doc/authentication/personal.html>
- Source: <https://console.xfyun.cn/>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-19` — Added: Free Spark Lite HTTP API

---

Generated from `registry.yaml` and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
