CUDA_VISIBLE_DEVICES=0,1,2,3 vllm serve Qwen/Qwen2.5-32B-Instruct \
--port 8020 \
--tensor-parallel-size 4 \
--max-model-len 131072 \
--rope-scaling '{"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}' \
--enable-auto-tool-choice \
--tool-call-parser hermes
