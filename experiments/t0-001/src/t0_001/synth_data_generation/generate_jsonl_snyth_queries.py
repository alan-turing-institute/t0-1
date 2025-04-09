import json
import logging
import os
import random
import re

import tqdm
from bs4 import BeautifulSoup
from t0_001.synth_data_generation.azure import (
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
    conditions_path="./nhs-use-case/conditions/",
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
        The path the NHS conditions data, by default "./nhs-use-case/conditions/"
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
    model = model
    save_path = save_path
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    filename = f"{model}_{n_queries}_synthetic_queries.jsonl"

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
    with open(os.path.join(save_path, filename), "w") as f:
        logging.info(f"Saving to {os.path.join(save_path, filename)}")
        for _ in tqdm.tqdm(range(n_queries)):
            # random pick
            query_type = random.choice(
                ["basic", "cluster", "hypochondriac", "vague", "downplay"]
            )
            severity_level = random.choice(
                [
                    "Ambulance",
                    "A&E",
                    "Urgent Primary Care",
                    "Routine GP appointment",
                    "Self-care",
                ]
            )
            sex = random.choice(["Male", "Female"])

            # loop a few times and pick something meaningful for now (some "conditions" are not really conditions!)
            selected_condition = random.choice(os.listdir(conditions_path))
            content = open(
                os.path.join(conditions_path, selected_condition, "index.html"), "r"
            ).read()
            soup = BeautifulSoup(content, "html.parser")
            # Extract the main element
            main_element = soup.find("main", class_="nhsuk-main-wrapper")

            # Extract the text from the main element
            conditions_content = main_element.get_text(separator="\n", strip=True)

            data = {
                "query_type": query_type,
                "severity_level": severity_level,
                "conditions_content": conditions_content,
                "conditions_title": selected_condition,
                "sex": sex,
            }

            prompt = fill_template(template, data)

            # Get the response from the model
            if model in {"gpt-4o", "o3-mini"}:
                logging.info(f"Using {model} model via Azure OpenAI.")
                client = set_up_azure_client()
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
                    json_object["conditions_title"] = selected_condition

                    f.write(json.dumps(json_object) + "\n")
                else:
                    print(
                        "Response does not contain the expected keys. Skipping this response."
                    )
            except json.JSONDecodeError:
                print("Response is not a valid JSON. Skipping this response.")
            except Exception as e:
                print(f"An error occurred: {e}")
    f.close()


if __name__ == "__main__":
    generate_synthetic_queries()
