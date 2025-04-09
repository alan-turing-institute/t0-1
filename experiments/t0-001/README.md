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


### Azure AI Foundry Endpoints

The endpoints and the corresponding API keys can be viewed on the Models + endpoints page of the Azure AI Foundry portal:

Go to `https://ai.azure.com/`, select the `ai_foundry_t0 project`, then in the left pane under `My Assets`, select `Models + endpoints`. You should see a list of endpoints for different models. The endpoints and keys can be viewed by clicking on a model (e.g., `o3-mini`). The key is in the protected section under Endpoint grouping, and the actual endpoint is the Target URI, but only up to the part including ai.azure.com (e.g., https://ai-aifoundrygpt4o065309524447.openai.azure.com).

<img src="img/Azure_Endpoint.png" alt="AI Foundry Endpoint" width="600"/>

To test the endpoints, you can run the `scripts/test_Azure_models.py` script, but don't forget to set the environment variables as listed in the `.env.example` file.

#### Pricing of the models

| Model         | Price per 1M Tokens (USD) |
|---------------|----------------------------|
| gpt-4o        | 4.38                       |
| o3-mini       | 1.93                       |
| DeepSeek-V3   | 2.00                       |
| DeepSeek-R1   | 2.36                       |
| o1            | 26.25                      |
