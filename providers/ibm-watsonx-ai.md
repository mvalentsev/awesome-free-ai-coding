---
layout: default
title: 'IBM watsonx.ai (Lite plan) free tier: limits, free models, verified 2026-09-24'
description: IBM's watsonx.ai Runtime on its Lite plan — 300,000 tokens a month of foundation-model inference (Granite, Llama, Mistral and other hosted models) on IBM Cloud, a plan IBM's own docs call free and never bill. "300,000 tokens per month", "20 CUH per month" of compute and "2 inference requests per…
permalink: /providers/ibm-watsonx-ai/
last_modified_at: 2026-09-26
crumb: IBM watsonx.ai (Lite plan)
---

{% raw %}

# IBM watsonx.ai (Lite plan) free tier

🔌 LLM APIs with free tier · card required · not offered in Vietnam, Türkiye, Taiwan and 24 more places · **live** — last verified by a probe on 2026-09-24 · [ibm.com](https://www.ibm.com/products/watsonx-ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

IBM's watsonx.ai Runtime on its Lite plan — 300,000 tokens a month of foundation-model inference (Granite, Llama, Mistral and other hosted models) on IBM Cloud, a plan IBM's own docs call free and never bill

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

"300,000 tokens per month", "20 CUH per month" of compute and "2 inference requests per second", on "A free plan with limited capacity" — the Lite plan of watsonx.ai Runtime as its service-plans page reads on 2026-09-16, with no expiry named. The card is taken at the door and not charged: the sign-up doc says "For your IBM Cloud account, you enter your email address, personal information, and credit card information, which is used to verify your identity" and "Lite plans do not incur charges". Which foundation models the 300,000 tokens reach is on a separate docs page the probe does not read, which is why the Free models column is empty

## Where it is offered

Not offered in Vietnam, Türkiye, Taiwan, Nigeria, Ukraine, Egypt, Saudi Arabia, Switzerland and 19 more places ([source](https://cloud.ibm.com/docs/account?topic=account-account-getting-started), read 2026-09-26). That leaves out 10.2% of the developers GitHub counts, beyond the embargoed countries most offers leave out ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “The following table shows the countries where personal use of the platform not related to business, trade, craft, or professional purposes is not supported”.

## What happens to what you send

What you send is not used to train models. In the vendor's words: “IBM does not use your work to improve IBM models. … The foundation models are hosted in IBM Cloud or AWS; your prompts are not sent to third-party platforms.” ([source](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-security.html?context=wx)).

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

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-05` — Added: IBM's watsonx.ai Runtime on its Lite plan — 300,000 tokens a month of foundation-model inference (Granite, Llama, Mistral and other hosted models) on IBM Cloud, a plan IBM's own docs call free and never bill

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
