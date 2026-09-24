---
layout: default
title: 'Alibaba Cloud Model Studio (DashScope, international) free tier: limits, free models, verified 2026-09-21'
description: 'Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible. 1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions". The grant is…'
permalink: /providers/alibaba-model-studio/
---

{% raw %}

# Alibaba Cloud Model Studio (DashScope, international)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-21 · [alibabacloud.com](https://www.alibabacloud.com/en/product/modelstudio) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible

## Free models

`qwen3.8-max`, `qwen3-max`, `qwen3-coder`

## Limits, in the vendor's words

1,000,000 free tokens per model, on the Singapore (international) region alone: "the following models offer a free quota only in Singapore. No free quota is available in other regions". The grant is "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later" (read 2026-09-16). Which ids carry it is read off the last column of each International table, "Free quota": the qwen3.8 generation — qwen3.8-max and qwen3.8-max-0902 at a $2/$6 list, qwen3.8-flash, qwen3.8-27b — qwen3-max, and the qwen3-coder line. qwen-long reads "No free quota", and the Global tables carry no free-quota column at all (ids read 2026-09-10). Since 2026-09-15 "you must complete your account information before activating Model Studio", and past the quota "you are automatically billed on a pay-as-you-go basis" unless Free Quota Only, which "is disabled by default", is switched on per model (read 2026-09-23)

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Alibaba Cloud strictly protects your data privacy and will never use your data for model training.” ([source](https://www.alibabacloud.com/help/en/model-studio/privacy-notice)).

## Connect

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Note: international (Singapore) endpoint; keys are region-specific

## Evidence

- Probe: the page at <https://www.alibabacloud.com/help/en/model-studio/model-pricing>, anchored on `free quota`, `valid for 90 days`
- Source: <https://www.alibabacloud.com/help/en/model-studio/model-pricing>
- Source: <https://www.alibabacloud.com/help/en/model-studio/new-free-quota>

## History

- `2026-09-12` — Free models changed: added qwen3.8-max
- `2026-07-19` — Added to the list: Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible

---

Generated from `registry.yaml` on 2026-09-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
