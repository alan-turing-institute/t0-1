import logging
import os
from typing import Annotated

import requests
import typer
from t0_001.defaults import CONDITIONS_FOLDER, DEFAULTS, DBChoice, LLMProvider
from t0_001.utils import load_env_file

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

HELP_TEXT = {
    "data_folder": "Path to the data folder.",
    "main_only": "If True, only the main element of the HTML file is extracted.",
    "embedding_model_name": "Name of the embedding model.",
    "chunk_overlap": "Chunk overlap for the text splitter.",
    "db_choice": "Database choice.",
    "persist_directory": "Path to the directory where the database is (or will be) stored.",
    "local_file_store": "Path to the directory where the local file store (or will be) stored.",
    "search_type": "Type of search to perform for retriever.",
    "force_create": "If True, force the creation of the database even if it already exists.",
    "trust_source": "If True, trust the source of the data index. This is needed for loading in FAISS databases.",
    "query": "The query to search for.",
    "k": "Number of results to return.",
    "with_score": "If True, return the score of the similarity search.",
    "llm_provider": "Service provider for the LLM.",
    "llm_model_name": "Name of the LLM model.",
    "prompt_template_path": "Path to the prompt template file.",
    "system_prompt_path": "Path to the system prompt file.",
    "generate_only": "If True, only generate the responses from the queries without evaluating.",
    "serve": "If True, serve the vector store as a FastAPI app. If False, make sure that persist_directory must be passed.",
    "host_serve": "Host to listen on.",
    "port_serve": "Port to listen on.",
    "host_query": "Host to query.",
    "port_query": "Port to query.",
    "env_file": "Path to the .env file.",
}


def set_up_logging_config(level: int = 20) -> None:
    logging.getLogger(__name__)
    logging.basicConfig(
        datefmt=r"%Y-%m-%d %H:%M:%S",
        format="%(asctime)s [%(levelname)8s] %(message)s",
        level=level,
    )


@cli.command()
def serve_vector_store(
    data_folder: Annotated[
        str, typer.Option(envvar="T0_DATA_FOLDER", help=HELP_TEXT["data_folder"])
    ] = CONDITIONS_FOLDER,
    main_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["main_only"]),
    ] = DEFAULTS["main_only"],
    embedding_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["embedding_model_name"])
    ] = DEFAULTS["embedding_model_name"],
    chunk_overlap: Annotated[
        int, typer.Option(help=HELP_TEXT["chunk_overlap"])
    ] = DEFAULTS["chunk_overlap"],
    db_choice: Annotated[
        DBChoice, typer.Option(help=HELP_TEXT["db_choice"])
    ] = DEFAULTS["db_choice"],
    persist_directory: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["persist_directory"]),
    ] = DEFAULTS["persist_directory"],
    force_create: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["force_create"]),
    ] = DEFAULTS["force_create"],
    trust_source: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["trust_source"]),
    ] = DEFAULTS["trust_source"],
    serve: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["serve"]),
    ] = DEFAULTS["serve"],
    host: Annotated[str, typer.Option(help=HELP_TEXT["host_serve"])] = DEFAULTS["host"],
    port: Annotated[int, typer.Option(help=HELP_TEXT["port_serve"])] = DEFAULTS["port"],
):
    """
    Run the query vector store server.
    """
    set_up_logging_config()
    if serve:
        logging.info("Starting query vector store server...")

    from t0_001.query_vector_store.index_endpoint import VectorStoreConfig, main

    main(
        conditions_folder=data_folder,
        main_only=main_only,
        config=VectorStoreConfig(
            embedding_model_name=embedding_model_name,
            chunk_overlap=chunk_overlap,
            db_choice=db_choice,
            persist_directory=persist_directory,
        ),
        force_create=force_create,
        trust_source=trust_source,
        serve=serve,
        host=host,
        port=port,
    )


