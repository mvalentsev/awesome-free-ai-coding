---
layout: default
title: 'Ollama Cloud free tier: limits, free models, verified 2026-09-03'
description: 'Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog. The $0 plan was rewritten between the 2026-08-27 and 2026-08-31 runs, and it is now a wallet rather than a lane: it reads "Starter usage credits included" and "Includes access to starter…'
permalink: /providers/ollama-cloud/
---

{% raw %}

# Ollama Cloud

🔌 LLM APIs with free tier · no card · **live** — last verified by a probe on 2026-09-03 · [ollama.com](https://ollama.com/cloud) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The $0 plan was rewritten between the 2026-08-27 and 2026-08-31 runs, and it is now a wallet rather than a lane: it reads "Starter usage credits included" and "Includes access to starter models", with "Add credits to unlock all models" under them. Neither figure is published — the page names no credit amount and no starter model list, and the cloud-model list it links (ollama.com/search?c=cloud) marks none of them starter. Every cloud model now carries a per-million-token price on that same page: gpt-oss:20b $0.07 in / $0.30 out, minimax-m3 $0.60 / $2.40, kimi-k3 $3.00 / $15.00. Free gets 1 concurrent request against Pro's 3, and the included usage "resets monthly from the date you signed up" and does not roll over. Gone with the rewrite: the $0 "Access cloud models" line this row was probed on, and the per-model usage level 1-4 that stood in for a free-model list. Read 2026-09-02, with the starter set mapped by calling it, since nothing publishes it: from one key on the $0 plan, gpt-oss:120b answered in 1-11s, gemma4:31b in 1-5s and nemotron-3-ultra in 50-279s, all on 2026-09-02, while minimax-m3 answered 402 Payment Required on both 2026-08-31 and 2026-09-02 after serving all month. The 402 is the edge of the starter set rather than a spent balance, and that edge is not the price: nemotron-3-ultra is inside it at $0.10/$3.00 while minimax-m3 is outside it at $0.60/$2.40

## Connect

- Base URL: `https://ollama.com/v1`
- Key: `OLLAMA_CLOUD_API_KEY` — get one at <https://ollama.com/settings/keys>
- Callable ids: `gpt-oss:120b`, `gemma4:31b`, `nemotron-3-ultra`
- Note: the three ids left are the ones a key on the $0 plan actually answered on 2026-09-02, in that order of speed; minimax-m3 was dropped from this list because the same key gets 402 Payment Required for it. Which models the starter credits reach is published nowhere, so this list is measured rather than read, and /v1/models still lists the whole catalog, starter and metered alike

## Evidence

- Probe: the page at <https://ollama.com/cloud>, anchored on `Starter usage credits included`, `Includes access to starter models`; ids checked in <https://ollama.com/v1/models>
- Source: <https://ollama.com/cloud>

## History

- `2026-08-17` — Free models changed: dropped gpt-oss, minimax-3, nemotron
- `2026-07-20` — Free models changed: added minimax-3, nemotron; dropped qwen3-coder
- `2026-07-19` — Added to the list: Cloud-hosted open models with free usage tier

---

Generated from `registry.yaml` on 2026-09-06 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
