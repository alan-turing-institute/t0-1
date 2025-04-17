import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
logging.basicConfig(level=logging.INFO)
from google import genai
from datasets import load_dataset, Dataset
from concurrent.futures import ProcessPoolExecutor
import time
from glob import glob
import random
from functools import partial
from tqdm import tqdm

from utils.io_utils import question_hash, jdump, jload

def gemini_qa(prompt: str):
    max_attempts = 1000
    answer = None 
    attempts = 0
    while answer is None and attempts < max_attempts:
        try:
            client = genai.Client(api_key="YOUR_API_KEY")
            response = client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp",
                contents=prompt
            )
            thinking = response.candidates[0].content.parts[0].text
            answer = response.candidates[0].content.parts[1].text
            attempts += 1
        except Exception as e:
            print(f"Exception: {str(e)}")
            time.sleep(60)
    return thinking, answer

def process_question(question: str, subdir: str):
    qhash = question_hash(question)
    logging.info(f"Processing question {qhash}")
    thinking, response = gemini_qa(question)
    result = dict(question_hash=qhash,
                question=question,
                thinking=thinking,
                response=response)
    jdump(result, f"results/gemini/{subdir}/{qhash}.json")
    logging.info(f"Processed question {qhash}")

def generate_gemini1k():
    questions = load_dataset("qfq/train_rawcot_summarized_irsub")['train']['question']
    existing_json = glob(f"results/gemini/gemini1k/*.json")
    existing_qhash_list = [jsonpath.split('/')[-1].split('.')[0] for jsonpath in existing_json]
    questions = [question for question in questions if question_hash(question) not in existing_qhash_list]
    process_map = partial(process_question, subdir="gemini1k")
    with ProcessPoolExecutor() as executor:
        executor.map(process_map, questions)

def generate_gemini():
    questions = load_dataset("qfq/train")['train']['question']
    random.shuffle(questions)
    logging.info(f"Processing {len(questions)} total questions")
    subdir = "geminiall"
    existing_json = glob(f"results/gemini/{subdir}/*.json")
    existing_qhash_list = [jsonpath.split('/')[-1].split('.')[0] for jsonpath in existing_json]
    logging.info(f"Found {len(existing_qhash_list)} existing questions")
    questions = [question for question in questions if question_hash(question) not in existing_qhash_list]
    logging.info(f"{len(questions)} questions left after filtering existing question hashes")
    process_map = partial(process_question, subdir=subdir)
    with ProcessPoolExecutor() as executor:
        executor.map(process_map, questions)

def upload_gemini():
    jsons = glob("results/gemini/geminiall/*.json")
    all_train = load_dataset("qfq/train")['train']
    all_train_dict= {}
    for example in tqdm(all_train):
        all_train_dict[question_hash(example['question'])] = example
    results = []
    for json_path in tqdm(jsons):
        qdict = jload(json_path)
        qhash = qdict['question_hash']
        if qhash in all_train_dict:
            all_train_example = all_train_dict[qhash]
            all_train_example['thinking_trajectories'] = [qdict['thinking']]
            all_train_example['attempt'] = qdict['response']
            results.append(all_train_example)
    dataset = Dataset.from_list(results)
    dataset.push_to_hub("qfq/geminiall")

if __name__ == "__main__":
    generate_gemini()
    upload_gemini()