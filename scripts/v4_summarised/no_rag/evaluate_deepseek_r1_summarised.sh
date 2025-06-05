uv run t0-1 evaluate-rag ./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl \
--llm-provider azure \
--llm-model-name deepseek-r1 \
--prompt-template-path ./templates/withoutrag_evaluation_prompt_deepseek_r1.txt \
--system-prompt-path ./templates/withoutrag_evaluation_system_prompt_deepseek_r1.txt \
--output-file ./evaluate-deepseek-r1.jsonl \
--conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl \
--deepseek-r1 \
--persist-directory ./v4-summarised-db \
--local-file-store ./v4-summarised-lfs
