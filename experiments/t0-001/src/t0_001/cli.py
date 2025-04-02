import logging
from typing import Annotated

import requests
import typer
from t0_001.query_vector_store.endpoint import main as query_vector_store_main
from t0_001.synth_data_generation.generate_jsonl_snyth_requests import generate_synthetic_requests

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def set_up_logging_config(level: int = 20) -> None:
    logging.basicConfig(
        datefmt=r"%Y-%m-%d %H:%M:%S",
        format="%(asctime)s [%(levelname)8s] %(message)s",
        level=level,
    )


@cli.command()
def serve_vector_store(
    data_folder: Annotated[
        str, typer.Option(help="Path to the data folder.")
    ] = "nhs-use-case/conditions",
    main_only: Annotated[
        bool,
        typer.Option(
            help="If True, only the main element of the HTML file is extracted."
        ),
    ] = True,
    embedding_model_name: Annotated[
        str, typer.Option(help="Name of the embedding model.")
    ] = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: Annotated[
        int, typer.Option(help="Chunk overlap for the text splitter.")
    ] = 50,
    host: Annotated[str, typer.Option(help="Host to listen on.")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="Port to listen on.")] = 8000,
):
    """
    Run the query vector store server.
    """
    set_up_logging_config()
    logging.info("Starting query vector store server...")
    query_vector_store_main(
        conditions_folder=data_folder,
        main_only=main_only,
        embedding_model_name=embedding_model_name,
        chunk_overlap=chunk_overlap,
        host=host,
        port=port,
    )


@cli.command()
def query_vector_store(
    query: Annotated[str, typer.Argument(help="The query to search for.")],
    host: Annotated[str, typer.Option(help="Host to listen on.")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="Port to listen on.")] = 8000,
):
    """
    Query the vector store.
    """
    set_up_logging_config()
    logging.info("Querying vector store...")
    logging.info(f"Query: {query}")
    req = requests.get(f"http://{host}:{port}/query", params={"query": query})
    if req.status_code != 200:
        logging.error(f"Error querying vector store: {req.text}")
        return
    logging.info(f"Response: {req.json()}")


@cli.command()
def generate_synth_requests(
    n_requests: Annotated[int, typer.Option(help="Number of requests to generate.")],
    template_path: Annotated[
        str, typer.Option(help="Path to the template file.")
    ] = "./templates/synthetic_data.txt",
    save_path: Annotated[
        str, typer.Option(help="Path to save the generated requests.")
    ] = "./data/synthetic_requests/",
    conditions_path: Annotated[
        str, typer.Option(help="Path to the NHS conditions folder.")
    ] = "./nhs-use-case/conditions/",
    model: Annotated[str, typer.Option(help="Model to use for generation.")] = "gpt-4o",
):
    """
    Generate synthetic requests for the NHS use case and save them to a file.
    """
    set_up_logging_config()
    logging.info("Generating synthetic requests...")

    if model=="gpt-4o":
        logging.info("Using GPT-4o model via Azure OpenAI.")
    else:
        logging.info("Using Ollama model.")

    generate_synthetic_requests(
        n_requests=n_requests,
        template_path=template_path,
        save_path=save_path,
        conditions_path=conditions_path,
        model=model,
    )
    logging.info("Synthetic requests generated.")
