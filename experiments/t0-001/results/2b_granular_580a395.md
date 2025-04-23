
## 2b_580a395.md split by query type

### all
| Embedding Method                        |   Supporting documents retrieved | Query Type   |   Condition skyline (p@k) | LLM          |   Conditions accuracy |   Severity accuracy |
|-----------------------------------------|----------------------------------|--------------|----------------------------|--------------|-----------------------|---------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          |                       0.69 | deepseek-r1  |                  0.42 |                0.43 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          |                       0.69 | o3-mini      |                  0.47 |                0.42 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          |                       0.69 | qwen2.5-1.5b |                  0.26 |                0.08 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          |                       0.69 | qwen2.5-32b  |                  0.42 |                0.41 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          |                       0.83 | deepseek-r1  |                  0.44 |                0.42 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          |                       0.83 | o3-mini      |                  0.48 |                0.46 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          |                       0.83 | qwen2.5-1.5b |                  0.16 |                0.05 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          |                       0.83 | qwen2.5-32b  |                  0.45 |                0.40 |

### cluster
| Embedding Method                        |   Supporting documents retrieved | Query Type   |   Condition skyline (p@k) | LLM          |   Conditions accuracy |   Severity accuracy |
|-----------------------------------------|----------------------------------|--------------|----------------------------|--------------|-----------------------|---------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      |                       0.66 | deepseek-r1  |                  0.39 |                0.46 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      |                       0.66 | o3-mini      |                  0.43 |                0.52 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      |                       0.66 | qwen2.5-1.5b |                  0.23 |                0.05 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      |                       0.66 | qwen2.5-32b  |                  0.39 |                0.48 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      |                       0.82 | deepseek-r1  |                  0.40 |                0.47 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      |                       0.81 | o3-mini      |                  0.46 |                0.58 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      |                       0.82 | qwen2.5-1.5b |                  0.16 |                0.04 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      |                       0.82 | qwen2.5-32b  |                  0.41 |                0.44 |

### vague
| Embedding Method                        |   Supporting documents retrieved | Query Type   |   Condition skyline (p@k) | LLM          |   Conditions accuracy |   Severity accuracy |
|-----------------------------------------|----------------------------------|--------------|----------------------------|--------------|-----------------------|---------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        |                       0.61 | deepseek-r1  |                  0.34 |                0.40 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        |                       0.61 | o3-mini      |                  0.44 |                0.35 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        |                       0.61 | qwen2.5-1.5b |                  0.21 |                0.09 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        |                       0.61 | qwen2.5-32b  |                  0.37 |                0.34 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        |                       0.73 | deepseek-r1  |                  0.39 |                0.37 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        |                       0.73 | o3-mini      |                  0.44 |                0.39 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        |                       0.73 | qwen2.5-1.5b |                  0.10 |                0.03 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        |                       0.73 | qwen2.5-32b  |                  0.42 |                0.35 |

### hypochondriac
| Embedding Method                        |   Supporting documents retrieved | Query Type    |   Condition skyline (p@k) | LLM          |   Conditions accuracy |   Severity accuracy |
|-----------------------------------------|----------------------------------|---------------|----------------------------|--------------|-----------------------|---------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac |                       0.88 | deepseek-r1  |                  0.52 |                0.47 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac |                       0.88 | o3-mini      |                  0.58 |                0.44 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac |                       0.88 | qwen2.5-1.5b |                  0.40 |                0.13 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac |                       0.88 | qwen2.5-32b  |                  0.49 |                0.39 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac |                       0.95 | deepseek-r1  |                  0.52 |                0.42 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac |                       0.95 | o3-mini      |                  0.56 |                0.45 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac |                       0.95 | qwen2.5-1.5b |                  0.24 |                0.07 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac |                       0.95 | qwen2.5-32b  |                  0.49 |                0.41 |

### basic
| Embedding Method                        |   Supporting documents retrieved | Query Type   |   Condition skyline (p@k) | LLM          |   Conditions accuracy |   Severity accuracy |
|-----------------------------------------|----------------------------------|--------------|----------------------------|--------------|-----------------------|---------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        |                       0.72 | deepseek-r1  |                  0.51 |                0.49 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        |                       0.72 | o3-mini      |                  0.52 |                0.52 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        |                       0.72 | qwen2.5-1.5b |                  0.29 |                0.07 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        |                       0.72 | qwen2.5-32b  |                  0.48 |                0.52 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        |                       0.86 | deepseek-r1  |                  0.51 |                0.51 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        |                       0.86 | o3-mini      |                  0.54 |                0.58 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        |                       0.86 | qwen2.5-1.5b |                  0.18 |                0.08 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        |                       0.86 | qwen2.5-32b  |                  0.51 |                0.52 |

### downplay
| Embedding Method                        |   Supporting documents retrieved | Query Type   |   Condition skyline (p@k) | LLM          |   Conditions accuracy |   Severity accuracy |
|-----------------------------------------|----------------------------------|--------------|----------------------------|--------------|-----------------------|---------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     |                       0.63 | deepseek-r1  |                  0.36 |                0.35 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     |                       0.63 | o3-mini      |                  0.40 |                0.31 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     |                       0.63 | qwen2.5-1.5b |                  0.16 |                0.07 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     |                       0.63 | qwen2.5-32b  |                  0.38 |                0.32 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     |                       0.80 | deepseek-r1  |                  0.40 |                0.35 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     |                       0.80 | o3-mini      |                  0.44 |                0.31 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     |                       0.80 | qwen2.5-1.5b |                  0.12 |                0.05 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     |                       0.80 | qwen2.5-32b  |                  0.42 |                0.32 |
