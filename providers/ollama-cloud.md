---
layout: default
title: 'Ollama Cloud free tier: limits, free models, verified 2026-10-05'
description: Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog. The Free plan includes starter usage and starter models, whose amount and list are unpublished. Usage resets monthly from signup and does not roll over; adding credit unlocks all models…
permalink: /providers/ollama-cloud/
last_modified_at: 2026-10-05
crumb: Ollama Cloud
---

{% raw %}

# Ollama Cloud free tier

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-10-05 · [ollama.com](https://ollama.com/cloud) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog

## Free models

The vendor does not say which models the free part reaches, so the column names none.

## Limits, in the vendor's words

Starter usage: Monthly credits allowance: amount not published per account

1 requests at once per account

The Free plan includes starter usage and starter models, whose amount and list are unpublished. Usage resets monthly from signup and does not roll over; adding credit unlocks all models. Per-token catalog prices do not identify the starter set. In a 2026-09-02 test, a Free key answered gpt-oss:120b, gemma4:31b and nemotron-3-ultra but returned 402 for minimax-m3. That measurement does not establish the current starter set.

## Where it is offered

The vendor names no country it keeps the offer from ([source](https://ollama.com/terms), read 2026-09-26).

## What happens to what you send

What you send is not used to train models. In the vendor's words: “Prompt or response data is never logged or trained on. … When Ollama partners with providers, we require no logging, no training, and zero data retention policies in place.” ([source](https://ollama.com/pricing)).

## Connect

- Base URL: `https://ollama.com/v1`
- Key: `OLLAMA_CLOUD_API_KEY` — get one at <https://ollama.com/settings/keys>
- Callable ids: `gpt-oss:120b`, `gemma4:31b`, `nemotron-3-ultra`
- Note: Starter-model eligibility is unpublished. The listed IDs answered a $0-plan key; minimax-m3 returned `402 Payment Required`. /v1/models lists the whole catalog, including models outside the starter allowance.

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

Generated from `registry.yaml` on 2026-10-07 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
