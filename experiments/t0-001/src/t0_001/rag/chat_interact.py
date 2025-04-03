from t0_001.rag.build_rag import build_rag

INPUT_PROMPT: str = ">>> "
EXIT_STRS: set[str] = {"exit", "exit()", "quit()", "bye"}


def run_chat_interact(
    conditions_folder: str,
    main_only: bool = True,
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: int = 50,
    db_choice: str = "chroma",
    k: int = 4,
    with_score: bool = False,
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
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
    user_id = "command_line_chat"
    mode = "query-with-sources"

    while True:
        message = input(INPUT_PROMPT)
        if message in EXIT_STRS:
            return
        elif message == "query-mode":
            mode = "query"
            print("Switched to query mode.")
            continue
        elif message == "query-with-sources-mode":
            mode = "query-with-sources"
            print("Switched to query-with-sources mode.")
            continue
        elif message == "query-with-context-mode":
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
