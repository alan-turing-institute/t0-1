import logging

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential
from t0_001.utils import get_environment_variable

AZURE_OPENAI_ENDPOINTS = {
    "gpt-4o",
    "o3-mini",
    "o1",
}


def get_azure_openai_endpoint(model: str):
    """Get the Azure OpenAI endpoint from the environment variables.

    Parameters
    ----------
    model : str
        The model to use. Must be one of the following: gpt-4o, o3-mini, o1.
    """
    logging.getLogger(__name__)

    endpoint = get_environment_variable("AZURE_OPENAI_ENDPOINT", model)
    endpoint = endpoint.rstrip("/")  # Remove trailing slash if present

    # add the deployment name to the endpoint
    if endpoint.endswith("openai.azure.com"):
        endpoint = endpoint + "/openai/deployments/" + model
    logging.info(f"Using Azure OpenAI endpoint: {endpoint}")
    return endpoint


def get_azure_openai_key(model: str):
    """Get the Azure OpenAI key from the environment variables.

    Parameters
    ----------
    model : str
        The model to use. Must be one of the following: gpt-4o, o3-mini, o1.
    """
    logging.getLogger(__name__)

    key = get_environment_variable("AZURE_OPENAI_API_KEY", model)
    return key


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
