from pathlib import Path

import uvicorn
from fastapi import FastAPI
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from t0_001.query_vector_store.build_index import get_vector_store


def create_db_app(db: VectorStore) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/query")
    async def query_endpoint(
        query: str,
        k: int = 4,
        with_score: bool = False,
    ):
        if with_score:
            response: list[tuple[float, Document]] = db.similarity_search_with_score(
                query=query, k=k
            )
            # if the scores are numpy floats, convert them to floats
            response = [
                (doc, float(score)) if hasattr(score, "item") else (doc, score)
                for doc, score in response
            ]
        else:
            response: list[Document] = db.similarity_search(query=query, k=k)
        return {"response": response}

    return app


def main(
    conditions_folder: str,
    main_only: bool = True,
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: int = 50,
    db_choice: str = "chroma",
    persist_directory: str | Path = None,
    force_create: bool = False,
    trust_source: bool = False,
    serve: bool = True,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    if not serve and persist_directory is None:
        raise ValueError(
            "If serve is False, persist_directory must be passed so that the vector store is saved."
        )
    db = get_vector_store(
        conditions_folder=conditions_folder,
        main_only=main_only,
        embedding_model_name=embedding_model_name,
        chunk_overlap=chunk_overlap,
        db_choice=db_choice,
        persist_directory=persist_directory,
        force_create=force_create,
        trust_source=trust_source,
    )
    if serve:
        app = create_db_app(db)
        uvicorn.run(app, host=host, port=port)
