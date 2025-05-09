# 001 s1 Replication

## Plan

1. Fine-tune a base model on the given training data (which was
   produced by running a reasoning model on the s1k dataset).

2. Evaluate the resulting Level 1 model on Stanford's evaluation
   datasets (which we think contain three sets of evaluation data).


## Azure VM Setup

1. Create a new `ND96amsr_A100_v4` in `UK South, Zone 3` and select as image `NVIDIA GPU-Optimized VMI`
2. When running, SSH into it as that would allow the machine to complete the final part of the installation of the drivers

## Environment setup
`uv venv`

`uv pip install -r pyproject.toml`

`source .venv/bin/activate`

## Running the code

`cd src`

`python overly_simple_s1.py --output_dir="fine_tuned_model"`


## The Code

The code in `s1_31a10f2` has been modified to incorporate LoRA, and an additional LoRA config file, `train/lora_config.json`, has been added.

## Training

To train any of the models, the following commands can be used as templates:

### Training on Multiple GPUs (8) on the Same Node/Server

```{bash}

torchrun \
  --standalone \
  --nproc-per-node=8 \
  train/sft_peft.py \
  --per_device_train_batch_size=1 \
  --per_device_eval_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --train_file_path='simplescaling/s1K-1.1_tokenized' \
  --block_size=32768 \
  --model_name=Qwen/Qwen2.5-14B-Instruct \
  --warmup_ratio=0.05 \
  --fsdp='full_shard auto_wrap' \
  --fsdp_config='train/fsdp_config_qwen.json' \
  --bf16=True \
  --eval_strategy='steps' \
  --eval_steps=50 \
  --logging_steps=1 \
  --save_steps=100 \
  --lr_scheduler_type cosine \
  --learning_rate 1e-5 \
  --weight_decay 1e-4 \
  --adam_beta1=0.9 \
  --adam_beta2=0.95 \
  --output_dir='ckpts/t0_14b' \
  --hub_model_id='t0/t0_14b' \
  --push_to_hub=False \
  --hub_always_push=True \
  --num_train_epochs 5 \
  --save_only_model=True \
  --gradient_checkpointing=True \
  --report_to none \
  --lora=False \
  > logs/t0_14b.log 2>&1 &

```

### Training on Multiple GPUs (8) on Two or More Nodes/Servers

The command is similar to the one above but requires additional parameters for torchrun (nnodes, node_rank, and rdzv). It must be run on all nodes individually.

For example, if two Azure VMs are used—one with IP address `10.0.0.5` (main node) and the other `10.0.0.6` — the command on the main node would be:

```{bash}
torchrun \
  --nnodes=2 \
  --node_rank=0 \
  --nproc-per-node=8 \
  --rdzv_id=12347 \
  --rdzv_backend=c10d \
  --rdzv_conf='read_timeout=420' \
  --rdzv_endpoint=10.0.0.5:29404 \
  train/sft_peft.py \
  --per_device_train_batch_size=1 \
  --per_device_eval_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --train_file_path='simplescaling/s1K-1.1_tokenized' \
  --block_size=32768 \
  --model_name=Qwen/Qwen2.5-14B-Instruct \
  --warmup_ratio=0.05 \
  --fsdp='full_shard auto_wrap' \
  --fsdp_config='train/fsdp_config_qwen.json' \
  --bf16=True \
  --eval_strategy='steps' \
  --eval_steps=50 \
  --logging_steps=1 \
  --save_steps=100 \
  --lr_scheduler_type cosine \
  --learning_rate 1e-5 \
  --weight_decay 1e-4 \
  --adam_beta1=0.9 \
  --adam_beta2=0.95 \
  --output_dir='ckpts/t0_14b' \
  --hub_model_id='t0/t0_14b' \
  --push_to_hub=False \
  --hub_always_push=True \
  --num_train_epochs 5 \
  --save_only_model=True \
  --gradient_checkpointing=True \
  --report_to none \
  --lora=False \
  > logs/t0_14b.log 2>&1 &
```

On the second node (`10.0.0.6`):

```{bash}
torchrun \
  --nnodes=2 \
  --node_rank=1 \
  --nproc-per-node=8 \
  --rdzv_id=12347 \
  --rdzv_backend=c10d \
  --rdzv_conf='read_timeout=420' \
  --rdzv_endpoint=10.0.0.5:29404 \
  train/sft_peft.py \
  --per_device_train_batch_size=1 \
  --per_device_eval_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --train_file_path='simplescaling/s1K-1.1_tokenized' \
  --block_size=32768 \
  --model_name=Qwen/Qwen2.5-14B-Instruct \
  --warmup_ratio=0.05 \
  --fsdp='full_shard auto_wrap' \
  --fsdp_config='train/fsdp_config_qwen.json' \
  --bf16=True \
  --eval_strategy='steps' \
  --eval_steps=50 \
  --logging_steps=1 \
  --save_steps=100 \
  --lr_scheduler_type cosine \
  --learning_rate 1e-5 \
  --weight_decay 1e-4 \
  --adam_beta1=0.9 \
  --adam_beta2=0.95 \
  --output_dir='ckpts/t0_14b' \
  --hub_model_id='t0/t0_14b' \
  --push_to_hub=False \
  --hub_always_push=True \
  --num_train_epochs 5 \
  --save_only_model=True \
  --gradient_checkpointing=True \
  --report_to none \
  --lora=False \
  > logs/t0_14b.log 2>&1 &
```

### Training on an HPC Cluster

The command remains mostly the same but must be adapted to the specific cluster. Some parameters will be configured by the job scheduler.

For example, a SLURM submission script for a job on Isambard-AI might look like:

```{bash}
#!/bin/bash

#SBATCH --job-name=7B_2
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

# Activate environment
source /home/u5q/tomas.u5q/miniforge3/bin/activate
conda activate pytorch_env

# Set training parameters
base_model="Qwen/Qwen2.5-7B-Instruct"
train_dataset_name="simplescaling/s1K-1.1_tokenized"
export HF_HOME=/home/u5q/tomas.u5q/S1_workspace/HF_cache

# Logging
mkdir -p logs

# Shell safety
set -euo pipefail

# Environment variables
export WANDB_MODE=offline
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=8
export NUM_NODES=${SLURM_NNODES}
export REPLICA_RANK=${SLURM_PROCID}
export MASTER_NODE=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
export CUDA_LAUNCH_BLOCKING=0
export REPLICA_HOSTNAME=${MASTER_NODE}

# Training config
uid=$(date +%Y%m%d_%H%M%S)
lr=1e-5
epochs=1
micro_batch_size=1
gpu_count=${SLURM_GPUS_ON_NODE}
gradient_accumulation_steps=1
block_size=32768



# Launch training
srun torchrun \
    --nnodes=${NUM_NODES} \
    --node_rank=${REPLICA_RANK} \
    --nproc-per-node=${gpu_count} \
    --rdzv_id=12347 \
    --rdzv_backend=c10d \
    --rdzv_conf='read_timeout=420' \
    --rdzv_endpoint=${REPLICA_HOSTNAME}:29401 \
    /home/u5q/tomas.u5q/S1_workspace/t0/experiments/t0-000/s1_31a10f2/train/sft.py \
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
    --push_to_hub=False \
    --hub_always_push=False \
    --num_train_epochs ${epochs} \
    --save_only_model=True \
    --gradient_checkpointing=True \
    --report_to none \
    --lora=False
```
