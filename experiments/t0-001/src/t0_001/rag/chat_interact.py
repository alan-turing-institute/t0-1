from pathlib import Path

from t0_001.rag.build_rag import DEFAULT_RETRIEVER_CONFIG, RetrieverConfig, build_rag

INPUT_PROMPT: str = ">>> "
EXIT_STRS: set[str] = {"exit", "exit()", "quit()", "bye"}


async def run_chat_interact(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    conversational: bool = False,
    conversational_agent_llm_provider: str | None = None,
    conversational_agent_llm_model_name: str | None = None,
    conversational_agent_extra_body: dict | str | None = None,
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
    extra_body: dict | str | None = None,
    budget_forcing: bool = False,
    budget_forcing_kwargs: dict | str | None = None,
    budget_forcing_tokenizer: str | None = None,
    rerank: bool = False,
    rerank_prompt_template_path: str | Path | None = None,
    rerank_llm_provider: str | None = None,
    rerank_llm_model_name: str | None = None,
    rerank_extra_body: dict | str | None = None,
    rerank_k: int = 5,
):
    rag = build_rag(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        conversational=conversational,
        conversational_agent_llm_provider=conversational_agent_llm_provider,
        conversational_agent_llm_model_name=conversational_agent_llm_model_name,
        conversational_agent_extra_body=conversational_agent_extra_body,
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
        extra_body=extra_body,
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
    user_id = "command_line_chat"
    mode = "query-with-sources"

    while True:
        message = input(INPUT_PROMPT)
        if message in EXIT_STRS:
            return
        elif message == "\\query-mode":
            mode = "query"
            print("Switched to query mode.")
            continue
        elif message == "\\query-with-sources-mode":
            mode = "query-with-sources"
            print("Switched to query-with-sources mode.")
            continue
        elif message == "\\query-with-context-mode":
            mode = "query-with-context"
            print("Switched to query-with-context mode.")
            continue
        elif message == "":
            continue

        if message == "\\clear-history":
            response = await rag.aclear_history(thread_id=user_id)
            print("Chat history cleared.")
            continue

        if mode == "query":
            response = await rag.aquery(question=message, user_id=user_id)
        elif mode == "query-with-sources":
            response = await rag.aquery_with_sources(question=message, user_id=user_id)
        elif mode == "query-with-context":
            response = await rag.aquery_with_context(question=message, user_id=user_id)

        print(f"\nModel: {response}")
