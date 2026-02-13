#!/bin/sh
CUDA_VISIBLE_DEVICES=4,5,6,7 vllm serve TomasLaz/t0-2.5-gemma-3-27b-it \
--seed 42 \
--generation-config vllm \
--port 8010 \
--tensor-parallel-size 4 \
--max-model-len 131072 \
--rope-scaling '{"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}'
