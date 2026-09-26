---
layout: default
title: 'Ollama Cloud free tier: limits, free models, verified 2026-09-24'
description: 'Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog. The $0 plan is a wallet rather than a lane: "Starter usage credits included" and "Includes access to starter models", with "Add credits to unlock all models" under them. Neither figure is…'
permalink: /providers/ollama-cloud/
last_modified_at: 2026-09-26
crumb: Ollama Cloud
---

{% raw %}

# Ollama Cloud free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-24 · [ollama.com](https://ollama.com/cloud) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

The $0 plan is a wallet rather than a lane: "Starter usage credits included" and "Includes access to starter models", with "Add credits to unlock all models" under them. Neither figure is published — no credit amount and no starter-model list — and every cloud model carries a per-million-token price on the same page (gpt-oss:20b $0.07 in / $0.30 out, kimi-k3 $3.00 / $15.00). Free gets 1 concurrent request against Pro's 3, and the included usage "resets monthly from the date you signed up" without rolling over. The starter set can only be measured: on 2026-09-02 a key on the $0 plan got answers from gpt-oss:120b, gemma4:31b and nemotron-3-ultra and 402 Payment Required from minimax-m3, so the edge of the set is not the price — nemotron-3-ultra is inside at $0.10/$3.00, minimax-m3 outside at $0.60/$2.40. Read 2026-09-02

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://ollama.com/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Prompt or response data is never logged or trained on. … When Ollama partners with providers, we require no logging, no training, and zero data retention policies in place.” ([source](https://ollama.com/pricing)).

## Connect

- Base URL: `https://ollama.com/v1`
- Key: `OLLAMA_CLOUD_API_KEY` — get one at <https://ollama.com/settings/keys>
- Callable ids: `gpt-oss:120b`, `gemma4:31b`, `nemotron-3-ultra`
- Note: the three ids left are the ones a key on the $0 plan actually answered on 2026-09-02, in that order of speed; minimax-m3 was dropped from this list because the same key gets 402 Payment Required for it. Which models the starter credits reach is published nowhere, so this list is measured rather than read, and /v1/models still lists the whole catalog, starter and metered alike

Try it from your terminal with your key in `OLLAMA_CLOUD_API_KEY` — it goes from your machine to the vendor and nowhere else:

```sh
curl -s https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_CLOUD_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-oss:120b","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the page at <https://ollama.com/cloud>, anchored on `Starter usage credits included`, `Includes access to starter models`; ids checked in <https://ollama.com/v1/models>
- Source: <https://ollama.com/cloud>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-08-14` — Free models changed: dropped gpt-oss, minimax-3, nemotron
- `2026-07-20` — Free models changed: added minimax-3, nemotron; dropped qwen3-coder
- `2026-07-19` — Added: Cloud-hosted open models with free usage tier

---

Generated from `registry.yaml` on 2026-09-26 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
