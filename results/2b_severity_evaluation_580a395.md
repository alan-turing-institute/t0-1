
## 2b_580a395.md severity level evaluation

### all
#### deepseek-r1
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | deepseek-r1 | correct                   |     431 |    0.43 |                    530 |                   0.53 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | deepseek-r1 | less severe               |     312 |    0.31 |                    248 |                   0.25 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | deepseek-r1 | more severe               |     256 |    0.26 |                    221 |                   0.22 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | deepseek-r1 | NA                        |       1 |    0.00 |                      1 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | deepseek-r1 | correct                   |     420 |    0.42 |                    521 |                   0.52 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | deepseek-r1 | less severe               |     324 |    0.32 |                    265 |                   0.27 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | deepseek-r1 | more severe               |     251 |    0.25 |                    209 |                   0.21 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | deepseek-r1 | NA                        |       5 |    0.01 |                      5 |                   0.01 |

#### o3-mini
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM     | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|---------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | o3-mini | correct                   |     423 |    0.42 |                    499 |                   0.50 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | o3-mini | less severe               |     219 |    0.22 |                    170 |                   0.17 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | o3-mini | more severe               |     268 |    0.27 |                    241 |                   0.24 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | o3-mini | NA                        |      88 |    0.09 |                     88 |                   0.09 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | o3-mini | correct                   |     455 |    0.46 |                    527 |                   0.53 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | o3-mini | less severe               |     237 |    0.24 |                    190 |                   0.19 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | o3-mini | more severe               |     276 |    0.28 |                    251 |                   0.25 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | o3-mini | NA                        |      30 |    0.03 |                     30 |                   0.03 |

#### qwen2.5-1.5b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM          | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|--------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-1.5b | correct                   |      83 |    0.08 |                     98 |                   0.10 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-1.5b | less severe               |      19 |    0.02 |                     19 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-1.5b | more severe               |     198 |    0.20 |                    183 |                   0.18 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-1.5b | NA                        |     700 |    0.70 |                    700 |                   0.70 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-1.5b | correct                   |      48 |    0.05 |                     54 |                   0.05 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-1.5b | less severe               |       6 |    0.01 |                      6 |                   0.01 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-1.5b | more severe               |     132 |    0.13 |                    126 |                   0.13 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-1.5b | NA                        |     814 |    0.81 |                    814 |                   0.81 |

#### qwen2.5-32b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-32b | correct                   |     408 |    0.41 |                    504 |                   0.50 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-32b | less severe               |     277 |    0.28 |                    187 |                   0.19 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-32b | more severe               |     294 |    0.29 |                    288 |                   0.29 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | all          | qwen2.5-32b | NA                        |      21 |    0.02 |                     21 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-32b | correct                   |     404 |    0.40 |                    494 |                   0.49 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-32b | less severe               |     263 |    0.26 |                    179 |                   0.18 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-32b | more severe               |     327 |    0.33 |                    321 |                   0.32 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | all          | qwen2.5-32b | NA                        |       6 |    0.01 |                      6 |                   0.01 |



### cluster
#### deepseek-r1
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | deepseek-r1 | correct                   |      94 |    0.46 |                    117 |                   0.58 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | deepseek-r1 | less severe               |      56 |    0.28 |                     48 |                   0.24 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | deepseek-r1 | more severe               |      53 |    0.26 |                     38 |                   0.19 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | deepseek-r1 | NA                        |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | deepseek-r1 | correct                   |      95 |    0.47 |                    119 |                   0.59 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | deepseek-r1 | less severe               |      60 |    0.30 |                     53 |                   0.26 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | deepseek-r1 | more severe               |      48 |    0.24 |                     31 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | deepseek-r1 | NA                        |       0 |    0.00 |                      0 |                   0.00 |

#### o3-mini
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM     | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|---------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | o3-mini | correct                   |     106 |    0.52 |                    127 |                   0.63 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | o3-mini | less severe               |      34 |    0.17 |                     26 |                   0.13 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | o3-mini | more severe               |      44 |    0.22 |                     31 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | o3-mini | NA                        |      18 |    0.09 |                     18 |                   0.09 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | o3-mini | correct                   |     117 |    0.58 |                    134 |                   0.66 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | o3-mini | less severe               |      39 |    0.19 |                     33 |                   0.16 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | o3-mini | more severe               |      39 |    0.19 |                     28 |                   0.14 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | o3-mini | NA                        |       7 |    0.03 |                      7 |                   0.03 |

