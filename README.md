<a name="top"></a>
<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="awesome-free-ai-coding — legal free LLM APIs & coding agents, probe-verified" src="assets/banner-light.svg" width="860">
</picture>

[![pipeline](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/update.yml/badge.svg)](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/update.yml)
[![tests](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/ci.yml/badge.svg)](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/ci.yml)
![Verified through](https://img.shields.io/badge/all%20entries%20verified-2026--08--10-3fb950)
![Live entries](https://img.shields.io/badge/live%20entries-38-58a6ff)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

**[🚀 Start now](#-start-in-one-command) · [🤖 Agents](#-coding-agents--clis) · [🔌 APIs](#-llm-apis-with-free-tier) · [🎁 Trials](#-trials-no-card-when-possible) · [🧭 Aggregators](#-aggregators-one-key-many-providers) · [🔧 Plug it in](#-plug-it-into-your-agent) · [📡 How it works](#-how-this-list-stays-fresh)**

</div>

> **Every row on this page is machine-verified.** Legal free tiers, trials and free-model APIs for AI coding — probed twice a week against live model APIs and pricing pages; dead offers drop to the [Archive](#-archive) automatically.

<div align="center">

| **38** | **37** | **2** | **25** | **47** |
|:---:|:---:|:---:|:---:|:---:|
| <sub>live offers</sub> | <sub>need no card</sub> | <sub>need no signup</sub> | <sub>OpenAI-compatible</sub> | <sub>free model families</sub> |

</div>

## 🚀 Start in one command

No account, no key, no card, no waiting — [OVHcloud AI Endpoints](https://endpoints.ai.cloud.ovh.net) answers this in the terminal you already have open:

```bash
curl -s https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-oss-120b","messages":[{"role":"user","content":"2+2?"}]}'
```

Liked it? **[Wire every provider below into your agent ↓](#-plug-it-into-your-agent)** — the configs for [opencode](https://opencode.ai), [LiteLLM](https://docs.litellm.ai) and plain OpenAI SDKs are generated from the same registry and regenerated on every update.

## 📋 The list

<sub>**Card required** — ✅ No means no card is ever asked for · **🧪** — added recently on fresh evidence, provisional until two weeks of probes confirm it · **Verified** — the day a live probe last confirmed the offer, earned by passing it and never typed by hand.</sub>

### 🤖 Coding agents & CLIs
| Tool | What you get | Free models | Limits | Card required | Verified |
|---|---|---|---|---|---|
| **[opencode](https://opencode.ai)** | Open-source TUI/desktop coding agent with free models included via the opencode Zen gateway (Big Pickle, DeepSeek V4 Flash, MiMo-V2.5, Nemotron 3 Ultra); any provider via BYOK too | `big-pickle`, `deepseek-v4-flash`, `mimo-v2.5`, `nemotron-3-ultra` | <sub>Bundled Zen models priced Free (some marked limited-time); frontier models pay-as-you-go</sub> | ✅ No | `2026-08-13` |
| **[Kilo Code](https://kilo.ai)** | Open-source VS Code / JetBrains / CLI agent; its $0 plan routes "Auto Free" to the zero-priced models the Kilo Gateway carries, and the same gateway answers any OpenAI client directly, with BYOK and local models (Ollama, LM Studio) alongside | `nemotron-3-ultra`, `nemotron-3-super`, `north-mini-code`, `step-3.7-flash`, `laguna-s-2.1`, `laguna-xs-2.1` | <sub>$0/mo, no hosted credit required — the free lane is a rotating set of zero-priced ids, 13 of them on 2026-08-14 with Nemotron 3 Ultra among them; everything else runs on pay-as-you-go credits or a Kilo Pass subscription</sub> | ✅ No | `2026-08-13` |
| **[Google Antigravity](https://antigravity.google)** | Google's agent-first IDE and CLI, and where the Gemini CLI free tier went — Gemini CLI and the Code Assist IDE extensions stopped serving free, AI Pro and Ultra users on 2026-06-18. The $0 Individual plan carries the same agent models the paid ones do | `gemini-3.1-pro`, `gemini-3.5-flash`, `claude-opus-4.6`, `claude-sonnet-4.6`, `gpt-oss` | <sub>$0/month, no subscription — Gemini 3.1 Pro, Gemini 3.5 Flash, Claude Sonnet & Opus 4.6 and gpt-oss-120b as agent models, unlimited Tab completions and unlimited Command requests, on a quota refreshed weekly. Google publishes no figure for that quota and says the baseline is set by the capacity it has</sub> | ✅ No | `2026-08-13 🧪` |
| **[OpenAI Codex CLI](https://developers.openai.com/codex/)** | Open-source coding CLI, free by signing in with a $0 ChatGPT Free account; local coding tasks included on all plans | `gpt-5.6` | <sub>Free ChatGPT plan carries the smallest allowance; shared 5-hour rolling + weekly rate limits; local tasks only</sub> | ✅ No | `2026-08-13` |
| **[Crush + Charm Hyper](https://hyper.charm.land)** | Charm's Crush terminal agent with Hyper, its official hosted model gateway; the free plan includes monthly Hypercredits, zero data retention | — | <sub>100 Hypercredits (≈$5) refreshed monthly; Hyper is in private beta (sign up from Crush or the site)</sub> | ✅ No | `2026-08-13` |
| **[CodeGPT](https://www.codegpt.co)** | VS Code / JetBrains coding agent whose $0 plan includes model usage rather than only BYOK — a small daily allowance on its own Economy models, plus BYOK across 15+ providers and local models (Ollama, LM Studio) beside it | — | <sub>10 free interactions a day on Economy models, described as free forever, plus a one-off $1.50 welcome credit for the premium ones; the pricing page says plainly "No credit card required". Unlimited use of the same Economy models is the paid Professional plan at $9-10/mo. CodeGPT does not publish which models the Economy tier routes to, so this row names none</sub> | ✅ No | `2026-08-14 🧪` |

### 🔌 LLM APIs with free tier
| Tool | What you get | Free models | Limits | Card required | Verified |
|---|---|---|---|---|---|
| **[NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com)** | Free hosted NIM endpoints for 100+ models via the free NVIDIA Developer Program (OpenAI-compatible at integrate.api.nvidia.com/v1) | `nemotron` | <sub>Free to start with no card — the account is gated by phone/business-email verification, and access is metered in API credits rather than left open: NVIDIA staff describe the catalog as "a trial experience of NVIDIA NIM limited to 5000 free API credits", 1000 granted on sign-up. That answer is from 2024 and NVIDIA publishes no current figure; reports since put the ceiling at a ~40 req/min rate limit instead. Production use needs NVIDIA AI Enterprise either way</sub> | ✅ No | `2026-08-13` |
| **[Groq](https://groq.com)** | Fast inference free tier | `llama-4`, `qwen3` | <sub>Free tier daily limits per model</sub> | ✅ No | `2026-08-13` |
| **[Cerebras Inference](https://www.cerebras.ai)** | Very fast inference; $5 in free credits on signup, no card | `qwen3` | <sub>$5 in free credits after making an account, usable on all Cerebras-hosted models; free-tier rate limits below the $10 Developer plan</sub> | ✅ No | `2026-08-13` |
| **[OVHcloud AI Endpoints](https://endpoints.ai.cloud.ovh.net)** | EU-hosted serverless open-model API; anonymous tier needs no signup or API key (OpenAI-compatible) | `qwen3`, `gpt-oss` | <sub>No-key anonymous access, rate-limited; free API key raises limits</sub> | ✅ No | `2026-08-13` |
| **[Z.ai (Zhipu GLM)](https://z.ai)** | GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4) | `glm-4.7-flash`, `glm-4.5-flash`, `glm-4.6v-flash` | <sub>GLM-4.7-Flash, GLM-4.5-Flash and the GLM-4.6V-Flash vision model are the three rows z.ai's own price table reads Free on all four columns — every other model there says "Limited-time Free" instead, including the flagship GLM-5.x. Rate-limited</sub> | ✅ No | `2026-08-13` |
| **[LongCat API Platform](https://longcat.chat/platform)** | Meituan's LongCat platform — OpenAI- and Anthropic-compatible API with a recurring daily free token quota | `longcat-2.0`, `longcat-flash` | <sub>100K free tokens/day; a larger free tier for Flash-Lite (50M tokens/day) is announced and the model is uncapped during rollout</sub> | ✅ No | `2026-08-13` |
| **[Cloudflare Workers AI](https://workers.cloudflare.com)** | 10k neurons/day free | `llama-4` | <sub>10,000 neurons/day free allocation</sub> | ✅ No | `2026-08-13` |
| **[Ollama Cloud](https://ollama.com/cloud)** | Cloud-hosted open models with free usage tier | `nemotron`, `minimax-3`, `gpt-oss` | <sub>Free tier with hourly/daily limits; open models only — flagship models (DeepSeek V4, GLM-5, Kimi K2.x, Qwen3.5) need a subscription</sub> | ✅ No | `2026-08-13` |
| **[SEA-LION (AI Singapore)](https://sea-lion.ai)** | AI Singapore's open Southeast-Asian model family behind a first-party OpenAI-compatible API — the vendor hosting its own weights rather than a gateway reselling somebody else's | `qwen-sea-lion-v4.5`, `llama-sea-lion-v3.5` | <sub>Free API meant for prototyping — rate limited at 10 calls/min per user, with no credit or token budget published and no expiry stated; production use is pointed at cloud partners (AWS, Cloudflare, GCP, IBM, NVIDIA, Qualcomm) instead</sub> | ✅ No | `2026-08-13 🧪` |
| **[Mistral La Plateforme](https://mistral.ai)** | Free experiment tier on La Plateforme | `mistral-medium` | <sub>Experiment tier rate limits</sub> | ✅ No | `2026-08-13` |
| **[Pollinations.AI](https://pollinations.ai)** | Open GenAI text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai) | `gpt-oss` | <sub>Anonymous 1 req/15s (no signup); anon text model is GPT-OSS-20B. The documented free registration that lifts this to 1 req/5s is unreachable — its host stopped resolving on 2026-08-14</sub> | ✅ No | `2026-08-13` |
| **[Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio)** | Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible | `qwen3-max`, `qwen3-coder` | <sub>1,000,000 free tokens per model, valid 90 days after activation; Singapore/international scope only</sub> | ✅ No | `2026-08-13` |
| **[Cohere (trial keys)](https://cohere.com)** | Cohere Command models via free trial API keys that never expire | `command-a` | <sub>Trial key: 1,000 API calls/month, rate-limited; production keys unlock paid volume</sub> | ✅ No | `2026-08-13` |
| **[Scaleway Generative APIs](https://www.scaleway.com/en/generative-apis/)** | EU-made serverless LLM API (OpenAI-compatible); 1M free tokens for every new customer | `glm-5.2`, `qwen3` | <sub>1,000,000 free tokens then pay-per-token; a valid payment method is required</sub> | 💳 Yes | `2026-08-13` |
| **[Google AI Studio (Gemini API)](https://aistudio.google.com)** | Free tier for Gemini 2.5 Flash/Pro API | `gemini-2.5` | <sub>Low per-model daily caps on the free tier (see rate-limits page) — among the stingiest here</sub> | ✅ No | `2026-08-13` |
| **[SambaNova Cloud](https://cloud.sambanova.ai)** | Open models on SambaNova's RDU hardware, OpenAI-compatible; the free tier is the one that applies while no payment method is linked, so linking a card is what ends it | `deepseek`, `gpt-oss`, `gemma-4` | <sub>20 req/min, 20 req/day and 200,000 tokens/day per model on the free tier; five models carry it (DeepSeek V3.1/V3.2, Llama 3.3 70B, gpt-oss-120b, Gemma 4)</sub> | ✅ No | `2026-08-13 🧪` |

### 🎁 Trials (no card when possible)
| Tool | What you get | Free models | Limits | Card required | Verified |
|---|---|---|---|---|---|
| **[GitHub Copilot Free](https://github.com/features/copilot)** | Free Copilot plan for individual developers in VS Code, JetBrains, Visual Studio and CLI; completions, limited chat and agent usage | — | <sub>2,000 code completions/month; limited chat & agent requests; auto model selection only</sub> | ✅ No | `2026-08-13` |
| **[Kiro](https://kiro.dev/)** | Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models | `claude-sonnet-4.5`, `qwen3-coder` | <sub>50 credits/month; requires social login or AWS Builder ID; credits do not roll over</sub> | ✅ No | `2026-08-13` |
| **[Google Jules](https://jules.google/)** | Free tier of Google's async cloud coding agent powered by Gemini 2.5 Pro; connects to GitHub repos and works autonomously | `gemini-2.5` | <sub>15 tasks per rolling 24 hours; 3 concurrent tasks</sub> | ✅ No | `2026-08-13` |
| **[Cursor (Hobby)](https://cursor.com/)** | Permanent free Hobby plan of the Cursor AI IDE with limited Agent requests and Tab completions, no credit card | — | <sub>Limited Agent requests and Tab completions; Auto model only; pauses at cap until reset</sub> | ✅ No | `2026-08-13` |
| **[Windsurf](https://windsurf.com)** | Free plan + trial of paid tiers | `claude-haiku`, `gpt-5.2-mini`, `kimi-k2.5` | <sub>Free plan credits</sub> | ✅ No | `2026-08-13` |
| **[Qoder](https://qoder.com)** | Alibaba's agentic coding IDE + CLI; Pro trial with credits on signup, then a free plan with basic models | — | <sub>Trial: 300 credits for 2 weeks; free plan afterwards serves basic models with a daily cap</sub> | ✅ No | `2026-08-13` |
| **[Trae](https://www.trae.ai)** | Free access to frontier models in IDE | — | <sub>Free tier quotas</sub> | ✅ No | `2026-08-13` |
| **[Upstage (Solar API)](https://console.upstage.ai/)** | Upstage Solar LLM API; $10 free credit on signup, no card | `solar-pro-3`, `solar-mini` | <sub>$10 signup credit (see console for validity); pay-as-you-go after</sub> | ✅ No | `2026-08-13` |
| **[AI21 Labs (Jamba)](https://www.ai21.com)** | AI21's Jamba models on a no-card trial credit — hybrid Mamba/attention models built for 256K-token context, so the trial is worth spending on a long file rather than on a chat | `jamba-mini`, `jamba-large` | <sub>$10 of credits for 7 days, stated on AI21's own pricing page, with no card asked for; sign-in is email, Google, GitHub or SSO. The shortest trial window on this page — after it, Jamba Mini is $0.2/$0.4 and Jamba Large $2/$8 per 1M tokens</sub> | ✅ No | `2026-08-14 🧪` |

### 🧭 Aggregators (one key, many providers)
| Tool | What you get | Free models | Limits | Card required | Verified |
|---|---|---|---|---|---|
| **[OpenRouter (free models)](https://openrouter.ai)** | One API key for rotating :free variants of frontier models | `gpt-oss`, `nemotron-3-ultra`, `gemma-4` | <sub>50 req/day free (1000/day with $10 balance)</sub> | ✅ No | `2026-08-13` |
| **[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers)** | Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account | `deepseek`, `qwen3` | <sub>Free users get $0.10/month credits (subject to change); credits apply only on HF-routed requests</sub> | ✅ No | `2026-08-13` |
| **[BazaarLink](https://bazaarlink.ai)** | OpenAI-compatible gateway to 199 models, with two always-free open models and an auto:free router | `deepseek-v4-flash`, `qwen3.7-flash` | <sub>10 req/min and 150 req/day on the free models (x3 for accounts that have topped up); the other 196 models are metered at list rates</sub> | ✅ No | `2026-08-13 🧪` |
| **[Requesty](https://www.requesty.ai)** | OpenAI-compatible router over a 500+ model catalog with routing, caching and fallbacks; ten rows in it are priced 0 and the free plan is the same gateway restricted to those | `nemotron-3-ultra`, `nemotron-3-super`, `gemma-4`, `ling-3.0-tiny` | <sub>Free plan is $0 with no credit card — 200 requests a day, free models only, with routing, caching, fallbacks, spend tracking and EU data residency included; past that the same key moves to pay-as-you-go</sub> | ✅ No | `2026-08-13 🧪` |
| **[Routeway](https://routeway.ai)** | OpenAI-compatible gateway carrying ten live zero-priced :free ids — Step 3.7 Flash, Gemma 4 31B, Nemotron 3 Nano, Poolside Laguna XS.2, gpt-oss-120b and the Llama 3.x line — beside a metered 100+ model catalog | `gpt-oss`, `step-3.7-flash`, `gemma-4`, `llama-3.3` | <sub>Starter plan is free — 200 req/day, one concurrent request, shared low-priority queue and best-effort availability; everything outside the :free ids is pay-as-you-go</sub> | ✅ No | `2026-08-13 🧪` |
| **[TokenRouter (PaleBlueDot)](https://www.tokenrouter.com)** | One zero-priced id — Nemotron 3 Nano Omni, in the default group — inside a 127-model catalog metered at list rates | `nemotron-3-nano-omni` | <sub>the free id sits in the default group and publishes no request cap; the other 126 models are metered at list rates. The zero-priced Kimi K3 this entry was registered for is gone — moonshotai/kimi-k3-free had left the catalog by 2026-08-14 and only the paid moonshotai/kimi-k3 remains</sub> | ✅ No | `2026-08-10 🧪` |
| **[Vercel AI Gateway](https://vercel.com/ai-gateway)** | One OpenAI-compatible endpoint for 300+ models, with $5 of gateway credits included every month and two models that never touch the credit | `laguna-s-2.1-free`, `glm-4.6v-flash` | <sub>$5/month credit at provider list rates, renewed monthly; lower per-model rate limits, no BYOK. Exactly two of the 327 catalogued models are priced 0 in and 0 out — Laguna S 2.1 Free for coding and z.ai's GLM-4.6V-Flash for vision (128k context, images and PDFs, tool use) — and neither draws the credit down. Buying credits ends the monthly free credit</sub> | ✅ No | `2026-08-13 🧪` |

<details>
<summary><b>🧠 Looking for one model in particular?</b> — 47 model families, and everyone who serves them free</summary>
<br>

| Model family | Free at |
|---|---|
| `gpt-oss` | [OpenRouter (free models)](https://openrouter.ai), [Google Antigravity](https://antigravity.google), [OVHcloud AI Endpoints](https://endpoints.ai.cloud.ovh.net), [Ollama Cloud](https://ollama.com/cloud), [Pollinations.AI](https://pollinations.ai), [Routeway](https://routeway.ai), [SambaNova Cloud](https://cloud.sambanova.ai) |
| `qwen3` | [Groq](https://groq.com), [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers), [Cerebras Inference](https://www.cerebras.ai), [OVHcloud AI Endpoints](https://endpoints.ai.cloud.ovh.net), [Scaleway Generative APIs](https://www.scaleway.com/en/generative-apis/) |
| `gemma-4` | [OpenRouter (free models)](https://openrouter.ai), [Requesty](https://www.requesty.ai), [Routeway](https://routeway.ai), [SambaNova Cloud](https://cloud.sambanova.ai) |
| `nemotron-3-ultra` | [opencode](https://opencode.ai), [OpenRouter (free models)](https://openrouter.ai), [Kilo Code](https://kilo.ai), [Requesty](https://www.requesty.ai) |
| `deepseek` | [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers), [SambaNova Cloud](https://cloud.sambanova.ai) |
| `deepseek-v4-flash` | [opencode](https://opencode.ai), [BazaarLink](https://bazaarlink.ai) |
| `gemini-2.5` | [Google Jules](https://jules.google/), [Google AI Studio (Gemini API)](https://aistudio.google.com) |
| `glm-4.6v-flash` | [Z.ai (Zhipu GLM)](https://z.ai), [Vercel AI Gateway](https://vercel.com/ai-gateway) |
| `llama-4` | [Groq](https://groq.com), [Cloudflare Workers AI](https://workers.cloudflare.com) |
| `nemotron` | [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com), [Ollama Cloud](https://ollama.com/cloud) |
| `nemotron-3-super` | [Kilo Code](https://kilo.ai), [Requesty](https://www.requesty.ai) |
| `qwen3-coder` | [Kiro](https://kiro.dev/), [Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio) |
| `step-3.7-flash` | [Kilo Code](https://kilo.ai), [Routeway](https://routeway.ai) |
| `big-pickle` | [opencode](https://opencode.ai) |
| `claude-haiku` | [Windsurf](https://windsurf.com) |
| `claude-opus-4.6` | [Google Antigravity](https://antigravity.google) |
| `claude-sonnet-4.5` | [Kiro](https://kiro.dev/) |
| `claude-sonnet-4.6` | [Google Antigravity](https://antigravity.google) |
| `command-a` | [Cohere (trial keys)](https://cohere.com) |
| `gemini-3.1-pro` | [Google Antigravity](https://antigravity.google) |
| `gemini-3.5-flash` | [Google Antigravity](https://antigravity.google) |
| `glm-4.5-flash` | [Z.ai (Zhipu GLM)](https://z.ai) |
| `glm-4.7-flash` | [Z.ai (Zhipu GLM)](https://z.ai) |
| `glm-5.2` | [Scaleway Generative APIs](https://www.scaleway.com/en/generative-apis/) |
| `gpt-5.2-mini` | [Windsurf](https://windsurf.com) |
| `gpt-5.6` | [OpenAI Codex CLI](https://developers.openai.com/codex/) |
| `jamba-large` | [AI21 Labs (Jamba)](https://www.ai21.com) |
| `jamba-mini` | [AI21 Labs (Jamba)](https://www.ai21.com) |
| `kimi-k2.5` | [Windsurf](https://windsurf.com) |
| `laguna-s-2.1` | [Kilo Code](https://kilo.ai) |
| `laguna-s-2.1-free` | [Vercel AI Gateway](https://vercel.com/ai-gateway) |
| `laguna-xs-2.1` | [Kilo Code](https://kilo.ai) |
| `ling-3.0-tiny` | [Requesty](https://www.requesty.ai) |
| `llama-3.3` | [Routeway](https://routeway.ai) |
| `llama-sea-lion-v3.5` | [SEA-LION (AI Singapore)](https://sea-lion.ai) |
| `longcat-2.0` | [LongCat API Platform](https://longcat.chat/platform) |
| `longcat-flash` | [LongCat API Platform](https://longcat.chat/platform) |
| `mimo-v2.5` | [opencode](https://opencode.ai) |
| `minimax-3` | [Ollama Cloud](https://ollama.com/cloud) |
| `mistral-medium` | [Mistral La Plateforme](https://mistral.ai) |
| `nemotron-3-nano-omni` | [TokenRouter (PaleBlueDot)](https://www.tokenrouter.com) |
| `north-mini-code` | [Kilo Code](https://kilo.ai) |
| `qwen-sea-lion-v4.5` | [SEA-LION (AI Singapore)](https://sea-lion.ai) |
| `qwen3-max` | [Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio) |
| `qwen3.7-flash` | [BazaarLink](https://bazaarlink.ai) |
| `solar-mini` | [Upstage (Solar API)](https://console.upstage.ai/) |
| `solar-pro-3` | [Upstage (Solar API)](https://console.upstage.ai/) |

</details>

<details>
<summary><b>🕰 What changed</b> — the last 10 registry events, and an <a href="https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml">Atom feed</a> of the rest</summary>
<br>

| When | What | Details |
|---|---|---|
| `2026-08-14` | ➖ Delisted **[Novita AI](https://novita.ai/)** | <sub>—</sub> |
| `2026-08-14` | ➕ Added **[CodeGPT](https://www.codegpt.co)** | <sub>VS Code / JetBrains coding agent whose $0 plan includes model usage rather than only BYOK — a small daily allowance on its own Economy models, plus BYOK across 15+ providers and local models (Ollama, LM Studio) beside it</sub> |
| `2026-08-14` | ➕ Added **[AI21 Labs (Jamba)](https://www.ai21.com)** | <sub>AI21's Jamba models on a no-card trial credit — hybrid Mamba/attention models built for 256K-token context, so the trial is worth spending on a long file rather than on a chat</sub> |
| `2026-08-14` | 🔄 Free models **[Vercel AI Gateway](https://vercel.com/ai-gateway)** | <sub>added glm-4.6v-flash</sub> |
| `2026-08-14` | 🔄 Free models **[Z.ai (Zhipu GLM)](https://z.ai)** | <sub>added glm-4.5-flash, glm-4.6v-flash</sub> |
| `2026-08-14` | 🔄 Free models **[Kilo Code](https://kilo.ai)** | <sub>dropped ling-3.0-tiny</sub> |
| `2026-08-14` | 🔄 Free models **[TokenRouter (PaleBlueDot)](https://www.tokenrouter.com)** | <sub>dropped kimi-k3</sub> |
| `2026-08-11` | ➖ Delisted **[Reka AI](https://platform.reka.ai)** | <sub>—</sub> |
| `2026-08-11` | ➕ Added **[SEA-LION (AI Singapore)](https://sea-lion.ai)** | <sub>AI Singapore's open Southeast-Asian model family behind a first-party OpenAI-compatible API — the vendor hosting its own weights rather than a gateway reselling somebody else's</sub> |
| `2026-08-11` | 🔄 Free models **[Routeway](https://routeway.ai)** | <sub>dropped ling-3.0-flash</sub> |

<sub>Every event is a change to what this page publishes: a row appearing, a row dropping to the Archive, a provider's free-model list moving. The full log is [`history.jsonl`](history.jsonl), append-only, one line per event — subscribe to <a href="https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml">the feed</a> instead of re-reading the table.</sub>

</details>

## 📦 Archive

<details>
<summary>Offers that stopped verifying — kept visible so a dead tier is never silently forgotten</summary>
<br>

| Tool | Last verified |
|---|---|
| [GitHub Models](https://github.com/marketplace/models) | `2026-07-30` |
| [MiMo Code](https://mimo.xiaomi.com/coder) | `2026-08-03` |

</details>

<details>
<summary><b>🔭 Checked and not listed</b> — 18 services whose free tier this list could not find or could not verify, and what would change the answer</summary>
<br>

<sub>Nothing here is disqualified — these are legitimate services with no free tier a developer can reach on the date checked. Each verdict expires after 90 days and gets asked again. The reasons live in [`watchlist.yaml`](watchlist.yaml); domains rejected for cause are a separate file, [`blocklist.yaml`](blocklist.yaml).</sub>

| Service | Why it is not on the list | Checked |
|---|---|---|
| **Agnes AI** | The site titles itself "Free Omni-Modal AI API" and then publishes nothing to back it — /pricing and /docs both 404, the pages are a client-rendered shell, and api.agnes-ai.com answers its own JSON 404 for /v1/models, so no catalog, no prices and no quota are public. A free claim with no page behind it is exactly what this list refuses to repeat. <sub>**Reopens if:** Public docs or a keyless catalog appear that state what is free and on what terms.</sub> | `2026-08-14` |
| **Aion Labs** | Re-checked 2026-08-14, and the first reason recorded here was wrong: this is an LLM API vendor, not the email-agent company of the same name. The site sells "Powerful AI Models & Agents" with "access via an OpenAI-compatible API"; api.aionlabs.ai/v1/models answers keyless with four models — aion-2.0, aion-3.0, aion-3.0-mini and aion-rp-llama-3.1-8b, roleplay and storytelling variants of DeepSeek and GLM. The verdict is unchanged for a different reason: every one of the four publishes a price and none of them is zero, the cheapest being aion-3.0-mini at $0.0000007 per prompt token. Note the catalog answers {"models": [...]} rather than the OpenAI {"data": [...]} shape, so an api-models probe here would need that read first. <sub>**Reopens if:** A zero-priced row appears in the api.aionlabs.ai catalog.</sub> | `2026-08-14` |
| **Amazon Q Developer** | The free tier is real — aws.amazon.com/q/developer/pricing is server-rendered and says "Amazon Q Developer offers a perpetual Free Tier with monthly limits", 50 agentic requests a month, "Access latest Claude models", "Use in the IDE or CLI", with IDE limits reserved for AWS Builder ID users. It is not listed because it is the predecessor of an entry this list already carries. AWS has folded both of its surfaces into Kiro: the product page runs an End of support notice reading "On April 30, 2027, AWS will discontinue support for Amazon Q Developer IDE plugins. For capabilities similar to Amazon Q Developer IDE plugins, explore Kiro", and the user guide is blunter about the other half — "The Q CLI has become the Kiro CLI." Kiro is listed with its own perpetual free tier, so carrying both would be one offer twice, the second copy with a shutdown date on it. Recorded because the pricing page still advertises the tier and keeps reaching us through curated feeds. <sub>**Reopens if:** Amazon Q Developer outlives the 2027-04-30 plugin end-of-support as a product with a free tier of its own rather than as a route into Kiro.</sub> | `2026-08-14` |
| **DeepSeek** | Re-checked against api-docs.deepseek.com/quick_start/pricing, which is server-rendered and prices every model — $0.14 in / $0.28 out per 1M for the cache-miss tier, no zero row anywhere. This confirms the 2026-07-27 removal: the 5M-token signup grant that used to be cited for DeepSeek was only ever reported by third parties and appears on no official page. <sub>**Reopens if:** An official DeepSeek page states a free grant or a zero-priced model.</sub> | `2026-08-14` |
| **glhf.chat** | The service does not answer. Both the site and its OpenAI-compatible endpoint return Cloudflare 522 "Connection timed out" — the origin is down, not the edge. An offer that cannot be reached cannot be verified, and a dead host is not evidence of a withdrawn tier either, which is why this is a watch and not a block. <sub>**Reopens if:** The origin answers again and its free lane is still there.</sub> | `2026-08-14` |
| **iFlow** | Reached through the models.dev digest, which lists iflowcn with 14 of 14 models at cost 0 — and a rival list that says iFlow shut down on 2026-04-17, which is wrong. The service is alive: iflow.cn serves 67k characters of a Chinese consumer assistant, and apis.iflow.cn answers 405 Method Not Allowed on /v1/chat/completions, so the route exists and only rejects a GET. What is missing is anything to verify. The catalog path /v1/models answers 404, platform.iflow.cn is a client-rendered shell (3446 characters of text inside 35262 bytes, all of it login config), and the only prices served anywhere are the consumer packages on iflow.cn, whose free column lists its features at "0 次/月" and disabled. A row this list cannot probe is a row it will not carry — the ModelScope bar. <sub>**Reopens if:** apis.iflow.cn serves a model catalog, or iFlow publishes a server-rendered page stating the free quota of its developer platform.</sub> | `2026-08-14` |
| **ModelScope (Alibaba)** | The free tier is real and large — 2,000 API calls a day across a catalog whose keyless api-inference.modelscope.cn/v1/models lists 43 served ids, DeepSeek V4 Flash/Pro, Qwen3.5-397B, Qwen3-Coder, GLM-5.2, MiniMax M3 and Step-3.7-Flash among them. Two things keep it off the list. Registration binds an Alibaba Cloud account and requires real-name verification, which is not something a developer outside mainland China can simply complete, so the offer is not directly usable the way this list means it. And there is nothing to probe — every docs page under /docs/model-service is a client-rendered shell (the served HTML carries 15 characters of text and an empty window.__detail_data__), while the models endpoint publishes no prices and no quota, so a probe there could only ever confirm that ids exist. A row this list cannot verify is a row it will not carry. <sub>**Reopens if:** ModelScope publishes a server-rendered quota page, or the free tier becomes reachable without real-name verification.</sub> | `2026-08-14` |
| **Nebius Token Factory** | Rebranded from Nebius AI Studio — studio.nebius.com now redirects to tokenfactory.nebius.com. Its served pages carry no free tier at all: the pricing page prices storage and GPU-hours, the product page offers a "Start free" button and a sales contact, and the docs quickstart carries no grant, quota or trial. The catalog answers 401 without a key. Nothing here is a free offer a developer can name, so there is nothing to list. <sub>**Reopens if:** Token Factory publishes a signup grant or a free model lane on a served page.</sub> | `2026-08-14` |
| **Novita AI** | Listed here from 2026-07-19 until 2026-08-14, when a hand check found the free lane gone with no announcement anywhere. novita.ai/pricing carries 102 published prices and not one of them is zero; the two models this entry named as free are now billed — inclusionai/ling-3.0-flash at $0.06/$0.18 per Mt and mindai/macaron-v1-venti at 15000/45000 micro-units — and novita.ai/models marks every one of its 102 rows "isFree": false in its own page data. The keyless catalog does carry eleven rows at input_token_price_per_m 0, but they publish no pricing object, four are plainly internal (ai_infer_test_1/2/3, bunny) and the rest 404 on their own model pages, so that is an unpriced shelf and not an offer. What is left is the ~$0.5 signup credit, and a trial is not a tier. The old probe passed through all of this because it anchored on the id "ling-3.0-flash" plus the word "free" — both still on the page — instead of on the price beside the id. <sub>**Reopens if:** novita.ai/pricing shows a zero price, or a model on novita.ai/models carries "isFree": true.</sub> | `2026-08-14` |
| **Nscale** | The serverless inference API exists — inference.api.nscale.com/v1/models answers 401 rather than 404 — but the company's public site is now enterprise AI-cloud marketing with no pricing page (/pricing and /serverless both 404) and the documentation redirects to a login wall. There is no public page stating a free tier and no public page a probe could read, which is two independent reasons the row cannot exist. <sub>**Reopens if:** Nscale puts its serverless pricing or free credits back on a public, server-rendered page.</sub> | `2026-08-14` |
| **SiliconFlow** | siliconflow.com/pricing is server-rendered and states the whole offer in one sentence — "postpaid billing—plus $1 in free credits to get you started". One dollar is a sign-up courtesy, not a free tier: the same reasoning that kept Nous Portal off this list. No model in the pricing tables is priced at zero, and the catalog endpoint answers 401 on both the .com and .cn hosts, so there is no free lane to point an agent at. <sub>**Reopens if:** A zero-priced model appears in the served catalog, or the free grant becomes a recurring quota rather than a one-off dollar.</sub> | `2026-08-14` |
| **Supermaven** | The free tier is real, recurring and cardless — supermaven.com/pricing is server-rendered and states "Free Tier $0 /month", "Fast, high-quality code suggestions", "Works with large codebases". It is completions and nothing else: the same page marks "Adapts to your coding style", the 1M-token context, the largest model and the "$5/month in Supermaven Chat credits" as Pro only, and there is no API. So the free plan hands a developer no model access to point a coding tool at, which is the bar that keeps BYOK-only tools off this list. Copilot Free is listed and this is not for exactly that reason: its free plan carries chat and agent use, not only inline completions. <sub>**Reopens if:** Supermaven's free plan gains chat credits, agent use, or an API endpoint.</sub> | `2026-08-14` |
| **xAI (Grok API)** | docs.x.ai prices every surface — text, Agent, TTS, STT, Imagine — and names no free tier or signup grant. x.ai/api answers HTTP 403 to every non-browser client, so even a stated offer could not be probed from here. The free API credits xAI ran in exchange for data sharing are not on any current page. <sub>**Reopens if:** A free tier or signup grant appears on a page that answers a plain HTTP client.</sub> | `2026-08-14` |
| **LLM7** | Carries a reputation for a shared free tier that its own catalog no longer supports: 35 models on api.llm7.io, every one of them tier `pro` or `turbo` and usage-priced, zero free rows. Curated feeds still credit it with 15 free models, which is how it keeps coming back. <sub>**Reopens if:** A zero-priced row reappears in the api.llm7.io catalog.</sub> | `2026-08-11` |
| **TokenRouter.io** | Legitimate commercial routing layer, and the third unrelated service to carry the TokenRouter name — check the TLD before acting on any lead here, because .com is the listed PaleBlueDot gateway and .me is blocklisted. Its quickstart says "You need at least one AI provider key to route requests" and sends you to platform.openai.com, i.e. BYOK-only with no bundled model usage, and its "Free tier available" covers the routing plan, not tokens — the pricing page's own words are "Pay only for routing and insights". Not blocklisted precisely because nothing is wrong with it. <sub>**Reopens if:** TokenRouter.io starts bundling model usage rather than routing only.</sub> | `2026-08-05` |
| **Arcee (Trinity)** | Direct API grants are application-gated, and an application with a selection step is not an offer a developer can simply use — the same bar that keeps TokenRouter's builder programme out of its entry. The :free Trinity variants that are open live on OpenRouter, which this list already covers. <sub>**Reopens if:** Arcee opens direct API credits without an application.</sub> | `2026-07-22` |
| **Morph (fast-apply)** | The one entry here with a free tier that is probably real — roughly 200 requests a month on the fast-apply model — and no way to verify it: morphllm.com/pricing is client-rendered, so the figure appears in no served HTML. Kept out on the verification rule alone, not on the offer. <sub>**Reopens if:** Morph's docs or pricing become server-rendered with the quota in them.</sub> | `2026-07-22` |
| **Nous Portal** | The free tier is $0.10 a month of credit — decorative rather than usable, and far below what the third-party claim of "50 RPM free" suggested. <sub>**Reopens if:** The monthly grant becomes large enough to run an agent session on.</sub> | `2026-07-22` |

<sub>⏰ — the verdict is older than 90 days, no longer suppresses anything, and is due for a fresh look.</sub>

</details>

## 🔧 Plug it into your agent

Connection details for every live OpenAI-compatible API above — paste the base URL into opencode, Codex CLI, aider, Cline or any OpenAI SDK:

| Provider | Base URL | Key env var | Get a key |
|---|---|---|---|
| **NVIDIA NIM (build.nvidia.com)**<br><sub>the catalog endpoint answers unauthenticated, which is what the probe reads — it confirms NVIDIA still hosts these models, not that your account still has credits to call them with</sub> | `https://integrate.api.nvidia.com/v1` | `NVIDIA_NIM_API_KEY` | [key](https://build.nvidia.com) |
| **OpenRouter (free models)**<br><sub>pick models with the :free suffix; the five listed were zero-priced on 2026-08-11</sub> | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | [key](https://openrouter.ai/settings/keys) |
| **Groq** | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` | [key](https://console.groq.com/keys) |
| **Hugging Face Inference Providers**<br><sub>chat-only; model ids namespaced (openai/gpt-oss-120b)</sub> | `https://router.huggingface.co/v1` | `HUGGINGFACE_INFERENCE_API_KEY` | [key](https://huggingface.co/settings/tokens) |
| **Kilo Code**<br><sub>every id listed is priced 0 — the same catalog meters 346 more. kilo-auto/free and openrouter/free are routers, and nemotron-3.5-content-safety is a guardrail classifier, so none of the three is a coding model. The lane rotates fast — Ling 3.0 Flash left it in 2026-08, ling-3.0-tiny:free stood in its place for three days and was gone by 2026-08-14, with liquid/lfm-2.5-2.6b:free arriving instead — which is why the ids that come and go stay here and out of the Models column</sub> | `https://api.kilo.ai/api/gateway` | `KILO_CODE_API_KEY` | [key](https://app.kilo.ai/profile) |
| **Cerebras Inference** | `https://api.cerebras.ai/v1` | `CEREBRAS_API_KEY` | [key](https://cloud.cerebras.ai) |
| **OVHcloud AI Endpoints**<br><sub>anonymous, rate-limited; free key raises limits</sub> | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | — | not needed |
| **Z.ai (Zhipu GLM)**<br><sub>Coding-Plan keys use https://api.z.ai/api/coding/paas/v4 instead</sub> | `https://api.z.ai/api/paas/v4` | `ZAI_GLM_API_KEY` | [key](https://z.ai/manage-apikey/apikey-list) |
| **LongCat API Platform**<br><sub>Anthropic-compatible sibling at /anthropic/v1/messages; docs include a Claude Code setup guide (cc-switch)</sub> | `https://api.longcat.chat/openai/v1` | `LONGCAT_API_KEY` | [key](https://longcat.chat/platform) |
| **Cloudflare Workers AI**<br><sub>substitute {account_id} with your Cloudflare account ID</sub> | `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1` | `CLOUDFLARE_WORKERS_AI_API_KEY` | [key](https://dash.cloudflare.com/profile/api-tokens) |
| **Ollama Cloud**<br><sub>Free-tier model set verified live 2026-07-20; /v1/models lists the full catalog including subscription-only models</sub> | `https://ollama.com/v1` | `OLLAMA_CLOUD_API_KEY` | [key](https://ollama.com/settings/keys) |
| **SEA-LION (AI Singapore)**<br><sub>the key manager calls it a Trial API Key but publishes no expiry and no credit balance — the documented ceiling is the 10 calls/min rate limit. /v1/models needs the key, so the probe reads the offer page</sub> | `https://api.sea-lion.ai/v1` | `SEA_LION_API_KEY` | [key](https://playground.sea-lion.ai/key-manager) |
| **Upstage (Solar API)** | `https://api.upstage.ai/v1` | `UPSTAGE_API_KEY` | [key](https://console.upstage.ai/api-keys) |
| **Mistral La Plateforme**<br><sub>Experiment tier needs account activation</sub> | `https://api.mistral.ai/v1` | `MISTRAL_API_KEY` | [key](https://console.mistral.ai/api-keys) |
| **Pollinations.AI**<br><sub>anonymous works and needs no key. The optional token that raises the rate limit has no working signup — auth.pollinations.ai, the host the vendor's own APIDOCS still sends you to, stopped resolving (NXDOMAIN from both Cloudflare and Google resolvers, 2026-08-14)</sub> | `https://text.pollinations.ai/openai` | — | not needed |
| **Alibaba Cloud Model Studio (DashScope, international)**<br><sub>international (Singapore) endpoint; keys are region-specific</sub> | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | `ALIBABA_MODEL_STUDIO_API_KEY` | [key](https://modelstudio.console.alibabacloud.com) |
| **Cohere (trial keys)**<br><sub>OpenAI-compatible endpoint; native API lives at https://api.cohere.com/v2</sub> | `https://api.cohere.com/compatibility/v1` | `COHERE_API_KEY` | [key](https://dashboard.cohere.com/api-keys) |
| **Scaleway Generative APIs**<br><sub>non-default project: https://api.scaleway.ai/{project_id}/v1</sub> | `https://api.scaleway.ai/v1` | `SCALEWAY_GENERATIVE_API_KEY` | [key](https://console.scaleway.com) |
| **Google AI Studio (Gemini API)**<br><sub>pass the key as Bearer</sub> | `https://generativelanguage.googleapis.com/v1beta/openai/` | `GOOGLE_AI_STUDIO_API_KEY` | [key](https://aistudio.google.com/apikey) |
| **BazaarLink**<br><sub>only the :free ids and auto:free cost nothing; auto:free picks a free model for you</sub> | `https://bazaarlink.ai/api/v1` | `BAZAARLINK_API_KEY` | [key](https://bazaarlink.ai/keys) |
| **Requesty**<br><sub>the ten ids listed are every row the catalog prices at 0, and the free plan serves those alone — ids here carry no :free suffix, so the price is the only thing separating them from the 585 metered rows beside them. nemotron-3.5-content-safety is a guardrail classifier rather than a coding model</sub> | `https://router.requesty.ai/v1` | `REQUESTY_API_KEY` | [key](https://app.requesty.ai/api-keys) |
| **Routeway**<br><sub>all ten ids are priced 0 and answering — the Free-models column names the four the probe anchors on, because a promo lane that rotates out must not archive a gateway that still has a free tier; laguna-m.1:free is priced 0 too but the catalog still marks it unavailable, so it is left out, and ling-3.0-flash:free left the catalog altogether in 2026-08. Only the :free suffix is zero-priced — the same catalog meters Claude and GPT at list rates. The gateway publishes no legal entity or terms of service and supports users through Discord alone, so treat these ids as a fallback lane, not a dependency</sub> | `https://api.routeway.ai/v1` | `ROUTEWAY_API_KEY` | [key](https://routeway.ai/dashboard/keys) |
| **SambaNova Cloud**<br><sub>model ids are case-sensitive; the catalog publishes list prices for every row, so the free tier is a quota rather than a zero-priced lane</sub> | `https://api.sambanova.ai/v1` | `SAMBANOVA_CLOUD_API_KEY` | [key](https://cloud.sambanova.ai/apis) |
| **TokenRouter (PaleBlueDot)**<br><sub>one id in the catalog is priced 0 and it is the whole free lane here. PaleBlueDot AI runs this gateway on tokenrouter.com; same-name gateways on other TLDs are separate services and their keys do not work here</sub> | `https://api.tokenrouter.com/v1` | `TOKENROUTER_API_KEY` | [key](https://www.tokenrouter.com/console/token) |
| **Vercel AI Gateway**<br><sub>both ids cost nothing; any other Free-Tier-eligible model spends the $5 monthly credit. glm-4.6v-flash is zero here because z.ai prices it at zero itself — its own table reads Free on all four columns while every neighbour reads "Limited-time Free" — so this is a vendor policy rather than a gateway promo lane. inclusionai/ling-3.0-flash-free left the catalog in 2026-08 and the ling-3.0-tiny-free standing where it was publishes an empty pricing object, so nothing there says it is free</sub> | `https://ai-gateway.vercel.sh/v1` | `VERCEL_AI_GATEWAY_API_KEY` | [key](https://vercel.com/dashboard/ai-gateway/api-keys) |

Ready-made artifacts, regenerated on every update:

| File | What it gives you |
|---|---|
| [`configs/opencode.json`](configs/opencode.json) | Drop-in [opencode](https://opencode.ai) config with every provider wired up — keys via `{env:...}`, keyless endpoints work immediately |
| [`configs/free-llm.env.example`](configs/free-llm.env.example) | Commented env exports for any OpenAI-compatible tool |
| [`configs/litellm.yaml`](configs/litellm.yaml) | [LiteLLM](https://docs.litellm.ai) proxy config: `litellm --config configs/litellm.yaml` puts every free model behind one local endpoint |
| [`index.json`](index.json) | Machine-readable registry: `curl -s https://raw.githubusercontent.com/mvalentsev/awesome-free-ai-coding/main/index.json \| jq '.entries[].id'` |
| [`history.jsonl`](history.jsonl) · [feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml) | Append-only log of every change to this list — one JSON object per line, and the same thing as an Atom feed your reader can subscribe to |

## 📡 How this list stays fresh

This repository is an autonomous system, not a hand-curated list:

```mermaid
flowchart LR
    S["🌐 web scout<br/>Tavily · HN · GitHub · feeds · models.dev"] --> L["🧠 LLM extract<br/>(evidence only)"]
    L --> G{"🛡 probe gate"}
    G -->|verified| PR["📬 pull request"]
    PR -->|human merge| R[("registry.yaml")]
    R --> P{"📡 live probes<br/>twice a week"}
    P -->|pass| V["✅ verified date updated"]
    P -->|fail ×3 · stale 60d · shutdown announced| A["📦 Archive"]
    R -->|render| MD["README.md<br/>(this page)"]

    classDef pass fill:#3fb95022,stroke:#3fb950,stroke-width:2px
    classDef drop fill:#f8514922,stroke:#f85149,stroke-width:2px
    classDef human fill:#58a6ff22,stroke:#58a6ff,stroke-width:2px
    classDef store fill:#8957e522,stroke:#8957e5,stroke-width:2px
    class G,P,V pass
    class A drop
    class PR,MD human
    class R store
```

- **Live probes, twice a week.** GitHub Actions hits every entry's public models API or pricing page and re-verifies the free offer. `Verified` dates are earned by passing a probe, never typed by hand.
- **Anchored on the offer, not on the word "free".** Each probe anchors on something that dies with the offer — the free model's id, its quota figure, its price row, or a sentence quoted from the vendor's own page. The word "free" survives on a vendor's page for months after the free tier does not, and so do "hobby" and "monthly credits"; validation rejects all of them. Where a gateway publishes prices, the probe also demands that the free model still costs zero — an id can stay in the catalog long after it stops being free. And a bot wall answering in place of a vendor's page counts as "could not check", never as "the offer is gone".
- **Web-evidence scout.** A discovery layer sweeps Tavily search, Hacker News, GitHub, curated feeds and a digest of every models.dev provider publishing a zero-cost model; an LLM extracts candidates strictly from fetched page evidence — it has no authority to invent anything.
- **Probe-gated proposals.** Every candidate must pass its own live probe before it is even proposed, and lands only through a reviewable pull request. The LLM never writes to this README or to `main`.
- **Self-pruning.** Entries that keep failing probes or stay unverified for 60+ days move to the Archive automatically, as does any entry whose vendor has announced a shutdown date once that day arrives. A newer model generation never archives a row — it just means the row's model list needs a bump, and one a reviewer has already declined is recorded in [`dismissed.yaml`](dismissed.yaml) instead of being proposed again. Rejected-for-cause domains live in [`blocklist.yaml`](blocklist.yaml).
- **A "no" that expires.** Most services checked here are neither listed nor rejected: they are legitimate and simply have nothing free today. Those go to [`watchlist.yaml`](watchlist.yaml) with the date and the reason, which stops the scout re-proposing them and stops a reviewer re-deriving the same answer — and then stops suppressing anything after 90 days, so the question comes back around instead of hardening into a verdict nobody revisits. Every one of them is on this page, above, with what would change the answer.
- **Nothing changes silently.** Every arrival, archival, delisting and free-model change is appended to [`history.jsonl`](history.jsonl) and published as an [Atom feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml) — the log is compared against the list itself rather than against the previous run, so an entry that goes stale without a single field changing is still reported.
- **Zero-secret resilient.** The scout's LLM chain falls back across providers down to a keyless anonymous endpoint, so the pipeline keeps running even with no API keys configured.

## 🤝 Contributing

`registry.yaml` is the single source of truth; this README is generated from it — don't edit it by hand.
Know a legal free offer that's missing? **[Suggest a service](../../issues/new?template=suggest-a-service.yml)** — it will be probed like everything else. Details in [CONTRIBUTING.md](CONTRIBUTING.md).

<div align="center">

**⭐ If this list saved you a credit-card form, star the repo — it keeps the radar visible.**

<sub>Maintained by robots · reviewed by humans · MIT · <a href="#top">back to top ↑</a></sub>

</div>
