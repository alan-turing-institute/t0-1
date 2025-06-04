uv run t0-1 evaluate-rag ./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl \
--db-choice chroma \
--llm-provider azure_openai \
--llm-model-name gpt-4o \
--prompt-template-path ./templates/withoutrag_evaluation_prompt.txt \
--system-prompt-path ./templates/withoutrag_evaluation_system_prompt.txt \
--output-file ./evaluate-gpt-4o-k5-chroma.jsonl \
--conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl \
--persist-directory ./v4-summarised-db \
--local-file-store ./v4-summarised-lfs
