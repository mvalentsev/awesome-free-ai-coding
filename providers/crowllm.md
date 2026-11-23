---
id: crowllm
name: CrowLLM
category: api-free-tier
url: https://crowllm.com
offering: Zero-rated model IDs ending in :free (40+ models), plus a signup credit; no credit card required.
first_seen: 2026-03-30
last_verified: 2026-03-30
probe:
  type: api-models
  endpoint: https://crowllm.com/v1/models
  free_marker: ":free"
  require_zero_price: true
  pricing_endpoint: https://crowllm.com/api/pricing
api:
  base_url: https://crowllm.com/v1
  auth: api-key
  openai_compatible: true
  key_url: https://crowllm.com/pricing
  model_ids:
    - gpt-6-luna:free
    - claude-sonnet-4.6:free
    - deepseek-v4-pro:free
    - qwen3.7-max:free
    - gemini-3.7-flash:free
    - glm-5.2:free
    - minimax-m2.7:free
    - nemotron-3-super:free
    - kimi-k3:free
    - longcat-2.5-preview:free
---
