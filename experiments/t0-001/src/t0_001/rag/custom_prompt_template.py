import logging
import os
from pathlib import Path

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)


def read_prompt_template(
    prompt_template_path: str | Path, system_prompt_path: str | Path | None = None
) -> ChatPromptTemplate:
    """
    Read a prompt template from a file and return it as a ChatPromptTemplate.

    Parameters
    ----------
    prompt_template_path : str | Path
        The path to the prompt template file.
    system_prompt_path : str | Path | None
        The path to the system prompt file. If None, no system prompt is passed.
        If provided, it will be read and included in the prompt template.
        Default is None.

    Returns
    -------
    ChatPromptTemplate
        The prompt template.
    """
    if not os.path.exists(prompt_template_path):
        raise FileNotFoundError(
            f"Prompt template file {prompt_template_path} does not exist."
        )

    if system_prompt_path:
        if not os.path.exists(system_prompt_path):
            raise FileNotFoundError(
                f"System prompt file {system_prompt_path} does not exist."
            )

        logging.info(f"Reading system prompt from {system_prompt_path}...")
        with open(system_prompt_path, "r") as f:
            system_template = f.read()

    logging.info(f"Reading prompt template from {prompt_template_path}...")
    with open(prompt_template_path, "r") as f:
        template = f.read()

    prompt_template = PromptTemplate.from_template(template)
    message = HumanMessagePromptTemplate(prompt=prompt_template)

    if system_prompt_path:
        from langchain_core.messages import SystemMessage

        system_message = SystemMessage(content=system_template)
        messages = [system_message, message]
    else:
        messages = [message]

    return ChatPromptTemplate.from_messages(messages)
