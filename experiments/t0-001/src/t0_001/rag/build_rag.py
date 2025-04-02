from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import VectorStore
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class RAG:
    def __init__(self, vector_store: VectorStore, prompt: PromptTemplate, llm: LLM):
        self.vector_store: VectorStore = vector_store
        self.prompt: PromptTemplate = prompt
        self.llm: LLM = llm
        self.graph: StateGraph = self.build_graph()

    def retrieve(self, state: State) -> dict[str, List[Document]]:
        retrieved_docs = self.vector_store.similarity_search(state["question"])
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
        graph = graph_builder.compile()
        return graph

    def query(self, question: str) -> State:
        result = self.graph.invoke({"question": question})
        return result
