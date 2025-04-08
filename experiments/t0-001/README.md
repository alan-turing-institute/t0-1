# 001

## Setup

Clone the repository:
```bash
git clone git@github.com:alan-turing-institute/t0.git
cd experiments/t0-001
```

Install required dependencies (in editable mode) using [uv](https://github.com/astral-sh/uv):
```bash
uv pip install -e .
```

(JG did `uv sync` and that also seemed to work.)

## Interacting with the RAG system

Symlink the `nhs-conditions/` directory to here. Then: 

```sh
uv run t0-001 rag-chat
```

## Overview (by JG)

(NB: JG wrote this to make sure he understands the pipeline. He did not
write the pipeline!)

### 1. Generating evaluation sets




