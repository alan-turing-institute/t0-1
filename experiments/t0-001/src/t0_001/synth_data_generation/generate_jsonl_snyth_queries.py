import json
import logging
import os
import random
import re

import git
import tqdm
from t0_001.synth_data_generation.azure import (
    AZURE_OPENAI_ENDPOINTS,
    get_azure_openai_endpoint,
    get_azure_openai_key,
    get_response_from_azure_model,
    set_up_azure_client,
)
from t0_001.synth_data_generation.ollama import get_response_from_ollama_model


def fill_template(template, data):
    # Replace the placeholders in the template with the data
    for key, value in data.items():
        # Remove spaces from the placeholders
        template = template.replace(f"{{{key}}}", str(value))
    return template


def generate_synthetic_queries(
    n_queries=10,
    template_path="./templates/synthetic_data.txt",
    save_path="./data/synthetic_queries/",
    conditions_path="./data/nhs-conditions/conditions.jsonl",
    model="gpt-4o",
    overwrite=False,
):
    """Generate synthetic queries for the NHS use case and save them to a file.

    Parameters
    ----------
    n_queries : int, optional
        Number of queries to generate, by default 10
    template_path : str, optional
        The path to the synthetic data template, by default "./templates/synthetic_data.txt"
    save_path : str, optional
        The path to save the outputs, by default "./data/synthetic_queries/"
    conditions_path : str, optional
        The path the NHS conditions file, by default "./data/nhs-conditions/conditions.jsonl"
    model : str, optional
        The name of the model to use, by default "gpt-4o". If "gpt-4o" or "o3-mini", it uses the Azure OpenAI API. Otherwise, it uses the Ollama API.
    overwrite : bool, optional
        Whether to overwrite the existing file, by default False.
    """
    logging.getLogger(__name__)

    # define template path relative to this file
    with open(template_path, "r") as f:
        template = f.read()

    # define jsonl file
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # get the current git commit hash
    repo = git.Repo(search_parent_directories=True)
    commit_hash = repo.head.object.hexsha[:7]

    filename = f"{commit_hash}_{model}_{n_queries}_synthetic_queries.jsonl"

    if os.path.exists(os.path.join(save_path, filename)):
        if overwrite:
            logging.warning(
                f"File {os.path.join(save_path, filename)} already exists. Overwriting."
            )
        else:
            logging.error(f"File {os.path.join(save_path, filename)} already exists.")
            raise FileExistsError(
                f"File {os.path.join(save_path, filename)} already exists."
            )

    # write the jsonl file
    with open(os.path.join(save_path, filename), "w") as out:
        logging.info(f"Saving to {os.path.join(save_path, filename)}")
        i = 0
        progress_bar = tqdm.tqdm(total=n_queries)
        while i < n_queries:
            # random pick
            query_type = random.choice(["basic", "hypochondriac", "downplay"])
            severity_level = random.choice(
                [
                    "A&E",
                    "Urgent Primary Care",
                    "Routine GP appointment",
                    "Self-care",
                ]
            )
            sex = random.choice(["Male", "Female"])

            conditions = []
            with open(conditions_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    conditions.append(json.loads(line))

            # loop a few times and pick something meaningful for now (some "conditions" are not really conditions!)
            selected_condition = random.choice(conditions)

            data = {
                "query_type": query_type,
                "severity_level": severity_level,
                "conditions_content": selected_condition["condition_content"],
                "conditions_title": selected_condition["condition_title"],
                "sex": sex,
            }

            prompt = fill_template(template, data)

            # Get the response from the model
            if model in AZURE_OPENAI_ENDPOINTS:
                logging.info(f"Using {model} model via Azure OpenAI.")
                # set up the client
                endpoint = get_azure_openai_endpoint(model)
                key = get_azure_openai_key(model)
                client = set_up_azure_client(endpoint=endpoint, key=key)
                response = get_response_from_azure_model(client=client, prompt=prompt)
            else:
                # assume otherwise it's ollama
                logging.info(f"Using Ollama {model} model.")
                response = get_response_from_ollama_model(prompt=prompt, model=model)

            if response is None:
                print("Response is None. Skipping this response.")
                continue

            try:
                # just a bit of cleaning up of the response
                response = re.sub(r"^```json\s*|\s*```$", "", response).strip()
                json_object = json.loads(response)
                if (
                    "general_demographics" in json_object
                    and "symptoms_description" in json_object
                ):
                    json_object["query_type"] = query_type
                    json_object["severity_level"] = severity_level
                    json_object["conditions_title"] = selected_condition[
                        "condition_title"
                    ]

                    out.write(json.dumps(json_object) + "\n")

                    # update the progress
                    progress_bar.update(1)
                    i += 1
                else:
                    print(
                        "Response does not contain the expected keys. Skipping this response."
                    )
            except json.JSONDecodeError:
                print("Response is not a valid JSON. Skipping this response.")
            except Exception as e:
                print(f"An error occurred: {e}")
    out.close()


if __name__ == "__main__":
    generate_synthetic_queries()
