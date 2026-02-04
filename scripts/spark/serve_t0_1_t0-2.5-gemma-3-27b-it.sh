CUDA_VISIBLE_DEVICES=0 vllm serve TomasLaz/t0-2.5-gemma-3-27b-it \
--tokenizer google/gemma-3-4b-it \
--seed 42 \
--generation-config vllm \
--port 8010 \
--tensor-parallel-size 1 \
--max-model-len 131072 \
--trust-remote-code \
--hf-overrides '{"rope-scaling": {"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}}' \
--gpu-memory-utilization 0.45
