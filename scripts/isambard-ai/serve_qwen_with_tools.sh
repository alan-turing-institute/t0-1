vllm serve Qwen/Qwen2.5-32B-Instruct \
--seed 42 \
--generation-config vllm \
--port 8020 \
--tensor-parallel-size 2 \
--max-model-len 131072 \
--hf-overrides '{"rope_scaling":{"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}}' \
--enable-auto-tool-choice \
--tool-call-parser hermes
