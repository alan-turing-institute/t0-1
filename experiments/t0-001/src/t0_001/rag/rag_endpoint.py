import uvicorn
from fastapi import FastAPI
from t0_001.rag.build_rag import (
    DEFAULT_RETRIEVER_CONFIG,
    RAG,
    RetrieverConfig,
    build_rag,
)


def create_rag_app(rag: RAG) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/query")
    async def query_endpoint(
        query: str,
    ):
        response = rag._query(query)
        return {"response": response}

    return app


def main(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    extra_body: dict | str | None = None,
    budget_forcing: bool = False,
    budget_forcing_kwargs: dict | str | None = None,
    budget_forcing_tokenizer: str | None = None,
):
    rag = build_rag(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
        extra_body=extra_body,
        budget_forcing=budget_forcing,
        budget_forcing_kwargs=budget_forcing_kwargs,
        budget_forcing_tokenizer=budget_forcing_tokenizer,
    )
    app = create_rag_app(rag)
    uvicorn.run(app, host=host, port=port)
