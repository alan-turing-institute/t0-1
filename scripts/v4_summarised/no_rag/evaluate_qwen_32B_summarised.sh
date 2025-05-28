uv run t0-001 evaluate-rag ./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl \
--db-choice chroma \
--llm-provider openai \
--llm-model-name Qwen/Qwen2.5-32B-Instruct \
--prompt-template-path ./templates/withoutrag_evaluation_prompt.txt \
--system-prompt-path ./templates/withoutrag_evaluation_system_prompt.txt \
--output-file ./evaluate-rag-qwen-32b-k5-chroma.jsonl \
--conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl \
--persist-directory ./v4-summarised-db \
--local-file-store ./v4-summarised-lfs