@cli.command()
def query_vector_store(
    query: Annotated[str, typer.Argument(help=HELP_TEXT["query"])],
    k: Annotated[int, typer.Option(help=HELP_TEXT["k"])] = DEFAULTS["k"],
    with_score: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["with_score"]),
    ] = DEFAULTS["with_score"],
    host: Annotated[str, typer.Option(help=HELP_TEXT["host_query"])] = DEFAULTS["host"],
    port: Annotated[int, typer.Option(help=HELP_TEXT["port_query"])] = DEFAULTS["port"],
):
    """
    Query the vector store.
    """
    set_up_logging_config()
    logging.info("Querying vector store...")
    logging.info(f"Query: {query}")

    req = requests.get(
        f"http://{host}:{port}/query",
        params={"query": query, "k": k, "with_score": with_score},
    )

    if req.status_code != 200:
        logging.error(f"Error querying vector store: {req.text}")
        return

    logging.info(f"Response: {req.json()}")


@cli.command()
def evaluate_vector_store(
    input_file: Annotated[str, typer.Argument(help="Path to the input file.")],
    output_file: Annotated[
        str, typer.Option(help="Path to the output file.")
    ] = "./data/evaluation/evaluation_vector_store_results.jsonl",
    query_field: Annotated[
        str, typer.Option(help="Field name for the query in the input file.")
    ] = "symptoms_description",
    target_document_field: Annotated[
        str,
        typer.Option(help="Field name for the target document in the input file."),
    ] = "conditions_title",
    conditions_folder: Annotated[
        str, typer.Option(envvar="T0_DATA_FOLDER", help=HELP_TEXT["data_folder"])
    ] = CONDITIONS_FOLDER,
    main_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["main_only"]),
    ] = DEFAULTS["main_only"],
    embedding_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["embedding_model_name"])
    ] = DEFAULTS["embedding_model_name"],
    chunk_overlap: Annotated[
        int, typer.Option(help=HELP_TEXT["chunk_overlap"])
    ] = DEFAULTS["chunk_overlap"],
    db_choice: Annotated[
        DBChoice, typer.Option(help=HELP_TEXT["db_choice"])
    ] = DEFAULTS["db_choice"],
    persist_directory: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["persist_directory"]),
    ] = DEFAULTS["persist_directory"],
    force_create: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["force_create"]),
    ] = DEFAULTS["force_create"],
    trust_source: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["trust_source"]),
    ] = DEFAULTS["trust_source"],
    k: Annotated[int, typer.Option(help=HELP_TEXT["k"])] = DEFAULTS["k"],
):
    """
    Evaluate the vector store.
    """
    set_up_logging_config()
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")

    logging.info("Evaluating vector store...")

    from t0_001.query_vector_store.evaluate import VectorStoreConfig, main

    main(
        input_file=input_file,
        output_file=output_file,
        query_field=query_field,
        target_document_field=target_document_field,
        conditions_folder=conditions_folder,
        main_only=main_only,
        config=VectorStoreConfig(
            embedding_model_name=embedding_model_name,
            chunk_overlap=chunk_overlap,
            db_choice=db_choice,
            persist_directory=persist_directory,
        ),
        force_create=force_create,
        trust_source=trust_source,
        k=k,
    )


@cli.command()
def serve_retriever(
    data_folder: Annotated[
        str, typer.Option(envvar="T0_DATA_FOLDER", help=HELP_TEXT["data_folder"])
    ] = CONDITIONS_FOLDER,
    main_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["main_only"]),
    ] = DEFAULTS["main_only"],
    embedding_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["embedding_model_name"])
    ] = DEFAULTS["embedding_model_name"],
    chunk_overlap: Annotated[
        int, typer.Option(help=HELP_TEXT["chunk_overlap"])
    ] = DEFAULTS["chunk_overlap"],
    db_choice: Annotated[
        DBChoice, typer.Option(help=HELP_TEXT["db_choice"])
    ] = DEFAULTS["db_choice"],
    persist_directory: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["persist_directory"]),
    ] = DEFAULTS["persist_directory"],
    local_file_store: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["local_file_store"]),
    ] = DEFAULTS["local_file_store"],
    search_type: Annotated[str, typer.Option(help=HELP_TEXT["search_type"])] = DEFAULTS[
        "search_type"
    ],
    k: Annotated[int, typer.Option(help=HELP_TEXT["k"])] = DEFAULTS["k"],
    force_create: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["force_create"]),
    ] = DEFAULTS["force_create"],
    trust_source: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["trust_source"]),
    ] = DEFAULTS["trust_source"],
    serve: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["serve"]),
    ] = DEFAULTS["serve"],
    host: Annotated[str, typer.Option(help=HELP_TEXT["host_serve"])] = DEFAULTS["host"],
    port: Annotated[int, typer.Option(help=HELP_TEXT["port_serve"])] = DEFAULTS["port"],
):
    """
    Run the retriever server.
    """
    set_up_logging_config()
    logging.info("Starting retriever server...")

    from t0_001.query_vector_store.build_retriever import RetrieverConfig
    from t0_001.query_vector_store.retriever_endpoint import main

    main(
        conditions_folder=data_folder,
        main_only=main_only,
        config=RetrieverConfig(
            embedding_model_name=embedding_model_name,
            chunk_overlap=chunk_overlap,
            db_choice=db_choice,
            persist_directory=persist_directory,
            local_file_store=local_file_store,
            search_type=search_type,
            k=k,
            search_kwargs={},
        ),
        force_create=force_create,
        trust_source=trust_source,
        serve=serve,
        host=host,
        port=port,
    )


