from enum import Enum
from typing import Final


class DBChoice(str, Enum):
    chroma = "chroma"
    faiss = "faiss"


CONDITIONS_FOLDER: Final[str] = "./nhs-use-case/conditions/"

DEFAULTS = {
    "main_only": True,
    "embedding_model_name": "sentence-transformers/all-mpnet-base-v2",
    "chunk_overlap": 50,
    "db_choice": DBChoice.chroma,
    "persist_directory": None,
    "force_create": False,
    "trust_source": False,
    "serve": True,
    "host": "0.0.0.0",
    "port": 8000,
    "k": 4,
    "with_score": False,
    "llm_model_name": "Qwen/Qwen2.5-1.5B-Instruct",
}
