import json
import os

from azure.ai.inference.models import UserMessage
from dotenv import load_dotenv
from tqdm import tqdm

from t0.llm.client import get_azure_client
from t0.utils import load_conditions


def create_summary(client, document):
    response = client.complete(
        messages=[
            UserMessage(
                content=f"Generate a summary for the following health condition document: {document}.",
            )
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "create_summary",
                    "description": "Generate a summary for the health condition of page.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the condition or procedure",
                            },
                            "summary": {"type": "string"},
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords related to the condition such as symptoms, causes, and treatments.",
                            },
                        },
                        "required": ["title", "summary", "keywords"],
                    },
                },
            }
        ],
        tool_choice="required",
    )
    return response


def main():
    load_dotenv()
    client = get_azure_client(model="4o")

    conditions_folder = os.path.join(os.environ["T0_DATA_FOLDER"], "conditions")
    html_folder = os.path.join(conditions_folder, "html")
    parsed_folder = os.path.join(conditions_folder, "parsed")
    os.makedirs(parsed_folder, exist_ok=True)
    conditions = load_conditions(html_folder, max_conditions=None)
    for name_raw, content in tqdm(conditions.items()):
        response = create_summary(client, content)
        page_json = json.loads(
            response.choices[0].message.tool_calls[0].function.arguments
        )
        page_json["name_raw"] = name_raw
        page_json["content"] = content
        output_fp = os.path.join(parsed_folder, f"{name_raw}.json")
        with open(output_fp, "w") as f:
            json.dump(page_json, f, indent=4)


if __name__ == "__main__":
    main()
