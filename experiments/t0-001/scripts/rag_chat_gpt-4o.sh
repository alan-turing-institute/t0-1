t0-001 rag-chat \
  --k 30 \
  --db-choice chroma \
  --llm-provider azure_openai \
  --llm-model-name gpt-4o \
  --prompt-template-path ../templates/rag_evaluation_prompt.txt \
  --system-prompt-path ../templates/rag_evaluation_system_prompt.txt \
  --conditions-file ../data/nhs-conditions/v3/conditions.jsonl \
  --extra-body '{"max_tokens":4056}' \
  --env-file ../.env
