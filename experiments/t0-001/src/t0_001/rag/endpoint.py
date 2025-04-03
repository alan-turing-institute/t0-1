import uvicorn
from fastapi import FastAPI
from t0_001.rag.build_rag import RAG, build_rag


def create_rag_app(rag: RAG) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/query")
    async def query_endpoint(
        query: str, k: int | None = None, with_score: bool | None = None
    ):
        if k is not None:
            rag.k = k
        if with_score is not None:
            rag.with_score = with_score
        response = rag.query(query)
        return {"response": response}

    return app


def main(
    conditions_folder: str,
    main_only: bool = True,
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: int = 50,
    db_choice: str = "chroma",
    k: int = 4,
    with_score: bool = False,
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    host: str = "0.0.0.0",
    port: int = 8000,
):
    rag = build_rag(
        conditions_folder=conditions_folder,
        main_only=main_only,
        embedding_model_name=embedding_model_name,
        chunk_overlap=chunk_overlap,
        db_choice=db_choice,
        k=k,
        with_score=with_score,
        llm_model_name=llm_model_name,
    )
    app = create_rag_app(rag)
    uvicorn.run(app, host=host, port=port)