@cli.command()
def query_retriever(
    query: Annotated[str, typer.Argument(help=HELP_TEXT["query"])],
    host: Annotated[str, typer.Option(help=HELP_TEXT["host_query"])] = DEFAULTS["host"],
    port: Annotated[int, typer.Option(help=HELP_TEXT["port_query"])] = DEFAULTS["port"],
):
    """
    Query the retriever.
    """
    set_up_logging_config()
    logging.info("Querying retriever...")
    logging.info(f"Query: {query}")

    req = requests.get(f"http://{host}:{port}/query", params={"query": query})

    if req.status_code != 200:
        logging.error(f"Error querying retriever: {req.text}")
        return

    logging.info(f"Response: {req.json()}")


@cli.command()
def serve_rag(
    data_folder: Annotated[
        str, typer.Option(envvar="T0_DATA_FOLDER", help=HELP_TEXT["data_folder"])
    ] = CONDITIONS_FOLDER,
    main_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["main_only"]),
    ] = DEFAULTS["main_only"],
    embedding_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["embedding_model_name"])
    ] = DEFAULTS["embedding_model_name"],
    chunk_overlap: Annotated[
        int, typer.Option(help=HELP_TEXT["chunk_overlap"])
    ] = DEFAULTS["chunk_overlap"],
    db_choice: Annotated[
        DBChoice, typer.Option(help=HELP_TEXT["db_choice"])
    ] = DEFAULTS["db_choice"],
    persist_directory: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["persist_directory"]),
    ] = DEFAULTS["persist_directory"],
    local_file_store: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["local_file_store"]),
    ] = DEFAULTS["local_file_store"],
    search_type: Annotated[str, typer.Option(help=HELP_TEXT["search_type"])] = DEFAULTS[
        "search_type"
    ],
    k: Annotated[int, typer.Option(help=HELP_TEXT["k"])] = DEFAULTS["k"],
    force_create: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["force_create"]),
    ] = DEFAULTS["force_create"],
    trust_source: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["trust_source"]),
    ] = DEFAULTS["trust_source"],
    llm_provider: Annotated[
        LLMProvider, typer.Option(help=HELP_TEXT["llm_provider"])
    ] = DEFAULTS["llm_provider"],
    llm_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["llm_model_name"])
    ] = DEFAULTS["llm_model_name"],
    prompt_template_path: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["prompt_template_path"]),
    ] = DEFAULTS["prompt_template_path"],
    system_prompt_path: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["system_prompt_path"]),
    ] = DEFAULTS["system_prompt_path"],
    env_file: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["env_file"]),
    ] = DEFAULTS["env_file"],
    host: Annotated[str, typer.Option(help=HELP_TEXT["host_serve"])] = DEFAULTS["host"],
    port: Annotated[int, typer.Option(help=HELP_TEXT["port_serve"])] = DEFAULTS["port"],
):
    """
    Run the RAG server.
    """
    set_up_logging_config()
    load_env_file(env_file)
    logging.info("Starting RAG server...")

    from t0_001.query_vector_store.build_retriever import RetrieverConfig
    from t0_001.rag.rag_endpoint import main

    main(
        conditions_folder=data_folder,
        main_only=main_only,
        config=RetrieverConfig(
            embedding_model_name=embedding_model_name,
            chunk_overlap=chunk_overlap,
            db_choice=db_choice,
            persist_directory=persist_directory,
            local_file_store=local_file_store,
            search_type=search_type,
            k=k,
            search_kwargs={},
        ),
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
        host=host,
        port=port,
    )


