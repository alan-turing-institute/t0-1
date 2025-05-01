from typing import Callable

NHS_RETRIEVER_TOOL_PROMPT = """You are a clinical AI assistant for question-answering tasks.

You are provided a tool that can retrieve context from a knowledge base taken from NHS condition web pages which provide information about various medical conditions.
You should always use the tool to find relevant information to answer the patient's question rather than relying on your own knowledge. Only do not use the tool in very simple messages that do not require any context like "Hello" or "Thank you"."""


def create_retreiver_tool(callable: Callable):
    """
    Create a tool for the retriever function which comes from
    a member method of the RAG class.

    This is used to bind the retriever function to the LLM
    when using the retriever as a tool. This is a workaround from using
    the @tool decorator which does not work out the box with
    member methods: see langchain#9404.
    """
    from langchain.tools import StructuredTool
    from pydantic.v1 import Field, create_model

    method = callable
    name = method.__name__
    func_desc = "Retrieve documents from the vector store based on the query."
    arg_desc = {
        "query": "The query to retrieve documents for.",
    }
    arg_fields = {
        "query": (str, Field(description=arg_desc["query"])),
    }

    Model = create_model("Model", **arg_fields)

    tool = StructuredTool.from_function(
        func=method,
        name=name,
        description=func_desc,
        args_schema=Model,
        return_direct=False,
        response_format="content_and_artifact",
    )
    return tool
