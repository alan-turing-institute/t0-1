import pandas as pd
from datasets import load_dataset


def explore_s1k():
    df1 = pd.read_parquet(  # noqa: F841
        "hf://datasets/simplescaling/s1K/data/train-00000-of-00001.parquet"
    )
    df2 = pd.read_parquet(
        "hf://datasets/simplescaling/s1K-1.1/data/train-00000-of-00001.parquet"
    )
    df = df2
    print(df.head())
    print(df.columns)
    row = df.iloc[0]
    print(row)
    for col in df.columns:
        print("COLUMN")
        print(col)
        print("DATA")
        print(row[col])
        print()
    print(df.columns)


def main():
    questions = load_dataset("qfq/train_rawcot_summarized_irsub")["train"]["question"]
    idx = 10
    print(questions[idx])


if __name__ == "__main__":
    main()
