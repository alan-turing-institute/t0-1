import os
import io
import json
from datasets import load_dataset, Dataset
import numpy as np
import os
from tqdm import tqdm
from hashlib import sha256

def set_openai_private_key():
    if "OPENAI_API_KEY" not in os.environ:
        with open('data/dataset/openai.key', 'r') as f:
            os.environ["OPENAI_API_KEY"] = f.read().strip()

def set_anthropic_private_key():
    if "ANTHROPIC_API_KEY" not in os.environ:
        with open('data/dataset/anthropic.key', 'r') as f:
            os.environ["ANTHROPIC_API_KEY"] = f.read().strip()

def set_genmini_private_key():
    if "GENMINI_API_KEY" not in os.environ:
        with open('data/dataset/genmini.key', 'r') as f:
            os.environ["GOOGLE_API_KEY"] = f.read().strip()

def _make_w_io_base(f, mode: str):
    if not isinstance(f, io.IOBase):
        f_dirname = os.path.dirname(f)
        if f_dirname != "":
            os.makedirs(f_dirname, exist_ok=True)
        f = open(f, mode=mode, encoding="utf-8")
    return f


def _make_r_io_base(f, mode: str):
    if not isinstance(f, io.IOBase):
        f = open(f, mode=mode, encoding="utf-8")
    return f


def jdump(obj, f: str, mode="w", indent=4, default=str):
    """Dump a str or dictionary to a file in json format.

    Args:
        obj: An object to be written.
        f: A string path to the location on disk.
        mode: Mode for opening the file.
        indent: Indent for storing json dictionaries.
        default: A function to handle non-serializable entries; defaults to `str`.
    """
    f = _make_w_io_base(f, mode)
    if isinstance(obj, (dict, list)):
        json.dump(obj, f, indent=indent, default=default)
    elif isinstance(obj, str):
        f.write(obj)
    else:
        raise ValueError(f"Unexpected type: {type(obj)}")
    f.close()


def jload_list(f, mode="r"):
    """Load multiple JSON objects from a file."""
    objects = []
    with open(f, mode) as file:
        for line in file:
            obj = json.loads(line)
            objects.append(obj)
    return objects

def jload(f, mode="r"):
    """Load a .json file into a dictionary."""
    f = _make_r_io_base(f, mode)
    jdict = json.load(f)
    f.close()
    return jdict

def tload(f, mode="r"):
    with open(f, mode) as file:
        output = file.read()
    return output

def upload_to_huggingface(cot_dataset_str: str, repo_name: str):
    # uploading to huggingface repo
    repo_name = f"qfq/{repo_name}"
    dataset = load_dataset("json", data_files=cot_dataset_str, encoding="utf-8")
    dataset.push_to_hub(repo_name)

def write_to_memmap(dset: Dataset, filename: str):
    dtype = np.int32
    arr_len = np.sum(dset['len'], dtype=np.uint64)
    print(f'Writing to {filename} with length {arr_len}')
    # Create dir if does not exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    arr = np.memmap(filename, dtype=dtype, mode='w+', shape=(arr_len,))
    total_batches = min(1024, len(dset))
    idx = 0
    for batch_idx in tqdm(range(total_batches), desc=f'writing {filename}'):
        # Batch together samples for faster write
        batch = dset.shard(num_shards=total_batches, index=batch_idx, contiguous=True).with_format('numpy')
        arr_batch = np.concatenate(batch['ids'])
        # Write into mmap
        arr[idx : idx + len(arr_batch)] = arr_batch
        idx += len(arr_batch)
        arr.flush()

def save_dataset(dataset: Dataset, filename: str):
    result = [example for example in dataset]
    jdump(result, filename)

def question_hash(question: str) -> str:
    return sha256(question.encode()).hexdigest()[:16]