@cli.command()
def query_rag(
    query: Annotated[str, typer.Argument(help=HELP_TEXT["query"])],
    host: Annotated[str, typer.Option(help=HELP_TEXT["host_query"])] = DEFAULTS["host"],
    port: Annotated[int, typer.Option(help=HELP_TEXT["port_query"])] = DEFAULTS["port"],
):
    """
    Query the vector store.
    """
    set_up_logging_config()
    logging.info("Querying RAG model...")
    logging.info(f"Query: {query}")

    req = requests.get(f"http://{host}:{port}/query", params={"query": query})

    if req.status_code != 200:
        logging.error(f"Error RAG model: {req.text}")
        return

    logging.info(f"Response: {req.json()}")


@cli.command()
def evaluate_rag(
    input_file: Annotated[str, typer.Argument(help="Path to the input file.")],
    generate_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["generate_only"]),
    ] = False,
    output_file: Annotated[
        str, typer.Option(help="Path to the output file.")
    ] = "./data/evaluation/evaluation_rag_results.jsonl",
    query_field: Annotated[
        str, typer.Option(help="Field name for the query in the input file.")
    ] = "symptoms_description",
    target_document_field: Annotated[
        str,
        typer.Option(help="Field name for the target document in the input file."),
    ] = "conditions_title",
    conditions_folder: Annotated[
        str, typer.Option(envvar="T0_DATA_FOLDER", help=HELP_TEXT["data_folder"])
    ] = CONDITIONS_FOLDER,
    main_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["main_only"]),
    ] = DEFAULTS["main_only"],
    embedding_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["embedding_model_name"])
    ] = DEFAULTS["embedding_model_name"],
    chunk_overlap: Annotated[
        int, typer.Option(help=HELP_TEXT["chunk_overlap"])
    ] = DEFAULTS["chunk_overlap"],
    db_choice: Annotated[
        DBChoice, typer.Option(help=HELP_TEXT["db_choice"])
    ] = DEFAULTS["db_choice"],
    persist_directory: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["persist_directory"]),
    ] = DEFAULTS["persist_directory"],
    local_file_store: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["local_file_store"]),
    ] = DEFAULTS["local_file_store"],
    search_type: Annotated[str, typer.Option(help=HELP_TEXT["search_type"])] = DEFAULTS[
        "search_type"
    ],
    k: Annotated[int, typer.Option(help=HELP_TEXT["k"])] = DEFAULTS["k"],
    force_create: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["force_create"]),
    ] = DEFAULTS["force_create"],
    trust_source: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["trust_source"]),
    ] = DEFAULTS["trust_source"],
    llm_provider: Annotated[
        LLMProvider, typer.Option(help=HELP_TEXT["llm_provider"])
    ] = DEFAULTS["llm_provider"],
    llm_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["llm_model_name"])
    ] = DEFAULTS["llm_model_name"],
    prompt_template_path: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["prompt_template_path"]),
    ] = DEFAULTS["prompt_template_path"],
    system_prompt_path: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["system_prompt_path"]),
    ] = DEFAULTS["system_prompt_path"],
    deepseek_r1: Annotated[
        bool,
        typer.Option(
            help="If True, evaluating deepseek-R1 responses which requires parsing the response."
        ),
    ] = False,
    env_file: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["env_file"]),
    ] = DEFAULTS["env_file"],
):
    """
    Evaluate the RAG.
    """
    set_up_logging_config()
    load_env_file(env_file)
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")

    logging.info("Evaluating RAG...")

    from t0_001.rag.evaluate import RetrieverConfig, main

    main(
        input_file=input_file,
        output_file=output_file,
        query_field=query_field,
        target_document_field=target_document_field,
        conditions_folder=conditions_folder,
        generate_only=generate_only,
        main_only=main_only,
        config=RetrieverConfig(
            embedding_model_name=embedding_model_name,
            chunk_overlap=chunk_overlap,
            db_choice=db_choice,
            persist_directory=persist_directory,
            local_file_store=local_file_store,
            search_type=search_type,
            k=k,
            search_kwargs={},
        ),
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
        deepseek_r1=deepseek_r1,
    )


