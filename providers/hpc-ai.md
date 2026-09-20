---
layout: default
title: 'HPC-AI Model APIs free tier: limits, free models, verified 2026-09-17'
description: OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit. The Model APIs page answers its FAQ "Do you offer a free trial for users?" in the…
permalink: /providers/hpc-ai/
---

{% raw %}

# HPC-AI Model APIs

🎁 Trials (no card when possible) · no card · provisional — added recently, two weeks of probes still to pass · **live** — last verified by a probe on 2026-09-17 · [hpc-ai.com](https://www.hpc-ai.com/model-apis) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit

## Free models

The page this row is verified against names no free model, so the column stays empty; callable ids, where the row has them, are under Connect.

## Limits, in the vendor's words

The Model APIs page answers its FAQ "Do you offer a free trial for users?" in the page's data rather than its text: every user receives $2 "in free credits. New accounts using the invite code" HPCAI-MAPI get $4, and "Supplies are limited". The console's welcome message, shipped in the same page, reads "Free credits have been added to your account — start calling open-source models right away." and "Make your first deposit to unlock higher RPM limits." The keyless model list gives the L0 tier, an account before its first deposit, 5 requests and 2M tokens a minute on 23 of its 24 models (DeepSeek V4 Pro gets 0), and the rate-limit docs say the move to L1 "is triggered by your first deposit rather than by spending". The credit buys list prices, GLM 5.3 Flash at $0.15 in and $0.50 out per million tokens and Kimi K3 at $3 and $15. No page read asks for a card before the credit is spent, and none gives it an expiry. Read 2026-09-17

## Connect

- Base URL: `https://api.hpc-ai.com/inference/v1`
- Key: `HPC_AI_API_KEY` — get one at <https://www.hpc-ai.com/models-console/api-key>
- Callable ids: `zai-org/glm-5.3-flash`, `moonshotai/kimi-k2.7-code`, `minimax/minimax-m3`
- Note: ids are the keyless model list's at www.hpc-ai.com/api/maas/v1/models, 2026-09-17, the quick start's own example being moonshotai/kimi-k2.7-code

## Evidence

- Probe: the page at <https://www.hpc-ai.com/model-apis>, anchored on `Do you offer a free trial for users?` and `in free credits. New accounts using the invite code` in the page's own data; ids checked in <https://www.hpc-ai.com/api/maas/v1/models>
- Source: <https://www.hpc-ai.com/model-apis>
- Source: <https://www.hpc-ai.com/doc/docs/Model-APIs/User-Guides/Rate-Limit/>
- Source: <https://www.hpc-ai.com/doc/docs/Model-APIs/User-Guides/QuickStart/>
- Source: <https://www.hpc-ai.com/api/maas/v1/models>

## History

- *next scheduled run* — Added to the list: OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit

---

Generated from `registry.yaml` on 2026-09-20 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
