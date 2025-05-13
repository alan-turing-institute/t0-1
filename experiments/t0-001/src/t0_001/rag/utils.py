from typing import Callable

NHS_RETRIEVER_TOOL_PROMPT = """You are a helpful clinical AI assistant called Marcel.

You are provided a tool that can retrieve context from a knowledge base taken from NHS condition web pages which provide information about various medical conditions.
You should always use the tool to find relevant information to answer the patient's question rather than relying on your own knowledge.
You should only not use the tool in very simple messages that do not require any context like "Hello" or "Thank you", or when the user is just writing something random.
If you are confused or unsure about the user's question, you should use the tool to find relevant information or ask the user for more information or ask further details about their symptoms.
For follow up questions from the user, you should always use the tool to find new relevant information to answer the user's question given the conversation history.

In your response, reply in English and always refer to the user in the second person.

You can also ask the user for more information or ask further details about their symptoms.
If you are going to reply to the user, always conclude with a question to keep the conversation going to help the user or ask for more details about their symptoms."""


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
