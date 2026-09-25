---
layout: default
title: 'Kiro free tier: limits, free models, verified 2026-09-24'
description: Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models. 50 credits/month; requires social login or AWS Builder ID; credits do not roll over; not available in AWS GovCloud, and free-tier requests are always served from…
permalink: /providers/kiro/
---

{% raw %}

# Kiro

🎁 Trials (no card when possible) · no card · **live** — last verified by a probe on 2026-09-24 · [kiro.dev](https://kiro.dev/) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models

## Free models

`claude-sonnet-4.5`, `claude-sonnet-4`, `glm-5`, `minimax-m2.5`, `deepseek-v3.2`, `qwen3-coder-next`, `minimax-m2.1`

## Limits, in the vendor's words

50 credits/month; requires social login or AWS Builder ID; credits do not roll over; not available in AWS GovCloud, and free-tier requests are always served from the US. Kiro's docs settle what those credits reach, in a table with a Free column: ticked for Claude Sonnet 4.5 and 4.0, Auto, GLM-5, Qwen3 Coder Next, DeepSeek 3.2 and MiniMax M2.5 and M2.1; blank for Claude Sonnet 4.6 and 5, every Opus, Haiku 4.5 and all three GPT-5.6 tiers. The pricing page contradicts itself on exactly that point — its plan card and footnote both say Sonnet 4.5, its FAQ prose says the free tier includes Sonnet 4.6 — so read the docs table, not the FAQ (checked 2026-09-25)

## What happens to what you send

What you send may be used to train or improve models unless you turn that off. In the vendor's words: “We may use certain content from Kiro Free Tier and Kiro individual subscribers for service improvement. … Kiro may use this content, for example, to provide better responses to common questions, fix Kiro operational issues, for de-bugging, or for model training.” ([source](https://kiro.dev/docs/privacy-and-security/data-protection/)).

## Connect

No API endpoint to paste: this row is a tool you install or sign in to.

## Evidence

- Probe: the page at <https://kiro.dev/pricing/>, anchored on `kiro free`, `50 credits`
- Source: <https://kiro.dev/pricing/>
- Source: <https://kiro.dev/docs/models>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-09-25` — Free models changed: added claude-sonnet-4, glm-5, minimax-m2.5, qwen3-coder-next; dropped qwen3-coder
- `2026-09-24` — Free models changed: added minimax-m2.1; dropped minimax-2.1
- `2026-08-20` — Free models changed: added deepseek-v3.2, minimax-2.1
- `2026-07-20` — Free models changed: dropped deepseek-v3.2, minimax-2.1
- `2026-07-19` — Free models changed: added claude-sonnet-4.5, deepseek-v3.2, minimax-2.1, qwen3-coder
- `2026-07-19` — Added: Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models

---

Generated from `registry.yaml` on 2026-09-25 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
