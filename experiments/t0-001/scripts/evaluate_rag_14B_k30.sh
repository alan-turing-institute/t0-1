t0-001 evaluate-rag ../data/synthetic_queries/5bb7345_gpt-4o_1000_synthetic_queries.jsonl \
  --k 30 \
  --db-choice chroma \
  --llm-provider openai \
  --llm-model-name Qwen/Qwen2.5-14B-Instruct \
  --prompt-template-path ../templates/rag_evaluation_prompt.txt \
  --system-prompt-path ../templates/rag_evaluation_system_prompt.txt \
  --output-file ../results/evaluation_1k/evaluate-rag-qwen2pt5-14b-k30-chroma.jsonl \
  --conditions-file ../data/nhs-conditions/v2/conditions.jsonl
