# Setting up finetuning environment on Isambard-AI

## UV

### 1. Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Set up the system environment

```bash
export CC=$(which gcc)
export CXX=$(which g++)

# REPLACE THIS PATH WITH YOUR OWN WORKSPACE
export WORKSPACE=<<replace_with_your_workspace_path>>
```

### 3. Create and activate the virtual environment

```bash
uv python install 3.11

# Create a virtual environment in your workspace
mkdir -p $WORKSPACE/venvs
uv venv $WORKSPACE/venvs/t0_phase3 --python 3.11

# Activate the environment
source $WORKSPACE/venvs/t0_phase3/bin/activate
```

### 4. Install PyTorch

```bash
uv pip install torch --extra-index-url https://download.pytorch.org/whl/cu130
```

### 5. Install required packages

```bash
uv pip install \
    "openai==1.56.1" \
    "transformers==4.50.0" \
    "wandb==0.17.3" \
    "datasets==3.1.0" \
    "accelerate==1.0.1" \
    "ipykernel==6.28.0" \
    "gradio==4.44.0" \
    "trl==0.12.0" \
    "peft==0.15.2"
```

###  7. Install additional dependencies (Compilation)

```bash
uv pip install "liger-kernel<0.7.0"
FLASH_ATTN_CUDA_ARCHS="120" uv pip install flash-attn --no-build-isolation -v
```

### 9. Verify installation

```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```
