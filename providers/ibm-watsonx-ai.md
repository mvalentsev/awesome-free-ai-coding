---
layout: default
title: 'IBM watsonx.ai (Lite plan) free tier: limits, free models, verified 2026-09-05'
description: IBM's watsonx.ai Runtime on its Lite plan — 300,000 tokens a month of foundation-model inference (Granite, Llama, Mistral and other hosted models) on IBM Cloud, a plan IBM's own docs call free and never bill. "300,000 tokens per month", "20 CUH per month" of compute and "2 inference requests per…
permalink: /providers/ibm-watsonx-ai/
---

{% raw %}

# IBM watsonx.ai (Lite plan)

🔌 LLM APIs with free tier · card required · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-05 · [ibm.com](https://www.ibm.com/products/watsonx-ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

IBM's watsonx.ai Runtime on its Lite plan — 300,000 tokens a month of foundation-model inference (Granite, Llama, Mistral and other hosted models) on IBM Cloud, a plan IBM's own docs call free and never bill

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

"300,000 tokens per month", "20 CUH per month" of compute and "2 inference requests per second", on "A free plan with limited capacity" that "does not support running a foundation model tuning experiment" — the Lite plan of watsonx.ai Runtime as its service-plans page reads on 2026-09-05, with no expiry named. The card is taken at the door and not charged: the sign-up doc says "For your IBM Cloud account, you enter your email address, personal information, and credit card information, which is used to verify your identity" and "Lite plans do not incur charges". Which foundation models the 300,000 tokens reach is on a separate docs page the probe does not read, which is why the Free models column is empty

## Connect

- Base URL: `https://us-south.ml.cloud.ibm.com/ml/v1` (not OpenAI-shaped)
- Key: `IBM_WATSONX_AI_API_KEY` — get one at <https://cloud.ibm.com/iam/apikeys>
- Note: not OpenAI-shaped: the API key is exchanged for an IAM bearer token, chat is POST /ml/v1/text/chat with a project_id in the body and a version date in the query, and the host is per region (us-south.ml.cloud.ibm.com is Dallas). LiteLLM's watsonx provider and the ibm-watsonx-ai SDK wrap it; a plain OpenAI client cannot

## Evidence

- Probe: the page at <https://www.ibm.com/docs/en/watsonx/saas?topic=cloud-watsonxai-runtime-plans>, anchored on `300,000 tokens per month`, `2 inference requests per second`
- Source: <https://www.ibm.com/docs/en/watsonx/saas?topic=cloud-watsonxai-runtime-plans>
- Source: <https://www.ibm.com/docs/en/watsonx/saas?topic=tutorials-signing-up-watsonx>
- Source: <https://www.ibm.com/products/watsonx-ai/pricing>

## History

No recorded event yet — the first scheduled run after a row lands writes its `added` line.

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
