# Knowledge retrieval with a reasoning model: summary results

## Goal

Answers to:
1. Does RAG improve over no RAG?
2. Does reasoning improve over only RAG?
3. Does domain-reasoning improve over general reasoning?

Performance is measured by the fraction of predictions of condition
and severity that are correct. Some evaluations return $k$ possible
conditions and there we give the "precision at $k$", or the fraction
of queries for which at least one of the returned conditions is
correct.

The evaluation dataset contains 1,000 synthetically generated patient queries.

## 1. Results: retrieval only

Retrieval only, by means of vector dB similarity lookup. Returns $k$
conditions based on the similarity with the patienty query and the summary of the condition. $p@k$ refers to the number of times the correct condition is present among the $k$ returned contisions.

Sets the highest precision possible through RAG, if the predicted
condition is constrained to be one of the $k$ retrieved documents.

| Embedding Method             | Eval Set |  p@1 |  p@5 | p@10 | p@30 | p@50 | p@100 |
|------------------------------|----------|-----:|-----:|-----:|-----:|-----:|------:|
| mpnet-base-v2 / Chroma       | Large    | 0.51 | 0.75 | 0.83 | 0.93 | 0.96 |  0.98 |
| mpnet-base-v2 / FAISS        | Large    | 0.51 | 0.76 | 0.83 | 0.93 | 0.96 |  0.98 |

### Conclusion

Chroma and FAISS perform very similarly on the large eval set, and
Chroma is just slightly faster, so we'll use this as retrieval system
for the rest of the evaluation. From now on, we'll consider two *k*,
5 and 30, as they provide an overview of performance when retrieving
documents where at least one is relevant in respectively 75% and 90%
of the queries.

## 2. Results: RAG vs no RAG

RAG with retrieval as above and a non--reasoning model as generator vs the same model, without RAG to support it. This will let us understanding the usefulness of RAG.


| $k$ | LLM            | Condition Accuracy | Severity Accuracy |
|----:|----------------|-------------------:|------------------:|
|  NA   | GPT-4o    |               0.49 |              0.56 |
|     | Qwen (32B)     |               0. |              0. |
|  5   | GPT-4o    |               0.55 |              0.54 |
|     | Qwen (32B)     |               0.52 |              0.50 |
|  30   | GPT-4o    |               0.58 |              0.53 |
|     | Qwen (32B)     |               0.51 |              0.50 |

### Conclusion


## 3. Results: RAG + reasoning model

Same as before but now we are using models post-trained on reasoning
data as generators:


| $k$ | LLM       | Condition Accuracy | Severity Accuracy |
|----:|-----------|-------------------:|------------------:|
|  5   | o3-mini    |               0.54 |              0.56 |
|     | DeepSeek-r1     |               0.56 |              0.51 |
|     | s1     |               0.50 |              0.44 |
|     | Qwen3     |               0.53 |              0.49 |
|     | t0-k5-32B*     |               0.56 |              0.51 |
|  30   | o3-mini    |               0.58 |              0.56 |
|     | DeepSeek-r1     |               0.56 |              0.51 |
|     | s1     |               0.45 |              0.45 |
|     | Qwen3     |               0.56 |              0.46 |
|     | t0-k5-32B*     |               0.55 |              0.50 |

* (budget forcing with 256 max thinking tokens, num_stop_skips=3)

### Conclusion
