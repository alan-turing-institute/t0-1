"""Split a local HuggingFace dataset into train/test splits.

Usage:
    python split_dataset.py /path/to/local/dataset [--test-size 0.1] [--seed 42]
"""

import argparse
import pathlib
from datasets import load_from_disk

parser = argparse.ArgumentParser(description="Split a local HuggingFace dataset into train/test splits")
parser.add_argument("dataset_path", type=pathlib.Path,  help="Local path to the HuggingFace dataset directory")
parser.add_argument("--test-size", type=float, default=0.1, help="Fraction of data for test split (default: 0.1)")
parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
args = parser.parse_args()

ds = load_from_disk(args.dataset_path)
print(f"Loaded dataset from {str(args.dataset_path)}")
print(f"Current splits: {list(ds.keys())}")
print(f"Train size: {len(ds['train'])}")

split = ds["train"].train_test_split(test_size=args.test_size, seed=args.seed)
print(f"\nAfter split:")
print(f"  Train: {len(split['train'])}")
print(f"  Test:  {len(split['test'])}")

save_path = args.dataset_path.resolve().parent / pathlib.Path(f"split_{args.dataset_path.resolve().name}")
split.save_to_disk(save_path)
print(f"\nSaved to {save_path}")
