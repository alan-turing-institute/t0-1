import logging

import ollama


# basic function to prompt the model
def get_response_from_ollama_model(prompt: str, model: str = "gemma3:1b"):
    """
    Get the response from the Ollama model.

    Parameters
    ----------
    prompt : str
        The prompt to send to the model.
    model : str, optional
        The ollama model to use, by default "gemma3:1b"

    Returns
    -------
    str
        The response from the model.
    """
    logging.getLogger(__name__)

    response = ollama.generate(model=model, prompt=prompt)
    try:
        return response["response"]
    except KeyError:
        logging.error(f"Model returned an invalid response: {response}")
        return None
