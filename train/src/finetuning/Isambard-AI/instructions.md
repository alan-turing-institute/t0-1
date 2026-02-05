# Setting up finetuning environment on Isambard-AI

## Miniforge (Conda)

### 1. Install Miniforge (Conda)

Install the latest version of Miniforge in your home directory:

```bash
cd $HOME
curl --location --remote-name "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
rm Miniforge3-$(uname)-$(uname -m).sh
```

Follow the prompts to complete the installation. After installation, restart your shell or run `source ~/.bashrc` to activate conda.

### 2. Request an interactive GPU session

Request an interactive session with 1 GPU and 4 hours of compute time:
```bash
srun -N 1 --gpus 1 --mem=0 --time=04:00:00 --pty bash
```

**Note**: The installation typically takes 30-60 minutes or even up to 2 hours if compiling `flash-attn`. The 4-hour allocation provides buffer time for troubleshooting.

### 3. Set up the environment

**Important**: Replace the WORKSPACE path below with your own directory path.

Load required modules and set environment variables:
```bash
module load cuda/12.6
module load gcc-native/13.2

export CC=$(which gcc)
export CXX=$(which g++)

# REPLACE THIS PATH WITH YOUR OWN WORKSPACE
export WORKSPACE=<<replace_with_your_workspace_path>>
```

### 4. Create and activate conda environment

Create a new conda environment with Python 3.11:
```bash
mkdir -p $WORKSPACE/conda_env/
mamba create --prefix $WORKSPACE/conda_env/t0_phase3 python=3.11 -y
conda activate $WORKSPACE/conda_env/t0_phase3
```

#### 5. Install PyTorch

Install PyTorch 2.6 with CUDA 12.6 support:
```bash
python -m pip install torch==2.6 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu126
```

#### 6. Install required packages

Install the remaining dependencies (updated from original S1 setup to use PyTorch 2.6 and Transformers 4.50.0):
```bash
python -m pip install \
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

**Changes from original S1 setup:**
- Updated: `torch` (2.5.1 → 2.6), `transformers` (4.46.1 → 4.50.0)
- Removed: `vllm` (not currently needed for this phase)

#### 7. Install additional dependencies

Install liger-kernel for Gemma model support and flash-attn for attention optimisation:

Note: `flash-attn` requires `cuda/12.6` and `gcc-native/13.2` modules to be loaded as done in step 3. It may take up to 1-2 hours to compile.

```bash
python -m pip install liger-kernel
python -m pip install flash-attn --no-build-isolation
```

#### 8. Clone the repository

Clone the t0-1 repository to your workspace:
```bash
cd $WORKSPACE
git clone https://github.com/alan-turing-institute/t0-1.git
cd t0-1
```

#### 9. Verify installation

Verify that PyTorch can detect the GPU:
```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```

Expected output should show PyTorch 2.6.x, CUDA available as `True`, and CUDA version 12.6.

## UV

### 1. Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Request an interactive GPU session

```bash
srun -N 1 --gpus 1 --mem=0 --time=04:00:00 --pty bash
```

### 3. Set up the system environment

```bash
module load cuda/12.6
module load gcc-native/13.2

export CC=$(which gcc)
export CXX=$(which g++)

# REPLACE THIS PATH WITH YOUR OWN WORKSPACE
export WORKSPACE=<<replace_with_your_workspace_path>>
```

### 4. Create and activate the virtual environment

```bash
uv python install 3.11

# Create a virtual environment in your workspace
mkdir -p $WORKSPACE/venvs
uv venv $WORKSPACE/venvs/t0_phase3 --python 3.11

# Activate the environment
source $WORKSPACE/venvs/t0_phase3/bin/activate
```

### 5. Install PyTorch

```bash
uv pip install torch==2.6 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

### 6. Install required packages

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
uv pip install liger-kernel
uv pip install flash-attn --no-build-isolation
```

### 8. Clone the repository

```bash
cd $WORKSPACE
git clone https://github.com/alan-turing-institute/t0-1.gi
```

### 9. Verify installation

```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```