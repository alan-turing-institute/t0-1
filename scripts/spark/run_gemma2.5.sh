#!/bin/bash
# vim: et:ts=4:sts=4:sw=4
# set working dir
cd ../..

# source venv
source .venv/bin/activate
echo $(which python)

./scripts/spark/serve_qwen_with_tools.sh > serve_qwen_with_tools_out.log 2>&1 &
sleep 60
./scripts/spark/serve_t0.sh TomasLaz/t0-2.5-gemma-3-4b-it > serve_t0_gemma2.5_out.log 2>&1 &

# Wait for the REST API to be available
until curl -s http://localhost:8010/v1/models >/dev/null 2>&1; do
    sleep 20
    echo "Waiting for vLLM to start..."
done

# Wait for the REST API to be available
until curl -s http://localhost:8020/v1/models >/dev/null 2>&1; do
    sleep 20
    echo "Waiting for vLLM to start..."
done

t0-1 evaluate-rag /t0-1_local/data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl --k 5 --db-choice chroma --llm-provider openai_completion --llm-model-name TomasLaz/t0-2.5-gemma-3-4b-it --budget-forcing --budget-forcing-kwargs '{"max_tokens_thinking": 256, "num_stop_skips": 3}' --extra-body '{"max_tokens": 256}' --prompt-template-path /t0-1_local/templates/rag_evaluation_prompt_deepseek_r1.txt --system-prompt-path /t0-1_local/templates/rag_evaluation_system_prompt_deepseek_r1.txt --output-file /t0-1_local/evaluate-rag-t0-2.5-k5-32B-thinking256-k5-chroma.jsonl --conditions-file /t0-1_local/data/nhs-conditions/v4/qwen_summarised_conditions.jsonl --persist-directory /t0-1_local/v4-summarised-db --local-file-store /t0-1_local/v4-summarised-lfs


