from t0_001.rag.build_rag import DEFAULT_RETRIEVER_CONFIG, RetrieverConfig, build_rag

INPUT_PROMPT: str = ">>> "
EXIT_STRS: set[str] = {"exit", "exit()", "quit()", "bye"}


def run_chat_interact(
    conditions_folder: str,
    main_only: bool = True,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
):
    rag = build_rag(
        conditions_folder=conditions_folder,
        main_only=main_only,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
        llm_model_name=llm_model_name,
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
            response = rag.query(question=message, user_id=user_id)
        elif mode == "query-with-sources":
            response = rag.query_with_sources(question=message, user_id=user_id)
        elif mode == "query-with-context":
            response = rag.query_with_context(question=message, user_id=user_id)

        print(f"\nModel: {response}")
