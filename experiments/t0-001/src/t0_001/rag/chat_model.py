import logging

from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint,
    HuggingFacePipeline,
)


def get_huggingface_chat_model(
    method: str, model_name: str, task: str = "text-generation", **kwargs
) -> ChatHuggingFace:
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
    if method == "pipeline":
        logging.info(f"Using HuggingFace pipeline for model: {model_name}")
        logging.info("Loading language model...")
        llm = HuggingFacePipeline.from_model_id(
            model_id=model_name,
            task=task,
            pipeline_kwargs={
                "max_new_tokens": 512,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False,
            }
            | kwargs,
        )
    elif method == "endpoint":
        logging.info(f"Using HuggingFace endpoint for model: {model_name}")
        llm = HuggingFaceEndpoint(repo_id=model_name, task=task, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'pipeline' or 'endpoint'.")

    return ChatHuggingFace(llm=llm)
