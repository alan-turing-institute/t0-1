import json
import logging
from pathlib import Path

from langchain_core.tools import tool
from t0_001.rag.build_rag import (
    DEFAULT_RETRIEVER_CONFIG,
    RAG,
    RetrieverConfig,
    build_rag,
)
from t0_001.utils import read_jsonl, timestamp_file_name
from tqdm import tqdm


@tool
def submit_condition_recommendation(
    condition: str,
    severity_level: str,
) -> str:
    """
    Submit a condition recommendation and severity level.

    Parameters
    ----------
    condition : str
        Name of the condition or procedure. This must be one of the sources
        provided or "inconclusive" if the model is not confident.
    severity_level : str
        Severity level of the condition. This must be one of
        ["Not urgent", "Medium", "Medium urgent", "Urgent"].
    """
    return f"Condition: {condition}, Severity Level: {severity_level}"


def remove_dash_and_spaces(string: str) -> str:
    return "".join([c for c in string if c.isalnum()]).lower()


def evaluate_rag(
    input_file: str | Path,
    output_file: str | Path,
    query_field: str,
    target_document_field: str,
    rag: RAG,
    generate_only: bool = False,
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
    rag : RAG
        The RAG model to use for querying.
    generate_only : bool, optional
        If True, only generate the RAG responses without evaluating the queries,
        by default False.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the query, retrieved documents, and the RAG responses
    """
    if not str(output_file).endswith(".jsonl"):
        raise ValueError(f"File {output_file} is not a JSONL file.")

    data = read_jsonl(input_file)
    retriever_match_sum = 0
    conditions_sum = 0
    severity_sum = 0
    results = []
    output_file = timestamp_file_name(output_file)

    logging.info(f"Writing results to {output_file}...")
    logging.info(f"Query field: {query_field}")
    logging.info(f"Target document field: {target_document_field}")

    for item in tqdm(data, desc="Evaluating Queries"):
        query = item[query_field]
        target_document = item[target_document_field]

        # obtain the top k documents from the vector store
        response = rag._query(
            question=query, demographics=str(item["general_demographics"])
        )

        if not generate_only:
            if (
                response["answer"].additional_kwargs.get("tool_calls") is not None
                and len(response["answer"].additional_kwargs["tool_calls"]) == 1
            ):
                arguments = json.loads(
                    response["answer"].additional_kwargs["tool_calls"][0]["function"][
                        "arguments"
                    ]
                )

                if arguments.get("condition") is not None:
                    prediction_condition = remove_dash_and_spaces(
                        arguments["condition"]
                    )
                    target_condition = remove_dash_and_spaces(target_document)
                    conditions_match = prediction_condition == target_condition
                    if conditions_match:
                        conditions_sum += 1
                else:
                    conditions_match = False

                if arguments.get("severity_level") is not None:
                    severity_match = (
                        arguments["severity_level"].lower()
                        == item["severity_level"].lower()
                    )
                    if severity_match:
                        severity_sum += 1
                else:
                    severity_match = False
            else:
                conditions_match = False
                severity_match = False

        # create dictionary to store the results
        res = item | {
            "query_field": query_field,
            "target_document_field": target_document_field,
            "retrieved_documents": [doc.page_content for doc in response["context"]],
            "retrieved_documents_scores": [
                float(doc.metadata["sub_docs"][-1].metadata["score"])
                for doc in response["context"]
            ],
            "retrieved_documents_sources": [
                doc.metadata["source"] for doc in response["context"]
            ],
            "rag_message": [
                message.content for message in response["messages"].messages
            ],
            "rag_answer": response["answer"].content,
            "rag_tool_calls": response["answer"].additional_kwargs.get("tool_calls"),
        }

        if not generate_only:
            res["conditions_match"] = conditions_match
            res["severity_match"] = severity_match

            # check for match between the source of the retrieved documents and the target document source
            res["retriever_match"] = target_document in set(
                res["retrieved_documents_sources"]
            )
            retriever_match_sum += res["retriever_match"]

        # write the results to the output file
        with open(output_file, "a") as f:
            json.dump(res, f)
            f.write("\n")

        # append the result to the results list
        results.append(res)

    if not generate_only:
        logging.info(
            f"Proportion of retriever matches: {retriever_match_sum}/{len(data)} = {retriever_match_sum / len(data):.2%}"
        )
        logging.info(
            f"Proportion of condition matches: {conditions_sum}/{len(data)} = {conditions_sum / len(data):.2%}"
        )
        logging.info(
            f"Proportion of severity matches: {severity_sum}/{len(data)} = {severity_sum / len(data):.2%}"
        )

    return results


def main(
    input_file: str | Path,
    output_file: str | Path,
    query_field: str,
    target_document_field: str,
    conditions_folder: str,
    generate_only: bool = False,
    main_only: bool = True,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
):
    rag = build_rag(
        conditions_folder=conditions_folder,
        main_only=main_only,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        tools=[submit_condition_recommendation],
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
    )

    evaluate_rag(
        input_file=input_file,
        output_file=output_file,
        query_field=query_field,
        target_document_field=target_document_field,
        rag=rag,
        generate_only=generate_only,
    )
