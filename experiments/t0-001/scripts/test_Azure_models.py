import os
import time

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Specify the path to your .env file
dotenv_path = Path("../.env")
load_dotenv(dotenv_path=dotenv_path)

# Constants
MAX_TOKENS = 2048
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"

# Models
OPENAI_MODELS = [
    #"o3-mini",
     "gpt-4o",
    # "o1",
]

DEEPSEEK_MODELS = [
    "v3",
    "r1",
]

AVAILABLE_MODELS = OPENAI_MODELS + DEEPSEEK_MODELS


def get_env_var(key: str) -> str:
    try:
        return os.environ[key]
    except KeyError:
        raise KeyError(f"Please set the {key} environment variable.")


for model in AVAILABLE_MODELS:
    print(f"Testing model: {model}")
    time.sleep(5)

    if model in OPENAI_MODELS:
        endpoint = get_env_var("AZURE_OPENAI_ENDPOINT_o3-mini")
        key = get_env_var("AZURE_OPENAI_API_KEY")

        client = AzureOpenAI(
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=endpoint,
            api_key=key,
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I am going to Paris, what should I see?",
                },
            ],
            max_completion_tokens=MAX_TOKENS,
            model=model,
        )

        print("*" * 100)
        print(f"{model} response:")
        print("*" * 100)
        print(response.choices[0].message.content)

    elif model in DEEPSEEK_MODELS:
        endpoint = get_env_var(f"AZURE_ENDPOINT_deepseek-{model}")
        key = get_env_var(f"AZURE_API_KEY_deepseek-{model}")

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        model_name = f"DeepSeek-{model}"

        response = client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="I am going to Paris, what should I see?"),
            ],
            max_tokens=MAX_TOKENS,
            model=model_name,
        )

        print("*" * 100)
        print(f"{model} response:")
        print("*" * 100)
        print(response.choices[0].message.content)

print("Finished testing all models.")
