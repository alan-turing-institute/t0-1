vllm serve openai/gpt-oss-20b \
--seed 42 \
--generation-config vllm \
--port 8020 \
--tensor-parallel-size 1 \
--max-model-len 131072 \
--hf-overrides '{"rope-scaling": {"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}}' \
--enable-auto-tool-choice \
--tool-call-parser openai \
--gpu-memory-utilization 0.5
