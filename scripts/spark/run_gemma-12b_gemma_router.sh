#!/bin/bash
# vim: et:ts=4:sts=4:sw=4

# set working dir
cd ../..

# source venv
source .venv/bin/activate
echo $(which python)

MODEL="t0-2.5-gemma-3-12b-it"

export VLLM_ALLOW_LONG_MAX_MODEL_LEN=1

./scripts/spark/serve_gemma3_with_tools.sh > serve_gemma3_with_tools_out.log 2>&1 &
./scripts/spark/serve_t0_1_${MODEL}.sh > serve_t0_1_gemma_${MODEL}_out.log 2>&1 &

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

t0-1 evaluate-rag ./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl --k 5 --db-choice chroma --llm-provider openai_completion --llm-model-name TomasLaz/${MODEL} --budget-forcing --budget-forcing-kwargs '{"max_tokens_thinking": 256, "num_stop_skips": 3}' --extra-body '{"max_tokens": 256}' --prompt-template-path ./templates/rag_evaluation_prompt_deepseek_r1.txt --system-prompt-path ./templates/rag_evaluation_system_prompt_deepseek_r1.txt --output-file ./evaluate-rag-t0-${MODEL}-gemma-router-k5-32B-thinking256-k5-chroma.jsonl --conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl --persist-directory ./v4-summarised-db --local-file-store ./v4-summarised-lfs

