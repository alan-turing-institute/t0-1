from enum import Enum
from typing import Final


class DBChoice(str, Enum):
    chroma = "chroma"
    faiss = "faiss"


class LLMProvider(str, Enum):
    huggingface = "huggingface"
    azure_openai = "azure_openai"
    azure = "azure"
    openai = "openai"
    openai_completion = "openai_completion"


CONDITIONS_FILE: Final[str] = "./data/nhs-conditions/v3/conditions.jsonl"

DEFAULTS = {
    "embedding_model_name": "sentence-transformers/all-mpnet-base-v2",
    "chunk_overlap": 50,
    "db_choice": DBChoice.chroma,
    "persist_directory": None,
    "local_file_store": None,
    "search_type": "similarity",
    "k": 4,
    "with_score": False,
    "llm_provider": LLMProvider.huggingface,
    "llm_model_name": "Qwen/Qwen2.5-1.5B-Instruct",
    "prompt_template_path": None,
    "system_prompt_path": None,
    "force_create": False,
    "trust_source": False,
    "serve": True,
    "host": "0.0.0.0",
    "port": 8000,
    "env_file": ".env",
    "budget_forcing": False,
    "budget_forcing_kwargs": '{"max_tokens_thinking": 1024, "num_stop_skips": 3}',
    "rerank_prompt_template_path": None,
    "rerank_llm_provider": LLMProvider.huggingface,
    "rerank_llm_model_name": "Qwen/Qwen2.5-1.5B-Instruct",
    "max_queries_per_minute": 60,
}
