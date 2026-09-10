---
layout: default
title: 'Alibaba Cloud Model Studio (DashScope, international) free tier: limits, free models, verified 2026-09-10'
description: 'Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible. 1,000,000 free tokens per model, on the Singapore (international) region alone — the newer of the two versions the CDN serves says so outright, over every table: "the following models offer a free quota…'
permalink: /providers/alibaba-model-studio/
---

{% raw %}

# Alibaba Cloud Model Studio (DashScope, international)

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-10 · [alibabacloud.com](https://www.alibabacloud.com/en/product/modelstudio) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible

## Free models

`qwen3.8-max`, `qwen3-max`, `qwen3-coder`

## Limits, in the vendor's words

1,000,000 free tokens per model, on the Singapore (international) region alone — the newer of the two versions the CDN serves says so outright, over every table: "the following models offer a free quota only in Singapore. No free quota is available in other regions". That same rollout rewords the validity, from "valid for 90 days after you activate Alibaba Cloud Model Studio" to "valid for 90 days from the date of Model Studio activation, model release, or application approval, whichever is later", and both versions were being served minutes apart, so the probe anchors on the half they share (read 2026-08-28). The quota is per model id, and the read of 2026-09-10 settles which ids carry it by reading the column header rather than the cell: the last column of every International table is "Free quota (Note) Valid for 90 days …", and it is the only place on that page where "1 million tokens" is a grant rather than the unit the price beside it is quoted in — the phrase occurs 377 times. The whole qwen3.8 generation is in that column: qwen3.8-max and qwen3.8-max-0902 at a $2/$6 list, qwen3.8-flash at $0.15/$0.47, qwen3.8-27b and qwen3.8-2.4t-a95b. So is qwen3-coder-next, beside the coder-plus and coder-flash ids already covered, and so is qwen3-max, which keeps its own grant rather than handing it on. The same column is what rules a model out: qwen-long reads "No free quota", the Global tables carry no such column at all, and the media models are quoted in images, characters or seconds instead

## Connect

- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Key: `ALIBABA_MODEL_STUDIO_API_KEY` — get one at <https://modelstudio.console.alibabacloud.com>
- Note: international (Singapore) endpoint; keys are region-specific

## Evidence

- Probe: the page at <https://www.alibabacloud.com/help/en/model-studio/model-pricing>, anchored on `free quota`, `valid for 90 days`
- Source: <https://www.alibabacloud.com/help/en/model-studio/model-pricing>

## History

- `2026-07-19` — Added to the list: Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible

---

Generated from `registry.yaml` on 2026-09-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
