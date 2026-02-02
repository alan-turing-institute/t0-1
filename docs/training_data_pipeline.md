# Training Data Generation Pipeline

This document describes the two-step pipeline to generate finetuning datasets from LLM reasoning traces.

## Step 1: Generate Reasoning Traces

Prompt an LLM with RAG-augmented patient queries and collect its reasoning traces.

```bash
uv run t0-1 evaluate-rag ./data/synthetic_queries/b971c41_gpt-4o_2000_synthetic_queries.jsonl \
    --k 5 \
    --db-choice chroma \
    --llm-provider azure \
    --llm-model-name gpt-oss-120b \
    --prompt-template-path ./templates/rag_evaluation_prompt_gpt_oss_native_reasoning.txt \
    --system-prompt-path ./templates/rag_evaluation_system_prompt_gpt_oss_native_reasoning.txt \
    --output-file ./evaluate-rag-gpt-oss-120b-k5-chroma-native.jsonl \
    --conditions-file ./data/nhs-conditions/v4/qwen_summarised_conditions.jsonl \
    --deepseek-r1 \
    --persist-directory ./v4-summarised-db \
    --local-file-store ./v4-summarised-lfs
```

**What it does:**
- For each synthetic patient query, retrieves k=5 relevant NHS condition documents via vector similarity search.
- Constructs a prompt with system instructions, retrieved context, patient symptoms, and demographics.
- Calls the LLM. The model reasons natively (reasoning is returned in `reasoning_content`) and `content` contains only the `(condition, severity)` answer.
- Writes results to a JSONL file with fields: `system_prompt`, `rag_message`, `rag_answer`, `rag_reasoning_content`, evaluation metrics, etc.

**Key files:**
- Shell scripts: `scripts/v4_summarised/k5/evaluate_rag_*.sh`
- Core logic: `src/t0_1/rag/evaluate.py`
- Prompt templates: `templates/rag_evaluation_prompt_*.txt`, `templates/rag_evaluation_system_prompt_*.txt`

**Notes:**
- Use `--llm-provider azure` (not `azure_openai`) — only the `azure` provider (patched `langchain-azure-ai`) forwards `reasoning_content`.
- The `_native_reasoning` prompt templates do not ask the model to use `<think>` tags. The model reasons natively and `content` is just the final answer.
- The `--deepseek-r1` flag enables parsing `(condition, severity)` from the response. It handles both `<think>`-tagged responses (legacy) and plain answers (native reasoning).

## Step 2: Apply Chat Template for SFT

Convert the JSONL output into a HuggingFace dataset with a `text` field formatted using the target model's chat template.

```bash
python scripts/apply_chat_template.py \
    --input-path ./evaluate-rag-gpt-oss-120b-k5-chroma-native.jsonl \
    --output-path ./data/reasoning_traces/2k-gpt-oss-120b-traces-k5_qwen_summarised_data_qwen_format \
    --model-name Qwen/Qwen2.5-32B-Instruct
```

For Gemma models (e.g., Gemma 3 27B):

```bash
python scripts/apply_chat_template.py \
    --input-path ./evaluate-rag-gpt-oss-120b-k5-chroma-native.jsonl \
    --output-path ./data/reasoning_traces/2k-gpt-oss-120b-traces-k5_qwen_summarised_data_gemma_format \
    --model-name google/gemma-3-27b-it
```

**What it does:**
- Loads the JSONL file and extracts: system prompt, user prompt, reasoning trace, and answer. If `rag_reasoning_content` is present, it is used as the reasoning trace and `rag_answer` as the answer. Otherwise, `<think>...</think>` tags are parsed from `rag_answer` (legacy format).
- Formats the reasoning trace and answer using model-appropriate thinking tokens:
  - **Qwen**: `<|im_start|>think` / `<|im_start|>answer`
  - **Gemma** (and others): `<think>` / `</think>`
- Applies the model's chat template via `tokenizer.apply_chat_template()` to produce the `text` field.
- Saves as a HuggingFace `DatasetDict` with a `train` split.

**Key file:** `scripts/apply_chat_template.py`
