# Claude Code on a free lane — generated from registry.yaml, do not edit by hand.
# Each function points Claude Code at a gateway this list verifies twice a week:
# the vendor documents the Anthropic-format route, and the probe confirms it still
# answers. Usage:  source configs/free-llm.env.example  (fill the key you use),
# then  source configs/claude-code.sh  and run the function named after the row,
# e.g. claude-openrouter-free. Works in bash and zsh.

# ── OpenRouter (free models) · get a key: https://openrouter.ai/settings/keys
#    free ids: nvidia/nemotron-3-ultra-550b-a55b:free, nvidia/nemotron-3-super-120b-a12b:free, nvidia/nemotron-3.5-lightning:free, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free, nvidia/nemotron-3.5-content-safety:free, google/gemma-4-31b-it:free, google/gemma-4-26b-a4b-it:free, cohere/north-mini-code:free, poolside/laguna-s-2.1:free, poolside/laguna-xs-2.1:free, z-ai/glm-5.2:free, minimax/minimax-m3:free, minimax/minimax-m2.7:free, thinkingmachines/inkling:free, thinkingmachines/inkling-small:free, dots-studio/dots-3-note-preview:free, inclusionai/ling-3.0-flash-fin:free, inclusionai/ling-3.0-flash-sante:free, liquid/lfm-2.5-2.6b:free, openrouter/free
claude-openrouter-free() {
  ANTHROPIC_BASE_URL="https://openrouter.ai/api" \
  ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="nvidia/nemotron-3-ultra-550b-a55b:free" \
  claude "$@"
}

# ── Requesty · get a key: https://app.requesty.ai/api-keys
#    free ids: nvidia/nemotron-3-ultra-550b-a55b, nvidia/nemotron-3-super-120b-a12b, nvidia/nemotron-3-nano-30b-a3b, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning, nvidia/nemotron-3.5-content-safety, novita/inclusionai/ling-3.0-tiny, google/gemma-4-31b-it, poolside/laguna-xs.2, poolside/laguna-m.1, mistral/leanstral-1-5, nvidia/muse-glimmer-30b, nvidia/nemotron-3.5-lightning-30b-a3b
claude-requesty() {
  ANTHROPIC_BASE_URL="https://router.requesty.ai" \
  ANTHROPIC_AUTH_TOKEN="$REQUESTY_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="nvidia/nemotron-3-ultra-550b-a55b" \
  claude "$@"
}

# ── AIHubMix (free models) · get a key: https://aihubmix.com/token
#    free ids: coding-glm-5.2-free, coding-glm-5.1-free, coding-kimi-k3-free, kimi-for-coding-free, xiaomi-mimo-v2.5-free, north-mini-code-free, gpt-oss-20b-free, ling-3.0-tiny-free, nemotron-3-ultra-550b-a55b-free, gemma-4-31b-it-free, coding-glm-4.6-free, coding-glm-4.7-free, coding-glm-5-free, coding-glm-5-turbo-free, coding-glm-5.3-flash-free, coding-glm-5.3-free, coding-minimax-m2-free, coding-minimax-m2.1-free, coding-minimax-m2.5-free, coding-minimax-m2.7-free, coding-minimax-m3-free, dots-3-note-preview-free, gemini-3-flash-preview-free, gemini-3.5-flash-lite-free, gemini-3.6-flash-free, gemini-3.7-flash-free, gemini-3.8-flash-free, gemma-4-26b-a4b-it-free, glm-4.7-flash-free, gpt-4.1-free, gpt-4.1-mini-free, gpt-4.1-nano-free, gpt-4o-free, gpt-5.5-free, hy3-free, k2.6-code-preview-free, laguna-s-2.1-free, laguna-xs-2.1-free, lfm-2.5-2.6b-free, ling-3.0-flash-free, mimo-v2-flash-free, minimax-m2.7-free, minimax-m3-free, nemotron-3-nano-30b-a3b-free, nemotron-3-nano-omni-30b-a3b-reasoning-free, nemotron-3-super-120b-a12b-free, nemotron-3.5-content-safety-free, nemotron-3.5-lightning-free, nemotron-nano-12b-v2-vl-free, nemotron-nano-9b-v2-free, xiaomi-mimo-v2-omni-free, xiaomi-mimo-v2-pro-free, xiaomi-mimo-v2.5-pro-free
claude-aihubmix() {
  ANTHROPIC_BASE_URL="https://aihubmix.com" \
  ANTHROPIC_AUTH_TOKEN="$AIHUBMIX_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="coding-glm-5.2-free" \
  claude "$@"
}

# ── Z.ai (Zhipu GLM) · get a key: https://z.ai/manage-apikey/apikey-list
#    the row lists no callable id: pass ANTHROPIC_MODEL=<a free id> before the function, or set it inside
claude-zai-glm() {
  ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
  ANTHROPIC_AUTH_TOKEN="$ZAI_GLM_API_KEY" \
  ANTHROPIC_API_KEY="" \
  claude "$@"
}

# ── Vercel AI Gateway · get a key: https://vercel.com/dashboard/ai-gateway/api-keys
#    free ids: poolside/laguna-s-2.1-free, minimax/minimax-m3-free, minimax/minimax-m2.7-free, inclusionai/ling-3.0-flash-fin, inclusionai/ling-3.0-flash-fin-free, inclusionai/ling-3.0-flash-sante, inclusionai/ling-3.0-flash-sante-free
claude-vercel-ai-gateway() {
  ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh" \
  ANTHROPIC_AUTH_TOKEN="$VERCEL_AI_GATEWAY_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="poolside/laguna-s-2.1-free" \
  claude "$@"
}

# ── Kenari · get a key: https://kenari.id/keys
#    free ids: glm-4-7-flash:free, nemotron-3-ultra-550b-a55b:free, nemotron-3-super-120b-a12b:free, step-3-7-flash:free, laguna-s-2-1:free, laguna-xs-2-1:free, hy3:free, mistral-medium-3-5:free, mimo-v2-5:free, agnes-2-0-flash:free, agnes-2-5-flash:free, muse-spark-1-2-contributor:free, muse-spark-1-3-contributor:free
claude-kenari() {
  ANTHROPIC_BASE_URL="https://kenari.id" \
  ANTHROPIC_AUTH_TOKEN="$KENARI_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="glm-4-7-flash:free" \
  claude "$@"
}

# ── FreeInference (Harvard SEAS) · get a key: https://freeinference.org
#    free ids: deepseek-v4-flash, qwen3.6-35b, diffusiongemma
claude-freeinference() {
  ANTHROPIC_BASE_URL="https://freeinference.org/anthropic" \
  ANTHROPIC_AUTH_TOKEN="$FREEINFERENCE_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="deepseek-v4-flash" \
  claude "$@"
}

