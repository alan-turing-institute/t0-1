import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import BaseLLM
from t0_001.utils import get_environment_variable


def get_huggingface_chat_model(
    method: str, model_name: str, task: str = "text-generation", **kwargs
) -> BaseChatModel:
    """
    Get a HuggingFace chat model based on the specified method and model name.

    Parameters
    ----------
    method : str
        The method to use for loading the model. Can be either "pipeline" or "endpoint".
    model_name : str
        The name of the model to load.
    task : str, optional
        The task to perform with the model. Default is "text-generation".

    Returns
    -------
    ChatHuggingFace
        The loaded HuggingFace chat model.
    """
    from langchain_huggingface import ChatHuggingFace

    if method == "pipeline":
        from langchain_huggingface import HuggingFacePipeline

        logging.info(f"Using HuggingFace pipeline for model: {model_name}")
        logging.info("Loading language model...")
        llm = HuggingFacePipeline.from_model_id(
            model_id=model_name,
            task=task,
            pipeline_kwargs={
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False,
            }
            | kwargs,
        )
    elif method == "endpoint":
        from langchain_huggingface import HuggingFaceEndpoint

        logging.info(f"Using HuggingFace endpoint for model: {model_name}")
        llm = HuggingFaceEndpoint(repo_id=model_name, task=task, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'pipeline' or 'endpoint'.")

    return ChatHuggingFace(llm=llm)


def get_azure_openai_chat_model(
    model_name: str,
    api_version: str = "2025-01-01-preview",
) -> BaseChatModel:
    """
    Get an Azure OpenAI chat model based on the specified model name and API version.
    Environment variables are used to get the API key and endpoint.
    The environment variables are expected to be in the format:
    AZURE_OPENAI_API_KEY_<model_name> and AZURE_OPENAI_ENDPOINT_<model_name>.
    If these environment variables do not exist, the function will look for
    AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.

    Parameters
    ----------
    model_name : str
        The name of the model to load.
    api_version : str, optional
        The API version to use. Default is "2025-01-01-preview".

    Returns
    -------
    AzureChatOpenAI
        The loaded Azure OpenAI chat model.
    """
    from langchain_openai import AzureChatOpenAI

    logging.info(f"Using Azure OpenAI for model: {model_name}")

    azure_openai_endpoint = get_environment_variable(
        "AZURE_OPENAI_ENDPOINT", model_name
    )
    azure_openai_api_key = get_environment_variable("AZURE_OPENAI_API_KEY", model_name)

    llm = AzureChatOpenAI(
        azure_deployment=model_name,
        api_key=azure_openai_api_key,
        azure_endpoint=azure_openai_endpoint,
        api_version=api_version,
    )

    return llm


def get_azure_endpoint_chat_model(
    model_name: str,
) -> BaseChatModel:
    """
    Get an Azure endpoint chat model based on the specified model name.
    Environment variables are used to get the API key and endpoint.
    The environment variables are expected to be in the format:
    AZURE_API_KEY_<model_name> and AZURE_ENDPOINT_<model_name>.
    If these environment variables do not exist, the function will look for
    AZURE_API_KEY and AZURE_ENDPOINT.

    Parameters
    ----------
    model_name : str
        The name of the model to load.

    Returns
    -------
    AzureAIChatCompletionsModel
        The loaded Azure endpoint chat model.
    """
    from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel

    logging.info(f"Using Azure endpoint for model: {model_name}")

    api_key = get_environment_variable("AZURE_API_KEY", model_name)
    endpoint_url = get_environment_variable("AZURE_ENDPOINT", model_name)

    llm = AzureAIChatCompletionsModel(
        endpoint=endpoint_url,
        credential=api_key,
    )

    return llm


def process_extra_body(extra_body: dict | str | None) -> dict:
    if extra_body is None:
        extra_body = {}
    else:
        import json

        try:
            extra_body = json.loads(extra_body)
        except json.JSONDecodeError:
            logging.error(f"extra_body is not a valid json: {extra_body}")
            raise


def get_openai_chat_model(
    model_name: str,
    extra_body: dict | str | None = None,
) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    logging.info(f"Using OpenAI for model: {model_name}")
    logging.info(f"Extra body to pass to chat/completions: {extra_body}")

    api_key = get_environment_variable("OPENAI_API_KEY", model_name)
    base_url = get_environment_variable("OPENAI_BASE_URL", model_name)
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        extra_body=process_extra_body(extra_body),
    )

    return llm


def get_openai_completion_model(
    model_name: str,
    extra_body: dict | str | None = None,
) -> BaseLLM:
    from langchain_openai import OpenAI

    logging.info(f"Using OpenAI (completion) for model: {model_name}")
    logging.info(f"Extra body to pass to completions: {extra_body}")

    api_key = get_environment_variable("OPENAI_API_KEY", model_name)
    base_url = get_environment_variable("OPENAI_BASE_URL", model_name)
    llm = OpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        extra_body=process_extra_body(extra_body),
    )

    return llm
