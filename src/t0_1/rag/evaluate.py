import asyncio
import json
import logging
import uuid
from pathlib import Path

from langchain_core.tools import tool
from tqdm.asyncio import tqdm_asyncio

from t0_1.rag.build_rag import (
    DEFAULT_RETRIEVER_CONFIG,
    RAG,
    RetrieverConfig,
    build_rag,
)
from t0_1.utils import read_jsonl, timestamp_file_name

FILE_WRITE_LOCK = asyncio.Lock()


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


def parse_s1(string: str) -> tuple[str]:
    """
    Responses from s1 should be in the format:
    <|im_start|>answer(condition, severity).
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
    string_after_answer = string.split("<|im_start|>answer")[-1]

    # extract the condition and severity level using regex
    match = re.search(r"\(([^)]*), ([^)]+)\)", string_after_answer)
    if match:
        condition = match.group(1).strip().strip('"')
        severity_level = match.group(2).strip().strip('"')
        return condition, severity_level
    else:
        return "", ""


async def process_query(
    item: dict,
    query_field: str,
    target_document_field: str,
    rag: RAG,
    conversational: bool,
    generate_only: bool,
    deepseek_r1: bool,
    s1: bool,
    output_file: str,
):
    query = item[query_field]
    target_document = item[target_document_field]

    try:
        # obtain the top k documents from the vector store
        thread_id = str(uuid.uuid4()) if conversational else "-"
        if conversational:
            # just clear ahead of querying just in case
            rag.clear_history(thread_id=thread_id)

        response = await rag._aquery(
            question=query,
            demographics=str(item["general_demographics"]),
            thread_id=thread_id,
        )

        if conversational:
            logging.info(f"Used thread_id {thread_id} for query {query}")

            # delete the thread_id after the query
            rag.clear_history(thread_id=thread_id)

            logging.info(f"Deleted thread_id {thread_id} after query")

        if not generate_only:
            if deepseek_r1:
                logging.info("Using deepseek-r1 parser for evaluation.")
                # extract condition and severity level from the response
                parsed_condition, parsed_severity_level = parse_deepseek_r1(
                    response["messages"][-1].content
                )
                prediction_condition = remove_dash_and_spaces(parsed_condition)
                target_condition = remove_dash_and_spaces(target_document)
                conditions_match = prediction_condition == target_condition
                severity_match = (
                    parsed_severity_level.lower() == item["severity_level"].lower()
                )
            elif s1:
                logging.info("Using s1 parser for evaluation.")
                # extract condition and severity level from the response
                parsed_condition, parsed_severity_level = parse_s1(
                    response["messages"][-1].content
                )
                prediction_condition = remove_dash_and_spaces(parsed_condition)
                target_condition = remove_dash_and_spaces(target_document)
                conditions_match = prediction_condition == target_condition
                severity_match = (
                    parsed_severity_level.lower() == item["severity_level"].lower()
                )
            else:
                logging.info("Using tool calls for evaluation.")
                if (
                    response["messages"][-1].additional_kwargs.get("tool_calls")
                    is not None
                    and len(response["messages"][-1].additional_kwargs["tool_calls"])
                    == 1
                ):
                    arguments = json.loads(
                        response["messages"][-1].additional_kwargs["tool_calls"][0][
                            "function"
                        ]["arguments"]
                    )

                    if arguments.get("condition") is not None:
                        parsed_condition = arguments["condition"]
                        prediction_condition = remove_dash_and_spaces(
                            arguments["condition"]
                        )
                        target_condition = remove_dash_and_spaces(target_document)
                        conditions_match = prediction_condition == target_condition
                    else:
                        parsed_condition = ""
                        conditions_match = False

                    if arguments.get("severity_level") is not None:
                        parsed_severity_level = arguments["severity_level"]
                        severity_match = (
                            arguments["severity_level"].lower()
                            == item["severity_level"].lower()
                        )
                    else:
                        parsed_severity_level = ""
                        severity_match = False
                else:
                    conditions_match = False
                    severity_match = False
                    parsed_condition = ""
                    parsed_severity_level = ""

        # create dictionary to store the results
        retrieved_docs_scores = [
            float(doc.metadata["sub_docs"][0].metadata["score"])
            for doc in response["context"][-1]
        ]
        reranked_docs_scores = [
            float(doc.metadata["sub_docs"][0].metadata["score"])
            for doc in response.get("reranked_context", [[]])[-1]
        ]
        res = item | {
            "query_field": query_field,
            "target_document_field": target_document_field,
            "retrieved_documents_sources": [
                doc.metadata["source"] for doc in response["context"][-1]
            ],
            "retrieved_documents_scores": retrieved_docs_scores,
            "retrieved_documents_scores_sorted": (
                retrieved_docs_scores == sorted(retrieved_docs_scores)
            ),
            "reranked_documents_sources": [
                doc.metadata["source"]
                for doc in response.get("reranked_context", [[]])[-1]
            ],
            "reranked_documents_scores": reranked_docs_scores,
            "reranked_documents_scores_sorted": (
                reranked_docs_scores == sorted(reranked_docs_scores)
                if reranked_docs_scores
                else None
            ),
            "reranker_response": response.get("reranker_response", [[]])[-1],
            "reranker_response_processed": response.get(
                "reranker_response_processed", [[]]
            )[-1],
            "reranker_success": response.get("reranker_success", [[]])[-1],
            "system_prompt": response["system_messages"][0].content,
            "rag_message": (
                response["rag_input_messages"][0].content
                if conversational
                else response["messages"][0].content
            ),
            "rag_answer": response["messages"][-1].content,
            "rag_tool_calls": response["messages"][-1].additional_kwargs.get(
                "tool_calls"
            ),
        }
    except (Exception, BaseException) as err:
        error_as_str = f"{type(err).__name__} - {err}"
        logging.error(f"Error querying RAG: {error_as_str}")

        retrieved_docs = await rag.retriever.ainvoke(input=query)

        # create dictionary to store the results
        retrieved_docs_scores = [
            float(doc.metadata["sub_docs"][0].metadata["score"])
            for doc in retrieved_docs
        ]
        res = item | {
            "query_field": query_field,
            "target_document_field": target_document_field,
            "retrieved_documents_sources": [
                doc.metadata["source"] for doc in retrieved_docs
            ],
            "retrieved_documents_scores": retrieved_docs_scores,
            "retrieved_documents_scores_sorted": (
                retrieved_docs_scores == sorted(retrieved_docs_scores)
            ),
            "reranked_documents_sources": [],
            "reranked_documents_scores": [],
            "reranked_documents_scores_sorted": None,
            "reranker_response": None,
            "reranker_response_processed": None,
            "reranker_success": None,
            "error": error_as_str,
        }

        conditions_match = False
        severity_match = False
        parsed_condition = ""
        parsed_severity_level = ""

    if not generate_only:
        res["conditions_match"] = conditions_match
        res["severity_match"] = severity_match

        # check for match between the source of the retrieved documents and the target document source
        res["retriever_match"] = target_document in set(
            res["retrieved_documents_sources"]
        )
        res["reranked_retriever_match"] = target_document in set(
            res["reranked_documents_sources"]
        )

        res["parsed_condition"] = parsed_condition
        res["parsed_severity_level"] = parsed_severity_level

        if parsed_condition == "inconclusive":
            # if model said inconclusive, then it is correct if the target document
            # is not in the retrieved documents
            if res["reranked_documents_sources"]:
                # we used reranking so need to check the reranked documents
                res["conditions_match"] = not res[
                    "reranked_retriever_match"
                ]  # i.e. False if res["reranked_retreiver_match"] else True
            else:
                res["conditions_match"] = not res["retriever_match"]

    # write the results to the output file
    async with FILE_WRITE_LOCK:
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
    conversational: bool,
    generate_only: bool = False,
    deepseek_r1: bool = False,
    s1: bool = False,
    max_queries_per_minute: int = 60,
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
    conversational : bool
        Whether the RAG model is in conversational mode. If True, we use a unique ID for each
        query and we delete that thread after the query. If False, we just use the same ID
        as chat history is not used in that pipeline.
    generate_only : bool, optional
        If True, only generate the RAG responses without evaluating the queries.
        By default False.
    deepseek_r1 : bool, optional
        If True, evaluating deepseek-R1 responses which requires parsing the response.
        By default False.
    s1 : bool, optional
        If True, evaluating s1-style responses which requires parsing the response.
        By default False.
    max_queries_per_minute : int, optional
        The number of queries to process per minute. By default 60.

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

    request_interval = 60 / max_queries_per_minute
    logging.info(f"Request interval: {request_interval} seconds")

    tasks = []

    from tqdm import tqdm

    for item in tqdm(
        data,
        desc=f"Sending {len(data)} queries with request interval {request_interval} seconds",
        unit="query",
    ):
        # wait interval between requests
        await asyncio.sleep(request_interval)

        task = asyncio.create_task(
            process_query(
                item=item,
                query_field=query_field,
                target_document_field=target_document_field,
                rag=rag,
                conversational=conversational,
                generate_only=generate_only,
                deepseek_r1=deepseek_r1,
                s1=s1,
                output_file=output_file,
            )
        )
        tasks.append(task)

    results = await tqdm_asyncio.gather(
        *tasks, desc="Waiting for responses...", unit="query"
    )
    logging.info("All tasks completed.")

    if not generate_only:
        # calculate sums
        retriever_match_sum = sum([res["retriever_match"] for res in results])
        reranked_retriever_match_sum = sum(
            [res["reranked_retriever_match"] for res in results]
        )
        conditions_sum = sum([res["conditions_match"] for res in results])
        severity_sum = sum([res["severity_match"] for res in results])

        logging.info(
            f"Proportion of retriever matches: {retriever_match_sum}/{len(data)} = {retriever_match_sum / len(data):.2%}"
        )
        logging.info(
            f"Proportion of reranked retriever matches: {reranked_retriever_match_sum}/{len(data)} = {reranked_retriever_match_sum / len(data):.2%}"
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
    extra_body: dict | str | None = None,
    conversational: bool = False,
    conversational_agent_llm_provider: str | None = None,
    conversational_agent_llm_model_name: str | None = None,
    conversational_agent_extra_body: dict | str | None = None,
    prompt_template_path: str | None = None,
    system_prompt_path: str | None = None,
    deepseek_r1: bool = False,
    budget_forcing: bool = False,
    budget_forcing_kwargs: dict | str | None = None,
    budget_forcing_tokenizer: str | None = None,
    rerank: bool = False,
    rerank_prompt_template_path: str | Path | None = None,
    rerank_llm_provider: str | None = None,
    rerank_llm_model_name: str | None = None,
    rerank_extra_body: dict | str | None = None,
    rerank_k: int = 5,
    seed: int | None = None,
    max_queries_per_minute: int = 60,
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
        tools=(
            [submit_condition_recommendation]
            if not (deepseek_r1 or budget_forcing)
            else None
        ),
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

    asyncio.run(
        evaluate_rag(
            input_file=input_file,
            output_file=output_file,
            query_field=query_field,
            target_document_field=target_document_field,
            rag=rag,
            conversational=conversational,
            generate_only=generate_only,
            deepseek_r1=deepseek_r1,
            s1=budget_forcing,
            max_queries_per_minute=max_queries_per_minute,
        )
    )
