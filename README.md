# t0

## Directory structure

```
src/                 -- Common code
use-cases/           -- Documentation and code for compiling use cases
  +-- nhs-conditions/
experiments/         -- Fine-tuning and evaluation
  +-- 001/
```


## Environment setup
`uv venv`

`uv pip install -r pyproject.toml`

`source .venv/bin/activate`

## Running the code

`cd src`

`python overly_simple_s1.py --output_dir="fine_tuned_model"`
