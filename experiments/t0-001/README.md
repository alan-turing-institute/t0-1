# 001

## Setup

Clone the repository:
```bash
git clone git@github.com:alan-turing-institute/t0.git
cd experiments/t0-001
```

Create a virtual environment, activate it and install required dependencies (in editable mode) using [uv](https://github.com/astral-sh/uv):
```bash
uv venv .venv --python=3.12
source .venv/bin/activate
uv pip install -r pyproject.toml --extra rag --extra dev
```

## Data

The data used in this project is scraped from the NHS website. Once you have downloaded the data, store it in a directory called `nhs-use-case`. This folder should have the following structure:
```
nhs-use-case/
  +-- nhs-conditions/
      +-- <condition-name>/
          +-- index.html
```

The convention is to run scripts and commands from the `experiments/t0-001` directory and use relative paths to the `nhs-use-case` directory. For the command line interfaces (CLIs) described below, the `--data-folder` argument is defaulted to `./nhs-use-case/conditions/`.

## Command Line Interfaces (CLIs)

For `t0-001`, we have several command line interfaces (CLIs) (implemented using `typer`) to facilitate different tasks. You can run `t0-001 --help` to see the available commands.

- [Serving and querying from the query vector store](#serving-and-querying-from-the-query-vector-store)
- [Evaluating the query vector store](#evaluating-the-query-vector-store)
- [Serving and querying from a retriever](#serving-and-querying-from-a-retriever)
- [Evaluating the retriever](#evaluating-the-retriever)
- [Serving and querying from a RAG model](#serving-and-querying-from-a-rag-model)
- [Initalising a RAG chat interaction](#initalising-a-rag-chat-interaction)
- [Generating synthetic queries](#generating-synthetic-queries)

### Serving and querying from the query vector store

**Commands**:
- Serving: `t0-001 serve-vector-store`
- Querying: `t0-001 query-vector-store`

#### Serving the vector store

For serving the vector store, you can use the `t0-001 serve-vector-store` command. This will start a FastAPI server that serves the vector store. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

There are several options for the `t0-001 serve-vector-store` command:
- `--data-folder`: The folder containing the data. Default is `./nhs-use-case/conditions/`.
- `--main-only`: If set, only the main element of the HTML file is extracted.
- `--embedding-model-name`: The name of the embedding model to use.
- `--chunk-overlap`: The character overlap between chunks.
- `--db-choice`: The choice of database to use (either `chroma` or `faiss`).

It is possible to save and load a vector store by using the `--persist-directory` option. By default, we try to load the vector store from the provided path. If it does not exist, we will create a new vector store and save it to the provided path. You can use the `--force-create` option to force the creation of a new vector store, even if it already exists.

Note for loading a `faiss` vector store: you must use the `--trust-source` option to load a `faiss` vector store - without it, you will not be able to load the vector store.

Lastly, you can decide to not serve and just build the vector store by using the `--no-serve` option. This will build the vector store and save it to the provided path, but will not start the FastAPI server.

All of these options have default arguments (see `t0-001 serve-vector-store --help`), so you can just run the command as is. But to save and load the vector store, you need to provide the `--persist-directory` option:
```bash
t0-001 serve-vector-store --persist-directory ./nhs-use-case-db
```

#### Querying the vector store

Once you have served the FastAPI to the vector store, you can query it with the `t0-001 query-vector-store` command. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

There are several options for the `t0-001 query-vector-store` command:
- `--k`: The number of results to return. Default is 4.
- `--with-score`: If True, return the score of the similarity search.

An example command to query the vector store is:
```bash
t0-001 query-vector-store \
  "What should I do if I have lost a lot of weight over the last 3 to 6 months?" \
  --k 5 \
  --with-score
```

#### Evaluating the vector store

For evaluating the vector store, you can use the `t0-001 evaluate-vector-store` command. This takes as input a JSONL file where each row has has a query and a target document (i.e. the name of the document or source of the chunk). In the evaluation, we query the vector database by performing a similarity search to obtain the top `k` relevant documents and assign a positive score if the retrieved documents are from the target document. In other words, we check if it's able to retrieve a chunk from that document.

There are some options for the `t0-001 evaluate-vector-store` command:
- `--output-file`: Path to the output file.
- `--query-field`: The field name in the JSONL corresponding to the query. Default is `"symptoms_description"`.
- `--target-document-field`: The field name in the JSONL corresponding to the target document name. Default is `"conditions_title"`.

The other options are same as for [serving the vector store](#serving-the-vector-store) to specify the configuration of the vector store to evaluate.

An example command to evaluate the vector store is:
```bash
t0-001 evaluate-vector-store <path-to-input-jsonl> \
  --output-file ./eval-vector-store-defaults-k10.jsonl \
  --k 10
```

### Serving and querying from a retriever

Retrievers in Langchain are used to retrieve documents - these could be from a vector store or other databases such as graph databases or relational databases. We are currently using vector stores as the retriever, but this could be extended to other databases in the future.

The implemented retriever is one that uses a vector store and retrieves **full documents** as opposed to just the chunks. The chunks / sub-documents are returned in the metadata of the retrieved documents.

**Commands**:
- Serving: `t0-001 serve-retriever`
- Querying: `t0-001 query-retriever`

#### Serving the retriever

For serving the retriever, you can use the `t0-001 serve-retriever` command. This will start a FastAPI server that serves the vector store. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

There are several options for the `t0-001 serve-retriever` command. Most are the similar to the `serve-vector-store` command with a few additional ones:
- `--search-type`: Type of search to perform for the retriever. By default, we perform a similarity search, but others are available such as `"mmr"` for maximal marginal relevance reranking of similarity search.
- `--k`: The number of results to return. Note that this is required for setting up the retriever whereas for the vector store, this can be specified when querying.

As with a vector store, you can save and load a vector store by using the `--persist-directory` and `--local-file-store` directory. The local file store is to store the full documents while the persist directory stores the vector store.

You can also decide to not serve and just build the vector store by using the `--no-serve` option. This will build the vector store and save it to the provided path, but will not start the FastAPI server.

All of these options have default arguments (see `t0-001 serve-retriever --help`), so you can just run the command as is. But to svae and load the vector store, you need to provide the `--persist-directory` and `--local-file-store` options:
```bash
t0-001 serve-retriever --persist-directory ./nhs-use-case-db --local-file-store ./nhs-use-case-fs
```

#### Querying the retriever

Once you have served the FastAPI to the retriever, you can query it with the `t0-001 query-retriever` command. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

An example command to query the RAG model is:
```bash
t0-001 query-retriever \
  "What should I do if I have lost a lot of weight over the last 3 to 6 months?"
```

### Serving and querying from a RAG model

**Commands**:
- Serving: `t0-001 serve-rag`
- Querying: `t0-001 query-rag`

#### Serving the RAG model

For serving the RAG model, you can use the `t0-001 serve-rag` command. This will start a FastAPI server that serves the RAG model. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

Many options are similar to the [vector store](#serving-the-vector-store) and [retriever](#serving-the-retriever) serving commands which are described above. The main difference is that you can specify the LLM to use with the `--llm-model-name` option.

All of these options have default arguments (see `t0-001 serve-rag --help`), so you can just run the command as is. But to save and load the vector store, you need to provide the `--persist-directory` and `--local-file-store` options:
```bash
t0-001 serve-rag --persist-directory ./nhs-use-case-db --local-file-store ./nhs-use-case-fs
```

#### Querying the RAG model

Once you have served the FastAPI to the RAG model, you can query it with the `t0-001 query-rag` command. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

An example command to query the RAG model is:
```bash
t0-001 query-rag \
  "What should I do if I have lost a lot of weight over the last 3 to 6 months?"
```

### Initalising a RAG chat interaction

For spinning up a local RAG chat interaction, you can use the `t0-001 rag-chat` command. Most of the options are similar to those discussed above in the `t0-001 serve-vector-store` and `t0-001 serve-rag` commands - use `t0-001 rag-chat --help` to see all the options.

You should be able to just spin it up with default options (below we are using the `--persist-directory` option to load the vector store if it exists, or create it if it doesn't):
```bash
t0-001 rag-chat --persist-directory ./nhs-use-case-db
```

You can then interact with the RAG model in a chat-like interface. You can type in your queries and the model will respond with the relevant information from the vector store.

You can exit the chat by typing `exit`, `exit()` or `quit()` in the chat or simply `Ctrl+C`/`cmd+C` in the terminal.

There are different "chat-modes", which are:
- **query-mode**: only the response from the LLM is returned after each query
- **query-with-sources-mode** (default): the response from the LLM and the sources used to generate the response are returned after each query
- **query-with-context-mode**: the response from the LLM and the context used to generate the response are returned after each query

You can switch between these during the chat by typing a backslash command: `/query-mode`, `/query-with-sources-mode` or `/query-with-context-mode`, e.g.
```bash
>>> /query-with-sources-mode
Model: Switched to query-with-context mode.
```

### Generating synthetic queries


### Azure AI Foundry Endpoints

The endpoints and the corresponding API keys can be viewed on the Models + endpoints page of the Azure AI Foundry portal:

Go to `https://ai.azure.com/`, select the `ai_foundry_t0 project`, then in the left pane under `My Assets`, select `Models + endpoints`. You should see a list of endpoints for different models. The endpoints and keys can be viewed by clicking on a model (e.g., `o3-mini`). The key is in the protected section under Endpoint grouping, and the actual endpoint is the Target URI, but only up to the part including ai.azure.com (e.g., https://ai-aifoundrygpt4o065309524447.openai.azure.com).

<img src="img/Azure_Endpoint.png" alt="AI Foundry Endpoint" width="600"/>

To test the endpoints, you can run the `scripts/test_Azure_models.py` script, but don't forget to set the environment variables as listed in the `.env.example` file.

#### Pricing of the models

| Model         | Price per 1M Tokens (USD) |
|---------------|----------------------------|
| gpt-4o        | 4.38                       |
| o3-mini       | 1.93                       |
| DeepSeek-V3   | 2.00                       |
| DeepSeek-R1   | 2.36                       |
| o1            | 26.25                      |
