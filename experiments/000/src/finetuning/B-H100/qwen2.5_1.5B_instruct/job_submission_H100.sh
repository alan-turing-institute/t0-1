#!/bin/bash
#SBATCH --job-name S1_TRAIN_1.5B
#SBATCH --account=<<needs to be filled>>
#SBATCH --qos=<<needs to be filled>>
#SBATCH --time 10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-task=4
#SBATCH --reservation=<<needs to be filled>>
#SBATCH --constraint=<<needs to be filled>>
#SBATCH --mem-per-gpu=177G
#SBATCH --cpus-per-task=32
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

# Set training exercise
base_model_size="1.5"
base_model="Qwen/Qwen2.5-${base_model_size}B-Instruct"
train_dataset_name="simplescaling/s1K-1.1_tokenized"

# HuggingFace cache
export HF_HOME=/bask/homes/u/usjs9456/ai_workloads_project/S1_workspace/cache

echo "*"*80
echo "Training model: ${base_model} on dataset: ${train_dataset_name}"
echo "*"*80

################################################################################################
# DO NOT MODIFY THE FOLLOWING PART IF YOU ARE NOT SUPER SURE WHAT YOU ARE DOING
################################################################################################

# logging
mkdir -p logs

# avoid silent issues
set -euo pipefail

# WANBD offline
report_to="wandb" # "wandb" or "none"
export WANDB_MODE=offline

# PyTorch CUDA memory management
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Parallelism
export OMP_NUM_THREADS=8
export NUM_NODES=${SLURM_NNODES}
export REPLICA_RANK=${SLURM_PROCID}
export MASTER_NODE=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
export NCCL_DEBUG=INFO
export CUDA_LAUNCH_BLOCKING=0

# Training parameters
# Don't change these parameters if you want to use the same configuration as the original training

block_size=32768

uid=$(date +%Y%m%d_%H%M%S)
lr=1e-5
epochs=5
micro_batch_size=1

batch_size=16
gpu_count=$(nvidia-smi -L | wc -l)
gradient_accumulation_steps=1 # 1 helps with reducing memory usage but reduce performance $((batch_size/(gpu_count * $NUM_NODES)))

srun --mpi=pmix apptainer exec --nv /bask/homes/u/usjs9456/ai_workloads_project/S1_workspace/s1_0326.sif bash -c "\
    uid=${uid} \
    && torchrun \
        --nnodes=${NUM_NODES} \
        --node_rank=${REPLICA_RANK} \
        --nproc-per-node=${gpu_count} \
        --rdzv_id=12347 \
        --rdzv_backend=c10d \
        --rdzv_conf='read_timeout=420' \
        --rdzv_endpoint=${MASTER_NODE}:29401 \
        ../../../s1/train/sft.py \
        --per_device_train_batch_size=${micro_batch_size} \
        --per_device_eval_batch_size=${micro_batch_size} \
        --gradient_accumulation_steps=${gradient_accumulation_steps} \
        --train_file_path=${train_dataset_name} \
        --block_size=${block_size} \
        --model_name=${base_model} \
        --warmup_ratio=0.05 \
        --fsdp='full_shard auto_wrap' \
        --fsdp_config='fsdp_config_qwen.json' \
        --bf16=True \
        --eval_strategy='steps' \
        --eval_steps=50 \
        --logging_steps=1 \
        --save_steps=100 \
        --lr_scheduler_type cosine \
        --learning_rate ${lr} \
        --weight_decay 1e-4 \
        --adam_beta1=0.9 \
        --adam_beta2=0.95 \
        --output_dir='ckpts/s1.1_'${uid} \
        --hub_model_id='simplescaling/s1.1-'${uid} \
        --report_to=${report_to} \
        --push_to_hub=False \
        --hub_always_push=False \
        --num_train_epochs ${epochs} \
        --save_only_model=True \
        --gradient_checkpointing=True"

echo "Training finished."
