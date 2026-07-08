# Reproducing phase 0 of t0 (NHS medical condition)

## Fine-tuning

Data: https://thealanturininstitute.sharepoint.com/:u:/s/t0/IQD0vN9WcdEMSp9LU9tCjesqAWnWyNXmQdq0kmSvDjM1FMA?e=Bxk5JP

Full fine-tuning of Qwen2.5-32B with FSDP full-shard on the `2k-deepseek-traces-k5_qwen_summarised_data` dataset.

**Command** (run from `train/s1_31a10f2/`):

```bash
uid="$(date +%Y%m%d_%H%M%S)"
gpu_count=$(nvidia-smi -L | wc -l)

torchrun --nproc-per-node ${gpu_count} --master_port 12345 \
    train/sft.py \
    --model_name="Qwen/Qwen2.5-32B-Instruct" \
    --train_file_path="2k-deepseek-traces-k5_qwen_summarised_data" \
    --block_size=32768 \
    --per_device_train_batch_size=1 \
    --per_device_eval_batch_size=1 \
    --gradient_accumulation_steps=1 \
    --num_train_epochs=5 \
    --warmup_ratio=0.05 \
    --fsdp="full_shard auto_wrap" \
    --fsdp_config="train/fsdp_config_qwen_cpu.json" \
    --gradient_checkpointing=True \
    --bf16=True \
    --eval_strategy="no" \
    --save_strategy="no" \
    --logging_steps=1 \
    --lr_scheduler_type="cosine" \
    --learning_rate=1e-5 \
    --weight_decay=1e-4 \
    --adam_beta1=0.9 --adam_beta2=0.95 \
    --output_dir="ckpts/t0_qwen32b-${uid}" \
    --push_to_hub=false \
    --save_only_model=True \
    --wandb_project="t0" \
    --wandb_entity="alan-turing-institute"
```

**Notes:**

- **CPU offload is required at 32B.** Full fine-tuning of a 32B model keeps params, gradients, and optimizer states in memory; on a single node these won't fit in GPU VRAM, so use `fsdp_config_qwen_cpu.json` (which enables CPU offload) rather than `fsdp_config_qwen.json`. This trades speed for the ability to fit — expect slower steps. If you have enough GPUs/nodes (e.g. multi-node with 8×80GB each), you can switch back to `fsdp_config_qwen.json` for full-GPU sharding and faster training.
- **Chat template is auto-detected** from the model name: `qwen` selects the `<|im_start|>user` / `<|im_start|>assistant` templates and the `<|fim_pad|>` pad token. Loss is computed only over the assistant response. No `--template_format` needed.
- **Dataset** `2k-deepseek-traces-k5_qwen_summarised_data` is loaded by `load_data()`, which tries `load_from_disk` for a local directory first, then falls back to the HF Hub. Point `--train_file_path` at the local path if it isn't on the Hub.
- **Multi-node/SLURM (recommended for 32B):** use `train/sft_slurm.sh` via `train/launch.sh` — it's already configured for `Qwen/Qwen2.5-32B-Instruct` with `batch_size=16` and `fsdp_config_qwen_cpu.json`, and computes gradient-accumulation steps from GPU count × nodes. Just update `--train_file_path` to the dataset above.

## Serving the Fine-Tuned Qwen2.5-32B for Evaluation

The evaluation talks to the model over an OpenAI-compatible endpoint served by vLLM. Start the endpoint, point `.env` at it, then run the eval.

### 1. Serve the model with vLLM

Adapt [`scripts/serve_t0_1.sh`](scripts/serve_t0_1.sh), replacing `TomasLaz/t0-1.1-k5-32B` with your checkpoint (a Hugging Face repo id or a local `ckpts/...` path):

```sh
CUDA_VISIBLE_DEVICES=4,5,6,7 vllm serve <your-model-id> \
--seed 42 \
--generation-config vllm \
--port 8010 \
--tensor-parallel-size 4 \
--max-model-len 131072 \
--rope-scaling '{"factor":4, "original_max_position_embeddings": 32768, "rope_type":"yarn"}'
```

Notes:

- `--tensor-parallel-size 4` must match the number of GPUs in `CUDA_VISIBLE_DEVICES`.
- Keep the YaRN `--rope-scaling` for a 32B trained at `block_size=32768` — it stretches the 32k context window to 131k.
- Leave it running (e.g. in `tmux` or a separate terminal) while you run the eval.

### 2. Point `.env` at the endpoint

The OpenAI-compatible providers (`openai` / `openai_completion`) resolve the base URL per-model from `.env`. Add these lines:

```
OPENAI_API_KEY="-"
OPENAI_BASE_URL_<your-model-id>="http://localhost:8010/v1/"
```

These three must agree:

- `<your-model-id>` — the model string you pass to `--llm-model-name` in the eval and to `vllm serve`.
- The port (`8010`) — must match `--port` in the serve command.
- `OPENAI_API_KEY` — any non-empty string; vLLM does not authenticate it.

### 3. Run the evaluation

Once the endpoint responds, run the `evaluate-rag` command with `--llm-model-name <your-model-id>` (see the Evaluation section).

## Evaluation

Qwen conditions: `./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl`

This reproduces **t0-k5-32B**, the best-performing configuration in the paper: budget forcing with `max_tokens_thinking=256` and `num_stop_skips=3`.

The fine-tuned model is served over the `openai_completion` endpoint — budget forcing is only supported on the completion API. The vector DB must exist at `./v4-summarised-db` (add `--force-create` on first run to build it from the conditions file above). `<your-model-id>` must match exactly across `vllm serve`, the `OPENAI_BASE_URL_<your-model-id>` key in `.env`, and `--llm-model-name`.

```bash
uv run t0-1 evaluate-rag ./data/synthetic_queries/5147cd8_gpt-4o_1000_synthetic_queries.jsonl \
--k 5 \
--db-choice chroma \
--llm-provider openai_completion \
--llm-model-name <your-model-id> \
--budget-forcing \
--budget-forcing-kwargs '{"max_tokens_thinking": 256, "num_stop_skips": 3}' \
--extra-body '{"max_tokens": 256}' \
--prompt-template-path ./templates/rag_evaluation_prompt_deepseek_r1.txt \
--system-prompt-path ./templates/rag_evaluation_system_prompt_deepseek_r1.txt \
--output-file ./evaluate-rag-<your-model-id>-thinking256-k5-chroma.jsonl \
--conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl \
--persist-directory ./v4-summarised-db \
--local-file-store ./v4-summarised-lfs
```
