import argparse
import datetime
import json
import os

from dotenv import load_dotenv
from t0_001.llm.client import get_azure_client
from t0_001.llm.reasoner import (
    CONDITION,
    SEVERITY_LEVEL,
    UNSURE,
    generate_recommendation,
)
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate the RAG system with a basic reasoner on top."
    )
    parser.add_argument(
        "--rag-output",
        type=str,
        default="results_2025-04-04_11-08-43.jsonl",
        help="The output of the RAG system. Should be stored under $T0_DATA_FOLDER/evaluation/rag.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="4o",
        help="The model to use for the reasoner.",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default="evaluation/reasoning",
        help="The output folder for the results within the $T0_DATA_FOLDER directory.",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()
    DATA = os.environ["T0_DATA_FOLDER"]
    # given the output of our RAG system
    with open(f"{DATA}/evaluation/rag/{args.rag_output}", "r") as file:
        data = [json.loads(line) for line in file]
    # Create output with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_fp = os.path.join(
        DATA, args.output_folder, f"{args.model}_{timestamp}.jsonl"
    )
    os.makedirs(os.path.dirname(output_fp), exist_ok=True)
    client = get_azure_client(model=args.model, use_async=False)

    ground_truths = []
    recommendations = []
    for patient_json in tqdm(data):
        severity_level = patient_json[SEVERITY_LEVEL]
        condition = patient_json["conditions_title"]
        ground_truth = {SEVERITY_LEVEL: severity_level, CONDITION: condition}
        ground_truths.append(ground_truth)
        # Handle API errors - e.g. refusals.
        try:
            recommendation = generate_recommendation(client, patient_json)
        except Exception as e:
            print(f"Error generating recommendation: {e} for condition {condition}")
            recommendation = {
                SEVERITY_LEVEL: "error",
                CONDITION: "error",
            }
        recommendations.append(recommendation)
        # Save the recommendation to the output file
        with open(output_fp, "a") as f:
            f.write(json.dumps(recommendation) + "\n")

    correct = 0
    unsure = 0
    total = 0
    for gt, rec in zip(ground_truths, recommendations):
        correct += gt[CONDITION] == rec[CONDITION]
        unsure += UNSURE in rec[CONDITION].lower()
        total += 1

    print(f"Correct: {correct}")
    print(f"Unsure: {unsure}")
    print(f"Total: {total}")
    print(f"Accuracy: {correct / total}")


if __name__ == "__main__":
    main()
