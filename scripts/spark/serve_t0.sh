#!/bin/bash

# Unified vllm serve script for t0 models

# Model name must be passed as the first argument, e.g. "TomasLaz/t0-2.5-gemma-3-270m-it"
if [[ -z "$1" ]]; then
    echo "Usage: $0 <model> [gpu-mem-util]"
    exit 1
fi

MODEL="$1"

# Optional second argument for GPU memory utilization (e.g. 0.45). Check this is a valid number if provided.
if [[ -n "$2" ]] && ! [[ "$2" =~ ^[0-9]*\.?[0-9]+$ ]]; then
    echo "Error: gpu-mem-util must be a number"
    exit 1
fi

# Default GPU memory utilization to 0.45 if not provided
GPU_MEM_UTIL="${2:-0.45}"

vllm serve "$MODEL" \
    --tokenizer google/gemma-3-4b-it \
    --seed 42 \
    --generation-config vllm \
    --port 8010 \
    --tensor-parallel-size 2 \
    --max-model-len 131072 \
    --trust-remote-code \
    --hf-overrides '{"rope-scaling": {"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}}' \
    --gpu-memory-utilization "$GPU_MEM_UTIL"
