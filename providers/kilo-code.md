---
layout: default
title: 'Kilo Code free tier: limits, free models, verified 2026-10-22'
description: 'Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models. Free models: nemotron-3-ultra, nemotron-3-super, north-mini-code, laguna-s-2.1, laguna-xs-2.1, nemotron-3.5-lightning, dots-3-note, nemotron-3-nano-omni. The free-model lineup…'
permalink: /providers/kilo-code/
last_modified_at: 2026-10-22
crumb: Kilo Code
---

{% raw %}

# Kilo Code free tier

🤖 Coding agents & CLIs · no card · not offered in Iran, Syria, Cuba and 1 more place · **live** — last verified by a probe on 2026-10-22 · [kilo.ai](https://kilo.ai) · [back to the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## What you get

Open-source coding agent with an Auto Free mode and a keyless OpenAI-compatible gateway, alongside BYOK and local models

## Free models

[`nemotron-3-ultra`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-ultra/), [`nemotron-3-super`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-super/), [`north-mini-code`](https://mvalentsev.github.io/awesome-free-ai-coding/models/north-mini-code/), [`laguna-s-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-s-2.1/), [`laguna-xs-2.1`](https://mvalentsev.github.io/awesome-free-ai-coding/models/laguna-xs-2.1/), [`nemotron-3.5-lightning`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3.5-lightning/), [`dots-3-note`](https://mvalentsev.github.io/awesome-free-ai-coding/models/dots-3-note/), [`nemotron-3-nano-omni`](https://mvalentsev.github.io/awesome-free-ai-coding/models/nemotron-3-nano-omni/)

## Limits, in the vendor's words

200 requests/hour per IP

The free-model lineup rotates. Auto Free routes over the free models in the catalog's autoRouting list. Other models use pay-as-you-go credits or a Kilo Pass subscription.

## Where it is offered

Not offered in Iran, Syria, Cuba and North Korea ([source](https://kilo.ai/terms), read 2026-09-26). That leaves out under 0.1% of the developers GitHub counts, beyond the countries under comprehensive US embargo ([Innovation Graph](https://innovationgraph.github.com/), 2026 Q1). In the vendor's words: “including Cuba, Iran, North Korea, Syria, or the Crimea, so-called Donetsk People’s Republic, or so-called Luhansk People’s Republic regions of Ukraine”.

## What happens to what you send

What you send may be used to train or improve models. In the vendor's words: “Prompts may be logged by the upstream provider and used to improve their services.” ([source](https://api.kilo.ai/api/gateway/models)).

## Connect

- Base URL: `https://api.kilo.ai/api/gateway`
- Key: none — the lane is anonymous
- Codex CLI: [`configs/codex/kilo-code.config.toml`](https://github.com/mvalentsev/awesome-free-ai-coding/blob/main/configs/codex/kilo-code.config.toml) — copy it to `~/.codex/`, then `codex -p kilo-code`
- Callable ids: `openrouter/free`, `kilo-auto/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `cohere/north-mini-code:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `liquid/lfm-2.5-2.6b:free`, `dots-studio/dots-3-note-preview:free`, `stealth/glyph-cluster`, `nvidia/nemotron-3.5-super-vl:free`, `xingchen-agi/xing4.0-29b-a4b:free`, `minimax/minimax-m3.1-flash:free`, `recursive/flint-v1.0:free`
- Note: Use free IDs without a key; metered IDs require sign-in. kilo-auto/free and openrouter/free choose a free model automatically. LiquidAI advises against agentic coding with lfm-2.5-2.6b.

Try it from your terminal — the lane takes no key:

```sh
curl -s https://api.kilo.ai/api/gateway/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"openrouter/free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```

## Evidence

- Probe: the models catalog at <https://api.kilo.ai/api/gateway/models>, free rows carrying `:free`, each listed family checked for a zero price
- Source: <https://kilo.ai/pricing>
- Source: <https://api.kilo.ai/api/gateway/models>
- Source: <https://kilo.ai/docs/gateway/authentication>
- Source: <https://kilocode.ai>

## History

Each line is a change to what this page publishes, dated the day it reached the list, in UTC.

- `2026-10-22` — Free models changed: dropped inkling-small
- `2026-10-12` — Free models changed: dropped ling-3.0-flash-sante, step-3.7-flash
- `2026-10-05` — Free models changed: dropped qwen3.8-27b
- `2026-10-02` — Free models changed: added qwen3.8-27b
- `2026-09-29` — Free models changed: dropped ling-3.0-flash-fin
- `2026-09-24` — Free models changed: added dots-3-note, inkling-small, ling-3.0-flash-fin, ling-3.0-flash-sante, nemotron-3-nano-omni, nemotron-3.5-lightning
- `2026-08-14` — Free models changed: dropped ling-3.0-tiny
- `2026-08-11` — Free models changed: added laguna-xs-2.1, ling-3.0-tiny, nemotron-3-super
- `2026-08-11` — Free models changed: added laguna-s-2.1, step-3.7-flash; dropped ling-3.0-flash
- `2026-08-05` — Free models changed: added ling-3.0-flash, nemotron-3-ultra, north-mini-code
- `2026-07-19` — Free models changed: dropped claude-sonnet-5, gemini-3.1-pro, gpt-5.5
- `2026-07-19` — Free models changed: added claude-sonnet-5, gemini-3.1-pro, gpt-5.5
- `2026-07-19` — Added: VS Code agent extension with free starter credits

---

Generated from `registry.yaml` on 2026-10-24 and re-verified twice a week; the full list, the Atom feed and the machinery are at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
