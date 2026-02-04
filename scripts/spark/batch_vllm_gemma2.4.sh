#!/bin/bash
# vim: et:ts=4:sts=4:sw=4

#SBATCH --time 2:00:0
#SBATCH --nodes 1
#SBATCH --gpus-per-node 4
#SBATCH --cpus-per-gpu 72
#SBATCH --mem 0
#SBATCH --job-name gemma2.4
#SBATCH --output gemma2.4.log

echo "--------------------------------------"
echo 
echo 
echo "New job: ${SLURM_JOB_ID}"
echo "--------------------------------------"

module purge
module load brics/default

# for vllm run
export PRIMARY_PORT=$((30000 + $SLURM_JOB_ID % 16384))
export PRIMARY_HOST=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export PRIMARY_IP=$(srun --nodes=1 --ntasks=1 -w $PRIMARY_HOST hostname -i | tr -d ' ')
echo "Primary IP: $PRIMARY_IP"

# set working dir
cd ../..

# source venv
source .venv/bin/activate
echo $(which python)

./scripts/spark/serve_qwen_with_tools.sh > serve_qwen_with_tools_out.log 2>&1 &
./scripts/spark/serve_t0_1_gemma2.4.sh > serve_t0_1_gemma2.4_out.log 2>&1 &

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

t0-1 evaluate-rag ./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl --k 5 --db-choice chroma --llm-provider openai_completion --llm-model-name TomasLaz/t0-2.4-gemma-3-4b-it --budget-forcing --budget-forcing-kwargs '{"max_tokens_thinking": 256, "num_stop_skips": 3}' --extra-body '{"max_tokens": 256}' --prompt-template-path ./templates/rag_evaluation_prompt_deepseek_r1.txt --system-prompt-path ./templates/rag_evaluation_system_prompt_deepseek_r1.txt --output-file ./evaluate-rag-t0-2.4-k5-32B-thinking256-k5-chroma.jsonl --conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl --persist-directory ./v4-summarised-db --local-file-store ./v4-summarised-lfs

wait

