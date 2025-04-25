"""Tokenize reasoning traces and answers for use with the s1k pipeline.

Adapted from: https://github.com/simplescaling/s1/blob/main/data/tokenization.py
"""

import argparse
import json
import logging
import multiprocessing
import os
import re
import tempfile
from functools import partial
from pathlib import Path
from typing import Dict

import datasets
import pandas as pd
from datasets import DatasetDict, load_dataset, load_from_disk
from dotenv import load_dotenv
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

DEFAULT_NUM_PROC = multiprocessing.cpu_count() - 1

# TODO: Standardise upstream export of prompts, reasoning traces and answers.
PROMPT = "rag_message"
RESPONSE = "rag_answer"


def stringify_all_values(obj):
    """Recursively convert all values in a dictionary or list to strings."""
    if isinstance(obj, dict):
        return {k: stringify_all_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [stringify_all_values(item) for item in obj]
    else:
        return str(obj) if obj is not None else None


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

    with open(input_file, "r", encoding="utf-8") as f:
        data = [stringify_all_values(dict(json.loads(line))) for line in f]

    return data


def load_hf_dataset(input_path: str | Path) -> datasets.DatasetDict:
    """Convert JSONL to Parquet and load as a Hugging Face dataset.

    Intermediate step converts mixed dtypes to strings.
    """
    if input_path.startswith("hf://"):
        input_path = input_path.replace("hf://", "")
        return load_dataset(input_path)
    dataset = read_jsonl(input_path)
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name + ".parquet"
        pd.DataFrame(dataset).to_parquet(tmp_file_path)
        return load_dataset("parquet", data_files=tmp_file_path)


def preprocess(text):
    if text is None:
        return " "
    text = text.strip()
    text = text.replace(" [title]", ". ")
    text = re.sub("\\[.*?\\]", "", text)
    text = text.replace("  ", " ")
    return text


def process_cot_example(
    example: Dict,
    tokenizer,
):
    system_prompt = example[PROMPT][0]
    user_prompt = example[PROMPT][1]
    model_output = example[RESPONSE]
    # Extract Deepseek-R1 reasoning trace and output.
    regex_match = re.match(r"<think>(.*?)</think>\s*(.*)", model_output, re.DOTALL)

    if not regex_match:
        condition = example["conditions_title"]
        logger.warning(
            f"Failed to extract reasoning trace and output for example of {condition=}."
        )
        return
    reasoning_trace = regex_match.group(1).strip()
    answer = regex_match.group(2).strip()

    text = tokenizer.apply_chat_template(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {
                "role": "assistant",
                "content": "<|im_start|>think\n"
                + reasoning_trace.strip()
                + "\n<|im_start|>answer\n"
                + answer.strip(),
            },
        ],
        tokenize=False,
    )
    return dict(text=text)


def process_for_sft(
    input_path: str,
    output_path: str,
    model_name: str = "Qwen/Qwen2.5-32B-Instruct",
    num_proc: int | None = None,
) -> None:
    # TODO: Fixed mixed types to enable direct load: load_dataset('json', data_files=input_path)["train"]
    dataset = load_hf_dataset(input_path)["train"]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    process_example_map = partial(process_cot_example, tokenizer=tokenizer)
    dataset = dataset.map(
        process_example_map,
        num_proc=num_proc,
        desc="Tokenizing SFT data",
    )
    # Save tokenized dataset and reload to verify.
    if output_path.startswith("hf://"):
        output_path = output_path.replace("hf://", "")
        dataset.push_to_hub(output_path)
        load_dataset(output_path, split="train")
    else:
        dataset_dict = DatasetDict({"train": dataset})
        dataset_dict.save_to_disk(output_path)
        load_from_disk(output_path)


def parse_args():
    parser = argparse.ArgumentParser(description="Tokenize SFT data")
    parser.add_argument(
        "--input-path",
        type=str,
        help="Path to the downloaded data",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Path to upload the tokenized data. Can be a Hugging Face Hub path (e.g., hf://<path>) or a local path.",
    )
    parser.add_argument(
        "--num_proc",
        type=int,
        default=DEFAULT_NUM_PROC,
        help="Number of processes to use for tokenization",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    load_dotenv()
    process_for_sft(
        input_path=args.input_path,
        output_path=args.output_path,
        num_proc=args.num_proc,
    )


if __name__ == "__main__":
    main()
