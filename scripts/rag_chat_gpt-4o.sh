t0-001 rag-chat \
  --k 30 \
  --db-choice chroma \
  --llm-provider huggingface \
  --llm-model-name Qwen/Qwen2.5-1.5B-Instruct \
  --prompt-template-path ../templates/rag_prompt.txt \
  --system-prompt-path ../templates/rag_system_prompt.txt \
  --conditions-file ../data/nhs-conditions/v3/conditions.jsonl \
  --persist-directory $HOME/test/_t0db \
  --local-file-store $HOME/test/_t0lfs \
  --extra-body '{"max_tokens":4056}' \
  --env-file ../.env

  # --llm-provider azure_openai \
  # --llm-model-name gpt-4o \
