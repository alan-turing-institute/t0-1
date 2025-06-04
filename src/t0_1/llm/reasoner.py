import json

from t0_1.llm.client import chat

CONDITION = "condition"
SEVERITY_LEVEL = "severity_level"
UNSURE = "inconclusive"

SYSTEM_PROMPT = """
"You are a clinical AI assistant.

You will be given a description of their symptms, information about the patient, and suggestions of possible conditions.

You need to suggest the most likely condition and the level of severity.

You should decide one of four options for severity:

### Severity Level:
* **Not urgent**: Monitor at home
* **Medium**: Go to the GP
* **Medium urgent**: Get an urgent GP appointment
* **Urgent**: Call 999

You should use the provided tool to submit the condition and severity level.

Importantly, if you think that the condition is not listed, please use "{UNSURE}" for the condition.
""".strip()


CONDITION_RECOMMENDATION_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_condition",
        "description": "Submit a condition recommendation and severity level.",
        "parameters": {
            "type": "object",
            "properties": {
                CONDITION: {
                    "type": "string",
                    "description": "Name of the condition or procedure",
                },
                SEVERITY_LEVEL: {
                    "type": "string",
                    "description": "Severity level of the condition",
                },
            },
            "required": [CONDITION, SEVERITY_LEVEL],
        },
    },
}


def generate_template(patient_json):
    demographics = patient_json["general_demographics"]
    symptoms = patient_json["symptoms_description"]
    doc_contents = patient_json["retrieved_documents"]
    doc_sources = patient_json["retrieved_documents_sources"]
    potential_condition_data = {x: [] for x in set(doc_sources)}

    for i in range(len(doc_sources)):
        potential_condition_data[doc_sources[i]].append((doc_contents[i]))

    return f"""
    A patient has given the following description of their symptoms: "{symptoms}".
    This is a summary of their demographics: {demographics}.

    Based on this information, our system suggests the patient might have one of the following conditions: {", ".join(set(potential_condition_data.keys()))}.

    For each potential condition, this is the most relevant information from the documents retrieved using RAG:

    {json.dumps(potential_condition_data, indent=2)}
    """


def generate_recommendation(client, patient_json) -> dict[str, str]:
    user_message = generate_template(patient_json)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    response = chat(
        client, messages, tools=[CONDITION_RECOMMENDATION_TOOL], tool_choice="required"
    )
    return json.loads(response.choices[0].message.tool_calls[0].function.arguments)
