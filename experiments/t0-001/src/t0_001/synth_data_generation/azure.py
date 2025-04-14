import logging
import os

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential

AZURE_OPENAI_ENDPOINTS = {
    "gpt-4o",
    "o3-mini",
    "o1",
}


def get_azure_openai_endpoint(model: str):
    """Get the Azure OpenAI endpoint from the environment variables.
    The endpoint is stored in the environment variable AZURE_OPENAI_ENDPOINT_{model}.

    Parameters
    ----------
    model : str
        The model to use. Must be one of the following: gpt-4o, o3-mini, o1.
    """
    logging.getLogger(__name__)

    try:
        endpoint = os.environ[f"AZURE_OPENAI_ENDPOINT_{model.lower()}"]
    except KeyError:
        raise KeyError(
            f"Please set the AZURE_OPENAI_ENDPOINT_{model.lower()} environment variable."
        )

    logging.info(f"Using Azure OpenAI endpoint: {endpoint}")
    return endpoint


def get_azure_openai_key():
    """Get the Azure OpenAI key from the environment variables."""
    try:
        return os.environ["AZURE_OPENAI_KEY"]
    except KeyError:
        raise KeyError("Please set the AZURE_OPENAI_KEY environment variable.")


def set_up_azure_client(endpoint: str, key: str) -> ChatCompletionsClient:
    """Set up the Azure OpenAI client.

    Parameters
    ----------
    endpoint : str
        The Azure OpenAI endpoint.
    key : str
        The Azure OpenAI key.

    Returns
    -------
    ChatCompletionsClient
        The Azure OpenAI client.
    """
    # set up the client
    return ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        api_version="2025-01-01-preview",
    )


def get_response_from_azure_model(client: ChatCompletionsClient, prompt: str):
    """Get a response from the Azure OpenAI model.
    Parameters
    ----------
    client : ChatCompletionsClient
        The Azure OpenAI client.
    prompt : str
        The prompt to send to the model.

    Returns
    -------
    str
        The response from the model.
    """
    logging.getLogger(__name__)

    response = client.complete(
        messages=[UserMessage(content=prompt)],
    )
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        logging.error(f"Model returned an invalid response: {response}")
        return None
