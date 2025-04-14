# Knowledge retrieval summary results

## Goal

Answers to:
1. Does RAG improve over no RAG? (results in table 2b vs 3a)
2. Does reasoning improve over only RAG? (s1 in Table 4 vs Qwen-32B in table 2b)
3. Does domain-reasoning improve over general reasoning? (s1 vs Marcel)

Performance is measured by the fraction of predictions of condition
and severity that are correct. Some evaluations return $k$ possible
conditions and there we give the "precision at $k$", or the fraction
of queries for which at least one of the returned conditions is
correct.

Two evaluation datasets are used: (1) "small," our original one of
~100 synthetic queries; (2) "large," our revised set of ~1,000
queries. (We may revise "large" to make "large2").

## 1. Retrieval only

Retrieval only, by means of vector dB similarity lookup. Returns $k$
chunks. $p@k$ refers to the fraction of those chunks coming from the
correct condition.

Sets the highest precision possible through RAG, if the predicted
condition is constrained to be one of the $k$ retrieved documents.

| Embedding Method                | Eval Set | p@1 | p@5 | p@10 | p@20 | p@50 | p@100 |
|--------------------------------|----------|-----|-----|------|------|------|-------|
| mpnet-base-v2 / Chroma         | Small    | 0.47| 0.56| 0.68 | 0.69 |  -   |   -   |
| mpnet-base-v2 / FAISS          | Small    | 0.47| 0.68| 0.71 | 0.78 |  -   |   -   |
| mxbai-embed-large-v1 / FAISS   | Small    | 0.51| 0.68| 0.71 | 0.76 |  -   |   -   |
| mpnet-base-v2 / Chroma         | Large    |  x  |  x  |  x   |  x   |  x   |   x   |
| mpnet-base-v2 / FAISS          | Large    | 0.44| 0.63| 0.70 | 0.77 | 0.86 | 0.90  |


## 2. Baseline models (RAG)

RAG with retrieval as above and a non--fine-tuned, baseline
model. Sets the baseline precision.

### 2 a. Small evaluation set

| LLM         | k  | Condition Accuracy | Severity Accuracy |
|-------------|----|--------------------|-------------------|
| GPT-4o      | 10 | 0.52               | 0.49              |
|             | 50 | **0.61**               | 0.53              |
| o3-mini     | 10 | 0.56               | 0.54              |
|             | 50 | 0.59               | **0.62**              |
| Qwen (1.5B) | 10 | 0.35               | 0.34              |
|             | 50 | 0.20               | 0.29              |
| Qwen (14B)  | 10 | 0.47               | 0.52              |
|             | 50 | 0.51               | 0.46              |
| Qwen (32B)  | 10 | 0.53               | 0.46              |
|             | 50 | 0.59               | 0.43              |

NB. Qwen is Qwen2.5 Instruct.

### 2.b Large evaluation set (cross-check with 2a)


| LLM        | k  | Condition Accuracy | Severity Accuracy |
|------------|----|--------------------|-------------------|
| Qwen (32B) | 10 | x                  | x                 |
|            | 50 | x                  | x                 |

### 2.c Large evaluation set (as time allows)

| LLM             | k  | Condition Accuracy | Severity Accuracy |
|-----------------|----|--------------------|-------------------|
| o3-mini         | 10 | x                  | x                 |
| DeepSeek-r1     | 50 | x                  | x                 |
| Qwen (1.5B)     | 10 | x                  | x                 |
|                 | 50 | x                  | x                 |

### 2.d Large evaluation set (not essential)

| LLM             | k   | Condition Accuracy | Severity Accuracy |
|-----------------|-----|--------------------|-------------------|
| o3-mini         | 100 | x                  | x                 |
| DeepSeek-r1     | 100 | x                  | x                 |
| Qwen (1.5B)     | 100 | x                  | x                 |


## 3. Baseline model (no RAG)

Results with a large model, without passing in documents for RAG,
large evaluation set.

### 3.a

| LLM         | Condition Accuracy | Severity Accuracy |
|-------------|--------------------|-------------------|
| DeepSeek-r1 | x                  | x                 |
| Qwen-32B    | x                  | x                 |

### 3.b (as time allows)

| LLM       | Condition Accuracy | Severity Accuracy |
|-----------|--------------------|-------------------|
| o3-mini   | x                  | x                 |
| Qwen-1.5B | x                  | x                 |


## 4. RAG + post-trained model

Same as before but now we are using models post-trained on reasoning
data. There are two ideas:

1. s1 (Qwen32B fine-tuned on reasoning)
2. "Marcel" aka t1 (Qwen32B fine-tuned on domain-specific reasoning
   traces).

| LLM    | Condition Accuracy | Severity Accuracy |
|--------|--------------------|-------------------|
| s1     | x                  | x                 |
| Marcel | x                  | x                 |
