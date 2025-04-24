import asyncio
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
from tqdm.asyncio import tqdm_asyncio


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


def parse_deepseek_r1(string: str) -> tuple[str]:
    """
    Responses from deepseek-R1 should be in the format:
    <think>some reasoning</think>(condition, severity).
    The function extracts the condition and severity level from the string.
    The condition and severity level are separated by a comma.

    Parameters
    ----------
    string : str
        The string to parse.

    Returns
    -------
    tuple[str]
        A tuple containing the condition and severity level.
    """
    import re

    # split the string into two parts: before and after the reasoning
    string_after_think_end = string.split("</think>")[-1]

    # extract the condition and severity level using regex
    match = re.search(r"\(([^,]+), ([^)]+)\)", string_after_think_end)
    if match:
        condition = match.group(1).strip()
        severity_level = match.group(2).strip()
        return condition, severity_level
    else:
        logging.warning(
            f"Could not extract condition and severity level from string: {string}"
        )
        return "", ""


async def process_query(
    item: dict,
    query_field: str,
    target_document_field: str,
    rag: RAG,
    generate_only: bool,
    deepseek_r1: bool,
    output_file: str,
):
    query = item[query_field]
    target_document = item[target_document_field]

    try:
        # obtain the top k documents from the vector store
        response = await rag._query(
            question=query, demographics=str(item["general_demographics"])
        )

        if not generate_only:
            if deepseek_r1:
                # extract condition and severity level from the response
                parsed_condition, parsed_severity_level = parse_deepseek_r1(
                    response["answer"].content
                )
                prediction_condition = remove_dash_and_spaces(parsed_condition)
                target_condition = remove_dash_and_spaces(target_document)
                conditions_match = prediction_condition == target_condition
                severity_match = (
                    parsed_severity_level.lower() == item["severity_level"].lower()
                )

            else:
                if (
                    response["answer"].additional_kwargs.get("tool_calls") is not None
                    and len(response["answer"].additional_kwargs["tool_calls"]) == 1
                ):
                    arguments = json.loads(
                        response["answer"].additional_kwargs["tool_calls"][0][
                            "function"
                        ]["arguments"]
                    )

                    if arguments.get("condition") is not None:
                        prediction_condition = remove_dash_and_spaces(
                            arguments["condition"]
                        )
                        target_condition = remove_dash_and_spaces(target_document)
                        conditions_match = prediction_condition == target_condition
                    else:
                        conditions_match = False

                    if arguments.get("severity_level") is not None:
                        severity_match = (
                            arguments["severity_level"].lower()
                            == item["severity_level"].lower()
                        )
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
                float(
                    doc.metadata["sub_docs"][-1].metadata["score"]
                    if "sub_docs" in doc.metadata
                    else 0
                )
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
    except Exception as e:
        logging.error(f"Error querying RAG: {e}")

        retrieved_docs = await rag.retriever.ainvoke(input=query)

        # create dictionary to store the results
        res = item | {
            "query_field": query_field,
            "target_document_field": target_document_field,
            "retrieved_documents": [doc.page_content for doc in retrieved_docs],
            "retrieved_documents_scores": [
                float(doc.metadata["sub_docs"][0].metadata["score"])
                for doc in retrieved_docs
            ],
            "retrieved_documents_sources": [
                doc.metadata["source"] for doc in retrieved_docs
            ],
            "error": str(e),
        }

        conditions_match = False
        severity_match = False

    if not generate_only:
        res["conditions_match"] = conditions_match
        res["severity_match"] = severity_match

        # check for match between the source of the retrieved documents and the target document source
        res["retriever_match"] = target_document in set(
            res["retrieved_documents_sources"]
        )

        if deepseek_r1:
            res["parsed_conditions"] = parsed_condition
            res["parsed_severity_level"] = parsed_severity_level

    # write the results to the output file
    with open(output_file, "a") as f:
        json.dump(res, f)
        f.write("\n")

    # return the results
    return res


async def evaluate_rag(
    input_file: str | Path,
    output_file: str | Path,
    query_field: str,
    target_document_field: str,
    rag: RAG,
    generate_only: bool = False,
    deepseek_r1: bool = False,
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
        If True, only generate the RAG responses without evaluating the queries.
        By default False.
    deepseek_r1 : bool, optional
        If True, evaluating deepseek-R1 responses which requires parsing the response.
        By default False.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the query, retrieved documents, and the RAG responses
    """
    if not str(output_file).endswith(".jsonl"):
        raise ValueError(f"File {output_file} is not a JSONL file.")

    data = read_jsonl(input_file)
    output_file = timestamp_file_name(output_file)

    logging.info(f"Writing results to {output_file}...")
    logging.info(f"Query field: {query_field}")
    logging.info(f"Target document field: {target_document_field}")

    tasks = [
        asyncio.create_task(
            process_query(
                item,
                query_field,
                target_document_field,
                rag,
                generate_only,
                deepseek_r1,
                output_file,
            )
        )
        for item in data
    ]
    results = await tqdm_asyncio.gather(*tasks)
    logging.info("All tasks completed.")

    if not generate_only:
        # calculate sums
        retriever_match_sum = sum([res["retriever_match"] for res in results])
        conditions_sum = sum([res["conditions_match"] for res in results])
        severity_sum = sum([res["severity_match"] for res in results])

        logging.info(
            f"Proportion of retriever matches: {retriever_match_sum}/{len(data)} = {retriever_match_sum / len(data):.2%}"
        )
        logging.info(
            f"Proportion of condition matches: {conditions_sum}/{len(data)} = {conditions_sum / len(data):.2%}"
        )
        logging.info(
            f"Proportion of severity matches: {severity_sum}/{len(data)} = {severity_sum / len(data):.2%}"
        )


def main(
    input_file: str | Path,
    output_file: str | Path,
    query_field: str,
    target_document_field: str,
    conditions_file: str,
    generate_only: bool = False,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
    deepseek_r1: bool = False,
    extra_body: dict | str | None = None,
):
    rag = build_rag(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        tools=[submit_condition_recommendation] if not deepseek_r1 else [],
        prompt_template_path=prompt_template_path,
        system_prompt_path=system_prompt_path,
        extra_body=extra_body,
    )

    asyncio.run(
        evaluate_rag(
            input_file=input_file,
            output_file=output_file,
            query_field=query_field,
            target_document_field=target_document_field,
            rag=rag,
            generate_only=generate_only,
            deepseek_r1=deepseek_r1,
        )
    )
