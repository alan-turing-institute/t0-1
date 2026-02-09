#!/bin/bash

# Unified vllm serve script for t0 models

if [[ -z "$1" ]]; then
    echo "Using default model: TomasLaz/t0-2.5-gemma-3-4b-it"
    MODEL="TomasLaz/t0-2.5-gemma-3-4b-it"
else
    MODEL="$1"
fi

vllm serve "$MODEL" \
    --tokenizer google/gemma-3-4b-it \
    --seed 42 \
    --generation-config vllm \
    --port 8010 \
    --tensor-parallel-size 2 \
    --max-model-len 131072 \
    --trust-remote-code \
    --rope-scaling '{"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}'