#### qwen2.5-1.5b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM          | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|--------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-1.5b | correct                   |      10 |    0.05 |                     13 |                   0.06 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-1.5b | less severe               |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-1.5b | more severe               |      38 |    0.19 |                     35 |                   0.17 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-1.5b | NA                        |     155 |    0.76 |                    155 |                   0.76 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-1.5b | correct                   |       7 |    0.03 |                      9 |                   0.04 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-1.5b | less severe               |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-1.5b | more severe               |      28 |    0.14 |                     26 |                   0.13 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-1.5b | NA                        |     168 |    0.83 |                    168 |                   0.83 |

#### qwen2.5-32b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-32b | correct                   |      98 |    0.48 |                    120 |                   0.59 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-32b | less severe               |      49 |    0.24 |                     29 |                   0.14 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-32b | more severe               |      50 |    0.25 |                     48 |                   0.24 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | cluster      | qwen2.5-32b | NA                        |       6 |    0.03 |                      6 |                   0.03 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-32b | correct                   |      89 |    0.44 |                    109 |                   0.54 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-32b | less severe               |      47 |    0.23 |                     30 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-32b | more severe               |      65 |    0.32 |                     62 |                   0.31 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | cluster      | qwen2.5-32b | NA                        |       2 |    0.01 |                      2 |                   0.01 |



### vague
#### deepseek-r1
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | deepseek-r1 | correct                   |      95 |    0.40 |                    120 |                   0.50 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | deepseek-r1 | less severe               |      85 |    0.36 |                     63 |                   0.26 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | deepseek-r1 | more severe               |      58 |    0.24 |                     55 |                   0.23 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | deepseek-r1 | NA                        |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | deepseek-r1 | correct                   |      89 |    0.37 |                    114 |                   0.48 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | deepseek-r1 | less severe               |      89 |    0.37 |                     69 |                   0.29 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | deepseek-r1 | more severe               |      58 |    0.24 |                     53 |                   0.22 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | deepseek-r1 | NA                        |       2 |    0.01 |                      2 |                   0.01 |

#### o3-mini
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM     | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|---------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | o3-mini | correct                   |      83 |    0.35 |                     97 |                   0.41 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | o3-mini | less severe               |      65 |    0.27 |                     52 |                   0.22 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | o3-mini | more severe               |      70 |    0.30 |                     69 |                   0.29 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | o3-mini | NA                        |      19 |    0.08 |                     19 |                   0.08 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | o3-mini | correct                   |      92 |    0.39 |                    111 |                   0.47 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | o3-mini | less severe               |      73 |    0.31 |                     55 |                   0.23 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | o3-mini | more severe               |      72 |    0.30 |                     71 |                   0.30 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | o3-mini | NA                        |       1 |    0.00 |                      1 |                   0.00 |

#### qwen2.5-1.5b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM          | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|--------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-1.5b | correct                   |      22 |    0.09 |                     25 |                   0.11 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-1.5b | less severe               |       4 |    0.02 |                      4 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-1.5b | more severe               |      41 |    0.17 |                     38 |                   0.16 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-1.5b | NA                        |     171 |    0.72 |                    171 |                   0.72 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-1.5b | correct                   |       8 |    0.03 |                     10 |                   0.04 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-1.5b | less severe               |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-1.5b | more severe               |      30 |    0.13 |                     28 |                   0.12 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-1.5b | NA                        |     200 |    0.84 |                    200 |                   0.84 |

#### qwen2.5-32b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-32b | correct                   |      82 |    0.34 |                    105 |                   0.44 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-32b | less severe               |      83 |    0.35 |                     60 |                   0.25 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-32b | more severe               |      69 |    0.29 |                     69 |                   0.29 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | vague        | qwen2.5-32b | NA                        |       4 |    0.02 |                      4 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-32b | correct                   |      84 |    0.35 |                    106 |                   0.45 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-32b | less severe               |      80 |    0.34 |                     58 |                   0.24 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-32b | more severe               |      73 |    0.31 |                     73 |                   0.31 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | vague        | qwen2.5-32b | NA                        |       1 |    0.00 |                      1 |                   0.00 |



