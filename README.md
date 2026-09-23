<a name="top"></a>
<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="awesome-free-ai-coding — legal free LLM APIs & coding agents, probe-verified" src="assets/banner-light.svg" width="860">
</picture>

[![pipeline](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/update.yml/badge.svg)](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/update.yml)
[![tests](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/ci.yml/badge.svg)](https://github.com/mvalentsev/awesome-free-ai-coding/actions/workflows/ci.yml)
![Every row verified](https://img.shields.io/badge/every%20row%20verified-2026--09--21%20or%20later-3fb950)
![Live entries](https://img.shields.io/badge/live%20entries-79-58a6ff)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

**[🌐 Website](https://mvalentsev.github.io/awesome-free-ai-coding/) · [🚀 Start here](#-start-here) · [🤖 Agents](#-coding-agents--clis) · [🔌 APIs](#-llm-apis-with-free-tier) · [🎁 Trials](#-trials-no-card-when-possible) · [🧭 Aggregators](#-aggregators-one-key-many-providers) · [🔧 Plug it in](#-plug-it-into-your-agent) · [📡 How it works](#-how-this-list-stays-fresh)**

| **79** | **75** | **7** | **59** | **70** |
|:---:|:---:|:---:|:---:|:---:|
| <sub>live offers</sub> | <sub>need no card</sub> | <sub>need no signup</sub> | <sub>OpenAI-compatible</sub> | <sub>free model families</sub> |

</div>

> **Every row is machine-verified** — legal free tiers, trials and free-model APIs for AI coding, probed twice a week against live model APIs and pricing pages; an offer that dies drops to the [Archive](#-archive) once 3 runs in a row find it gone. Each date below links the row's own page: the quota in the vendor's words, the evidence the probe reads, the history. [The website](https://mvalentsev.github.io/awesome-free-ai-coding/) has every row with a filter box and dark mode.

## 🚀 Start here

**Free is not the same as weak.** These agents run on a $0 plan, ask for no card, and this is what they hand you:

| Agent | Models you get for nothing |
|---|---|
| **[opencode](https://opencode.ai)** | `big-pickle` · `mimo-v2.5` · `ling-3.0-flash-fin` · `nemotron-3-ultra` · `nemotron-3.5-lightning` · `muse-spark-1.3-contributor` |
| **[Kilo Code](https://kilo.ai)** | `nemotron-3-ultra` · `nemotron-3-super` · `north-mini-code` · `step-3.7-flash` · `laguna-s-2.1` · `laguna-xs-2.1` |
| **[Google Antigravity](https://antigravity.google)** | `gemini-3.1-pro` · `gemini-3.8-flash` · `gemini-3.7-flash` · `gemini-3.6-flash` · `claude-opus-4.6` · `claude-sonnet-4.6` · `gpt-oss` |
| **[Freebuff](https://freebuff.com)** | `glm-5.3-flash` · `deepseek-v4.1-flash` |

<sub>Every model name above is read back from the vendor's own API or pricing page twice a week; the quota that comes with it is one click from the [table below](#-coding-agents--clis), on the row's own page.</sub>

**Or pick by what you need:**

| I want… | Start with |
|---|---|
| **An API key that gets the most done for free** | [Google AI Studio (Gemini API)](https://aistudio.google.com) · [Groq](https://groq.com) · [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com) |
| **One key, many free models** | [OpenRouter (free models)](https://openrouter.ai) · [Requesty](https://www.requesty.ai) · [AIHubMix (free models)](https://aihubmix.com) |
| **No account at all** | [Kilo Code](https://kilo.ai) · [LLM7.io](https://llm7.io) · [LLM Tech](https://llmtech.eu) |
| **A trial that asks for no card** | [GitHub Copilot Free](https://github.com/features/copilot) · [Kiro](https://kiro.dev/) · [Google Jules](https://jules.google/) |
| **Claude Code on a free lane** | [OpenRouter (free models)](https://openrouter.ai) · [Requesty](https://www.requesty.ai) · [AIHubMix (free models)](https://aihubmix.com) |

<sub>Each answer is the registry's own order read from the top — of its section, or of every section for no account at all and Claude Code — so a row that stops verifying leaves this table on the run it leaves the list, and the ranking is [explained in CONTRIBUTING](CONTRIBUTING.md#how-rows-are-ordered). The Claude Code line names gateways whose vendor documents an Anthropic-format route, which every run calls; [`configs/claude-code.sh`](configs/claude-code.sh) is one shell function per gateway.</sub>

**No account at all?** [Kilo Code](https://kilo.ai) answers in the terminal you already have open — a rate-limited lane to prove this page is live, not a setup to write code on:

```bash
curl -s https://api.kilo.ai/api/gateway/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"kilo-auto/free","messages":[{"role":"user","content":"2+2? MAKE NO MISTAKES."}]}'
```
<details><summary><sub>no key at all for the free ids, capped at 200 requests per hour per IP; a metered id answers 401 `You need to sign in to use this model`. Every id …</sub></summary><sub>no key at all for the free ids, capped at 200 requests per hour per IP; a metered id answers 401 `You need to sign in to use this model`. Every id listed is one the catalog marks isFree and mayTrainOnYourPrompts. kilo-auto/free leads because it routes over the free models the catalog's autoRouting list names; it and openrouter/free are routers, not models, and nemotron-3.5-content-safety, a guardrail classifier, is left out</sub></details>

**Ready to wire one in?** Base URL and key name for every OpenAI-compatible API on this page are in [`configs/README.md`](configs/README.md), beside drop-in configs for [opencode](https://opencode.ai), [LiteLLM](https://docs.litellm.ai) and [Claude Code](https://code.claude.com/docs) — all generated from the same registry and regenerated on every update.

## 📋 The list

<sub>**💳** beside a name is the whole of the fine print about payment — 4 rows of 79 carry it, and nothing else here asks for a card · **👁** — what you send may be used to train models, in the vendor's own words on the row's page · **🧪** — added recently on fresh evidence, provisional until two weeks of probes confirm it · **Last verified** — the day a live probe last confirmed the offer, earned by passing it and never typed by hand; the date links the row's own page with the quota in the vendor's words, the evidence and the history.</sub>

### 🤖 Coding agents & CLIs
<sub>**8** live · not one of them asks for a card · sorted by how much work you can get done for free</sub>

| Tool | What you get | Free models | Last verified |
|---|---|---|---|
| **[opencode](https://opencode.ai)** 👁 | Open-source coding agent whose opencode Zen gateway prices a rotating set of models at zero — Big Pickle, MiMo-V2.5, Ling 3.0 Flash Fin, Nemotron 3 Ultra, Nemotron 3.5 Lightning, Muse Spark 1.3 Contributor — inside OpenCode only, no sign-in; any provider via BYOK | `big-pickle`, `mimo-v2.5`, `ling-3.0-flash-fin`, `nemotron-3-ultra`, `nemotron-3.5-lightning`, `muse-spark-1.3-contributor` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opencode/) |
| **[Kilo Code](https://kilo.ai)** 👁 | Open-source VS Code / JetBrains / CLI agent whose $0 plan routes "Auto Free" to the models the Kilo Gateway marks free; the same gateway serves them to any OpenAI client without a key, with BYOK and local models alongside | `nemotron-3-ultra`, `nemotron-3-super`, `north-mini-code`, `step-3.7-flash`, `laguna-s-2.1`, `laguna-xs-2.1` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kilo-code/) |
| **[Google Antigravity](https://antigravity.google)** 👁 | Google's agent-first IDE and CLI, and where the Gemini CLI free tier went — Gemini CLI and the Code Assist IDE extensions stopped serving free, AI Pro and Ultra users on 2026-06-18. The $0 Individual plan carries the same agent models the paid ones do | `gemini-3.1-pro`, `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`, `claude-opus-4.6`, `claude-sonnet-4.6`, `gpt-oss` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/antigravity/) |
| **[Freebuff](https://freebuff.com)** 👁 | Ad-funded coding agent — CLI, desktop, web, cloud and chat — with no API key and no card; GLM 5.3 Flash by default, with DeepSeek V4.1 Flash, MiMo 2.6 Flash and Solar Mini 4 among the free hours | `glm-5.3-flash`, `deepseek-v4.1-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freebuff/) |
| **[Cline](https://cline.bot)** 👁 🧪 | Open-source coding agent for VS Code, JetBrains and the terminal; signing in to its own Cline provider unlocks a rotating set of free models, each with a daily allowance, beside pay-as-you-go credits, the $9.99 ClinePass plan and BYOK | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cline/) |
| **[OpenAI Codex CLI](https://learn.chatgpt.com/docs/codex/cli)** | Open-source coding CLI, free by signing in with a $0 ChatGPT Free account; local coding tasks included on all plans | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openai-codex-cli/) |
| **[Crush + Charm Hyper](https://hyper.charm.land)** | Charm's Crush terminal agent with Hyper, its official hosted model gateway; the free plan includes monthly Hypercredits, zero data retention | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/charm-hyper/) |
| **[CodeGPT](https://www.codegpt.co)** | VS Code / JetBrains coding agent whose $0 plan includes model usage rather than only BYOK — a small daily allowance on its own Economy models, plus BYOK across 15+ providers and local models (Ollama, LM Studio) beside it | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/codegpt/) |

### 🔌 LLM APIs with free tier
<sub>**31** live · **29** of them ask for no card · sorted by how much work you can get done for free</sub>

| Tool | What you get | Free models | Last verified |
|---|---|---|---|
| **[Google AI Studio (Gemini API)](https://aistudio.google.com)** 👁 | Free tier on the Gemini API, priced model by model rather than as one account quota | `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.5-flash-lite` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/google-ai-studio/) |
| **[Groq](https://groq.com)** | Fast inference against a free plan Groq publishes as a per-model rate table | `gpt-oss`, `qwen3.6`, `qwen3.8-27b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/groq-free/) |
| **[NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com)** 👁 | Free endpoints for the models build.nvidia.com marks "Free Endpoint", open-weight models from several labs among them, called with a free NVIDIA Developer Program key at integrate.api.nvidia.com/v1 (OpenAI-compatible) | `kimi-k3`, `nemotron-3-ultra`, `nemotron-3-super`, `laguna-xs-2.1` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nvidia-nim/) |
| **[Z.ai (Zhipu GLM)](https://z.ai)** | GLM Flash models free on the API, vision included (OpenAI-compatible at api.z.ai/api/paas/v4) | `glm-4.7-flash`, `glm-4.5-flash`, `glm-4.6v-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zai-glm/) |
| **[Cloudflare Workers AI](https://www.cloudflare.com/products/workers-ai/)** | 10k neurons/day free | `llama-4` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cloudflare-workers-ai/) |
| **[LLM7.io](https://llm7.io)** 🧪 | OpenAI-compatible API with an anonymous tier — no account, no key — of 500,000 tokens a day on its turbo models, GLM 5.3 Flash, MiniMax M2.7 and Codestral among them; a free token doubles it | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llm7/) |
| **[LLM Tech](https://llmtech.eu)** 🧪 | EU provider of one model, Qwen3.8 27B, whose quickstart prints a shared trial key for anyone: 2M tokens a day per address and 4 concurrent requests, tool calls included, no account | `qwen3.8-27b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtech/) |
| **[Hetzner Inference API](https://docs.hetzner.com/general/company-and-policy/experiments/inference/)** | OpenAI-compatible API on Hetzner's own EU hardware, free for as long as the experiment runs | `qwen3.6`, `qwen3.8-27b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hetzner-inference/) |
| **[Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio)** | Free quota for Qwen models on DashScope, international (Singapore) region; OpenAI-compatible | `qwen3.8-max`, `qwen3-max`, `qwen3-coder` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/alibaba-model-studio/) |
| **[Cohere (trial keys)](https://cohere.com)** 👁 | Cohere Command models via free trial API keys that never expire, plus North Mini Code — a 30B/3B Apache-2.0 coding model Cohere prices at zero on every key type | `command-a`, `north-mini-code` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cohere/) |
| **[Mistral Studio](https://mistral.ai)** 👁 | Mistral's Free plan — API keys with $10 a month of included usage, shared by the API, Studio and the Vibe coding CLI, no card | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mistral-free/) |
| **[VLM Run Gateway](https://vlm.run)** 🧪 | OpenAI-compatible gateway for vision and language models whose models on VLM Run's own GPUs, Qwen3.8 27B among them, answer anonymous callers — no signup, no key — at 100 requests a day per IP, in alpha | `qwen3.8-27b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vlm-run-gateway/) |
| **[OVHcloud AI Endpoints](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/)** | EU-hosted serverless open-model API whose anonymous lane needs no signup, no key and no card (OpenAI-compatible) | `gpt-oss`, `qwen3.6`, `qwen3.8-27b`, `qwen3-coder` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ovh-ai-endpoints/) |
| **[ModelScope API-Inference (Alibaba)](https://modelscope.cn)** 🧪 | Alibaba's model community serves 35 models free — DeepSeek V4 Pro, GLM-5.2, MiniMax M3 and Qwen3.8 among them — for 250 魔粒 a day at 0.5 to 2 a call, after Alibaba Cloud real-name verification | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/modelscope/) |
| **[SEA-LION (AI Singapore)](https://sea-lion.ai)** | AI Singapore's open Southeast-Asian model family behind a first-party OpenAI-compatible API — the vendor hosting its own weights rather than a gateway reselling somebody else's | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sea-lion/) |
| **[OpenTyphoon (SCB 10X)](https://opentyphoon.ai)** 👁 | Thai-tuned open models from SCB 10X, the venture arm of Siam Commercial Bank, behind an OpenAI-compatible API whose FAQ calls it a research showcase and free to use | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opentyphoon/) |
| **[Agnes AI](https://agnes-ai.com)** 👁 🧪 | Agnes AI's own models behind an OpenAI-compatible API, with its Flash text models charged at zero today and image generation free beside them | `agnes-3.0-flash`, `agnes-2.5-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/agnes-ai/) |
| **[SenseNova (SenseTime 商汤)](https://www.sensenova.cn)** | SenseTime's own SenseNova models behind an OpenAI-compatible url, free for everyone while the token plan is in public beta | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sensenova/) |
| **[Tencent Cloud TokenHub](https://cloud.tencent.com/document/product/1823)** 🧪 | Tencent Cloud's model platform — Hy3, Kimi K3, GLM-5.3 and MiniMax-M3 among its models — with a one-time grant of a million tokens on its language models, valid a year and no card, on an account that has passed Tencent Cloud real-name verification | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/tencent-tokenhub/) |
| **[FreeInference (Harvard SEAS)](https://freeinference.org)** | Harvard SEAS's MadSys Lab serving open models — DeepSeek V4 Flash, GLM-5.1, GLM 5.3 Flash, MiniMax M3, Qwen3.6 35B — free to every account behind both an OpenAI-shaped and an Anthropic-shaped endpoint, with a documented Claude Code setup | `deepseek-v4-flash`, `glm-5.1`, `glm-5.3-flash`, `minimax-m3`, `qwen3.6` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/freeinference/) |
| **[Ollama Cloud](https://ollama.com/cloud)** | Cloud-hosted open models on a $0 plan that grants starter usage credits for a starter subset of the catalog | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ollama-cloud/) |
| **[Poolside Platform](https://poolside.ai)** 👁 | Free self-serve developer access to the Laguna coding models, direct from the vendor whose models this list already carries second-hand through OpenRouter and Kilo Gateway | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/poolside/) |
| **[Sail Research](https://www.sailresearch.com)** 💳 🧪 | Open-weight models for long-running agents — Kimi K3, GLM-5.3, DeepSeek V4 Pro — behind OpenAI- and Anthropic-compatible APIs, with $5 of free credit every month once a payment method is on the account | `kimi-k3`, `glm-5.3`, `deepseek-v4-pro`, `glm-5.3-flash`, `deepseek-v4-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sail-research/) |
| **[SiliconFlow (China)](https://siliconflow.cn)** 🧪 | China's SiliconFlow prices eight small chat models at ¥0 — Qwen3-8B, GLM-4-9B-0414 and the 29B Xing4.0 among them — for an account verified with Chinese, Hong Kong, Macau or Taiwan papers | `xing4.0-29b`, `qwen3-8b`, `glm-4-9b-0414` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/siliconflow-cn/) |
| **[uncloseai (unturf)](https://uncloseai.com)** | Keyless OpenAI-compatible chat endpoint — no signup, no key, no account | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/uncloseai/) |
| **[Pollinations.AI](https://pollinations.ai)** | Legacy open text API, no signup, OpenAI-compatible (POST text.pollinations.ai/openai), on one model — GPT-OSS 20B | `gpt-oss` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/pollinations/) |
| **[IBM watsonx.ai (Lite plan)](https://www.ibm.com/products/watsonx-ai)** 💳 | IBM's watsonx.ai Runtime on its Lite plan — 300,000 tokens a month of foundation-model inference (Granite, Llama, Mistral and other hosted models) on IBM Cloud, a plan IBM's own docs call free and never bill | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ibm-watsonx-ai/) |
| **[Arli AI](https://www.arliai.com)** 🧪 | OpenAI-compatible inference on open models and their fine-tunes, whose Free plan tries each model five times every two days at 12K tokens of context, one request at a time | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/arli-ai/) |
| **[Bytez](https://bytez.com)** 🧪 | Serverless API over open models, whose Free plan grants $1 of credit every four weeks for open models of up to 7B parameters, one request at a time, with no billing | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bytez/) |
| **[Mixlayer](https://www.mixlayer.com)** 🧪 | Serverless open models priced per token, with one of them at $0 — Qwen3.5 4B as qwen/qwen3.5-4b-free, at 131K context — callable without prepaid credit | `qwen3.5-4b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mixlayer/) |
| **[Yolo-Auto](https://yolo-auto.com)** 🧪 | One model, Qwen3.8 Flash — Qwen's open-weight Qwen3.8-Flash-Next — served on the vendor's own flat-rate API for coding agents; the free plan is a small daily allowance with no card | `qwen3.8-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/yolo-auto/) |

### 🎁 Trials (no card when possible)
<sub>**25** live · not one of them asks for a card · sorted by how much work you can get done for free</sub>

| Tool | What you get | Free models | Last verified |
|---|---|---|---|
| **[GitHub Copilot Free](https://github.com/features/copilot)** 👁 | Free Copilot plan for individual developers in VS Code, JetBrains, Visual Studio and CLI; completions, limited chat and agent usage | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/github-copilot-free/) |
| **[Kiro](https://kiro.dev/)** 👁 | Perpetual free tier of AWS's spec-driven agentic IDE (successor to Amazon Q Developer) with Claude Sonnet 4.5 and open-weight models | `claude-sonnet-4.5`, `qwen3-coder`, `deepseek-v3.2`, `minimax-2.1` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kiro/) |
| **[Google Jules](https://jules.google/)** 👁 | Free tier of Google's async cloud coding agent, on Gemini 3 Flash — its base model on every tier — beside the Gemini 2.5 Pro its plan card names; connects to GitHub repos and works autonomously | `gemini-2.5` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/google-jules/) |
| **[Cursor (Hobby)](https://cursor.com/)** 👁 | Permanent free Hobby plan of the Cursor AI IDE with limited Agent requests and Tab completions, no credit card | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cursor-hobby/) |
| **[Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview)** 🧪 | Google Cloud's express mode: an API key and 90 days of Gemini models within the free tier's quotas, with no billing information, for a new Google Cloud user on a @gmail.com account | `gemini-3.1-pro`, `gemini-3-flash`, `gemini-2.5-pro`, `gemini-2.5-flash` | [`2026-09-23`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vertex-ai-express/) |
| **[Devin Desktop (formerly Windsurf)](https://devin.ai/desktop)** 👁 | Free plan of Cognition's desktop coding agent — the IDE that shipped as Windsurf | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/windsurf/) |
| **[JetBrains AI (AI Free)](https://www.jetbrains.com/ai/)** 👁 🧪 | AI Free in JetBrains IDEs — unlimited code completion on JetBrains' Mellum model and 3 AI Credits ($3) of cloud models every 30 days for chat and agents | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/jetbrains-ai/) |
| **[Qoder](https://qoder.com)** | Alibaba's agentic coding apps — the Qoder desktop agent, Qoder IDE and CLI — with a 2-week Pro trial of 300 credits on signup, then 100 credits a day to claim in the desktop app while that promotion runs | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/qoder/) |
| **[CodeBuddy (Tencent)](https://www.codebuddy.ai)** | Tencent's VS Code / JetBrains / CLI coding agent whose Free plan carries 100 credits a month, a daily activity bonus of 30 and 250 welcome credits, with every model open while the promotion runs | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/codebuddy/) |
| **[TRAE (TraeCode)](https://www.trae.ai)** 👁 | TRAE's AI IDE, TraeCode, whose Free plan runs Auto mode only — no model choice — on a monthly Basic usage allowance of a few dollars and 5,000 autocompletions | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/trae/) |
| **[Regolo AI](https://regolo.ai/pricing/)** | EU (Italian) zero-retention inference; a month of full model access on a daily token allowance, no card | `glm-5.2`, `gpt-oss`, `qwen3.8-27b`, `apertus-70b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/regolo/) |
| **[Upstage (Solar API)](https://console.upstage.ai/)** | Upstage Solar LLM API; $10 free credit on signup, no card | `solar-pro-3`, `solar-mini` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/upstage/) |
| **[Zed](https://zed.dev)** 🧪 | Open-source code editor with a hosted AI agent: a 14-day Pro trial with $5 of GPT-5.6 Luna and unlimited edit predictions, no card, then 2,000 accepted edit predictions on the $0 Personal plan | `gpt-5.6-luna` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/zed/) |
| **[Qodo](https://www.qodo.ai)** | Agentic PR code review plus Git and IDE integrations on a 14-day Pro Team trial with unlimited reviews and credits and no card | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/qodo/) |
| **[The Grid](https://thegrid.ai)** 🧪 | OpenAI- and Anthropic-compatible inference market that sells quality tiers rather than model names — Agent Max was served by Claude Opus 5 in the 30 days to 2026-09-03 — with a $25 signup credit, for a limited time | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/the-grid/) |
| **[Dahl Inference](https://inference.dahl.global)** 🧪 | An OpenAI-compatible gateway to open models served by the Gonka decentralized GPU network — GLM-5.3-Flash, DeepSeek V4 Flash and MiniMax M2.7 — whose sign-up asks for a username and nothing else and puts 100 million tokens in the account | `glm-5.3-flash`, `deepseek-v4-flash`, `minimax-m2.7` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/dahl-inference/) |
| **[Sarvam AI](https://www.sarvam.ai)** 👁 | India's Sarvam AI credits every new account ₹100 that never expire, spendable on any of its APIs — including its own Sarvam-105B chat model on an OpenAI-shaped endpoint | `sarvam-105b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sarvam/) |
| **[HPC-AI Model APIs](https://www.hpc-ai.com/model-apis)** 🧪 | OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/hpc-ai/) |
| **[Inception Labs (Mercury)](https://platform.inceptionlabs.ai)** 👁 | A signup grant on the Mercury diffusion models — Mercury 2.5 and Mercury 2 for chat, Mercury Edit 2 for fill-in-the-middle and code edits; the last is the reason this row is here, since an FIM endpoint is what an IDE completion plugin actually calls | `mercury-2.5`, `mercury-2`, `mercury-edit-2` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/inception-labs/) |
| **[Blue Claw Network](https://blueclaw.network)** 🧪 | OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/blue-claw/) |
| **[Fireworks AI](https://fireworks.ai)** 🧪 | Serverless inference on open-weight models — Kimi K3, GLM 5.3, DeepSeek V4.1 Flash among them — with a one-time $1 of credit that is spent without a card, at 10 requests a minute until a payment method is added | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/fireworks-ai/) |
| **[RouterPlex](https://routerplex.com)** 🧪 | A one-time $1 of free credit on a prepaid reseller that bills 56 models at catalog rates with 0% markup, no card — one key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routerplex/) |
| **[abliteration.ai](https://abliteration.ai)** 🧪 | OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/abliteration-ai/) |
| **[Impossibl](https://impossibl.com)** 🧪 | Prepaid gateway at provider list prices over 128 models, Claude, GPT, Gemini, DeepSeek and GLM among them, whose keyless sign-up funds an account with $0.05 and adds $1 once a person claims it by email — no card | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/impossibl/) |
| **[Standard Compute](https://standardcompute.com)** | A one-time $0.25 of smart-routed compute on a flat-rate agent gateway, no card — a real key on both wires, OpenAI-compatible Chat Completions and an Anthropic Messages base Claude Code takes as it is | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/standardcompute/) |

### 🧭 Aggregators (one key, many providers)
<sub>**15** live · **13** of them ask for no card · sorted by how much work you can get done for free</sub>

| Tool | What you get | Free models | Last verified |
|---|---|---|---|
| **[OpenRouter (free models)](https://openrouter.ai)** 👁 | One API key for a rotating set of :free model variants, open-weight and stealth models among them | `nemotron-3-ultra`, `gemma-4` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/openrouter-free/) |
| **[Requesty](https://www.requesty.ai)** 👁 | OpenAI-compatible router over a 690+ model catalog with routing, caching and fallbacks; twelve rows in it are priced 0 and the free plan is the same gateway restricted to those | `nemotron-3-ultra`, `nemotron-3-super`, `gemma-4`, `ling-3.0-tiny`, `muse-glimmer-30b`, `nemotron-3.5-lightning` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/requesty/) |
| **[AIHubMix (free models)](https://aihubmix.com)** | One OpenAI-compatible gateway over 800+ models, dozens of which the platform prices at 0 and subsidises itself — GLM-5.3 and Kimi K3 coding routes among them — with an Anthropic-format /v1/messages too, so a free id can back Claude Code | `glm-5.3`, `kimi-k3`, `glm-5`, `mimo-v2.5`, `north-mini-code` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aihubmix/) |
| **[Routeway](https://routeway.ai)** | OpenAI-compatible gateway whose :free lane rotates — three zero-priced chat models on 2026-09-23, Meta's Muse Glimmer 30B, DeepSeek V4 Flash and MiniMax M2.7 — beside 269 metered rows in the same catalog | `deepseek-v4-flash`, `minimax-m2.7`, `muse-glimmer-30b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/routeway/) |
| **[LLMTR](https://llmtr.com)** 👁 | Turkish OpenAI-compatible gateway whose free rows answer on a zero balance — nine zero-priced chat ids on 2026-09-23, Nemotron 3 Ultra, Qwen3.8 27B and Agnes 3.0 Flash among them | `nemotron-3-ultra` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/llmtr/) |
| **[Vercel AI Gateway](https://vercel.com/ai-gateway)** 💳 👁 | One OpenAI-compatible endpoint for 360+ models, with $5 of gateway credits every month once the team has a payment method on file, and three language models priced at zero that never touch the credit | `laguna-s-2.1`, `ling-3.0-flash-fin`, `ling-3.0-flash-sante` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/vercel-ai-gateway/) |
| **[BazaarLink](https://bazaarlink.ai)** | OpenAI-compatible gateway to a 173-id catalog whose free page counts two models on 2026-09-14 — Qwen3.7 Flash and DeepSeek V4 Flash 0731 — beside the auto:free router | `qwen3.7-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/bazaarlink/) |
| **[Nous Portal (Hermes Agent)](https://portal.nousresearch.com)** 👁 🧪 | Nous Research's inference portal behind its Hermes Agent: a $0 Free plan limited to the models it prices at zero — seven on 2026-09-18, Step 3.7 Flash and Laguna S 2.1 among them — on an OpenAI-compatible API | `step-3.7-flash`, `laguna-s-2.1` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/nous-portal/) |
| **[TokenRouter (PaleBlueDot)](https://www.tokenrouter.com)** | One zero-priced id — Nemotron 3 Nano Omni, in the default group — inside a 140-row catalog that meters the rest | `nemotron-3-nano-omni` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/tokenrouter/) |
| **[Token Harbor](https://tokenharbor.ai)** 👁 🧪 | OpenAI- and Anthropic-compatible gateway with a standing $0 plan: a rotating lineup of :free ids, DeepSeek V4.1 Flash and MiMo V2.6 Flash among them, on a value-based allowance per rolling 7-day period, no card | `deepseek-v4.1-flash` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/token-harbor/) |
| **[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers)** | Routed access to 200+ models across providers (Groq, Cerebras, Together, etc.) with a free HF account | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/huggingface-inference/) |
| **[Opper](https://opper.ai)** 🧪 | EU-hosted gateway over 700+ models whose free models — Gemma 4 31B and Gemma 4 26B on Google's route, Laguna S 2.1 and XS 2.1 through Poolside — answer an account with no card on file; every other model needs a card and credits | `gemma-4-31b` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/opper/) |
| **[MegaNova](https://meganova.ai)** | OpenAI-compatible gateway whose no-card Tier 1 account gets 50 free requests a day on each of Mistral Small 3.2 and the house Manta routers — 550 a day across its free rows | `mistral-small-3.2` | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/meganova/) |
| **[Moark (Gitee AI)](https://moark.com)** 🧪 | Gitee's model platform, formerly Gitee AI — 200+ open models behind OpenAI- and Anthropic-compatible APIs — whose free experience token gives every user 100 calls a day across its featured models, with nothing bought | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/moark/) |
| **[Experiential Labs](https://www.experientiallabs.ai)** 💳 🧪 | An open-source AI gateway backed by Y Combinator — every hosted provider behind one OpenAI-compatible key at the providers' list prices — whose free plan carries 500 credits ($5) a month after a one-time $1 card check | — | [`2026-09-21`](https://mvalentsev.github.io/awesome-free-ai-coding/providers/experiential-labs/) |

<details>
<summary><b>🧠 Looking for one model in particular?</b> — 70 model families, and everyone who serves them free</summary>
<br>

| Model family | Free at |
|---|---|
| `nemotron-3-ultra` | [opencode](https://opencode.ai), [OpenRouter (free models)](https://openrouter.ai), [Kilo Code](https://kilo.ai), [Requesty](https://www.requesty.ai), [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com), [LLMTR](https://llmtr.com) |
| `qwen3.8-27b` | [Groq](https://groq.com), [LLM Tech](https://llmtech.eu), [Hetzner Inference API](https://docs.hetzner.com/general/company-and-policy/experiments/inference/), [Regolo AI](https://regolo.ai/pricing/), [VLM Run Gateway](https://vlm.run), [OVHcloud AI Endpoints](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/) |
| `gpt-oss` | [Groq](https://groq.com), [Google Antigravity](https://antigravity.google), [Regolo AI](https://regolo.ai/pricing/), [OVHcloud AI Endpoints](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/), [Pollinations.AI](https://pollinations.ai) |
| `deepseek-v4-flash` | [Routeway](https://routeway.ai), [Dahl Inference](https://inference.dahl.global), [FreeInference (Harvard SEAS)](https://freeinference.org), [Sail Research](https://www.sailresearch.com) 💳 |
| `glm-5.3-flash` | [Freebuff](https://freebuff.com), [Dahl Inference](https://inference.dahl.global), [FreeInference (Harvard SEAS)](https://freeinference.org), [Sail Research](https://www.sailresearch.com) 💳 |
| `qwen3.6` | [Groq](https://groq.com), [Hetzner Inference API](https://docs.hetzner.com/general/company-and-policy/experiments/inference/), [OVHcloud AI Endpoints](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/), [FreeInference (Harvard SEAS)](https://freeinference.org) |
| `kimi-k3` | [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com), [AIHubMix (free models)](https://aihubmix.com), [Sail Research](https://www.sailresearch.com) 💳 |
| `laguna-s-2.1` | [Kilo Code](https://kilo.ai), [Vercel AI Gateway](https://vercel.com/ai-gateway) 💳, [Nous Portal (Hermes Agent)](https://portal.nousresearch.com) |
| `nemotron-3-super` | [Kilo Code](https://kilo.ai), [Requesty](https://www.requesty.ai), [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com) |
| `north-mini-code` | [Kilo Code](https://kilo.ai), [AIHubMix (free models)](https://aihubmix.com), [Cohere (trial keys)](https://cohere.com) |
| `qwen3-coder` | [Kiro](https://kiro.dev/), [Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio), [OVHcloud AI Endpoints](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/) |
| `deepseek-v4.1-flash` | [Freebuff](https://freebuff.com), [Token Harbor](https://tokenharbor.ai) |
| `gemini-3.1-pro` | [Google Antigravity](https://antigravity.google), [Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview) |
| `gemini-3.7-flash` | [Google AI Studio (Gemini API)](https://aistudio.google.com), [Google Antigravity](https://antigravity.google) |
| `gemini-3.8-flash` | [Google AI Studio (Gemini API)](https://aistudio.google.com), [Google Antigravity](https://antigravity.google) |
| `gemma-4` | [OpenRouter (free models)](https://openrouter.ai), [Requesty](https://www.requesty.ai) |
| `glm-5.3` | [AIHubMix (free models)](https://aihubmix.com), [Sail Research](https://www.sailresearch.com) 💳 |
| `laguna-xs-2.1` | [Kilo Code](https://kilo.ai), [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com) |
| `ling-3.0-flash-fin` | [opencode](https://opencode.ai), [Vercel AI Gateway](https://vercel.com/ai-gateway) 💳 |
| `mimo-v2.5` | [opencode](https://opencode.ai), [AIHubMix (free models)](https://aihubmix.com) |
| `minimax-m2.7` | [Routeway](https://routeway.ai), [Dahl Inference](https://inference.dahl.global) |
| `muse-glimmer-30b` | [Requesty](https://www.requesty.ai), [Routeway](https://routeway.ai) |
| `nemotron-3.5-lightning` | [opencode](https://opencode.ai), [Requesty](https://www.requesty.ai) |
| `step-3.7-flash` | [Kilo Code](https://kilo.ai), [Nous Portal (Hermes Agent)](https://portal.nousresearch.com) |
| `agnes-2.5-flash` | [Agnes AI](https://agnes-ai.com) |
| `agnes-3.0-flash` | [Agnes AI](https://agnes-ai.com) |
| `apertus-70b` | [Regolo AI](https://regolo.ai/pricing/) |
| `big-pickle` | [opencode](https://opencode.ai) |
| `claude-opus-4.6` | [Google Antigravity](https://antigravity.google) |
| `claude-sonnet-4.5` | [Kiro](https://kiro.dev/) |
| `claude-sonnet-4.6` | [Google Antigravity](https://antigravity.google) |
| `command-a` | [Cohere (trial keys)](https://cohere.com) |
| `deepseek-v3.2` | [Kiro](https://kiro.dev/) |
| `deepseek-v4-pro` | [Sail Research](https://www.sailresearch.com) 💳 |
| `gemini-2.5` | [Google Jules](https://jules.google/) |
| `gemini-2.5-flash` | [Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview) |
| `gemini-2.5-pro` | [Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview) |
| `gemini-3-flash` | [Gemini Enterprise Agent Platform express mode (formerly Vertex AI)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/express-mode/overview) |
| `gemini-3.5-flash-lite` | [Google AI Studio (Gemini API)](https://aistudio.google.com) |
| `gemini-3.6-flash` | [Google Antigravity](https://antigravity.google) |
| `gemma-4-31b` | [Opper](https://opper.ai) |
| `glm-4-9b-0414` | [SiliconFlow (China)](https://siliconflow.cn) |
| `glm-4.5-flash` | [Z.ai (Zhipu GLM)](https://z.ai) |
| `glm-4.6v-flash` | [Z.ai (Zhipu GLM)](https://z.ai) |
| `glm-4.7-flash` | [Z.ai (Zhipu GLM)](https://z.ai) |
| `glm-5` | [AIHubMix (free models)](https://aihubmix.com) |
| `glm-5.1` | [FreeInference (Harvard SEAS)](https://freeinference.org) |
| `glm-5.2` | [Regolo AI](https://regolo.ai/pricing/) |
| `gpt-5.6-luna` | [Zed](https://zed.dev) |
| `ling-3.0-flash-sante` | [Vercel AI Gateway](https://vercel.com/ai-gateway) 💳 |
| `ling-3.0-tiny` | [Requesty](https://www.requesty.ai) |
| `llama-4` | [Cloudflare Workers AI](https://www.cloudflare.com/products/workers-ai/) |
| `mercury-2` | [Inception Labs (Mercury)](https://platform.inceptionlabs.ai) |
| `mercury-2.5` | [Inception Labs (Mercury)](https://platform.inceptionlabs.ai) |
| `mercury-edit-2` | [Inception Labs (Mercury)](https://platform.inceptionlabs.ai) |
| `minimax-2.1` | [Kiro](https://kiro.dev/) |
| `minimax-m3` | [FreeInference (Harvard SEAS)](https://freeinference.org) |
| `mistral-small-3.2` | [MegaNova](https://meganova.ai) |
| `muse-spark-1.3-contributor` | [opencode](https://opencode.ai) |
| `nemotron-3-nano-omni` | [TokenRouter (PaleBlueDot)](https://www.tokenrouter.com) |
| `qwen3-8b` | [SiliconFlow (China)](https://siliconflow.cn) |
| `qwen3-max` | [Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio) |
| `qwen3.5-4b` | [Mixlayer](https://www.mixlayer.com) |
| `qwen3.7-flash` | [BazaarLink](https://bazaarlink.ai) |
| `qwen3.8-flash` | [Yolo-Auto](https://yolo-auto.com) |
| `qwen3.8-max` | [Alibaba Cloud Model Studio (DashScope, international)](https://www.alibabacloud.com/en/product/modelstudio) |
| `sarvam-105b` | [Sarvam AI](https://www.sarvam.ai) |
| `solar-mini` | [Upstage (Solar API)](https://console.upstage.ai/) |
| `solar-pro-3` | [Upstage (Solar API)](https://console.upstage.ai/) |
| `xing4.0-29b` | [SiliconFlow (China)](https://siliconflow.cn) |

</details>

<details>
<summary><b>🕰 What changed</b> — the last 10 registry events, and an <a href="https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml">Atom feed</a> of each new one</summary>
<br>

| When | What | Details |
|---|---|---|
| `2026-09-21` | 🔄 Free models **[AIHubMix (free models)](https://aihubmix.com)** | <sub>dropped gpt-oss</sub> |
| `2026-09-21` | 🔄 Free models **[Regolo AI](https://regolo.ai/pricing/)** | <sub>dropped llama-3.3</sub> |
| `2026-09-21` | ➕ Added **[abliteration.ai](https://abliteration.ai)** | <sub>OpenAI- and Anthropic-compatible API for three uncensored reasoning models, the large one derived from GLM-5.3, that opens with a one-credit free preview and no card</sub> |
| `2026-09-21` | ➕ Added **[Arli AI](https://www.arliai.com)** | <sub>OpenAI-compatible inference on open models and their fine-tunes, whose Free plan tries each model five times every two days at 12K tokens of context, one request at a time</sub> |
| `2026-09-21` | ➕ Added **[Blue Claw Network](https://blueclaw.network)** | <sub>OpenAI-compatible endpoint that routes calls to a network of independent GPU operators running open models; every new account starts with a $5 welcome credit, and no card is asked to start</sub> |
| `2026-09-21` | ➕ Added **[Bytez](https://bytez.com)** | <sub>Serverless API over open models, whose Free plan grants $1 of credit every four weeks for open models of up to 7B parameters, one request at a time, with no billing</sub> |
| `2026-09-21` | ➕ Added **[Fireworks AI](https://fireworks.ai)** | <sub>Serverless inference on open-weight models — Kimi K3, GLM 5.3, DeepSeek V4.1 Flash among them — with a one-time $1 of credit that is spent without a card, at 10 requests a minute until a payment method is added</sub> |
| `2026-09-21` | 🔄 Free models **[Groq](https://groq.com)** | <sub>added qwen3.8-27b; dropped qwen3.8</sub> |
| `2026-09-21` | 🔄 Free models **[Hetzner Inference API](https://docs.hetzner.com/general/company-and-policy/experiments/inference/)** | <sub>added qwen3.8-27b; dropped qwen3.8</sub> |
| `2026-09-21` | ➕ Added **[HPC-AI Model APIs](https://www.hpc-ai.com/model-apis)** | <sub>OpenAI-compatible APIs over 24 models, GLM 5.3 Flash, Kimi K3 and MiniMax M3 among them, with $2 of free credit for every user — $4 with the vendor's invite code — at 5 requests a minute until a first deposit</sub> |

<sub>Every event is a change to what this page publishes: a row appearing, a row dropping to the Archive, a provider's free-model list moving. The full log is [`history.jsonl`](history.jsonl), append-only, one line per event — subscribe to <a href="https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml">the feed</a> instead of re-reading the table.</sub>

</details>

## 📦 Archive

<details>
<summary>16 rows this list carried and carries no more, each with why it left — kept so a dead tier is never silently forgotten</summary>
<br>

| Tool | Why it left |
|---|---|
| [SambaNova Cloud](https://mvalentsev.github.io/awesome-free-ai-coding/providers/sambanova-cloud/) | <details><summary><sub>delisted on 2026-09-23: new accounts get no free usage — the console's Free plan has read "Add a payment method and purchase credits to run your …</sub></summary><sub>delisted on 2026-09-23: new accounts get no free usage — the console's Free plan has read "Add a payment method and purchase credits to run your first requests" since 2026-08, where until 2026-06-20 it read "free API credits. No credit card required"; only the docs still describe a free tier</sub></details> |
| [Scaleway Generative APIs](https://mvalentsev.github.io/awesome-free-ai-coding/providers/scaleway-generative/) | <sub>delisted on 2026-09-16: 1,000,000 free tokens once per customer, and "Ordering Scaleway resources requires a valid credit card" — a one-off credit behind a card, which CONTRIBUTING does not admit</sub> |
| [Kenari](https://mvalentsev.github.io/awesome-free-ai-coding/providers/kenari/) | <sub>delisted on 2026-09-16: rejected for cause — the operator's own JavaScript bundle showed its capacity coming from pooled ChatGPT and Codex OAuth credentials, captcha solvers and a proxy pool that multiplies per-IP free quotas</sub> |
| [Infomaniak AI Services](https://mvalentsev.github.io/awesome-free-ai-coding/providers/infomaniak-ai/) | <sub>delisted on 2026-09-16: a one-month wallet of a million credits, and "A credit card is required to start using the API" — a one-off credit behind a card, which CONTRIBUTING does not admit</sub> |
| [Cerebras Inference](https://mvalentsev.github.io/awesome-free-ai-coding/providers/cerebras-free/) | <sub>delisted on 2026-09-16: its only free offer was $5 of credit granted after a verified payment method is added, expiring in 30 days — a one-off credit behind a card, which CONTRIBUTING does not admit</sub> |
| [Novita AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/novita/) | <sub>delisted on 2026-08-14: the free lane ended without an announcement — both models the row named free were billed, and not one of the 102 prices on novita.ai/pricing was zero</sub> |
| [LongCat API Platform](https://mvalentsev.github.io/awesome-free-ai-coding/providers/longcat/) | <sub>delisted on 2026-08-14: the daily free quota was gone before the row was listed — the change log retired the Flash line on 2026-05-29 and switched billing on for LongCat-2.0 on 2026-06-30, and no LongCat page still published the 100K tokens a day</sub> |
| [Reka AI](https://mvalentsev.github.io/awesome-free-ai-coding/providers/reka/) | <sub>delisted on 2026-08-11: the $10 of free credits a month rested on one dated announcement post; no live Reka page corroborated a recurring grant, and the platform sells pay-as-you-go credits</sub> |
| [AI21 Labs (Jamba)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/ai21-labs/) | <sub>vendor-announced shutdown on 2026-08-09</sub> |
| [DeepSeek Platform](https://mvalentsev.github.io/awesome-free-ai-coding/providers/deepseek/) | <sub>delisted on 2026-07-27: the 5M-token signup grant was only ever reported by third parties, and DeepSeek's own pricing page prices every model and names no free grant</sub> |
| [MiMo Code](https://mvalentsev.github.io/awesome-free-ai-coding/providers/mimo-code/) | <sub>vendor-announced shutdown on 2026-07-26</sub> |
| [Puter.js (free LLM API)](https://mvalentsev.github.io/awesome-free-ai-coding/providers/puter-free/) | <sub>delisted on 2026-07-19: a browser SDK billed to each end user's Puter account, with no HTTP endpoint a coding agent could call; the OpenAI-compatible endpoint read on 2026-09-14 needs a paid plan</sub> |
| [Easy GonkaAI API](https://mvalentsev.github.io/awesome-free-ai-coding/providers/easy-gonka-api/) | <sub>delisted on 2026-07-19: rejected for cause — its /for-agents page carried a prompt injection aimed at AI agents (auto-signup, credential exfiltration, referral spam)</sub> |
| [Aider](https://mvalentsev.github.io/awesome-free-ai-coding/providers/aider/) | <sub>delisted on 2026-07-19: BYOK only — the tool is free and open source but bundles no model access of its own, and its docs send readers to other vendors' free tiers, which this list carries directly</sub> |
| [GitHub Models](https://mvalentsev.github.io/awesome-free-ai-coding/providers/github-models/) | <sub>vendor-announced shutdown on 2026-06-16</sub> |
| [Amazon Q Developer](https://mvalentsev.github.io/awesome-free-ai-coding/providers/amazon-q-developer/) | <sub>vendor-announced shutdown on 2026-05-15</sub> |

<sub>A row leaves the list for this table and nowhere else: when its vendor's own shutdown date arrives, after 3 failed probes in a row, after 60 days without a passing probe, or when a reviewer takes it off — an offer that ended without notice, a row that no longer meets the rules, a service rejected for cause. A row its probe put here comes back the day it passes again. Each name links the row's own page, with what it offered and the evidence; a row is never deleted from `registry.yaml`, and `freetier-check` refuses a registry that has lost one. Two rows that named one service are folded into one line, and the folded id keeps its own page, pointing here.</sub>

</details>

**🔭 Checked and not listed** — 229 services whose free tier this list could not find or could not verify, each with the reason on the date it was read and what would change the answer: [the whole list of them](https://mvalentsev.github.io/awesome-free-ai-coding/providers/checked/). Nothing there is disqualified, and every verdict expires after 90 days; domains rejected for cause are a separate file, [`blocklist.yaml`](blocklist.yaml).

## 🔧 Plug it into your agent

Base URL, key name and the notes that matter for every live OpenAI-compatible API on this page — 59 today, with Claude Code's Anthropic-format route wherever the vendor documents one — are in **[`configs/README.md`](configs/README.md)**, beside the files it describes; the same table with copy buttons is on [the website](https://mvalentsev.github.io/awesome-free-ai-coding/#plug). Ready-made, regenerated on every update:

| File | What it gives you |
|---|---|
| [`configs/opencode.json`](configs/opencode.json) | Drop-in [opencode](https://opencode.ai) config with every provider wired up — keys via `{env:...}`, keyless endpoints work immediately |
| [`configs/litellm.yaml`](configs/litellm.yaml) | [LiteLLM](https://docs.litellm.ai) proxy config — `litellm --config configs/litellm.yaml --host 127.0.0.1` puts every free model LiteLLM can call behind one local endpoint; ask for `free/strong` or `free/nokey` instead of a model and a call moves to the next free lane when one runs out |
| [`configs/claude-code.sh`](configs/claude-code.sh) | One shell function per gateway that serves the Anthropic Messages format — `source` it and run [Claude Code](https://code.claude.com/docs) on a free lane, key and model filled in where the row lists one |
| [`configs/free-llm.env.example`](configs/free-llm.env.example) | Commented env exports for any OpenAI-compatible tool |
| [`llms.txt`](llms.txt) · [`index.json`](index.json) · [feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml) | The list for machines — one text file for LLM search and agents, the JSON registry, and an Atom feed of every change |
| [`browse.html`](https://mvalentsev.github.io/awesome-free-ai-coding/browse.html) · [provider pages](https://mvalentsev.github.io/awesome-free-ai-coding/providers/) | The list as a filterable table, and one page per row — the offer in the vendor's own words, the connection details, the evidence and the history |

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

- **Live probes, twice a week.** GitHub Actions calls every row's models API or reads its pricing page and re-verifies the offer; a `Last verified` date is earned by passing, never typed. A probe anchors on something that dies with the offer — a model id, a quota figure, a price row, a sentence quoted from the vendor's own page — never on the word "free", which outlives most free tiers; where a lane needs no key, the probe calls it without one, and a bot wall answering for a vendor counts as "could not check", never as "gone".
- **Probe-gated discovery.** A scout sweeps Tavily search, Hacker News, GitHub, curated feeds and every models.dev provider that publishes a zero-cost model; an LLM extracts candidates strictly from fetched evidence, and a candidate lands only through a pull request, after passing its own live probe. The LLM never writes to this README or to `main`.
- **Self-pruning, never silent.** 3 failed probes in a row, 60 days without a passing one, a vendor's announced shutdown date or a reviewer's delisting move a row to the [Archive](#-archive) with the reason — and no row is ever deleted. Every arrival, departure and free-model change is appended to [`history.jsonl`](history.jsonl) and published as an [Atom feed](https://mvalentsev.github.io/awesome-free-ai-coding/feed.xml). Services checked and found to have nothing free today are on [a page of their own](https://mvalentsev.github.io/awesome-free-ai-coding/providers/checked/), each verdict expiring after 90 days so the question comes back around.

The whole mechanism, file by file — the scout's sources and their expiry, the blocklist's rules, what a row's prose may say — is in [CONTRIBUTING.md](CONTRIBUTING.md).

## 🤝 Contributing

`registry.yaml` is the single source of truth; this README is generated from it — don't edit it by hand.
Know a legal free offer that's missing? **[Suggest a service](../../issues/new?template=suggest-a-service.yml)** — it will be probed like everything else. Details in [CONTRIBUTING.md](CONTRIBUTING.md).

<div align="center">

**⭐ If this list saved you a credit-card form, star the repo — it keeps the radar visible.**

<sub>Maintained by robots · reviewed by humans · MIT · <a href="#top">back to top ↑</a></sub>

</div>
