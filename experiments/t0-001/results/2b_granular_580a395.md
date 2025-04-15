| Embedding Method                        |   Supporting documents retrieved | Query Type    |   Condition baseline (p@1) | LLM          |   Conditions accuracy |   Severity accuracy |
|:----------------------------------------|---------------------------------:|:--------------|---------------------------:|:-------------|----------------------:|--------------------:|
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster       |                   0.82266  | qwen2.5-1.5b |             0.162562  |           0.044335  |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague         |                   0.731092 | qwen2.5-1.5b |             0.0966387 |           0.0336134 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac |                   0.948187 | qwen2.5-1.5b |             0.243523  |           0.0725389 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic         |                   0.864706 | qwen2.5-1.5b |             0.182353  |           0.0764706 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay      |                   0.80102  | qwen2.5-1.5b |             0.122449  |           0.0459184 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster       |                   0.660099 | qwen2.5-1.5b |             0.231527  |           0.0492611 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague         |                   0.609244 | qwen2.5-1.5b |             0.205882  |           0.092437  |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac |                   0.875648 | qwen2.5-1.5b |             0.404145  |           0.134715  |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic         |                   0.723529 | qwen2.5-1.5b |             0.294118  |           0.0705882 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay      |                   0.627551 | qwen2.5-1.5b |             0.163265  |           0.0663265 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster       |                   0.655172 | qwen2.5-32b  |             0.394089  |           0.482759  |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague         |                   0.613445 | qwen2.5-32b  |             0.37395   |           0.344538  |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac |                   0.875648 | qwen2.5-32b  |             0.492228  |           0.393782  |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic         |                   0.723529 | qwen2.5-32b  |             0.482353  |           0.523529  |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay      |                   0.627551 | qwen2.5-32b  |             0.377551  |           0.321429  |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster       |                   0.82266  | qwen2.5-32b  |             0.413793  |           0.438424  |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague         |                   0.731092 | qwen2.5-32b  |             0.415966  |           0.352941  |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac |                   0.948187 | qwen2.5-32b  |             0.492228  |           0.414508  |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic         |                   0.864706 | qwen2.5-32b  |             0.505882  |           0.523529  |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay      |                   0.80102  | qwen2.5-32b  |             0.418367  |           0.316327  |