### hypochondriac
#### deepseek-r1
| Embedding Method                        |   Supporting documents retrieved | Query Type    | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|---------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | deepseek-r1 | correct                   |      90 |    0.47 |                    107 |                   0.55 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | deepseek-r1 | less severe               |      52 |    0.27 |                     41 |                   0.21 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | deepseek-r1 | more severe               |      50 |    0.26 |                     44 |                   0.23 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | deepseek-r1 | NA                        |       1 |    0.01 |                      1 |                   0.01 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | deepseek-r1 | correct                   |      81 |    0.42 |                    102 |                   0.53 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | deepseek-r1 | less severe               |      59 |    0.31 |                     47 |                   0.24 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | deepseek-r1 | more severe               |      51 |    0.26 |                     42 |                   0.22 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | deepseek-r1 | NA                        |       2 |    0.01 |                      2 |                   0.01 |

#### o3-mini
| Embedding Method                        |   Supporting documents retrieved | Query Type    | LLM     | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|---------------|---------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | o3-mini | correct                   |      85 |    0.44 |                     97 |                   0.50 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | o3-mini | less severe               |      29 |    0.15 |                     22 |                   0.11 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | o3-mini | more severe               |      58 |    0.30 |                     53 |                   0.27 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | o3-mini | NA                        |      21 |    0.11 |                     21 |                   0.11 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | o3-mini | correct                   |      87 |    0.45 |                    104 |                   0.54 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | o3-mini | less severe               |      38 |    0.20 |                     28 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | o3-mini | more severe               |      60 |    0.31 |                     53 |                   0.28 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | o3-mini | NA                        |       7 |    0.04 |                      7 |                   0.04 |

#### qwen2.5-1.5b
| Embedding Method                        |   Supporting documents retrieved | Query Type    | LLM          | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|---------------|--------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-1.5b | correct                   |      26 |    0.13 |                     29 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-1.5b | less severe               |       8 |    0.04 |                      8 |                   0.04 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-1.5b | more severe               |      34 |    0.18 |                     31 |                   0.16 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-1.5b | NA                        |     125 |    0.65 |                    125 |                   0.65 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-1.5b | correct                   |      13 |    0.07 |                     14 |                   0.07 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-1.5b | less severe               |       3 |    0.02 |                      3 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-1.5b | more severe               |      29 |    0.15 |                     28 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-1.5b | NA                        |     148 |    0.77 |                    148 |                   0.77 |

#### qwen2.5-32b
| Embedding Method                        |   Supporting documents retrieved | Query Type    | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|---------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-32b | correct                   |      76 |    0.39 |                     95 |                   0.49 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-32b | less severe               |      37 |    0.19 |                     20 |                   0.10 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-32b | more severe               |      75 |    0.39 |                     73 |                   0.38 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | hypochondriac | qwen2.5-32b | NA                        |       5 |    0.03 |                      5 |                   0.03 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-32b | correct                   |      80 |    0.41 |                    100 |                   0.52 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-32b | less severe               |      39 |    0.20 |                     20 |                   0.10 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-32b | more severe               |      74 |    0.38 |                     73 |                   0.38 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | hypochondriac | qwen2.5-32b | NA                        |       0 |    0.00 |                      0 |                   0.00 |



### basic
#### deepseek-r1
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | deepseek-r1 | correct                   |      84 |    0.49 |                    106 |                   0.62 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | deepseek-r1 | less severe               |      53 |    0.31 |                     40 |                   0.24 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | deepseek-r1 | more severe               |      33 |    0.19 |                     24 |                   0.14 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | deepseek-r1 | NA                        |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | deepseek-r1 | correct                   |      86 |    0.51 |                    107 |                   0.63 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | deepseek-r1 | less severe               |      53 |    0.31 |                     42 |                   0.25 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | deepseek-r1 | more severe               |      31 |    0.18 |                     21 |                   0.12 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | deepseek-r1 | NA                        |       0 |    0.00 |                      0 |                   0.00 |

#### o3-mini
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM     | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|---------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | o3-mini | correct                   |      88 |    0.52 |                    109 |                   0.64 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | o3-mini | less severe               |      41 |    0.24 |                     28 |                   0.16 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | o3-mini | more severe               |      31 |    0.18 |                     23 |                   0.14 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | o3-mini | NA                        |      10 |    0.06 |                     10 |                   0.06 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | o3-mini | correct                   |      98 |    0.58 |                    110 |                   0.65 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | o3-mini | less severe               |      31 |    0.18 |                     25 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | o3-mini | more severe               |      31 |    0.18 |                     25 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | o3-mini | NA                        |      10 |    0.06 |                     10 |                   0.06 |

