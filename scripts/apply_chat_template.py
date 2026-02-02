"""Apply chat templates to reasoning traces and answers for use with the s1k pipeline.

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
SYSTEM_PROMPT = "system_prompt"


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
    dataset = [i for i in dataset if "error" not in i]

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


_warned_model_families: set[str] = set()


def _format_thinking_content(reasoning_trace: str, answer: str, model_name: str) -> str:
    """Format the assistant's thinking and answer content for a given model family."""
    model_lower = model_name.lower()
    if "qwen" in model_lower:
        return (
            "<|im_start|>think\n"
            + reasoning_trace
            + "\n<|im_start|>answer\n"
            + answer
        )
    elif "gemma" in model_lower:
        return "<think>\n" + reasoning_trace + "\n</think>\n" + answer
    else:
        # Default: use generic <think> tags (works for most models)
        if model_name not in _warned_model_families:
            _warned_model_families.add(model_name)
            logger.warning(
                f"Unknown model family '{model_name}'. Using generic <think> tags. "
                "If this model requires specific thinking tokens, please add support."
            )
        return "<think>\n" + reasoning_trace + "\n</think>\n" + answer


def process_cot_example(
    example: Dict,
    tokenizer,
    model_name: str,
):
    # Handle both list format (old) and separate fields (new)
    if isinstance(example[PROMPT], list):
        # Old format: rag_message is [system_prompt, user_prompt]
        system_prompt = example[PROMPT][0]
        user_prompt = example[PROMPT][1]
    else:
        # New format: system_prompt is separate, rag_message is just user prompt
        system_prompt = example.get(SYSTEM_PROMPT, "")
        user_prompt = example[PROMPT]

    model_output = example[RESPONSE]

    # Prefer native reasoning_content if available (e.g. gpt-oss-120b)
    reasoning_content = example.get("rag_reasoning_content")
    if reasoning_content and reasoning_content != "None":
        reasoning_trace = reasoning_content.strip()
        answer = model_output.strip()
        if not answer:
            condition = example.get("conditions_title", "unknown")
            logger.warning(
                f"Skipping example with empty answer for {condition=} (native reasoning)."
            )
            return
        if not reasoning_trace:
            condition = example.get("conditions_title", "unknown")
            logger.warning(
                f"Skipping example with empty reasoning for {condition=} (native reasoning)."
            )
            return
    else:
        # Fallback: parse <think> tags from content (DeepSeek-R1, older data)
        regex_match = re.match(r"<think>(.*?)</think>\s*(.*)", model_output, re.DOTALL)

        if not regex_match:
            condition = example["conditions_title"]
            logger.warning(
                f"Failed to extract reasoning trace and output for example of {condition=}."
            )
            return
        reasoning_trace = regex_match.group(1).strip()
        answer = regex_match.group(2).strip()

    assistant_content = _format_thinking_content(reasoning_trace, answer, model_name)

    messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assistant_content},
    ]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
    )
    # Strip leading BOS token — the training tokenizer adds it automatically
    if tokenizer.bos_token and text.startswith(tokenizer.bos_token):
        text = text[len(tokenizer.bos_token):]
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
    process_example_map = partial(process_cot_example, tokenizer=tokenizer, model_name=model_name)
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
    parser = argparse.ArgumentParser(description="Apply chat templates to SFT data")
    parser.add_argument(
        "--input-path",
        type=str,
        help="Path to the downloaded data",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Path to upload the processed data. Can be a Hugging Face Hub path (e.g., hf://<path>) or a local path.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="Qwen/Qwen2.5-32B-Instruct",
        help="Model name or path for the tokenizer and chat template (default: Qwen/Qwen2.5-32B-Instruct)",
    )
    parser.add_argument(
        "--num_proc",
        type=int,
        default=DEFAULT_NUM_PROC,
        help="Number of processes to use",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    load_dotenv()
    process_for_sft(
        input_path=args.input_path,
        output_path=args.output_path,
        model_name=args.model_name,
        num_proc=args.num_proc,
    )


if __name__ == "__main__":
    main()
