import pandas as pd

# load data
one_k = pd.read_json(
    "./data/synthetic_queries/5bb7345_gpt-4o_1000_synthetic_queries.jsonl", lines=True
)
two_k = pd.read_json(
    "./data/synthetic_queries/5bb7345_gpt-4o_2000_synthetic_queries.jsonl", lines=True
)
extra = pd.read_json(
    "./data/synthetic_queries/5bb7345_gpt-4o_517_synthetic_queries.jsonl", lines=True
)

# create combination column that combines severity_level and conditions_title
one_k["combination"] = one_k["severity_level"] + ", " + one_k["conditions_title"]
two_k["combination"] = two_k["severity_level"] + ", " + two_k["conditions_title"]
extra["combination"] = extra["severity_level"] + ", " + extra["conditions_title"]

# create sets from unique combinations
one_k_combinations = set(one_k["combination"].unique())
two_k_combinations = set(two_k["combination"].unique())
extra_combinations = set(extra["combination"].unique())

# find common combinations between one_k and two_k
common_combinations = set.intersection(one_k_combinations, two_k_combinations)
print(f"Number of common combinations: {len(common_combinations)}")

# remove common combinations from two_k so its disjoint from one_k
two_k_unique = two_k[~two_k["combination"].isin(common_combinations)]
print(f"Number of unique combinations in two_k: {len(two_k_unique)}")

# also remove common combinations from extra
extra_unique = extra[~extra["combination"].isin(common_combinations)]

# add extra_unique to two_k_unique to get back to 2000 queries
two_k_final = pd.concat([two_k_unique, extra_unique], ignore_index=True).reset_index(
    drop=True
)[:2000]
two_k_final = two_k_final.drop(columns=["combination"])
print(f"Number of combinations in two_k_final: {len(two_k_final)}")

# save to jsonl
two_k_final.to_json(
    "./data/synthetic_queries/5bb7345_gpt-4o_2000_synthetic_queries_cleaned.jsonl",
    orient="records",
    lines=True,
)
