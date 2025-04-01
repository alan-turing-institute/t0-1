import uvicorn
from fastapi import FastAPI
from langchain_core.vectorstores import VectorStore
from t0_001.query_vector_store.build_index import (
    DataIndexCreator,
    setup_embedding_model,
    setup_text_splitter,
)
from t0_001.query_vector_store.utils import load_conditions


def create_db_app(db: VectorStore) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/query")
    async def query_endpoint(query: str):
        # Perform the query on the vector store
        results = db.similarity_search(query)
        return {"results": results}

    return app


def main(
    conditions_folder: str,
    main_only: bool = True,
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: int = 50,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    conditions = load_conditions(conditions_folder, main_only)
    embedding_model = setup_embedding_model(embedding_model_name)
    text_splitter = setup_text_splitter(embedding_model_name, chunk_overlap)
    index_creator = DataIndexCreator(embedding_model, text_splitter)
    index_creator.create_index(
        db="chroma",
        documents=list(conditions.values()),
        metadatas=[{"source": k} for k in conditions.keys()],
    )
    app = create_db_app(index_creator.db)
    uvicorn.run(app, host=host, port=port)
