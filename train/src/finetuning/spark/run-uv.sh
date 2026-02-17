#!/bin/bash

JOB_NAME="t0-2.5-270m"

# ==============================================================================
# 1. USER CONFIGURATION
# ==============================================================================

# Default values (override with sbatch --export=ALL,MODEL_NAME="...")
: "${MODEL_NAME:="google/gemma-3-270m-it"}"
: "${DATASET_PATH:="/t0/t0_1/2k-gpt-oss-120b-traces-k5_qwen_summarised_data_gemma_format"}"
: "${RUN_NAME:="t0-2.5"}"
: "${BLOCK_SIZE:=32768}"
: "${EPOCHS:=1}"
: "${LR:=1e-5}"
: "${FSDP_CONFIG:="fsdp_config_gemma.json"}"

# ==============================================================================
# 2. SYSTEM & ENVIRONMENT
# ==============================================================================

UV_PATH="/t0/t0_1/t0-1/train/src/finetuning/venvs/t0_phase3"
SCRIPT_PATH="/t0/t0_1/t0-1/train/s1_31a10f2/train/sft.py"
export HF_HOME="/t0/models/.cache/huggingface"


# ==============================================================================
# BEYOND THIS POINT, AVOID EDITS UNLESS NECESSARY
# ==============================================================================

mkdir -p logs
set -euo pipefail
export PYTHONUNBUFFERED=1

# Activate Environment
source "${UV_PATH}/bin/activate"

# Offline/Online Logic
# export HF_CACHE_DIR="${HF_HOME}/huggingface"
# export TRANSFORMERS_OFFLINE=1
# export HF_HUB_OFFLINE=1

if [ -d "$DATASET_PATH" ]; then
    echo "[INFO] Dataset found locally at $DATASET_PATH. OFFLINE mode."
    export HF_DATASETS_OFFLINE=1
else
    echo "[INFO] Dataset '$DATASET_PATH' not found locally. ONLINE mode."
    export HF_DATASETS_OFFLINE=0
fi

# SPARK - MULTI_NODE SET UP NOT NEEDED, 1 GPU

echo "****************************************************************************"
echo "Run Name: $RUN_NAME"
echo "****************************************************************************"

# ==============================================================================
# 4. EXECUTION
# ==============================================================================

uid=$(date +%Y%m%d_%H%M%S)
export WANDB_MODE=offline
export WANDB_DIR="logs"

# Clean up function
cleanup() {
    echo "Cleaning up..."
    [[ -n "${VMSTAT_PID:-}" ]] && kill $VMSTAT_PID 2>/dev/null || true
    [[ -n "${NVIDIA_PID:-}" ]] && kill $NVIDIA_PID 2>/dev/null || true
}
trap cleanup EXIT

# Start monitoring
stdbuf -o0 vmstat -t 1 > "logs/${JOB_NAME}-vmstat-${uid}.txt" &
VMSTAT_PID=$!
stdbuf -o0 nvidia-smi dmon -o TD -s puct -d 1 > "logs/${JOB_NAME}-dmon-${uid}.txt" &
NVIDIA_PID=$!

# THE LAUNCH COMMAND
bash -c "
    torchrun \
    --nnodes=1 \
    --nproc_per_node=1 \
    --node_rank=0 \
    $SCRIPT_PATH \
    --per_device_train_batch_size=1 \
    --per_device_eval_batch_size=1 \
    --gradient_accumulation_steps=1 \
    --train_file_path=\"$DATASET_PATH\" \
    --block_size=$BLOCK_SIZE \
    --model_name=\"$MODEL_NAME\" \
    --warmup_ratio=0.05 \
    --bf16=True \
    --eval_strategy='steps' \
    --eval_steps=50 \
    --logging_steps=1 \
    --save_steps=500 \
    --lr_scheduler_type cosine \
    --learning_rate $LR \
    --weight_decay 1e-4 \
    --adam_beta1=0.9 \
    --adam_beta2=0.95 \
    --output_dir=\"ckpts/${RUN_NAME}_${uid}\" \
    --hub_model_id=\"alan-turing-institute/${RUN_NAME}_${uid}\" \
    --push_to_hub=False \
    --hub_always_push=False \
    --num_train_epochs $EPOCHS \
    --save_only_model=True \
    --gradient_checkpointing=False \
    --report_to none \
    --lora=False \
    --eval_accumulation_steps=1
"

echo "Training finished."
