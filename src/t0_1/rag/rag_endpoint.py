import os
import random
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from t0_1.rag.build_rag import (
    DEFAULT_RETRIEVER_CONFIG,
    RAG,
    RetrieverConfig,
    build_rag,
)
from t0_1.rag.request_logger import logged_stream


class QueryRequest(BaseModel):
    query: str
    thread_id: str | None = "0"
    demographics: str | None = None


class ClearHistoryRequest(BaseModel):
    thread_id: str | None = "0"


def create_rag_app(rag: RAG) -> FastAPI:
    app = FastAPI()
    app.state.active_thread_ids = set()
    log_dir = os.environ.get("T0_LOG_DIR", "./logs")

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/new_thread_id")
    async def new_thread_id():
        ADJECTIVES = [
            "adorable",
            "bubbly",
            "cheerful",
            "dizzy",
            "fluffy",
            "happy",
            "jolly",
            "kind",
            "lovely",
            "mellow",
            "nifty",
            "peppy",
            "plucky",
            "precious",
            "quiet",
            "rosy",
            "sleepy",
            "soft",
            "sparkly",
            "sunny",
            "sweet",
            "tiny",
            "warm",
            "zesty",
            "zany",
            "glowy",
            "gentle",
            "bright",
            "dreamy",
            "charming",
            "fuzzy",
            "smiley",
            "tender",
            "chirpy",
        ]
        ANIMALS = [
            "bunny",
            "kitten",
            "puppy",
            "duckling",
            "hedgehog",
            "penguin",
            "panda",
            "fawn",
            "lamb",
            "koala",
            "hamster",
            "otter",
            "sloth",
            "mouse",
            "calf",
            "seal",
            "whale",
            "swan",
            "cub",
            "foal",
            "quokka",
            "flamingo",
            "starling",
            "parakeet",
            "caterpillar",
            "guinea",
            "deerling",
            "shrew",
            "snail",
            "turtle",
            "wren",
            "goldfinch",
            "bluebird",
            "mole",
            "cygnet",
            "gosling",
        ]

        def _generate():
            return (
                f"{random.choice(ADJECTIVES)}"
                f"-{random.choice(ANIMALS)}"
                f"-{random.randint(0, 99):02}"
            )

        while (new_random_thread_id := _generate()) in app.state.active_thread_ids:
            pass
        app.state.active_thread_ids.add(new_random_thread_id)
        return {"thread_id": new_random_thread_id}

    @app.post("/query")
    async def query_endpoint(req: QueryRequest):
        app.state.active_thread_ids.add(req.thread_id)
        response = await rag._aquery(
            req.query, thread_id=req.thread_id, demographics=req.demographics
        )
        return {
            "response": response,
            "thread_id": req.thread_id,
            "demographics": req.demographics,
        }

    @app.post("/query_stream")
    async def query_stream_endpoint(req: QueryRequest):
        app.state.active_thread_ids.add(req.thread_id)
        stream = rag._query_stream(
            req.query,
            thread_id=req.thread_id,
            demographics=req.demographics,
        )
        return StreamingResponse(
            logged_stream(stream, req.model_dump(), req.thread_id, log_dir),
        )

    # Delete history
    @app.post("/clear_history")
    async def clear_history_endpoint(req: ClearHistoryRequest):
        rag.clear_history(thread_id=req.thread_id)
        app.state.active_thread_ids.discard(req.thread_id)
        return {"status": "success", "thread_id": req.thread_id}

    @app.get("/get_history")
    async def get_history(thread_id: str = "0"):
        try:
            conversation_messages = rag.get_message_history(thread_id=thread_id)
        except AttributeError as e:
            raise HTTPException(status_code=404, detail="Thread ID not found") from e
        else:
            return {"messages": conversation_messages, "thread_id": thread_id}

    @app.get("/get_thread_ids")
    async def get_thread_ids():
        return {"thread_ids": rag.get_thread_ids()}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
    seed: int | None = None,
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
        seed=seed,
    )
    app = create_rag_app(rag)
    uvicorn.run(app, host=host, port=port)
