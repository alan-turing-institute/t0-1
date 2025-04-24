import uvicorn
from fastapi import FastAPI
from t0_001.query_vector_store.build_retriever import (
    DEFAULT_RETRIEVER_CONFIG,
    CustomParentDocumentRetriever,
    RetrieverConfig,
    get_parent_doc_retriever,
)


def create_retriever_app(retriever: CustomParentDocumentRetriever) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/query")
    async def query_endpoint(query: str):
        response = await retriever.ainvoke(input=query)
        return {"response": response}

    return app


def main(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    serve: bool = True,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    if not serve and config.persist_directory is None:
        raise ValueError(
            "If serve is False, persist_directory must be passed so that the vector store is saved."
        )

    retriever = get_parent_doc_retriever(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
    )

    if serve:
        app = create_retriever_app(retriever)
        uvicorn.run(app, host=host, port=port)
