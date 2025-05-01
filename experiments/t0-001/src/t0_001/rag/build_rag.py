import logging
from pathlib import Path

from langchain import hub
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.messages.ai import AIMessage
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from t0_001.query_vector_store.build_retriever import (
    DEFAULT_RETRIEVER_CONFIG,
    RetrieverConfig,
    get_parent_doc_retriever,
)
from t0_001.query_vector_store.custom_parent_document_retriever import (
    CustomParentDocumentRetriever,
)
from t0_001.rag.utils import NHS_RETRIEVER_TOOL_PROMPT, create_retreiver_tool
from t0_001.utils import process_arg_to_dict
from typing_extensions import TypedDict


class State(TypedDict):
    """
    State is a TypedDict that represents the state of a RAG query.
    It contains the question, context, reranked context (if applicable), demographics, messages, and answer.
    """

    question: str
    context: list[Document]
    reranked_context: list[Document] | None
    reranker_response: str | None
    reranker_response_processed: list[str] | None
    reranker_success: bool | None
    demographics: str | None
    messages: list[str]
    answer: str


class CustomMessagesState(MessagesState):
    """
    Messages state for the RAG class.
    """

    system_messages: list[str | None]
    retriever_queries: list[str]
    context: list[list[Document]]
    reranked_context: list[list[Document] | None]
    reranker_response: list[str | None]
    reranker_response_processed: list[list[str] | None]
    reranker_success: list[bool | None]
    demographics: str | None


