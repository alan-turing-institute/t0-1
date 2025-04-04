import os

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential


def get_azure_client(model: str = "o3") -> ChatCompletionsClient:
    """Get Azure OpenAI client for a specific model.
    The model should be available in the Azure OpenAI service.
    The endpoint and key should be set in the environment variables:
    AZURE_OPENAI_CHAT_ENDPOINT_<model> and AZURE_OPENAI_CHAT_KEY.
    Parameters
    ----------
    model : str
        The model to use. This should be the name of the model, e.g. "gpt-35-turbo".
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

    # set up the client
    return ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        api_version="2025-01-01-preview",
    )
