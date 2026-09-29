---
layout: default
title: 'agnes-2.5-flash free: 2 providers, limits and ids, verified 2026-09-28'
description: agnes-2.5-flash is served free by LLMTR and Agnes AI. None asks for a card. Each one's limits in the vendor's words, the ids to call and the day a live probe last confirmed it.
permalink: /models/agnes-2.5-flash/
last_modified_at: 2026-09-28
crumb: agnes-2.5-flash
---

{% raw %}

# Where agnes-2.5-flash is free

**2 rows on the list serve `agnes-2.5-flash` free:** LLMTR and Agnes AI. None asks for a card. A live probe confirmed each one on 2026-09-28 and reads them again twice a week.

[Every free model](https://mvalentsev.github.io/awesome-free-ai-coding/models/) · [the whole list](https://mvalentsev.github.io/awesome-free-ai-coding/)

## Who serves it free

### [LLMTR](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/)

🧭 Aggregators (one key, many providers) · no card · verified 2026-09-28 · listed since 2026-09-28

Turkish OpenAI-compatible gateway whose free rows answer on a zero balance — ten zero-priced chat ids on 2026-09-27

- Limits, in the vendor's words: A new account calls the free rows before any top-up: the migration guide says "Model kataloğunda ücretsiz olarak işaretlenen bir chat modelini seçin" (pick a chat model marked free in the catalog), and "Bu adım, sıfır bakiye ile gateway ve kullanım kaydı akışının çalıştığını doğrular" (this step checks that the gateway and usage logging work on a zero balance). Four free rows carry a daily quota whose figure is published nowhere (Nemotron 3 Ultra and Super, Qwen3.8 27B, Ling 3.0 Flash Fin); Laguna XS 2.1 is free because "Poolside serves these models free on its own inference API", with "no extra token allowance to track"; dots-3-note-preview closes on 30 September 2026. Paid use is prepaid credit: "An 8% platform margin is added on top of the requested top-up amount" and "We never modify model prices". The privacy page says prompt and response bodies are not written permanently to its usage and billing database ("kalıcı olarak yazılmaz"). Read 2026-09-21
- Base URL: `https://llmtr.com/v1`
- Key: `LLMTR_API_KEY` — get one at <https://llmtr.com/dashboard/api-keys>
- Callable ids: `agnes/agnes-2.5-flash`
- What you send may be used to train or improve models ([the vendor's words](https://llmtr.com/docs/en/gateway/poolside-laguna/)).

### [Agnes AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/agnes-ai/)

🔌 LLM APIs with free tier · no card · verified 2026-09-28 · listed since 2026-09-14

Agnes AI's own models behind an OpenAI-compatible API, with its Flash text models charged at zero today and image generation free beside them

- Limits, in the vendor's words: "Is the API free to use? Yes. Our core AI models are free to use indefinitely", the FAQ says, and the pricing page shows the mechanism: agnes-2.5-flash and agnes-3.0-flash list at $0.05 in / $0.15 out per 1M and are charged $0 — "Cached input, input tokens, and output tokens are currently free for agnes-2.5-flash and agnes-3.0-flash" — while agnes-2.5-pro bills $0.45/$0.90 and the pro beta $0.10/$0.30. The page is candid that the zero is a current price rather than a contract: "Promotional end dates are subject to Agnes AI platform announcements and your account bill". The ceiling is a rate, not a quota: a key that is neither on a paid Token Plan nor enterprise-verified gets 30 requests a minute allowed and 10 effective on text models since 2026-09-23, when "effective text model RPM (requests per minute) limits for free and enterprise users have been reduced by 50%", and no daily figure is published. Image models are free at every resolution too. The terms are governed by Singapore law. The docs live on wiki.agnes-ai.com. Read 2026-09-27
- Base URL: `https://apihub.agnes-ai.com/v1`
- Key: `AGNES_AI_API_KEY` — get one at <https://platform.agnes-ai.com>
- Callable ids: `agnes-2.5-flash`
- What you send may be used to train or improve models unless you turn that off ([the vendor's words](https://wiki.agnes-ai.com/en/docs/privacy-policy)).

## Related models

- [`agnes-3.0-flash`](https://mvalentsev.github.io/awesome-free-ai-coding/models/agnes-3.0-flash/) — free at LLMTR and Agnes AI

---

Generated from `registry.yaml` on 2026-09-29 and re-verified twice a week; every free model on the list is at <https://mvalentsev.github.io/awesome-free-ai-coding/models/>, and the full list, the Atom feed and the machinery at <https://github.com/mvalentsev/awesome-free-ai-coding>.

{% endraw %}
