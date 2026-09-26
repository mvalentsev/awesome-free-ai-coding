---
layout: default
title: 'SiliconFlow (China) free tier: limits, free models, verified 2026-09-24'
description: 'China''s SiliconFlow prices eight small chat models at ¥0 — Qwen3-8B, GLM-4-9B-0414 and the 29B Xing4.0 among them — for an account verified with Chinese, Hong Kong, Macau or Taiwan papers. The rate-limit FAQ: free models cost nothing ("免费模型调用免费", billed at 0), their limits are fixed per model…'
permalink: /providers/siliconflow-cn/
last_modified_at: 2026-09-26
crumb: SiliconFlow (China)
---

{% raw %}

# SiliconFlow (China) free tier

🔌 LLM APIs with free tier · no card · offered only in mainland China, Hong Kong, Taiwan and Macao · provisional — added on 2026-09-19, a regular row from the first probe it passes on or after 2026-10-03 · **live** — last verified by a probe on 2026-09-24 · [siliconflow.cn](https://siliconflow.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

China's SiliconFlow prices eight small chat models at ¥0 — Qwen3-8B, GLM-4-9B-0414 and the 29B Xing4.0 among them — for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

## Free models

`xing4.0-29b`, [`qwen3-8b`](https://mvalentsev.github.io/awesome-free-ai-coding/models/qwen3-8b/), `glm-4-9b-0414`

## Limits, in the vendor's words

The rate-limit FAQ: free models cost nothing ("免费模型调用免费", billed at 0), their limits are fixed per model ("免费模型的 Rate Limits 固定", shown in the client-rendered model square), and "实名认证后使用全部的免费模型" — they open only after real-name verification. That is an Alipay face scan taking a mainland ID card, a Hong Kong, Macau or Taiwan travel or residence permit, or China's permanent-residence card for foreigners; without one "暂时不支持线上个人认证", and the FAQ offers a form to the staff instead. Sign-in is by SMS or email. The free rows are in the price list's own data, each at ¥0 in and out: Qwen3-8B, GLM-4-9B-0414, GLM-Z1-9B-0414, Qwen2.5-7B-Instruct, Qwen3.5-4B, DeepSeek-R1-0528-Qwen3-8B, Hunyuan-MT-7B and Xing4.0-29B, the last two also marked 免费 in the table the page renders. Read 2026-09-18

## Where it is offered

Offered only in mainland China, Hong Kong, Taiwan and Macao ([source](https://docs.siliconflow.cn/docs/userguide/faqs/authentication), read 2026-09-26). That leaves out 90.8% of the developers GitHub counts, beyond the embargoed countries most offers leave out ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “不具有以上证件的用户，暂时不支持线上个人认证”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “我们不会长期存储您的任何业务输入与输出数据；不会将您的业务数据用于任何大模型的预训练、微调或其他商业用途；” ([source](https://docs.siliconflow.cn/docs/legals/privacy-policy)).

## Connect

- Base URL: `https://api.siliconflow.cn/v1`
- Key: `SILICONFLOW_CN_API_KEY` — get one at <https://cloud.siliconflow.cn/account/ak>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api.siliconflow.cn`
- Callable ids: `XingChenAGI/Xing4.0-29B`, `Qwen/Qwen3-8B`, `THUDM/GLM-4-9B-0414`, `THUDM/GLM-Z1-9B-0414`, `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`, `Qwen/Qwen3.5-4B`, `Qwen/Qwen2.5-7B-Instruct`
- Note: ids are the price list's own; Hunyuan-MT-7B, the other chat row at ¥0, is a translation model. /v1/models needs a key, and the Messages route the API reference documents is https://api.siliconflow.cn/v1/messages

## Evidence

- Probe: the page at <https://siliconflow.cn/pricing>, anchored on `Qwen2.5-7B-Instruct (Free)`, `DeepSeek-R1-0528-Qwen3-8B (Free)` in the page's own data
- Source: <https://siliconflow.cn/pricing>
- Source: <https://docs.siliconflow.cn/docs/userguide/faqs/rate-limit-and-upgradation>
- Source: <https://docs.siliconflow.cn/docs/userguide/faqs/authentication>
- Source: <https://docs.siliconflow.cn/docs/userguide/quickstart>
- Source: <https://docs.siliconflow.cn/docs/api/messages-post>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-19` — Added: China's SiliconFlow prices eight small chat models at ¥0 — Qwen3-8B, GLM-4-9B-0414 and the 29B Xing4.0 among them — for an account verified with Chinese, Hong Kong, Macau or Taiwan papers

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
