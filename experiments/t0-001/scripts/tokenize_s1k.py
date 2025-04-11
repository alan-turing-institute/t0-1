"""Tokenize reasoning traces and answers for use with the s1k pipeline.

Adapted from: https://github.com/simplescaling/s1/blob/main/data/tokenization.py
"""

import argparse
import multiprocessing
import re
from functools import partial
from typing import Dict

from datasets import load_dataset
from transformers import AutoTokenizer

DEFAULT_NUM_PROC = multiprocessing.cpu_count() - 1


QUERY_TEMPLATE_NOANSWER = """{Question}""".strip()


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
    thinking_trajectory = example["thinking_trajectories"]
    question = example["question"]
    answer = example["attempt"]
    prompt = QUERY_TEMPLATE_NOANSWER.format(Question=question)
    answer = "Answer: " + answer if "Answer:" not in answer else answer
    text = tokenizer.apply_chat_template(
        [
            {"role": "user", "content": prompt},
            {
                "role": "assistant",
                "content": "<|im_start|>think\n"
                + "\n".join(thinking_trajectory).strip()
                + "\n<|im_start|>answer\n"
                + answer.strip(),
            },
        ],
        tokenize=False,
    )
    return dict(text=text)


def process_for_sft(
    download_data_path: str,
    model_name: str = "Qwen/Qwen2.5-32B-Instruct",
    num_proc: int | None = None,
):
    dataset = load_dataset(download_data_path, download_mode="force_redownload")
    if "train" in dataset:
        dataset = dataset["train"]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    process_example_map = partial(process_cot_example, tokenizer=tokenizer)
    dataset = dataset.map(
        process_example_map,
        num_proc=num_proc,
        desc="Tokenizing SFT data",
    )
    return dataset


def parse_args():
    parser = argparse.ArgumentParser(description="Tokenize SFT data")
    parser.add_argument(
        "--input-path",
        type=str,
        default="simplescaling/s1K",
        help="Path to the downloaded data",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=False,
        help="Path to upload the tokenized data",
    )
    parser.add_argument(
        "--num_proc",
        type=int,
        default=DEFAULT_NUM_PROC,
        help="Number of processes to use for tokenization",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    process_for_sft(
        download_data_path=args.input_path,
        # upload_data_path="simplescaling/s1K_tokenized",
        num_proc=args.num_proc,
    )
