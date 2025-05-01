uv run t0-001 evaluate-rag data/synthetic_queries/b971c41_gpt-4o_2000_synthetic_queries.jsonl \
--k 5  \
--db-choice chroma  \
--llm-provider azure \
--llm-model-name deepseek_r1  \
--prompt-template-path templates/rag_evaluation_prompt_deepseek_r1.txt \
--system-prompt-path templates/rag_evaluation_system_prompt_deepseek_r1.txt \
--deepseek-r1 \
--output-file ./results/NEW_evaluate_rag_deepseek_r1_k5_qwen_summarised.jsonl \
--conditions-file data/nhs-conditions/v4/qwen_summarised_conditions.jsonl
