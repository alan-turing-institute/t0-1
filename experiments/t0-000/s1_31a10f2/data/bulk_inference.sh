#! /bin/bash
# iterate over shard_index for 0 to 6, including 0 and 6
for shard_index in {0..5}; do
    srun --job-name=bulk \
        --nodes=1 \
        --account=marlowe-m000027 \
        --partition=beta \
        --gpus-per-task=2 \
        --mem=256G \
        --time=3-00:00:00 \
        python data/scripts/bulk_inference.py \
        --shard_index ${shard_index} \
        --model_name Qwen/Qwen2.5-7B-Instruct \
        > data/scripts/log/qwen_7b_base_${shard_index}.txt 2>&1 &
done

# iterate over shard_index for 0 to 6, including 0 and 6
for shard_index in {0..5}; do
    srun --job-name=bulk \
        --nodes=1 \
        --account=marlowe-m000027 \
        --partition=beta \
        --gpus-per-task=2 \
        --mem=256G \
        --time=3-00:00:00 \
        python data/scripts/bulk_inference.py \
        --shard_index ${shard_index} \
        --model_name Qwen/Qwen2.5-32B-Instruct \
        > data/scripts/log/qwen_32b_base_${shard_index}.txt 2>&1 &
done
