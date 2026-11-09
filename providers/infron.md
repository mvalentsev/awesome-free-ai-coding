---
layout: default
title: 'Infron free tier: limits, free models, verified 2026-11-09'
description: OpenAI-compatible model gateway with a shared recurring Free request allowance, unlocked by a retained prepaid balance. Keep at least $5 in account credit to use standard :free models. Free requests do not consume that balance. New accounts start at $0. Top-ups add a 5% platform fee plus $0.35 per…
permalink: /providers/infron/
last_modified_at: 2026-11-09
crumb: Infron
---

{% raw %}

# Infron free tier

🔌 LLM APIs with free tier · no card · requires $5 one-time top-up + 5% fee · provisional — added on 2026-11-01, a regular row from the first probe it passes on or after 2026-11-15 · **live** — last verified by a probe on 2026-11-09 · [infron.ai](https://infron.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible model gateway with a shared recurring Free request allowance, unlocked by a retained prepaid balance

## Free models

No free model family is currently listed here; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

Standard free models: 1,000 requests/day per account. 00:00 UTC

Keep at least $5 in account credit to use standard :free models. Free requests do not consume that balance. New accounts start at $0. Top-ups add a 5% platform fee plus $0.35 per transaction; payment methods include cards and Alipay. Ordinary per-account rate limits also apply. Free routes can use different providers from paid variants, share capacity and have no SLA. The separate Qwen Max Preview promotion ended on July 28, 2026. Unused purchased credit may expire after 365 days. Infron does not store prompts or responses by default; upstream retention varies and an account setting excludes providers that train on prompts.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://infron.ai/terms-of-use), read 2026-10-31).

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “If you opt out of training in your account settings, Infron AI will not route to providers that train.” ([source](https://infronai.gitbook.io/docs/support/privacy-logging)).

## Connect

- Base URL: `https://llm.onerouter.pro/v1`
- Key: `INFRON_API_KEY` — get one at <https://infron.ai/dashboard/apiKeys>
- Callable ids: `qwen/qwen3.8-27b:free`, `qwen/qwen3.8-27b-abliterated-cyber:free`, `internlm/atria-dawn-preview:free`, `apodex/apodex-1.1-mini:free`
- Note: Use exact :free IDs with an Infron account key; the OneRouter API domain is documented by Infron. Their daily request pool is shared, and the required balance is held rather than spent on free calls. Catalog availability is public; authenticated generation and account eligibility have not been checked here.

Try it from your terminal with your key in `INFRON_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://llm.onerouter.pro/v1/chat/completions \
  -H "Authorization: Bearer $INFRON_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3.8-27b:free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://llm.onerouter.pro/v1/models>, each listed family checked for a zero price
- Source: <https://infronai.gitbook.io/docs/overview/free-models>
- Source: <https://infronai.gitbook.io/docs/overview/pricing-and-fee-structure>
- Source: <https://infronai.gitbook.io/docs/support/privacy-logging>
- Source: <https://infronai.gitbook.io/docs/llm-apis>
- Source: <https://infron.ai/terms-of-use>
- Source: <https://infron.ai/privacy-policy>
- Source: <https://llm.onerouter.pro/v1/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-11-01` — Added: OpenAI-compatible model gateway with a shared recurring Free request allowance, unlocked by a retained prepaid balance

---

Generated from `registry.yaml` on 2026-11-09 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