class RAG:
    def __init__(
        self,
        retriever: CustomParentDocumentRetriever,
        prompt: PromptTemplate,
        llm: LLM,
        conversational: bool = False,
        conversational_agent_llm: LLM | None = None,
        tools: list | None = None,
        tools_kwargs: dict = {},
        budget_forcing: bool = False,
        budget_forcing_kwargs: dict | str | None = None,
        budget_forcing_tokenizer: str | None = None,
        rerank: bool = False,
        rerank_prompt: str | Path | None = None,
        rerank_llm: LLM | None = None,
        rerank_k: int = 5,
    ):
        """
        Initialise the RAG class with the vector store, prompt, and LLM.
        The vector store is used to retrieve documents, the prompt is used to
        format the input for the LLM, and the LLM is used to generate the answer.
        Upon initialisation, the class builds a Langchain compiled state graph
        with the retrieve and generate functions as nodes.

        Parameters
        ----------
        vector_store : VectorStore
            Vector store to use for retrieval.
        prompt : PromptTemplate
            Prompt template to use for the LLM.
        llm : LLM
            LLM to use for generation.
        conversational : bool, optional
            Whether to use conversational mode. By default False.
            This uses a different state graph with a tool node for
            retrieval to allow for the LLM to call the retriever as a tool
            and use the conversational memory to rewrite the query
            to the retriever.
        conversational_agent_llm : LLM | None, optional
            LLM to use for the conversational retriever agent.
            This essentially is the LLM that decides whether or not to
            query the retriever or respond directly to the user.
            By default None. If None, the LLM used for the RAG is used.
        tools : list | None, optional
            List of tools to bind to the LLM. By default None.
        tools_kwargs : dict, optional
            Keyword arguments to pass to the tools. By default {}.
        budget_forcing : bool, optional
            Whether to use budget forcing. By default False.
        budget_forcing_kwargs : dict | str | None, optional
            Keyword arguments to pass to the budget forcing. By default None.
        budget_forcing_tokenizer : str | None, optional
            Tokenizer to use for the LLM if using budget forcing. By default None.
            If None, will use the LLM model name.
        rerank : bool, optional
            Whether to use reranking. By default False.
        rerank_prompt : str | Path | None, optional
            Prompt template to use for reranking. By default None.
        rerank_llm : LLM | None, optional
            LLM to use for reranking. By default None.
        rerank_k : int, optional
            Number of documents to rerank and filter to. By default 5.
        """
        self.retriever: CustomParentDocumentRetriever = retriever
        self.prompt: PromptTemplate = prompt
        self.llm: LLM = llm
        self.conversational: bool = conversational
        self.conversational_agent_llm: LLM | None = conversational_agent_llm
        self.tools: list | None = tools
        if tools is not None:
            self.llm = self.llm.bind_tools(tools, **tools_kwargs)
        self.budget_forcing: bool = budget_forcing
        self.budget_forcing_kwargs: dict = budget_forcing_kwargs
        self.budget_forcing_tokenizer: str | None = budget_forcing_tokenizer
        self.rerank: bool = rerank
        self.rerank_prompt: PromptTemplate | None = rerank_prompt
        self.rerank_llm: LLM | None = rerank_llm
        self.rerank_k: int = rerank_k
        self.memory: MemorySaver = MemorySaver()
        if self.conversational:
            self.graph: CompiledStateGraph = self.build_conversation_graph()
        else:
            self.graph: CompiledStateGraph = self.build_graph()

    async def aretrieve(self, state: State) -> dict[str, list[Document]]:
        """
        Retrieve documents from the vector store based on the question in the state.

        Parameters
        ----------
        state : State
            The state of the RAG query, containing the question.

        Returns
        -------
        dict[str, list[Document]]
            A dictionary containing the retrieved documents.
        """
        logging.info(f"Retrieving documents for question: {state['question']}")
        retrieved_docs: list[Document] = await self.retriever.ainvoke(
            input=state["question"]
        )

        return {"context": retrieved_docs}

    def retrieve(self, state: State) -> dict[str, list[Document]]:
        """
        Retrieve documents from the vector store based on the question in the state.

        Parameters
        ----------
        state : State
            The state of the RAG query, containing the question.

        Returns
        -------
        dict[str, list[Document]]
            A dictionary containing the retrieved documents.
        """
        logging.info(f"Retrieving documents for question: {state['question']}")
        retrieved_docs: list[Document] = self.retriever.invoke(input=state["question"])

        return {"context": retrieved_docs}

    def retrieve_as_tool(
        self,
        query: str,
    ) -> tuple[str, dict[str, str | list[Document]]]:
        """
        Retrieve documents from the vector store based on the query.

        Parameters
        ----------
        query : str
            The query to retrieve documents for.

        Returns
        ------
        dict[str, str | list[Document]]
            A dictionary containing the query and the retrieved documents.
        """
        logging.info(f"Retrieving documents for query: {query}")
        retrieved_docs: list[Document] = self.retriever.invoke(input=query)
        serialised = "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )

        return serialised, {"query": query, "context": retrieved_docs}

    def rerank_documents(
        self,
        state: State,
    ) -> dict[str, list[Document]]:
        # rerank the documents using an LLM to select the top rerank_k documents
        logging.info(f"Reranking documents to {self.rerank_k} documents...")

        if self.conversational:
            context = state["context"][-1]
        else:
            context = state["context"]

        # obtain the sources and the context from the retrieved documents
        sources = [doc.metadata["source"] for doc in context]
        source_scores = [
            round(float(doc.metadata["sub_docs"][0].metadata["score"]), 3)
            for doc in context
        ]

        if len(sources) <= self.rerank_k:
            logging.info(
                f"No need to rerank, retrieval already has less than {self.rerank_k} documents"
            )

            # no need to rerank if we have less than k documents
            if self.conversational:
                return {
                    "reranked_context": state.get("reranked_context", []) + [context],
                    "reranker_response": state.get("reranker_response", []) + [None],
                    "reranker_response_processed": state.get(
                        "reranker_response_processed", []
                    )
                    + [None],
                    "reranker_success": state.get("reranker_success", []) + [None],
                }
            else:
                return {
                    "reranked_context": context,
                    "reranker_response": None,
                    "reranker_response_processed": None,
                    "reranker_success": None,
                }

        messages = self.rerank_prompt.invoke(
            {
                "symptoms_description": (
                    state["messages"] if self.conversational else state["question"]
                ),
                "document_titles": zip(sources, source_scores),
                "document_text": context,
                "k": self.rerank_k,
            },
        )

        reranker_response = self.rerank_llm.invoke(messages)

        reranked_docs_titles = [
            title.strip()
            .lower()
            .replace(" ", "-")
            .replace("'", "")
            .replace('"', "")
            .replace("(", "")
            .replace(")", "")
            for title in reranker_response.content.split(",")
        ]
        reranked_docs = [
            doc for doc in context if doc.metadata["source"] in reranked_docs_titles
        ]

        if len(reranked_docs) == self.rerank_k:
            # reranker able to select rerank_k number of documents
            logging.info("Reranker successfully selected the top k documents")
            reranker_success = True
        else:
            # fall back to the top rerank_k retrieved documents
            logging.info(
                "Reranker failed to select the top k documents - falling back to the top retrieved documents"
            )
            reranker_success = False
            reranked_docs = context[: self.rerank_k]

        if self.conversational:
            return {
                "reranked_context": state.get("reranked_context", []) + [reranked_docs],
                "reranker_response": state.get("reranker_response", [])
                + [reranker_response.content],
                "reranker_response_processed": state.get(
                    "reranker_response_processed", []
                )
                + [reranked_docs_titles],
                "reranker_success": state.get("reranker_success", [])
                + [reranker_success],
            }
        else:
            return {
                "reranked_context": reranked_docs,
                "reranker_response": reranker_response.content,
                "reranker_response_processed": reranked_docs_titles,
                "reranker_success": reranker_success,
            }

    def set_up_tokenizer(self):
        from transformers import AutoTokenizer

        if self.budget_forcing_tokenizer is not None:
            tokenizer = AutoTokenizer.from_pretrained(self.budget_forcing_tokenizer)
        else:
            tokenizer = AutoTokenizer.from_pretrained(
                self.budget_forcing_kwargs["model_name"]
            )

        return tokenizer

    def _budget_forcing_invoke(self, messages) -> AIMessage:
        logging.info("Budget forcing invoked")

        from langchain_openai import OpenAI

        if not isinstance(self.llm, OpenAI):
            raise ValueError(
                "Budget forcing is only supported for OpenAI completion endpoint."
            )

        tokenizer = self.set_up_tokenizer()

        from langchain_openai.chat_models.base import _convert_message_to_dict

        # convert the messages to dicts and apply the chat template
        messages_as_dicts = [
            _convert_message_to_dict(message) for message in messages.to_messages()
        ]
        prompt = tokenizer.apply_chat_template(
            messages_as_dicts,
            tokenize=False,
        )

        if self.budget_forcing_kwargs["max_tokens_thinking"] <= 0:
            # don't need to think, just generate the answer directly
            prompt += "<|im_start|>think\n<|im_start|>answer\n"
            response = self.llm.invoke(prompt)
            return AIMessage(response)

        # otherwise we need to think and apply budget forcing
        # output tracks the generated output after the initial prompt
        # prompt tracks the prompt used for generation which will need to keep adding the responses
        output = "<|im_start|>think\n"
        prompt += output

        # stop if reach end of thinking ("<|im_stard|>") or end ("|<im_end|>"),
        # or reached the max thinking tokens
        stop_token_ids = tokenizer("<|im_start|><|im_end|>")["input_ids"]
        ignore_str = "Wait"

        thinking_tokens_remaining = self.budget_forcing_kwargs["max_tokens_thinking"]
        sampling_params = {
            "max_tokens": thinking_tokens_remaining,
            "min_tokens": 0,
            "stop_token_ids": stop_token_ids,
            "skip_special_tokens": False,
        }

        i = 0
        # + 1 accounts for the first generation w/o ignoring
        max_thinking_steps = self.budget_forcing_kwargs["num_stop_skips"] + 1
        while i < max_thinking_steps and thinking_tokens_remaining > 0:
            if i > 0:
                # if we are not the first generation, need to add ignore string
                # to suppress the ending
                output += ignore_str
                prompt += ignore_str
                logging.info("Suppressing end to encourage more thinking")

            logging.info(f"Thinking round {i + 1} out of {max_thinking_steps}")
            logging.info(f"Thinking tokens remaining: {thinking_tokens_remaining}")
            response = self.llm.invoke(prompt, extra_body=sampling_params)
            output += response
            prompt += response

            # subtract the number of tokens used for thinking
            # we continue until we reach the max tokens or reach max number of skips
            thinking_tokens_remaining -= len(tokenizer.tokenize(response))
            sampling_params["max_tokens"] = thinking_tokens_remaining
            sampling_params["min_tokens"] = 1
            i += 1

        if thinking_tokens_remaining <= 0:
            logging.info("Max thinking tokens reached, stopping thinking")
        else:
            logging.info(
                f"Max thinking rounds {max_thinking_steps} reached, stopping thinking"
            )

        logging.info(
            f"Thinking tokens used: {self.budget_forcing_kwargs['max_tokens_thinking'] - thinking_tokens_remaining}"
        )

        # generate the final answer
        stop_token_ids = tokenizer("<|im_end|>")["input_ids"]
        sampling_params = {
            "min_tokens": 0,
            "stop_token_ids": stop_token_ids,
            "skip_special_tokens": False,
        }

        output += "<|im_start|>answer\n"
        prompt += "<|im_start|>answer\n"
        response = self.llm.invoke(prompt, extra_body=sampling_params)

        return AIMessage(output + response)

    async def _budget_forcing_ainvoke(self, messages) -> AIMessage:
        logging.info("Budget forcing invoked")

        from langchain_openai import OpenAI

        if not isinstance(self.llm, OpenAI):
            raise ValueError(
                "Budget forcing is only supported for OpenAI completion endpoint."
            )

        tokenizer = self.set_up_tokenizer()

        from langchain_openai.chat_models.base import _convert_message_to_dict

        # convert the messages to dicts and apply the chat template
        messages_as_dicts = [
            _convert_message_to_dict(message) for message in messages.to_messages()
        ]
        prompt = tokenizer.apply_chat_template(
            messages_as_dicts,
            tokenize=False,
        )

        if self.budget_forcing_kwargs["max_tokens_thinking"] <= 0:
            # don't need to think, just generate the answer directly
            prompt += "<|im_start|>think\n<|im_start|>answer\n"
            response = await self.llm.ainvoke(prompt)
            return AIMessage(response)

        # otherwise we need to think and apply budget forcing
        # output tracks the generated output after the initial prompt
        # prompt tracks the prompt used for generation which will need to keep adding the responses
        output = "<|im_start|>think\n"
        prompt += output

        # stop if reach end of thinking ("<|im_stard|>") or end ("|<im_end|>"),
        # or reached the max thinking tokens
        stop_token_ids = tokenizer("<|im_start|><|im_end|>")["input_ids"]
        ignore_str = "Wait"

        thinking_tokens_remaining = self.budget_forcing_kwargs["max_tokens_thinking"]
        sampling_params = {
            "max_tokens": thinking_tokens_remaining,
            "min_tokens": 0,
            "stop_token_ids": stop_token_ids,
            "skip_special_tokens": False,
        }

        i = 0
        # + 1 accounts for the first generation w/o ignoring
        max_thinking_steps = self.budget_forcing_kwargs["num_stop_skips"] + 1
        while i < max_thinking_steps and thinking_tokens_remaining > 0:
            if i > 0:
                # if we are not the first generation, need to add ignore string
                # to suppress the ending
                output += ignore_str
                prompt += ignore_str
                logging.info("Suppressing end to encourage more thinking")

            logging.info(f"Thinking round {i + 1} out of {max_thinking_steps}")
            logging.info(f"Thinking tokens remaining: {thinking_tokens_remaining}")
            response = await self.llm.ainvoke(prompt, extra_body=sampling_params)
            output += response
            prompt += response

            # subtract the number of tokens used for thinking
            # we continue until we reach the max tokens or reach max number of skips
            thinking_tokens_remaining -= len(tokenizer.tokenize(response))
            sampling_params["max_tokens"] = thinking_tokens_remaining
            sampling_params["min_tokens"] = 1
            i += 1

        if thinking_tokens_remaining <= 0:
            logging.info("Max thinking tokens reached, stopping thinking")
        else:
            logging.info(
                f"Max thinking rounds {max_thinking_steps} reached, stopping thinking"
            )

        logging.info(
            f"Thinking tokens used: {self.budget_forcing_kwargs['max_tokens_thinking'] - thinking_tokens_remaining}"
        )

        # generate the final answer
        stop_token_ids = tokenizer("<|im_end|>")["input_ids"]
        sampling_params = {
            "min_tokens": 0,
            "stop_token_ids": stop_token_ids,
            "skip_special_tokens": False,
        }

        output += "<|im_start|>answer\n"
        prompt += "<|im_start|>answer\n"
        response = await self.llm.ainvoke(prompt, extra_body=sampling_params)

        return AIMessage(output + response)

    def query_or_respond(self, state: CustomMessagesState):
        logging.info("Query or respond invoked")

        # generate tool call for retrieval or respond
        # model can decide whether to use the tool or respond directly
        from langchain_core.messages.system import SystemMessage

        llm_with_retrieve_tool = self.conversational_agent_llm.bind_tools(
            [create_retreiver_tool(self.retrieve_as_tool)]
        )
        response = llm_with_retrieve_tool.invoke(
            [SystemMessage(NHS_RETRIEVER_TOOL_PROMPT)] + state["messages"]
        )

        return {"messages": [response]}

    def process_tool_response(
        self, state: CustomMessagesState
    ) -> dict[str, str | list[Document]]:
        logging.info("Process tool response invoked")

        # get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break

        if recent_tool_messages:
            # extract the latest query and context pulled
            query, context = (
                recent_tool_messages[-1].artifact["query"],
                recent_tool_messages[-1].artifact["context"],
            )
        else:
            query, context = "", []

        return {
            "context": state.get("context", []) + [context],
            "retriever_queries": state.get("retriever_queries", []) + [query],
        }

    def obtain_context_and_sources(
        self, state: State | CustomMessagesState
    ) -> dict[str, str | list[str]]:
        logging.info("Obtaining context and sources...")

        # obtain the sources and the context from the retrieved documents
        if self.rerank:
            context = state["reranked_context"]
            context = context[-1] if self.conversational else context
        else:
            context = state["context"]
            context = context[-1] if self.conversational else context

        # obtain the sources and the context from the retrieved documents
        sources = [doc.metadata["source"] for doc in context]
        source_scores = [
            round(float(doc.metadata["sub_docs"][0].metadata["score"]), 3)
            for doc in context
        ]
        sources_and_scores = [
            f"({source}, {score:.3f})" for source, score in zip(sources, source_scores)
        ]
        sources_str = (
            f"Sources and similarity scores (lower is better): {sources_and_scores}"
        )
        retrieved_docs = [
            (
                f"\nSource: {doc.metadata['source']}, "
                f"similarity score: {round(float(doc.metadata['sub_docs'][0].metadata['score']), 3)}. "
                f"Content:\n{doc.page_content}"
            )
            for doc in context
        ]

        docs_content = "\n".join(retrieved_docs + [sources_str])

        return {
            "serialised_docs": docs_content,
            "sources": sources,
        }

    def generate(self, state: State | CustomMessagesState) -> dict[str, str]:
        """
        Generate an answer based on the question and retrieved documents.
        The retrieved documents are passed to the LLM along with the question
        using the prompt template.

        Parameters
        ----------
        state : State
            The state of the RAG query, containing the question and retrieved documents.

        Returns
        -------
        dict[str, str]
            A dictionary containing the generated answer and the messages used to generate it.
        """
        logging.info("Generating answer...")

        retriever_response = self.obtain_context_and_sources(state)
        messages_from_prompt = self.prompt.invoke(
            {
                "question": (
                    state["messages"] if self.conversational else state["question"]
                ),
                "context": retriever_response["serialised_docs"],
                "demographics": state["demographics"],
                "sources": retriever_response["sources"],
            },
        )

        if self.conversational:
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]
            if messages_from_prompt.messages[0].type == "system":
                messages = [messages_from_prompt.messages[0]] + conversation_messages
            else:
                messages = conversation_messages

            if (
                messages_from_prompt.messages[-1].type == "human"
                and messages_from_prompt.messages[-1].content != ""
                and messages[-1].type == "human"
            ):
                messages[-1] = messages_from_prompt.messages[-1]
        else:
            messages = messages_from_prompt

        if self.budget_forcing:
            response = self._budget_forcing_invoke(messages)
        else:
            response = self.llm.invoke(messages)

        if self.conversational:
            return {
                "system_messages": (
                    state.get("system_messages", [])
                    + [messages_from_prompt.messages[0]]
                    if messages_from_prompt.messages[0].type == "system"
                    else state.get("system_messages", []) + [None]
                ),
                "messages": [response],
            }
        else:
            return {"messages": messages, "answer": response}

    async def agenerate(self, state: State | CustomMessagesState) -> dict[str, str]:
        """
        Generate an answer based on the question and retrieved documents.
        The retrieved documents are passed to the LLM along with the question
        using the prompt template.

        Parameters
        ----------
        state : State
            The state of the RAG query, containing the question and retrieved documents.

        Returns
        -------
        dict[str, str]
            A dictionary containing the generated answer and the messages used to generate it.
        """
        logging.info("Generating answer...")

        retriever_response = self.obtain_context_and_sources(state)
        messages_from_prompt = self.prompt.invoke(
            {
                "question": (
                    state["messages"] if self.conversational else state["question"]
                ),
                "context": retriever_response["serialised_docs"],
                "demographics": state["demographics"],
                "sources": retriever_response["sources"],
            },
        )

        if self.conversational:
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]
            if messages_from_prompt.messages[0].type == "system":
                messages = [messages_from_prompt.messages[0]] + conversation_messages
            else:
                messages = conversation_messages

            if (
                messages_from_prompt.messages[-1].type == "human"
                and messages_from_prompt.messages[-1].content != ""
                and messages[-1].type == "human"
            ):
                messages[-1] = messages_from_prompt.messages[-1]
        else:
            messages = messages_from_prompt

        if self.budget_forcing:
            response = await self._budget_forcing_ainvoke(messages)
        else:
            response = await self.llm.ainvoke(messages)

        if self.conversational:
            return {
                "system_messages": (
                    state.get("system_messages", [])
                    + [messages_from_prompt.messages[0]]
                    if messages_from_prompt.messages[0].type == "system"
                    else state.get("system_messages", []) + [None]
                ),
                "messages": [response],
            }
        else:
            return {"messages": messages, "answer": response}

    def build_graph(self) -> CompiledStateGraph:
        """
        Build a Langchain compiled state graph with the retrieve and generate functions
        as nodes.

        Returns
        -------
        CompiledStateGraph
            The compiled state graph.
        """
        if self.rerank:
            graph_builder = StateGraph(State).add_sequence(
                [self.retrieve, self.rerank_documents, self.generate]
            )
        else:
            graph_builder = StateGraph(State).add_sequence(
                [self.retrieve, self.generate]
            )
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile(checkpointer=self.memory)
        return graph

    def build_conversation_graph(self) -> CompiledStateGraph:
        """
        Build a Langchain compiled state graph for conversational RAG.

        Returns
        -------
        CompiledStateGraph
            The compiled state graph.
        """
        tools = ToolNode([create_retreiver_tool(self.retrieve_as_tool)])

        graph_builder = StateGraph(CustomMessagesState)
        graph_builder.add_node(self.query_or_respond)
        graph_builder.add_node(tools)
        graph_builder.add_node(self.process_tool_response)
        if self.rerank:
            graph_builder.add_node(self.rerank_documents)
        graph_builder.add_node(self.generate)

        graph_builder.add_edge(START, "query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "process_tool_response")
        if self.rerank:
            graph_builder.add_edge("process_tool_response", "rerank_documents")
            graph_builder.add_edge("rerank_documents", "generate")
        else:
            graph_builder.add_edge("process_tool_response", "generate")
        graph_builder.add_edge("generate", END)

        graph = graph_builder.compile(checkpointer=self.memory)

        return graph

    def _query(
        self, question: str, user_id: str = "0", demographics: str | None = None
    ) -> State | CustomMessagesState:
        if self.conversational:
            input = {
                "messages": {"role": "user", "content": question},
                "demographics": demographics,
            }
        else:
            input = {"question": question, "demographics": demographics}

        response = self.graph.invoke(
            input=input,
            config={"configurable": {"thread_id": user_id}},
        )
        return response

    async def _aquery(
        self, question: str, user_id: str = "0", demographics: str | None = None
    ) -> State | CustomMessagesState:
        if self.conversational:
            input = {
                "messages": {"role": "user", "content": question},
                "demographics": demographics,
            }
        else:
            input = {"question": question, "demographics": demographics}

        response = await self.graph.ainvoke(
            input=input,
            config={"configurable": {"thread_id": user_id}},
        )
        return response

    def query(self, question: str, user_id: str = "0") -> str:
        """
        Query the RAG with a question and return response.

        Parameters
        ----------
        question : str
            The question to ask the RAG.
        user_id : str, optional
            The user ID for the query, by default "0".

        Returns
        -------
        str
            The answer generated by the RAG.
        """
        response = self._query(question=question, user_id=user_id)
        if self.conversational:
            return response["messages"][-1].content
        else:
            return response["answer"].content

    async def aquery(self, question: str, user_id: str = "0") -> str:
        """
        Async query the RAG with a question and return response.

        Parameters
        ----------
        question : str
            The question to ask the RAG.
        user_id : str, optional
            The user ID for the query, by default "0".

        Returns
        -------
        str
            The answer generated by the RAG.
        """
        response = await self._aquery(question=question, user_id=user_id)
        if self.conversational:
            return response["messages"][-1].content
        else:
            return response["answer"].content

    async def aquery_with_sources(self, question: str, user_id: str = "0") -> str:
        """
        Asynchronously query the RAG with a question and return response with sources used
        in the context.

        Parameters
        ----------
        question : str
            The question to ask the RAG.
        user_id : str, optional
            The user ID for the query, by default "0".

        Returns
        -------
        str
            The answer generated by the RAG along with the sources used
            in the context.
        """
        response = await self._aquery(question=question, user_id=user_id)

        if self.conversational:
            answer = response["messages"][-1].content
        else:
            answer = response["answer"].content

        if "context" in response:
            context = (
                response["reranked_context"] if self.rerank else response["context"]
            )
            context = context[-1] if self.conversational else context

            # extract the sources of the documents used in the context
            sources = [doc.metadata["source"] for doc in context]

            # compose response with the context and answer
            response_with_context = "\n".join(
                [
                    f"Sources: {sources}",
                    f"{answer}",
                ]
            )
        else:
            # if no context, just return the answer
            response_with_context = answer

        return response_with_context

    async def aquery_with_context(self, question: str, user_id: str = "0") -> str:
        """
        Asynchronously query the RAG with a question and return response with context
        used in the context.

        Parameters
        ----------
        question : str
            The question to ask the RAG.
        user_id : str, optional
            The user ID for the query, by default "0".

        Returns
        -------
        str
            The answer generated by the RAG along with the context used
            in the context.
        """
        response = await self._aquery(question=question, user_id=user_id)

        if self.conversational:
            answer = response["messages"][-1].content
        else:
            answer = response["answer"].content

        if "context" in response:
            context = (
                response["reranked_context"] if self.rerank else response["context"]
            )
            context = context[-1] if self.conversational else context

            # extract the sources and contents of the documents used in the context
            pulled_context = [
                f"{'-' * 100}\nSource: {doc.metadata['source']}\nContent:\n{doc.page_content}"
                for doc in context
            ]
            sources = [doc.metadata["source"] for doc in context]

            # compose response with the context and answer
            response_with_context = "\n".join(
                ["\nContext:"] + pulled_context + [f"Sources: {sources}"] + [answer]
            )
        else:
            # if no context, just return the answer
            response_with_context = answer

        return response_with_context


def load_llm(
    llm_provider: str, llm_model_name: str, extra_body: dict | str | None = None
) -> LLM:
    if not llm_provider:
        raise ValueError(
            "LLM provider is not specified. Please provide a valid LLM provider."
        )
    if not llm_model_name:
        raise ValueError(
            "LLM model name is not specified. Please provide a valid LLM model name."
        )

    if llm_provider == "huggingface":
        from t0_001.rag.chat_model import get_huggingface_chat_model

        llm = get_huggingface_chat_model(method="pipeline", model_name=llm_model_name)
    elif llm_provider == "azure_openai":
        from t0_001.rag.chat_model import get_azure_openai_chat_model

        llm = get_azure_openai_chat_model(model_name=llm_model_name)
    elif llm_provider == "azure":
        from t0_001.rag.chat_model import get_azure_endpoint_chat_model

        llm = get_azure_endpoint_chat_model(model_name=llm_model_name)
    elif llm_provider == "openai":
        from t0_001.rag.chat_model import get_openai_chat_model

        llm = get_openai_chat_model(model_name=llm_model_name, extra_body=extra_body)
    elif llm_provider == "openai_completion":
        from t0_001.rag.chat_model import get_openai_completion_model

        llm = get_openai_completion_model(
            model_name=llm_model_name, extra_body=extra_body
        )
    else:
        raise ValueError(
            f"Unknown LLM provider: {llm_provider}. Use 'huggingface', "
            "'azure_openai', 'azure', 'openai', or 'openai_completion'."
        )

    return llm


def build_rag(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    conversational: bool = False,
    conversational_agent_llm_provider: str | None = None,
    conversational_agent_llm_model_name: str | None = None,
    tools: list | None = None,
    tools_kwargs: dict = {},
    prompt_template_path: str | Path | None = None,
    system_prompt_path: str | Path | None = None,
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
) -> RAG:
    if budget_forcing and llm_provider != "openai_completion":
        raise ValueError(
            "Budget forcing is only supported for OpenAI completion endpoint."
        )

    # obtain the retriever for RAG
    retriever = get_parent_doc_retriever(
        conditions_file=conditions_file,
        config=config,
        force_create=force_create,
        trust_source=trust_source,
    )

    # obtain the prompt template for RAG
    if prompt_template_path is None:
        prompt_template = hub.pull("rlm/rag-prompt")
    else:
        from t0_001.rag.custom_prompt_template import read_prompt_template

        prompt_template = read_prompt_template(
            prompt_template_path=prompt_template_path,
            system_prompt_path=system_prompt_path,
        )

    # obtain the LLM for RAG
    llm = load_llm(
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        extra_body=extra_body,
    )

    if conversational:
        # obtain the LLM for conversational retriever agent
        conversational_agent_llm = load_llm(
            llm_provider=conversational_agent_llm_provider,
            llm_model_name=conversational_agent_llm_model_name,
            extra_body=extra_body,
        )
    else:
        conversational_agent_llm = None

    if rerank:
        # obtain the prompt template for reranking
        if rerank_prompt_template_path is None:
            raise ValueError(
                "Reranking is enabled, but no prompt template path is provided. Please provide a `rerank_prompt_template_path`."
            )
        else:
            from t0_001.rag.custom_prompt_template import read_prompt_template

            rerank_prompt_template = read_prompt_template(
                prompt_template_path=rerank_prompt_template_path,
            )

        # obtain the LLM for reranking
        rerank_llm = load_llm(
            llm_provider=rerank_llm_provider,
            llm_model_name=rerank_llm_model_name,
            extra_body=rerank_extra_body,
        )
    else:
        rerank_llm = None
        rerank_prompt_template = None
        rerank_extra_body = None
        rerank_k = 0

    rag = RAG(
        retriever=retriever,
        prompt=prompt_template,
        llm=llm,
        conversational=conversational,
        conversational_agent_llm=conversational_agent_llm,
        tools=tools,
        tools_kwargs=tools_kwargs,
        budget_forcing=budget_forcing,
        budget_forcing_kwargs={
            "model_name": llm_model_name,
            "max_tokens_thinking": 1024,
            "num_stop_skips": 3,
        }
        | process_arg_to_dict(budget_forcing_kwargs),
        budget_forcing_tokenizer=budget_forcing_tokenizer,
        rerank=rerank,
        rerank_prompt=rerank_prompt_template,
        rerank_llm=rerank_llm,
        rerank_k=rerank_k,
    )

    return rag
