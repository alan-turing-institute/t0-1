from pathlib import Path

from langchain import hub
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import START, CompiledStateGraph, StateGraph
from t0_001.query_vector_store.build_retriever import (
    DEFAULT_RETRIEVER_CONFIG,
    RetrieverConfig,
    get_parent_doc_retriever,
)
from t0_001.query_vector_store.custom_parent_document_retriever import (
    CustomParentDocumentRetriever,
)
from typing_extensions import TypedDict


class State(TypedDict):
    """
    State is a TypedDict that represents the state of a RAG query.
    It contains the question, context, and answer.
    """

    question: str
    context: list[Document]
    demographics: str | None
    messages: str
    answer: str


class RAG:
    def __init__(
        self,
        retriever: CustomParentDocumentRetriever,
        prompt: PromptTemplate,
        llm: LLM,
        tools: list | None = None,
        tools_kwargs: dict = {},
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
        tools : list | None, optional
            List of tools to bind to the LLM. By default None.
        tools_kwargs : dict, optional
            Keyword arguments to pass to the tools. By default {}.
        """
        self.retriever: CustomParentDocumentRetriever = retriever
        self.prompt: PromptTemplate = prompt
        self.llm: LLM = llm
        self.tools: list | None = tools
        if tools is not None:
            self.llm = self.llm.bind_tools(tools, **tools_kwargs)
        self.memory: MemorySaver = MemorySaver()
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
        retrieved_docs: list[Document] = self.retriever.invoke(input=state["question"])

        return {"context": retrieved_docs}

    def obtain_context_and_sources(self, state: State) -> tuple[str, list[str]]:
        # obtain the sources and the context from the retrieved documents
        sources = [doc.metadata["source"] for doc in state["context"]]
        source_scores = [
            round(float(doc.metadata["sub_docs"][0].metadata["score"]), 3)
            for doc in state["context"]
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
            for doc in state["context"]
        ]

        docs_content = "\n".join(retrieved_docs + [sources_str])

        return docs_content, sources

    def generate(self, state: State) -> dict[str, str]:
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
        docs_content, sources = self.obtain_context_and_sources(state)
        messages = self.prompt.invoke(
            {
                "question": state["question"],
                "context": docs_content,
                "demographics": state["demographics"],
                "sources": sources,
            },
        )

        response = self.llm.invoke(messages)
        return {"messages": messages, "answer": response}

    async def agenerate(self, state: State) -> dict[str, str]:
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
        docs_content, sources = self.obtain_context_and_sources(state)
        messages = await self.prompt.ainvoke(
            {
                "question": state["question"],
                "context": docs_content,
                "demographics": state["demographics"],
                "sources": sources,
            },
        )

        response = await self.llm.ainvoke(messages)
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
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile(checkpointer=self.memory)
        return graph

    def _query(
        self, question: str, user_id: str = "0", demographics: str | None = None
    ) -> State:
        response = self.graph.invoke(
            input={"question": question, "demographics": demographics},
            config={"configurable": {"thread_id": user_id}},
        )
        return response

    async def _aquery(
        self, question: str, user_id: str = "0", demographics: str | None = None
    ) -> State:
        response = await self.graph.ainvoke(
            input={"question": question, "demographics": demographics},
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
        return response["answer"].content

    async def query_with_sources(self, question: str, user_id: str = "0") -> str:
        """
        Query the RAG with a question and return response with sources used
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
        response = await self._query(question=question, user_id=user_id)

        # extract the sources of the documents used in the context
        pulled_context = [doc.metadata["source"] for doc in response["context"]]

        # compose response with the context and answer
        response_with_context = "\n".join(
            [
                f"{response['answer'].content}",
                f"\nSources: {pulled_context}",
            ]
        )

        return response_with_context

    async def query_with_context(self, question: str, user_id: str = "0") -> str:
        """
        Query the RAG with a question and return response with context
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

        # extract the sources and contents of the documents used in the context
        pulled_context = [
            f"{'-' * 100}\nSource: {doc.metadata['source']}\nContent:\n{doc.page_content}"
            for doc in response["context"]
        ]

        # compose response with the context and answer
        response_with_context = "\n".join(
            [
                f"{response['answer'].content}",
                "\nContext:",
            ]
            + pulled_context
        )

        return response_with_context


def build_rag(
    conditions_file: str,
    config: RetrieverConfig = DEFAULT_RETRIEVER_CONFIG,
    force_create: bool = False,
    trust_source: bool = False,
    llm_provider: str = "huggingface",
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
    tools: list | None = None,
    tools_kwargs: dict = {},
    prompt_template_path: str | Path | None = None,
    system_prompt_path: str | Path | None = None,
    extra_body: dict | str | None = None,
) -> RAG:
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
    else:
        raise ValueError(
            f"Unknown LLM provider: {llm_provider}. Use 'huggingface', 'azure_openai', or 'azure'."
        )

    rag = RAG(
        retriever=retriever,
        prompt=prompt_template,
        llm=llm,
        tools=tools,
        tools_kwargs=tools_kwargs,
    )

    return rag
