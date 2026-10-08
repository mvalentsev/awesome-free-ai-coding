---
layout: default
title: 'SiliconFlow (China) free tier: limits, free models, verified 2026-10-08'
description: 'China''s SiliconFlow prices eight small chat models at ¥0 for an account verified with Chinese, Hong Kong, Macau or Taiwan papers. Free models: xing4.0-29b, qwen3-8b, glm-4-9b-0414, qwen2.5-7b, qwen3.5-4b, glm-z1-9b-0414, deepseek-r1-0528-qwen3-8b. Free models are zero-priced but require real-name…'
permalink: /providers/siliconflow-cn/
last_modified_at: 2026-10-08
crumb: SiliconFlow (China)
---

{% raw %}

# SiliconFlow (China) free tier

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · **live** — last verified by a probe on 2026-10-08 · [siliconflow.cn](https://siliconflow.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

China's SiliconFlow prices eight small chat models at ¥0 for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

## Free models

`xing4.0-29b`, [`qwen3-8b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3-8b/), `glm-4-9b-0414`, `qwen2.5-7b`, [`qwen3.5-4b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3.5-4b/), `glm-z1-9b-0414`, `deepseek-r1-0528-qwen3-8b`

## Limits, in the vendor's words

Verified free models: Usage allowance: see your account for values (period not published) per account per model

Free models are zero-priced but require real-name verification. Online verification uses an Alipay face scan and accepted mainland, Hong Kong, Macau, Taiwan or Chinese permanent-residence documents; other applicants must contact staff. Sign in by SMS or email. Per-model fixed rate values are shown in the client-rendered model square, rather than public docs.

## Where it is offered

Offered only in mainland China, Hong Kong, Taiwan and Macao ([source](https://docs.siliconflow.cn/docs/userguide/faqs/authentication), read 2026-09-26). That leaves out 90.8% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “不具有以上证件的用户，暂时不支持线上个人认证”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “我们不会长期存储您的任何业务输入与输出数据；不会将您的业务数据用于任何大模型的预训练、微调或其他商业用途；” ([source](https://docs.siliconflow.cn/docs/legals/privacy-policy)).

## Connect

- Base URL: `https://api.siliconflow.cn/v1`
- Key: `SILICONFLOW_CN_API_KEY` — get one at <https://cloud.siliconflow.cn/account/ak>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.siliconflow.cn`
- Callable ids: `XingChenAGI/Xing4.0-29B`, `Qwen/Qwen3-8B`, `THUDM/GLM-4-9B-0414`, `THUDM/GLM-Z1-9B-0414`, `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`, `Qwen/Qwen3.5-4B`, `Qwen/Qwen2.5-7B-Instruct`
- Note: ids are the price list's own; Hunyuan-MT-7B, the other chat row at ¥0, is a translation model. /v1/models needs a key, and the Messages route the API reference documents is https://api.siliconflow.cn/v1/messages

Try it from your terminal with your key in `SILICONFLOW_CN_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer $SILICONFLOW_CN_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"XingChenAGI/Xing4.0-29B","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://siliconflow.cn/pricing>, anchored on `Qwen2.5-7B-Instruct (Free)`, `DeepSeek-R1-0528-Qwen3-8B (Free)` in the page's own data
- Source: <https://siliconflow.cn/pricing>
- Source: <https://docs.siliconflow.cn/docs/userguide/faqs/rate-limit-and-upgradation>
- Source: <https://docs.siliconflow.cn/docs/userguide/faqs/authentication>
- Source: <https://docs.siliconflow.cn/docs/userguide/quickstart>
- Source: <https://docs.siliconflow.cn/docs/api/messages-post>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-03` — Free models changed: added deepseek-r1-0528-qwen3-8b, glm-z1-9b-0414, qwen2.5-7b, qwen3.5-4b
- `2026-09-19` — Added: China's SiliconFlow prices eight small chat models at ¥0 — Qwen3-8B, GLM-4-9B-0414 and the 29B Xing4.0 among them — for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

---

Generated from `registry.yaml` on 2026-10-08 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
