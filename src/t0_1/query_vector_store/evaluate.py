import json
import logging
from pathlib import Path

from langchain_core.vectorstores import VectorStore
from tqdm import tqdm

from t0_1.query_vector_store.build_index import (
    DEFAULT_VECTOR_STORE_CONFIG,
    VectorStoreConfig,
    get_vector_store,
)
from t0_1.utils import read_jsonl, timestamp_file_name


def evaluate_query_store(
    input_file: str | Path,
    output_file: str | Path,
    query_field: str,
    target_document_field: str,
    vector_store: VectorStore,
    k: int = 4,
) -> list[dict]:
    """
    Evaluate the query store by comparing the query results with the target documents.

    Parameters
    ----------
    input_file : str | Path
        The path to the JSONL file containing the queries and target documents.
    output_file : str | Path
        The path to the JSONL file where the results will be saved.
    query_field : str
        The field name in the JSONL file that contains the query.
    target_document_field : str
        The field name in the JSONL file that contains the target document.
    vector_store : VectorStore
        The vector store to use for querying.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the query, retrieved documents, and whether they match.
    """
    if not str(output_file).endswith(".jsonl"):
        raise ValueError(f"File {output_file} is not a JSONL file.")

    data = read_jsonl(input_file)
    results = []
    sum = 0
    output_file = timestamp_file_name(output_file)

    logging.info(f"Writing results to {output_file}...")
    logging.info(f"Query field: {query_field}")
    logging.info(f"Target document field: {target_document_field}")

    for item in tqdm(data, desc="Evaluating Queries"):
        query = item[query_field]
        target_document = item[target_document_field]

        # obtain the top k documents from the vector store
        retrieved_docs = vector_store.similarity_search_with_score(query=query, k=k)

        # create dictionary to store the results
        res = item | {
            "query_field": query_field,
            "target_document_field": target_document_field,
            "k": k,
            "retrieved_documents": [doc.page_content for doc, _ in retrieved_docs],
            "retrieved_documents_scores": [float(score) for _, score in retrieved_docs],
            "retrieved_documents_sources": [
                doc.metadata["source"] for doc, _ in retrieved_docs
            ],
        }

        # check for match between the source of the retrieved documents and the target document source
        res["match"] = target_document in res["retrieved_documents_sources"]
        sum += res["match"]

        # write the results to the output file
        with open(output_file, "a") as f:
            json.dump(res, f)
            f.write("\n")

        # append the result to the results list
        results.append(res)

    logging.info(f"Proportion of matches: {sum}/{len(data)} = {sum / len(data):.2%}")

    return results


def main(
    input_file: str | Path,
    output_file: str | Path,
    query_field: str,
    target_document_field: str,
    conditions_file: str,
    config: VectorStoreConfig = DEFAULT_VECTOR_STORE_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    k: int = 4,
):
    vector_store = get_vector_store(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
    )

    evaluate_query_store(
        input_file=input_file,
        output_file=output_file,
        query_field=query_field,
        target_document_field=target_document_field,
        vector_store=vector_store,
        k=k,
    )
