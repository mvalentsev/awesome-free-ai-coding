---
layout: default
title: 'Tencent Cloud TokenHub free tier: limits, free models, verified 2026-10-08'
description: Tencent Cloud's model platform, with a one-time grant of a million tokens on each of its language models, valid a year and no card, on an account that has passed Tencent Cloud real-name verification. The claiming promotion runs through December 31, 2026. Grants are selected per model or claimed on…
permalink: /providers/tencent-tokenhub/
last_modified_at: 2026-10-08
crumb: Tencent Cloud TokenHub
---

{% raw %}

# Tencent Cloud TokenHub free tier

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · **live** — last verified by a probe on 2026-10-08 · [cloud.tencent.com](https://cloud.tencent.com/document/product/1823) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Tencent Cloud's model platform, with a one-time grant of a million tokens on each of its language models, valid a year and no card, on an account that has passed Tencent Cloud real-name verification

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Claimed promotional package: 1,000,000 tokens once per account per model (Valid for 1 year)

The claiming promotion runs through December 31, 2026. Grants are selected per model or claimed on its first call; one note instead says models share the account's quota, so confirm the console's scope. Exhaustion stops usage unless post-payment is enabled. Real-name verification accepts residents of mainland China, Hong Kong, Macau and Taiwan; other identity documents are directed to the international service.

## Where it is offered

Offered only in mainland China, Hong Kong, Taiwan and Macao ([source](https://cloud.tencent.com/document/product/378/3629), read 2026-09-26). That leaves out 90.8% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “其他类型国际证件请前往 国际站 进行认证”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “不会，我们非常重视您的隐私保护，不会将您的数据用于为您提供服务以外的场景，更不会用于训练。” ([source](https://cloud.tencent.com/document/product/1823/130104)).

## Connect

- Base URL: `https://tokenhub.tencentmaas.com/v1`
- Key: `TENCENT_TOKENHUB_API_KEY` — get one at <https://console.cloud.tencent.com/tokenhub/apikey>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://tokenhub.tencentmaas.com`
- Callable ids: `kimi-k3`, `glm-5.3`, `hy3`, `minimax-m3`
- Note: Use the IDs in the models page's 调用参数 column; /v1/models requires a key. For Claude Code, set ANTHROPIC_BASE_URL=https://tokenhub.tencentmaas.com and ANTHROPIC_MODEL=hy3.

Try it from your terminal with your key in `TENCENT_TOKENHUB_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://tokenhub.tencentmaas.com/v1/chat/completions \
  -H "Authorization: Bearer $TENCENT_TOKENHUB_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"kimi-k3","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://cloud.tencent.com/document/product/1823/130053>, anchored on `100 万 Tokens 的免费体验额度`, `2026 年 12 月 31 日`
- Source: <https://cloud.tencent.com/document/product/1823/130053>
- Source: <https://cloud.tencent.com/document/product/1823/130058>
- Source: <https://cloud.tencent.com/document/product/378/3629>
- Source: <https://cloud.tencent.com/document/product/1823/130051>
- Source: <https://cloud.tencent.com/document/product/1823/131903>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-17` — Added: Tencent Cloud's model platform — Hy3, Kimi K3, GLM-5.3 and MiniMax-M3 among its models — with a one-time grant of a million tokens on its language models, valid a year and no card, on an account that has passed Tencent Cloud real-name verification

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
