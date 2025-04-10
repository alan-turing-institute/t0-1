import logging
import os

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential


def set_up_azure_client():
    """Set up the Azure OpenAI client.

    Returns
    -------
    ChatCompletionsClient
        The Azure OpenAI client.
    """
    # set up the environment
    try:
        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    except KeyError:
        raise KeyError("Please set the AZURE_OPENAI_ENDPOINT environment variable.")

    try:
        key = os.environ["AZURE_OPENAI_KEY"]
    except KeyError:
        raise KeyError("Please set the AZURE_OPENAI_KEY environment variable.")

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
    except [KeyError, IndexError]:
        logging.error(f"Model returned an invalid response: {response}")
        return None
