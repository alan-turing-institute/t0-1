uv run t0-1 evaluate-rag \
./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl \
--llm-provider openai_completion \
--llm-model-name simplescaling/s1.1-32B \
--budget-forcing \
--budget-forcing-kwargs '{"max_tokens_thinking": 1024, "num_stop_skips": 3}' \
--extra-body '{"max_tokens": 256}' \
--prompt-template-path ./templates/withoutrag_evaluation_prompt.txt \
--system-prompt-path ./templates/withoutrag_evaluation_system_prompt.txt \
--output-file ./evaluate-s1-thinking1024.jsonl \
--conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl \
--persist-directory ./v4-summarised-db \
--local-file-store ./v4-summarised-lfs
