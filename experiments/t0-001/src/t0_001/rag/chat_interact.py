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
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
    extra_body: dict | str | None = None,
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
    )
    user_id = "command_line_chat"
    mode = "query-with-sources"

    while True:
        message = input(INPUT_PROMPT)
        if message in EXIT_STRS:
            return
        elif message == "\query-mode":
            mode = "query"
            print("Switched to query mode.")
            continue
        elif message == "\query-with-sources-mode":
            mode = "query-with-sources"
            print("Switched to query-with-sources mode.")
            continue
        elif message == "\query-with-context-mode":
            mode = "query-with-context"
            print("Switched to query-with-context mode.")
            continue
        elif message == "":
            continue

        if mode == "query":
            response = await rag.aquery(question=message, user_id=user_id)
        elif mode == "query-with-sources":
            response = await rag.aquery_with_sources(question=message, user_id=user_id)
        elif mode == "query-with-context":
            response = await rag.aquery_with_context(question=message, user_id=user_id)

        print(f"\nModel: {response}")
