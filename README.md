# t0

## Directory structure

This repository contains subfolders for different parts of the `t0` project:
```
experiments/         -- Fine-tuning and evaluation
  |
  +-- t0-000/        -- s1 replication work
  +-- t0-001/        -- Retrieval + Reasoning demonstration work

use-cases/           -- Documentation and code for generating use cases
  |
  +-- nhs-conditions/

planning/            -- Sprint planning
```

## Environment set-up

Each subfolder should have it's own environment.

Install `uv` for Python dependency management.

Copy the `.env.example` to `.env` and populate the environment variables within the `.env` file.