@cli.command()
def generate_synth_queries(
    n_queries: Annotated[int, typer.Option(help="Number of queries to generate.")],
    template_path: Annotated[
        str, typer.Option(help="Path to the template file.")
    ] = "./templates/synthetic_data.txt",
    save_path: Annotated[
        str, typer.Option(help="Path to save the generated queries.")
    ] = "./data/synthetic_queries/",
    conditions_path: Annotated[
        str, typer.Option(help="Path to the NHS conditions folder.")
    ] = CONDITIONS_FOLDER,
    model: Annotated[str, typer.Option(help="Model to use for generation.")] = "gpt-4o",
    overwrite: Annotated[bool, typer.Option(help="Overwrite existing files.")] = False,
    env_file: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["env_file"]),
    ] = DEFAULTS["env_file"],
):
    """
    Generate synthetic queries for the NHS use case and save them to a file.
    """
    set_up_logging_config()
    load_env_file(env_file)
    logging.info("Generating synthetic queries...")

    from t0_001.synth_data_generation.generate_jsonl_snyth_queries import (
        generate_synthetic_queries,
    )

    generate_synthetic_queries(
        n_queries=n_queries,
        template_path=template_path,
        save_path=save_path,
        conditions_path=conditions_path,
        model=model,
        overwrite=overwrite,
    )
    logging.info("Synthetic requests generated.")


@cli.command()
def rag_chat(
    conditions_folder: Annotated[
        str, typer.Option(envvar="T0_DATA_FOLDER", help=HELP_TEXT["data_folder"])
    ] = CONDITIONS_FOLDER,
    main_only: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["main_only"]),
    ] = DEFAULTS["main_only"],
    embedding_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["embedding_model_name"])
    ] = DEFAULTS["embedding_model_name"],
    chunk_overlap: Annotated[
        int, typer.Option(help=HELP_TEXT["chunk_overlap"])
    ] = DEFAULTS["chunk_overlap"],
    db_choice: Annotated[
        DBChoice, typer.Option(help=HELP_TEXT["db_choice"])
    ] = DEFAULTS["db_choice"],
    persist_directory: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["persist_directory"]),
    ] = DEFAULTS["persist_directory"],
    local_file_store: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["local_file_store"]),
    ] = DEFAULTS["local_file_store"],
    search_type: Annotated[str, typer.Option(help=HELP_TEXT["search_type"])] = DEFAULTS[
        "search_type"
    ],
    k: Annotated[int, typer.Option(help=HELP_TEXT["k"])] = DEFAULTS["k"],
    force_create: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["force_create"]),
    ] = DEFAULTS["force_create"],
    trust_source: Annotated[
        bool,
        typer.Option(help=HELP_TEXT["trust_source"]),
    ] = DEFAULTS["trust_source"],
    llm_provider: Annotated[
        LLMProvider, typer.Option(help=HELP_TEXT["llm_provider"])
    ] = DEFAULTS["llm_provider"],
    llm_model_name: Annotated[
        str, typer.Option(help=HELP_TEXT["llm_model_name"])
    ] = DEFAULTS["llm_model_name"],
    prompt_template_path: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["prompt_template_path"]),
    ] = DEFAULTS["prompt_template_path"],
    system_prompt_path: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["system_prompt_path"]),
    ] = DEFAULTS["system_prompt_path"],
    env_file: Annotated[
        str | None,
        typer.Option(help=HELP_TEXT["env_file"]),
    ] = DEFAULTS["env_file"],
):
    """
    Interact with the RAG model in a command line interface.
    """
    set_up_logging_config()
    load_env_file(env_file)
    logging.info("Starting RAG chat interaction...")

    from t0_001.query_vector_store.build_retriever import RetrieverConfig
    from t0_001.rag.chat_interact import run_chat_interact

    run_chat_interact(
        conditions_folder=conditions_folder,
        main_only=main_only,
        config=RetrieverConfig(
            embedding_model_name=embedding_model_name,
            chunk_overlap=chunk_overlap,
            db_choice=db_choice,
            persist_directory=persist_directory,
            local_file_store=local_file_store,
            search_type=search_type,
            k=k,
            search_kwargs={},
        ),
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
    )