#### qwen2.5-1.5b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM          | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|--------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-1.5b | correct                   |      12 |    0.07 |                     18 |                   0.11 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-1.5b | less severe               |       4 |    0.02 |                      4 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-1.5b | more severe               |      26 |    0.15 |                     20 |                   0.12 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-1.5b | NA                        |     128 |    0.75 |                    128 |                   0.75 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-1.5b | correct                   |      12 |    0.07 |                     13 |                   0.08 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-1.5b | less severe               |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-1.5b | more severe               |      18 |    0.11 |                     17 |                   0.10 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-1.5b | NA                        |     140 |    0.82 |                    140 |                   0.82 |

#### qwen2.5-32b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-32b | correct                   |      89 |    0.52 |                    110 |                   0.65 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-32b | less severe               |      44 |    0.26 |                     25 |                   0.15 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-32b | more severe               |      33 |    0.19 |                     31 |                   0.18 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | basic        | qwen2.5-32b | NA                        |       4 |    0.02 |                      4 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-32b | correct                   |      89 |    0.52 |                    112 |                   0.66 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-32b | less severe               |      42 |    0.25 |                     21 |                   0.12 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-32b | more severe               |      39 |    0.23 |                     37 |                   0.22 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | basic        | qwen2.5-32b | NA                        |       0 |    0.00 |                      0 |                   0.00 |



### downplay
#### deepseek-r1
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | deepseek-r1 | correct                   |      68 |    0.35 |                     80 |                   0.41 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | deepseek-r1 | less severe               |      66 |    0.34 |                     56 |                   0.29 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | deepseek-r1 | more severe               |      62 |    0.32 |                     60 |                   0.31 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | deepseek-r1 | NA                        |       0 |    0.00 |                      0 |                   0.00 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | deepseek-r1 | correct                   |      69 |    0.35 |                     79 |                   0.40 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | deepseek-r1 | less severe               |      63 |    0.32 |                     54 |                   0.28 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | deepseek-r1 | more severe               |      63 |    0.32 |                     62 |                   0.32 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | deepseek-r1 | NA                        |       1 |    0.01 |                      1 |                   0.01 |

#### o3-mini
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM     | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|---------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | o3-mini | correct                   |      61 |    0.31 |                     69 |                   0.35 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | o3-mini | less severe               |      50 |    0.26 |                     42 |                   0.21 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | o3-mini | more severe               |      65 |    0.33 |                     65 |                   0.33 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | o3-mini | NA                        |      20 |    0.10 |                     20 |                   0.10 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | o3-mini | correct                   |      61 |    0.31 |                     68 |                   0.35 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | o3-mini | less severe               |      56 |    0.29 |                     49 |                   0.25 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | o3-mini | more severe               |      74 |    0.38 |                     74 |                   0.38 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | o3-mini | NA                        |       5 |    0.03 |                      5 |                   0.03 |

#### qwen2.5-1.5b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM          | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|--------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-1.5b | correct                   |      13 |    0.07 |                     13 |                   0.07 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-1.5b | less severe               |       3 |    0.02 |                      3 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-1.5b | more severe               |      59 |    0.30 |                     59 |                   0.30 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-1.5b | NA                        |     121 |    0.62 |                    121 |                   0.62 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-1.5b | correct                   |       8 |    0.04 |                      8 |                   0.04 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-1.5b | less severe               |       3 |    0.02 |                      3 |                   0.02 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-1.5b | more severe               |      27 |    0.14 |                     27 |                   0.14 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-1.5b | NA                        |     158 |    0.81 |                    158 |                   0.81 |

#### qwen2.5-32b
| Embedding Method                        |   Supporting documents retrieved | Query Type   | LLM         | Predicted Severity Type   |   Count |   Score |   Count (no Ambulance) |   Score (no Ambulance) |
|-----------------------------------------|----------------------------------|--------------|-------------|---------------------------|---------|---------|------------------------|------------------------|
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-32b | correct                   |      63 |    0.32 |                     74 |                   0.38 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-32b | less severe               |      64 |    0.33 |                     53 |                   0.27 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-32b | more severe               |      67 |    0.34 |                     67 |                   0.34 |
| sentence-transformers/all-mpnet-base-v2 |                               10 | downplay     | qwen2.5-32b | NA                        |       2 |    0.01 |                      2 |                   0.01 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-32b | correct                   |      62 |    0.32 |                     67 |                   0.34 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-32b | less severe               |      55 |    0.28 |                     50 |                   0.26 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-32b | more severe               |      76 |    0.39 |                     76 |                   0.39 |
| sentence-transformers/all-mpnet-base-v2 |                               30 | downplay     | qwen2.5-32b | NA                        |       3 |    0.02 |                      3 |                   0.02 |
