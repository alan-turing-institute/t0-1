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
