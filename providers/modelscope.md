---
layout: default
title: 'ModelScope API-Inference (Alibaba) free tier: limits, free models, verified 2026-09-24'
description: 'Alibaba''s model community serves 35 models free — DeepSeek V4 Pro, GLM-5.2, MiniMax M3 and Qwen3.8 among them — for 250 魔粒 a day at 0.5 to 2 a call, after Alibaba Cloud real-name verification. The limits page: "免费推理API由阿里云提供算力支持，要求您的ModelScope账号必须首先绑定阿里云账号", and the Alibaba Cloud account must…'
permalink: /providers/modelscope/
---

{% raw %}

# ModelScope API-Inference (Alibaba)

🔌 LLM APIs with free tier · no card · provisional — added on 2026-09-19, a regular row from the first probe it passes on or after 2026-10-03 · **live** — last verified by a probe on 2026-09-24 · [modelscope.cn](https://modelscope.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Alibaba's model community serves 35 models free — DeepSeek V4 Pro, GLM-5.2, MiniMax M3 and Qwen3.8 among them — for 250 魔粒 a day at 0.5 to 2 a call, after Alibaba Cloud real-name verification

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The limits page: "免费推理API由阿里云提供算力支持，要求您的ModelScope账号必须首先绑定阿里云账号", and the Alibaba Cloud account must have passed real-name verification before API-Inference works — which Alibaba Cloud does through a personal Alipay account that has passed its own. Calls are paid in 魔粒, "轻量模型（0.5 魔粒/次），主流模型（1 魔粒/次），旗舰模型（2 魔粒/次）", and the 魔粒 page grants 200 a day for signing in and 50 more with the Alibaba Cloud account bound, each valid 24 hours: 125 to 500 calls a day. Spending 魔粒 first needs a verified personal email. Concurrency is throttled to the platform's load, the service calls itself non-commercial and not for production — "请勿用于需要高并发以及SLA保障的线上任务" — and older models leave as new ones arrive. The docs are read through the index that names the current release (Data.TargetPrefix). Read 2026-09-19

## Connect

- Base URL: `https://api-inference.modelscope.cn/v1`
- Key: `MODELSCOPE_API_KEY` — get one at <https://modelscope.cn/my/myaccesstoken>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api-inference.modelscope.cn`
- Callable ids: `deepseek-ai/DeepSeek-V4.1-Flash`, `deepseek-ai/DeepSeek-V4-Pro`, `ZhipuAI/GLM-5.2`, `MiniMax/MiniMax-M3`, `Qwen/Qwen3.8-27B`, `Qwen/Qwen3.8-Flash-Next`, `stepfun-ai/Step-3.7-Flash`, `Qwen/Qwen3.5-397B-A17B`, `nex-agi/Nex-N2.5-Pro`, `deepseek-ai/DeepSeek-V4-Flash-0731`, `ZhipuAI/GLM-4.7-Flash`
- Note: the key is a ModelScope access token, and it calls only once the account is bound to an Alibaba Cloud account that has passed real-name verification. The ids are the coding-capable rows of the keyless catalog; the Anthropic-format route is in beta

## Evidence

- Probe: the page the index at <https://www.modelscope.cn/api/v1/document/main_doc_CN_prod> names in `Data.TargetPrefix`, followed by `/dist/model-service/API-Inference/limits/limits_CN.md`, anchored on `轻量模型（0.5 魔粒/次）`, `旗舰模型（2 魔粒/次）`; ids checked in <https://api-inference.modelscope.cn/v1/models>
- Source: <https://modelscope.cn/docs/model-service/API-Inference/limits>
- Source: <https://modelscope.cn/docs/magicube/intro>
- Source: <https://modelscope.cn/docs/model-service/API-Inference/intro>
- Source: <https://api-inference.modelscope.cn/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-19` — Added: Alibaba's model community serves 35 models free — DeepSeek V4 Pro, GLM-5.2, MiniMax M3 and Qwen3.8 among them — for 250 魔粒 a day at 0.5 to 2 a call, after Alibaba Cloud real-name verification

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
