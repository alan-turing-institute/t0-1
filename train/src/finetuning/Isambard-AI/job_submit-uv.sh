#!/bin/bash

#SBATCH --job-name=t0-2.4
#SBATCH --nodes=1
#SBATCH --gpus-per-node=4
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=18
#SBATCH --mem=0
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --exclusive

# ==============================================================================
# 1. USER CONFIGURATION
# ==============================================================================

# Default values (override with sbatch --export=ALL,MODEL_NAME="...")
: "${MODEL_NAME:="google/gemma-3-4b-it"}"
: "${DATASET_PATH:="<<replace_with_your_data_path>>/2k-gpt-oss-120b-traces-k5_qwen_summarised_data_gemma_format"}"
: "${RUN_NAME:="t0-2.4"}"
: "${BLOCK_SIZE:=32768}"
: "${EPOCHS:=5}"
: "${LR:=1e-5}"
: "${FSDP_CONFIG:="fsdp_config_gemma.json"}"

# ==============================================================================
# 2. SYSTEM & ENVIRONMENT
# ==============================================================================

UV_PATH="<<replace_with_your_uv_env_path>>"
SCRIPT_PATH="<<replace_with_your_script_path>>/t0-1/train/s1_31a10f2/train/sft.py"
export HF_HOME="/projects/u5gf/t0/tomas/hf_cache"


# ==============================================================================
# BEYOND THIS POINT, AVOID EDITS UNLESS NECESSARY
# ==============================================================================

mkdir -p logs
set -euo pipefail
export PYTHONUNBUFFERED=1

# Activate Environment
source "${UV_PATH}/bin/activate"

# Offline/Online Logic
export HF_CACHE_DIR="${HF_HOME}/huggingface"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

if [ -d "$DATASET_PATH" ]; then
    echo "[INFO] Dataset found locally at $DATASET_PATH. OFFLINE mode."
    export HF_DATASETS_OFFLINE=1
else
    echo "[INFO] Dataset '$DATASET_PATH' not found locally. ONLINE mode."
    export HF_DATASETS_OFFLINE=0
fi

# ==============================================================================
# 3. DISTRIBUTED SETUP (CRITICAL FOR MULTI-NODE)
# ==============================================================================

export MASTER_NODE=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_ADDR=$MASTER_NODE 
export MASTER_PORT=$(shuf -i 20000-60000 -n 1)
export RDZV_ID=$SLURM_JOB_ID

GPUS_PER_NODE=$SLURM_GPUS_ON_NODE
# Fallback if variable is unset (though --gpus-per-node should set it)
if [ -z "$GPUS_PER_NODE" ]; then
    GPUS_PER_NODE=4
fi

# 5. Network Interface (UNCOMMENT IF TRAINING HANGS)
# You often need to force NCCL to use InfiniBand (ib0) or RoCE (bond0)
# instead of the slow management Ethernet (eth0).
# export NCCL_SOCKET_IFNAME=ib0
# export NCCL_DEBUG=INFO

echo "****************************************************************************"
echo "Nodes: $SLURM_NNODES | GPUs per Node: $GPUS_PER_NODE"
echo "Head Node: $MASTER_ADDR:$MASTER_PORT"
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

# Start monitoring on the head node only
if [ "$SLURM_NODEID" -eq 0 ]; then
    stdbuf -o0 vmstat -t 1 > "logs/${SLURM_JOB_NAME}_${SLURM_JOB_ID}-vmstat-${uid}.txt" &
    VMSTAT_PID=$!
    stdbuf -o0 nvidia-smi dmon -o TD -s puct -d 1 > "logs/${SLURM_JOB_NAME}_${SLURM_JOB_ID}-dmon-${uid}.txt" &
    NVIDIA_PID=$!
fi

# THE LAUNCH COMMAND
srun --export=ALL bash -c "
    torchrun \
    --nnodes=$SLURM_NNODES \
    --nproc_per_node=$GPUS_PER_NODE \
    --rdzv_id=$RDZV_ID \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$MASTER_ADDR:$MASTER_PORT \
    --node_rank=\$SLURM_NODEID \
    $SCRIPT_PATH \
    --per_device_train_batch_size=1 \
    --per_device_eval_batch_size=1 \
    --gradient_accumulation_steps=1 \
    --train_file_path=\"$DATASET_PATH\" \
    --block_size=$BLOCK_SIZE \
    --model_name=\"$MODEL_NAME\" \
    --warmup_ratio=0.05 \
    --fsdp='full_shard auto_wrap' \
    --fsdp_config=\"$FSDP_CONFIG\" \
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
