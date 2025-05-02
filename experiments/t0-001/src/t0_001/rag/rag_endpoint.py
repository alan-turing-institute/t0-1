from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from t0_001.rag.build_rag import (
    DEFAULT_RETRIEVER_CONFIG,
    RAG,
    RetrieverConfig,
    build_rag,
)


class QueryRequest(BaseModel):
    query: str
    thread_id: str | None = "0"


class ClearHistoryRequest(BaseModel):
    thread_id: str | None = "0"


def create_rag_app(rag: RAG) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.post("/query")
    async def query_endpoint(req: QueryRequest):
        response = rag._query(req.query, user_id=req.thread_id)
        return {"response": response, "thread_id": req.thread_id}

    # Delete history
    @app.post("/clear_history")
    async def clear_history_endpoint(req: ClearHistoryRequest):
        rag.clear_history(thread_id=req.thread_id)
        return {"status": "success", "thread_id": req.thread_id}

    return app


def main(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    extra_body: dict | str | None = None,
    conversational: bool = False,
    conversational_agent_llm_provider: str | None = None,
    conversational_agent_llm_model_name: str | None = None,
    conversational_agent_extra_body: dict | str | None = None,
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
    budget_forcing: bool = False,
    budget_forcing_kwargs: dict | str | None = None,
    budget_forcing_tokenizer: str | None = None,
    rerank: bool = False,
    rerank_prompt_template_path: str | Path | None = None,
    rerank_llm_provider: str | None = None,
    rerank_llm_model_name: str | None = None,
    rerank_extra_body: dict | str | None = None,
    rerank_k: int = 5,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    rag = build_rag(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        extra_body=extra_body,
        conversational=conversational,
        conversational_agent_llm_provider=conversational_agent_llm_provider,
        conversational_agent_llm_model_name=conversational_agent_llm_model_name,
        conversational_agent_extra_body=conversational_agent_extra_body,
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
        budget_forcing=budget_forcing,
        budget_forcing_kwargs=budget_forcing_kwargs,
        budget_forcing_tokenizer=budget_forcing_tokenizer,
        rerank=rerank,
        rerank_prompt_template_path=rerank_prompt_template_path,
        rerank_llm_provider=rerank_llm_provider,
        rerank_llm_model_name=rerank_llm_model_name,
        rerank_extra_body=rerank_extra_body,
        rerank_k=rerank_k,
    )
    app = create_rag_app(rag)
    uvicorn.run(app, host=host, port=port)
