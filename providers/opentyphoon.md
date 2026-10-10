---
layout: default
title: 'OpenTyphoon (SCB 10X) free tier: limits, free models, verified 2026-10-08'
description: Thai-tuned open models from SCB 10X, the venture arm of Siam Commercial Bank, behind an OpenAI-compatible API whose FAQ calls it a research showcase and free to use. A free research showcase, with higher limits available by email. Usage data is collected to improve the model and API; the vendor…
permalink: /providers/opentyphoon/
last_modified_at: 2026-10-08
crumb: OpenTyphoon (SCB 10X)
---

{% raw %}

# OpenTyphoon (SCB 10X) free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-08 · [opentyphoon.ai](https://opentyphoon.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Thai-tuned open models from SCB 10X, the venture arm of Siam Commercial Bank, behind an OpenAI-compatible API whose FAQ calls it a research showcase and free to use

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

5 requests/second; 200 requests/minute per account per model; for `typhoon-v2.5-30b-a3b-instruct`

A free research showcase, with higher limits available by email. Usage data is collected to improve the model and API; the vendor says it is not shared with third parties. Production users are directed to Together AI. A key is minted in the playground after signup; no page read mentions a card. OCR has its own lower rates, separate from the coding model.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://opentyphoon.ai/tac), read 2026-09-26).

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Yes, we are collecting usage data from the Typhoon API. We use this data to improve the model and the API.” ([source](https://docs.opentyphoon.ai/en/faq/)).

## Connect

- Base URL: `https://api.opentyphoon.ai/v1`
- Key: `OPENTYPHOON_API_KEY` — get one at <https://playground.opentyphoon.ai/api-key>
- Callable ids: `typhoon-v2.5-30b-a3b-instruct`
- Note: Use typhoon-v2.5-30b-a3b-instruct for chat; it is a Thai fine-tune of Qwen3-30B-A3B. Other catalog routes handle OCR or speech.

Try it from your terminal with your key in `OPENTYPHOON_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://api.opentyphoon.ai/v1/chat/completions \
  -H "Authorization: Bearer $OPENTYPHOON_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"typhoon-v2.5-30b-a3b-instruct","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://docs.opentyphoon.ai/en/faq/>, anchored on `the typhoon api is a research showcase and`, `free to use`; ids checked in <https://api.opentyphoon.ai/v1/models>
- Source: <https://docs.opentyphoon.ai/en/faq/>
- Source: <https://docs.opentyphoon.ai/en/rate-limits/>
- Source: <https://api.opentyphoon.ai/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-05` — Added: Thai-tuned open models from SCB 10X, the venture arm of Siam Commercial Bank, behind an OpenAI-compatible API whose FAQ calls it a research showcase and free to use

---

Generated from `registry.yaml` on 2026-10-10 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
