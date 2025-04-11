from enum import Enum
from typing import Final


class DBChoice(str, Enum):
    chroma = "chroma"
    faiss = "faiss"


class LLMProvider(str, Enum):
    huggingface = "huggingface"
    azure_openai = "azure_openai"
    azure = "azure"


CONDITIONS_FOLDER: Final[str] = "./nhs-use-case/conditions/"

DEFAULTS = {
    "main_only": True,
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
    "force_create": False,
    "trust_source": False,
    "serve": True,
    "host": "0.0.0.0",
    "port": 8000,
    "env_file": ".env",
}
