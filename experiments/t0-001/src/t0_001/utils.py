import logging
import os

from dotenv import load_dotenv


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
