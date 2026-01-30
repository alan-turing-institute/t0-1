CUDA_VISIBLE_DEVICES=2,3 vllm serve TomasLaz/t0-2.4-gemma-3-4b-it \
--tokenizer google/gemma-3-4b-it \
--seed 42 \
--generation-config vllm \
--port 8010 \
--tensor-parallel-size 2 \
--max-model-len 131072 \
--trust-remote-code \
--rope-scaling '{"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}'
