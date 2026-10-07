---
layout: default
title: 'ModelScope API-Inference (Alibaba) free tier: limits, free models, verified 2026-10-05'
description: Alibaba's model community serves 35 models free — DeepSeek V4 Pro, GLM-5.2, MiniMax M3 and Qwen3.8 among them — for 250 魔粒 a day at 0.5 to 2 a call, after Alibaba Cloud real-name verification. API inference requires a bound Alibaba Cloud account with real-name verification; spending Magicube also…
permalink: /providers/modelscope/
last_modified_at: 2026-10-05
crumb: ModelScope API-Inference (Alibaba)
---

{% raw %}

# ModelScope API-Inference (Alibaba) free tier

🔌 LLM APIs with free tier · no card · offered only in mainland China · **live** — last verified by a probe on 2026-10-05 · [modelscope.cn](https://modelscope.cn) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Alibaba's model community serves 35 models free — DeepSeek V4 Pro, GLM-5.2, MiniMax M3 and Qwen3.8 among them — for 250 魔粒 a day at 0.5 to 2 a call, after Alibaba Cloud real-name verification

## Free models

No model is free by itself here: the free part is an amount the account spends across the catalog, so the column names none. The limits below say what it buys; the ids to call, where the row has them, are under Connect.

## Limits, in the vendor's words

Magicube daily login: 200 credits/day per account (Valid for the day)

Daily bound-account bonus: 50 credits/day per account (Alibaba Cloud account bound; valid for the day)

Additional community rewards: Credits allowance: amount varies (period not published) per account

API inference requires a bound Alibaba Cloud account with real-name verification; spending Magicube also requires a verified personal email. Calls cost 0.5, 1 or 2 credits by model class, so credits are not a fixed request count. Community rewards are separate and variable. Concurrency follows platform load. This is non-commercial, unsuitable for production requiring high concurrency or SLA; older models can be replaced.

## Where it is offered

Offered only in mainland China ([source](https://help.aliyun.com/zh/account/verify-your-identity-individual-account), read 2026-09-26). That leaves out 93.6% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “输入个人认证的姓名和身份证号码”.

## Connect

- Base URL: `https://api-inference.modelscope.cn/v1`
- Key: `MODELSCOPE_API_KEY` — get one at <https://modelscope.cn/my/myaccesstoken>
- Anthropic-format base (Claude Code's `ANTHROPIC_BASE_URL`): `https://api-inference.modelscope.cn`
- Callable ids: `deepseek-ai/DeepSeek-V4.1-Flash`, `deepseek-ai/DeepSeek-V4-Pro`, `ZhipuAI/GLM-5.2`, `MiniMax/MiniMax-M3`, `Qwen/Qwen3.8-27B`, `Qwen/Qwen3.8-Flash-Next`, `stepfun-ai/Step-3.7-Flash`, `Qwen/Qwen3.5-397B-A17B`, `nex-agi/Nex-N2.5-Pro`, `deepseek-ai/DeepSeek-V4-Flash-0731`, `ZhipuAI/GLM-4.7-Flash`
- Note: the key is a ModelScope access token, and it calls only once the account is bound to an Alibaba Cloud account that has passed real-name verification. The ids are the coding-capable rows of the keyless catalog; the Anthropic-format route is in beta

Try it from your terminal with your key in `MODELSCOPE_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api-inference.modelscope.cn/v1/chat/completions \
  -H "Authorization: Bearer $MODELSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-ai/DeepSeek-V4.1-Flash","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

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

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
