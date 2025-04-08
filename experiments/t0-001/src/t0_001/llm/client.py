import os
from typing import Any

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential


def get_azure_client(
    model: str = "o3", use_async: bool = False
) -> ChatCompletionsClient | AsyncChatCompletionsClient:
    """Get Azure OpenAI client for a specific model.
    The model should be available in the Azure OpenAI service.
    The endpoint and key should be set in the environment variables:
    AZURE_OPENAI_CHAT_ENDPOINT_<model> and AZURE_OPENAI_CHAT_KEY.
    Parameters
    ----------
    model : str
        The model to use. This should be the name of the model, e.g. "gpt-35-turbo".
    use_async : bool
        Whether to use the async client or not. Default is False.

    Returns
    -------
    ChatCompletionsClient
        The Azure OpenAI client.
    """
    # set up the environment
    try:
        endpoint = os.environ[f"AZURE_OPENAI_CHAT_ENDPOINT_{model}"]
    except KeyError:
        raise KeyError(
            "Please set the AZURE_OPENAI_CHAT_ENDPOINT environment variable."
        )

    try:
        key = os.environ["AZURE_OPENAI_CHAT_KEY"]
    except KeyError:
        raise KeyError("Please set the AZURE_OPENAI_CHAT_KEY environment variable.")

    Client = AsyncChatCompletionsClient if use_async else ChatCompletionsClient
    return Client(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        api_version="2025-01-01-preview",
    )


def parse_messages(messages: list[dict[str, str]]) -> list[UserMessage | SystemMessage]:
    """Parse messages from a list of dictionaries to a list of UserMessage or SystemMessage objects.
    Parameters
    ----------
    messages : list[dict[str, str]]
        The messages to parse.

    Returns
    -------
    list[UserMessage | SystemMessage]
        The parsed messages.
    """
    parsed_messages = []
    for message in messages:
        if message["role"] == "user":
            del message["role"]
            parsed_messages.append(UserMessage(**message))
        elif message["role"] == "system":
            del message["role"]
            parsed_messages.append(SystemMessage(**message))
        else:
            raise ValueError(f"Unknown role: {message['role']}")
    return parsed_messages


def chat(
    client: ChatCompletionsClient,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]] = None,
    **kwargs,
):
    response = client.complete(
        messages=parse_messages(messages),
        tools=tools,
        **kwargs,
    )
    return response


async def async_chat(
    client: AsyncChatCompletionsClient,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]] = None,
    **kwargs,
):
    """Asynchronous chat with Azure OpenAI.

    Could be used to handle large volumes of requests with multiple threads.
    """
    async with client:
        response = await client.complete(
            messages=parse_messages(messages), tools=tools, **kwargs
        )
        return response
