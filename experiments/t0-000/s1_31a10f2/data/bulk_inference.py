import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, Sequence
from vllm import LLM, SamplingParams
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, HfArgumentParser
from tqdm import tqdm
from glob import glob
from dataclasses import dataclass, field, asdict
import time

from data.utils.io_utils import question_hash, jdump, jload


@dataclass
class DataModuleConfigs:
    model_name: str = field(default="Qwen/Qwen2.5-32B-Instruct", metadata={'help': 'Model name'})
    shard_index: int = field(default=0, metadata={'help': 'Shard index'})

def shard_question(chunk_size: int=10_000):
    questions = load_dataset("qfq/train")['train']['question']
    for i in range(0, len(questions), chunk_size):
        shard = questions[i:i+chunk_size]
        jdump(shard,f"results/difficulty_classification/qwen32b_instruct_inference/shard_{i//chunk_size}_input.json")

def _qwen_forward(
    prompts: Sequence[str],
    model_name: str,
    tokenizer_path: str,
    max_length: int = 32768,
    temperature: float = 0.05,
) -> Optional[Sequence[str]]:
    sampling_params = SamplingParams(temperature=temperature,
                                     max_tokens=max_length)
    if "7B" in model_name:
        tensor_parallel_size = 1
    else:
        tensor_parallel_size = 2
    model = None
    while model is None:
        try:
            model = LLM(model=model_name,
                        tokenizer=tokenizer_path,
                        tensor_parallel_size=tensor_parallel_size)
        except Exception as e:
            print(f"Error loading model: {e}")
            time.sleep(10)
    outputs = model.generate(prompts=prompts,
                             sampling_params=sampling_params)
    result = []
    for output in outputs:
        result.append(output.outputs[0].text)
    return result
    
def difficulty_classification(shard_index: int, model_name: str):
    pretty_name = model_name.replace("/", "_").replace("-", "_").replace(".", "_")
    questions = jload(f"results/difficulty_classification/{pretty_name}/shard_{shard_index}_input.json")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    prompts = []
    for question in tqdm(questions):
        dialog = [{"role" : "user", "content": question}]
        prompts.append(f"{tokenizer.apply_chat_template(dialog, tokenize=False)}<|im_start|>assistant\n")
    results = _qwen_forward(prompts, model_name, model_name)
    result_dict = {}
    for question, result in zip(questions, results):
        result_dict[question_hash(question)] = result
    jdump(result_dict, f"results/difficulty_classification/{pretty_name}/shard_{shard_index}_output.json")

def assemble_output(model_name: str, upload: bool = False):
    pretty_name = model_name.replace("/", "_").replace("-", "_").replace(".", "_")
    output = {}
    for shard_index in range(7):
        output.update(jload(f"results/difficulty_classification/{pretty_name}/shard_{shard_index}_output.json"))
    dataset = load_dataset("qfq/train")['train']
    key_map_dataset = {}
    for example in tqdm(dataset, desc="Mapping dataset to hash"):
        key_map_dataset[question_hash(example['question'])] = example
    result = []
    for qhash, attempt in tqdm(output.items(), desc="Creating output json"):
        if qhash in key_map_dataset:
            example = dict(question=key_map_dataset[qhash]['question'],
                           solution=key_map_dataset[qhash]['solution'],
                           attempt=attempt)
            jdump(example, f"results/difficulty_classification/{pretty_name}/grading_input/{qhash}.json")
            result.append(example)
    if upload:
        new_dataset = []
        for example in dataset:
            example[pretty_name] = output[question_hash(example['question'])]
            new_dataset.append(example)
        new_dataset = Dataset.from_list(new_dataset)
        new_dataset.push_to_hub(f"qfq/train_{pretty_name}_inference")
    jdump(result, f"results/difficulty_classification/{pretty_name}/inference_output.json")

def assemble_output_gemini():
    jsons = glob("results/gemini/geminiall/*.json")
    dataset = load_dataset("qfq/train")['train']
    key_map_dataset = {}
    for example in tqdm(dataset, desc="Mapping dataset to hash"):
        key_map_dataset[question_hash(example['question'])] = example
    for json_path in tqdm(jsons, desc="Creating grading input"):
        qdict = jload(json_path)
        qhash = qdict['question_hash']
        if qhash in key_map_dataset:
            new_qdict = dict(question=qdict['question'],
                             solution=key_map_dataset[qhash]['solution'],
                             attempt=qdict['response'])
            jdump(new_qdict, f"results/difficulty_classification/gemini/grading_input/{qhash}.json")

if __name__ == "__main__":
    shard_question()
    parser = HfArgumentParser(DataModuleConfigs)
    difficulty_classification(**asdict(parser.parse_args_into_dataclasses()[0]))

    assemble_output("Qwen/Qwen2.5-7B-Instruct")
    assemble_output("Qwen/Qwen2.5-32B-Instruct")
    assemble_output_gemini()