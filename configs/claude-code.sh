# Claude Code on a free lane — generated from registry.yaml, do not edit by hand.
# Each function points Claude Code at a gateway this list verifies twice a week:
# the vendor documents the Anthropic-format route, and the probe confirms it still
# answers. Usage:  source configs/free-llm.env.example  (fill the key you use),
# then  source configs/claude-code.sh  and run the function named after the row,
# e.g. claude-openrouter-free. Works in bash and zsh.

# ── OpenRouter (free models) · get a key: https://openrouter.ai/settings/keys
#    free ids: nvidia/nemotron-3-ultra-550b-a55b:free, nvidia/nemotron-3-super-120b-a12b:free, nvidia/nemotron-3.5-lightning:free, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free, nvidia/nemotron-3.5-content-safety:free, google/gemma-4-31b-it:free, google/gemma-4-26b-a4b-it:free, cohere/north-mini-code:free, poolside/laguna-s-2.1:free, poolside/laguna-xs-2.1:free, thinkingmachines/inkling:free, thinkingmachines/inkling-small:free, dots-studio/dots-3-note-preview:free, inclusionai/ling-3.0-flash-fin:free, inclusionai/ling-3.0-flash-sante:free, liquid/lfm-2.5-2.6b:free, inclusionai/ling-3.0-flash-vl:free, nex-agi/nex-n2.5-pro:free, nex-agi/nex-n2.5-mini:free, z-ai/glm-5.2:free, openrouter/free
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
#    free ids: coding-glm-5.2-free, coding-glm-5.1-free, coding-kimi-k3-free, kimi-for-coding-free, xiaomi-mimo-v2.5-free, north-mini-code-free, gpt-oss-20b-free, ling-3.0-tiny-free, nemotron-3-ultra-550b-a55b-free, gemma-4-31b-it-free, agents-a1-free, coding-glm-4.6-free, coding-glm-4.7-free, coding-glm-5-free, coding-glm-5-turbo-free, coding-glm-5.3-flash-free, coding-glm-5.3-free, coding-minimax-m2-free, coding-minimax-m2.1-free, coding-minimax-m2.5-free, coding-minimax-m2.7-free, coding-minimax-m3-free, dots-3-note-preview-free, gemini-3-flash-preview-free, gemini-3.5-flash-lite-free, gemini-3.6-flash-free, gemini-3.7-flash-free, gemini-3.8-flash-free, gemma-4-26b-a4b-it-free, glm-4.7-flash-free, gpt-4.1-free, gpt-4.1-mini-free, gpt-4.1-nano-free, gpt-4o-free, gpt-5.5-free, hy3-free, intern-s2-free, k2.6-code-preview-free, laguna-s-2.1-free, laguna-xs-2.1-free, lfm-2.5-2.6b-free, ling-3.0-flash-free, mimo-v2-flash-free, minimax-m2.7-free, nemotron-3-nano-30b-a3b-free, nemotron-3-nano-omni-30b-a3b-reasoning-free, nemotron-3-super-120b-a12b-free, nemotron-3.5-content-safety-free, nemotron-3.5-lightning-free, nemotron-nano-12b-v2-vl-free, nemotron-nano-9b-v2-free, union-alpha-free, xiaomi-mimo-v2-omni-free, xiaomi-mimo-v2-pro-free, xiaomi-mimo-v2.5-pro-free, ox-alpha
claude-aihubmix() {
  ANTHROPIC_BASE_URL="https://aihubmix.com" \
  ANTHROPIC_AUTH_TOKEN="$AIHUBMIX_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="coding-glm-5.2-free" \
  claude "$@"
}

# ── Z.ai (Zhipu GLM) · get a key: https://z.ai/manage-apikey/apikey-list
#    free ids: glm-4.7-flash, glm-4.5-flash, glm-4.6v-flash
claude-zai-glm() {
  ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
  ANTHROPIC_AUTH_TOKEN="$ZAI_GLM_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="glm-4.7-flash" \
  claude "$@"
}

# ── Vercel AI Gateway · get a key: https://vercel.com/dashboard/ai-gateway/api-keys
#    free ids: poolside/laguna-s-2.1-free, inclusionai/ling-3.0-flash-fin, inclusionai/ling-3.0-flash-fin-free, inclusionai/ling-3.0-flash-sante, inclusionai/ling-3.0-flash-sante-free, inclusionai/ling-3.0-flash-vl, inclusionai/ling-3.0-flash-vl-free
claude-vercel-ai-gateway() {
  ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh" \
  ANTHROPIC_AUTH_TOKEN="$VERCEL_AI_GATEWAY_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="poolside/laguna-s-2.1-free" \
  claude "$@"
}

# ── Tencent Cloud TokenHub · get a key: https://console.cloud.tencent.com/tokenhub/apikey
#    free ids: kimi-k3, glm-5.3, hy3, minimax-m3
claude-tencent-tokenhub() {
  ANTHROPIC_BASE_URL="https://tokenhub.tencentmaas.com" \
  ANTHROPIC_AUTH_TOKEN="$TENCENT_TOKENHUB_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="kimi-k3" \
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

# ── Fireworks AI · get a key: https://app.fireworks.ai/settings/users/api-keys
#    free ids: accounts/fireworks/models/deepseek-v4p1-flash, accounts/fireworks/models/glm-5p3-flash, accounts/fireworks/models/minimax-m3, accounts/fireworks/models/glm-5p3, accounts/fireworks/models/kimi-k3
claude-fireworks-ai() {
  ANTHROPIC_BASE_URL="https://api.fireworks.ai/inference" \
  ANTHROPIC_AUTH_TOKEN="$FIREWORKS_AI_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="accounts/fireworks/models/deepseek-v4p1-flash" \
  claude "$@"
}

# ── RouterPlex · get a key: https://routerplex.com/sign-up
#    free ids: deepseek-v4-flash, glm-5.3-flash, claude-sonnet-4-6
claude-routerplex() {
  ANTHROPIC_BASE_URL="https://api.routerplex.com" \
  ANTHROPIC_AUTH_TOKEN="$ROUTERPLEX_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="deepseek-v4-flash" \
  claude "$@"
}

# ── Standard Compute · get a key: https://standardcompute.com/signup
#    free ids: anthropic/claude-standardcompute, StandardCompute
claude-standardcompute() {
  ANTHROPIC_BASE_URL="https://api.stdcmpt.com" \
  ANTHROPIC_AUTH_TOKEN="$STANDARDCOMPUTE_API_KEY" \
  ANTHROPIC_API_KEY="" \
  ANTHROPIC_MODEL="anthropic/claude-standardcompute" \
  claude "$@"
}

