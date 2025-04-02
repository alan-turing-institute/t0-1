import json
import os
import random
import re
import pathlib

import tqdm
from bs4 import BeautifulSoup

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage


def set_up_client():
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


def get_response_from_model(client, user_prompt):
    response = client.complete(
        messages=[
            UserMessage(content=user_prompt)
        ],
    )
    return response["choices"][0]["message"]["content"]


def fill_template(template, data):
    # Replace the placeholders in the template with the data
    for key, value in data.items():
        # Remove spaces from the placeholders
        template = template.replace(f"{{{key}}}", str(value))
    return template


def generate_synthetic_requests(
    n_requests=10, 
    template_path="../../templates/synthetic_data.txt",
    save_path="../../data/synthetic_requests/",
    conditions_path="./nhs-use-case/conditions/",
    ):

    """Generate synthetic requests for the NHS use case using the OpenAI API (GPT-4o).

    Args:
        n_requests (int): Number of requests to generate. Default is 10.
        template_path (str): Path to the template file. Default is "../../templates/synthetic_data.txt".
        save_path (str): Path to save the generated requests. Default is "../../data/synthetic_requests/".
        conditions_path (str): Path to the NHS conditions folder. Default is "./nhs-use-case/conditions/".
    """
    # define template path relative to this file
    with open(template_path, "r") as f:
        template = f.read()

    # define jsonl file
    model = "gpt-4o"
    save_path = save_path
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    filename = f"{model}_{n_requests}_synthetic_requests.jsonl"

    # write the jsonl file
    with open(os.path.join(save_path, filename), "w") as f:
        for _ in tqdm.tqdm(range(n_requests)):
            # random pick
            request_type = random.choice(
                ["basic", "cluster", "hypochondriac", "unspecified"]
            )
            severity_level = random.choice(
                ["Not urgent", "Medium", "Medium urgent", "Urgent"]
            )

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
                "request_type": request_type,
                "severity_level": severity_level,
                "conditions_content": conditions_content,
                "conditions_title": selected_condition,
            }

            prompt = fill_template(template, data)

            # Get the response from the model
            client = set_up_client()
            response = get_response_from_model(client=client, user_prompt=prompt)

            try:
                # just a bit of cleaning up of the response
                response = re.sub(r"^```json\s*|\s*```$", "", response).strip()
                json_object = json.loads(response)
                if (
                    "general_demographics" in json_object
                    and "symptoms_description" in json_object
                ):
                    json_object["request_type"] = request_type
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
    generate_synthetic_requests()