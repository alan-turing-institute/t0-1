import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm


def load_env_file(env_file: str) -> bool:
    """
    Load environment variables from a .env file using
    dotenv.load_dotenv.

    Will log info if the file is loaded successfully and
    a warning if the file is not found.

    Parameters
    ----------
    env_file : str
        Path to the .env file to load

    Returns
    -------
    bool
        Returned from dotenv.load_dotenv
    """
    loaded = load_dotenv(env_file)
    if loaded:
        logging.info(f"Loaded environment variables from {env_file}")
    else:
        logging.warning(f"No environment file found at {env_file}")

    return loaded


def get_environment_variable(env_variable: str, model_name: str) -> str:
    """
    Get the value of an environment variable for a specific model.
    We first check if the environment variable with the model name identifier
    exists. If it does, we return the value of that environment variable.
    If it does not exist, we return the value of the environment variable
    without the model name identifier.
    If neither environment variables exist, we raise a KeyError.

    Parameters
    ----------
    env_variable : str
        The name of the environment variable to get
    model_name : str
        The name of the model to get the environment variable for

    Returns
    -------
    str
        The value of the environment variable for the specific model.
        If no model-specific environment variable exists, the value of the
        environment variable without the model name identifier is returned.
    """
    # use the model specific environment variables if they exist
    env_variable_with_idenfier = f"{env_variable}_{model_name}"

    if env_variable_with_idenfier in os.environ:
        logging.info(
            f"Using environment variable '{env_variable_with_idenfier}' for model '{model_name}'"
        )
        return os.environ[env_variable_with_idenfier]
    elif env_variable in os.environ:
        logging.info(
            f"Using environment variable '{env_variable}' for model '{model_name}'"
        )
        return os.environ[env_variable]
    else:
        raise KeyError(
            f"Neither '{env_variable}' nor '{env_variable_with_idenfier}' environment variable is set."
        )


def read_jsonl(input_file: str | Path) -> list[dict]:
    """
    Read a JSONL file and return a list of dictionaries.

    Parameters
    ----------
    input_file : str | Path
        The path to the JSONL file.

    Returns
    -------
    list[dict]
        A list of dictionaries representing the JSONL file.
    """
    if not str(input_file).endswith(".jsonl"):
        raise ValueError(f"File {input_file} is not a JSONL file.")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File {input_file} does not exist.")

    logging.info(f"Reading JSONL file: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        data = [dict(json.loads(line)) for line in tqdm(f, desc="Loading JSONL")]

    return data


def timestamp_file_name(file_name: str) -> str:
    """
    Add a timestamp to the file name.

    Parameters
    ----------
    file_name : str
        The original file name.

    Returns
    -------
    str
        The file name with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_name, ext = os.path.splitext(file_name)
    return f"{base_name}_{timestamp}{ext}"


def process_arg_to_dict(json_cli: dict | str | None) -> dict:
    """
    Process an argument that can be a dict, a string, or None and converts it to a dict.
    If the argument is a string, it tries to parse it as JSON and convert it to a dict.
    If the argument is None, it returns an empty dict.
    If the argument is already a dict, it returns it as is.

    Parameters
    ----------
    json_cli : dict | str | None
        The argument to process. Can be a dict, a string, or None.
        If it is a string, it should be a valid JSON string.
        If it is None, an empty dict will be returned.
        If it is a dict, it will be returned as is.

    Returns
    -------
    dict
        The processed argument as a dict.
    """
    if json_cli is None:
        json_cli = {}
    elif isinstance(json_cli, dict):
        json_cli = json_cli
    else:
        try:
            json_cli = dict(json.loads(json_cli))
        except Exception as e:
            logging.error(f"json_cli is not a valid json: {json_cli}")
            raise e
    
    return json_cli