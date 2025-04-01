import json
import os
import random
import re

import ollama
import tqdm
from bs4 import BeautifulSoup


# basic function to prompt the model
def get_response_from_model(prompt, model="gemma3:1b"):
    response = ollama.generate(model=model, prompt=prompt)
    return response["response"]


template = open("../../templates/synthetic_data.txt", "r").read()


def fill_template(template, data):
    # Replace the placeholders in the template with the data
    for key, value in data.items():
        # Remove spaces from the placeholders
        template = template.replace(f"{{{key}}}", str(value))
    return template


# write jsonl file
model = "gemma3:1b"
n_requests = 10
location = "../../data/synthetic_requests/"
if not os.path.exists(location):
    os.makedirs(location)
filename = f"{model}_{n_requests}_synthetic_requests.jsonl"


with open(os.path.join(location, filename), "w") as f:
    for i in tqdm.tqdm(range(n_requests)):
        # random pick
        request_type = random.choice(
            ["basic", "cluster", "hypochondriac", "unspecified"]
        )
        severity_level = random.choice(
            ["Not urgent", "Medium", "Medium urgent", "Urgent"]
        )

        conditions_folder = (
            "../../../../use-cases/nhs-conditions/nhs-use-case/conditions/"
        )

        # loop a few times and pick something meaningful for now (some "conditions" are not really conditions!)
        selected_condition = random.choice(os.listdir(conditions_folder))
        content = open(
            os.path.join(conditions_folder, selected_condition, "index.html"), "r"
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
        response = get_response_from_model(prompt, model=model)
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
