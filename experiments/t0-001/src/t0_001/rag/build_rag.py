from pathlib import Path

from langchain import hub
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import VectorStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import START, CompiledStateGraph, StateGraph
from t0_001.query_vector_store.build_index import get_vector_store
from t0_001.rag.chat_model import get_huggingface_chat_model
from typing_extensions import List, TypedDict


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def build_rag(
    conditions_folder: str,
    main_only: bool = True,
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
    chunk_overlap: int = 50,
    db_choice: str = "chroma",
    persist_directory: str | Path = None,
    force_create: bool = False,
    trust_source: bool = False,
    k: int = 4,
    with_score: bool = False,
    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
):
    db = get_vector_store(
        conditions_folder=conditions_folder,
        main_only=main_only,
        embedding_model_name=embedding_model_name,
        chunk_overlap=chunk_overlap,
        db_choice=db_choice,
        persist_directory=persist_directory,
        force_create=force_create,
        trust_source=trust_source,
    )
    llm = get_huggingface_chat_model(method="pipeline", model_name=llm_model_name)
    rag = RAG(
        vector_store=db,
        prompt=hub.pull("rlm/rag-prompt"),
        llm=llm,
        k=k,
        with_score=with_score,
    )

    return rag


class RAG:
    def __init__(
        self,
        vector_store: VectorStore,
        prompt: PromptTemplate,
        llm: LLM,
        k: int = 4,
        with_score: bool = False,
    ):
        self.vector_store: VectorStore = vector_store
        self.k: int = k
        self.with_score: bool = with_score
        self.prompt: PromptTemplate = prompt
        self.llm: LLM = llm
        self.memory: MemorySaver = MemorySaver()
        self.graph: CompiledStateGraph = self.build_graph()

    def retrieve(self, state: State) -> dict[str, List[Document]]:
        if self.with_score:
            retrieved_docs = self.vector_store.similarity_search_with_score(
                query=state["question"], k=self.k
            )
        else:
            retrieved_docs = self.vector_store.similarity_search(
                query=state["question"], k=self.k
            )
        return {"context": retrieved_docs}

    def generate(self, state: State) -> dict[str, str]:
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.invoke(
            {"question": state["question"], "context": docs_content}
        )
        response = self.llm.invoke(messages)
        return {"answer": response}

    def build_graph(self) -> StateGraph:
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile(checkpointer=self.memory)
        return graph

    def _query(self, question: str, user_id: str = "0") -> State:
        response = self.graph.invoke(
            input={"question": question},
            config={"configurable": {"thread_id": user_id}},
        )
        return response

    def query(self, question: str, user_id: str = "0") -> str:
        response = self._query(question=question, user_id=user_id)
        return response["answer"].content

    def query_with_sources(self, question: str, user_id: str = "0") -> str:
        response = self._query(question=question, user_id=user_id)
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

    def query_with_context(self, question: str, user_id: str = "0") -> str:
        response = self._query(question=question, user_id=user_id)
        # extract the sources and contents of the documents used in the context
        pulled_context = [
            f"Source: {doc.metadata['source']}\nContent:\n{doc.page_content}"
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
