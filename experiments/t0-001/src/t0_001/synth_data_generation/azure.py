import os

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage

def set_up_azure_client():
    """Set up the Azure OpenAI client.
    """
    # set up the environment
    try:
        endpoint = os.environ["AZURE_OPENAI_CHAT_ENDPOINT"]
    except KeyError:
        raise KeyError("Please set the AZURE_OPENAI_CHAT_ENDPOINT environment variable.")
    
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


def get_response_from_azure_model(client, prompt):
    response = client.complete(
        messages=[
            UserMessage(content=prompt)
        ],
    )
    return response["choices"][0]["message"]["content"]
