# 001

## Setup

Clone the repository:
```bash
git clone git@github.com:alan-turing-institute/t0.git
cd experiments/t0-001
```

Create a virtual environment, activate it and install required dependencies (in editable mode) using [uv](https://github.com/astral-sh/uv):
```bash
uv venv --python=3.12
source .venv/bin/activate
uv pip install -e ".[rag,dev]"
```

## Data

The data used in this project is scraped from the NHS website using [this script](scripts/Makefile) and running `make download`. Once you have downloaded the data, we can either process the html directly, or we can use [pandoc](https://pandoc.org/) to convert them into plain txt files - you can do this by running `make all`. We recommend using the txt files as they are easier to process and work with.

Next, you can generate a JSONL file using [this script](scripts/convert_txt_conditions_to_dataset.py) and store it in a directory called `data/nhs-conditions`. In this JSONL file each line has a JSON object with fields `"condition_title"` and `"condition_content"`.

The convention is to run scripts and commands from the `experiments/t0-001` directory and use relative paths to the `data/nhs-conditions` directory. For the command line interfaces (CLIs) described below, the `--conditions-file` argument is defaulted to `"./data/nhs-conditions/conditions.jsonl"`.

## Command Line Interfaces (CLIs)

For `t0-001`, we have several command line interfaces (CLIs) (implemented using `typer`) to facilitate different tasks. You can run `t0-001 --help` to see the available commands.

- [Serving and querying from the query vector store](#serving-and-querying-from-the-query-vector-store)
- [Evaluating the query vector store](#evaluating-the-query-vector-store)
- [Serving and querying from a retriever](#serving-and-querying-from-a-retriever)
- [Serving and querying from a RAG model](#serving-and-querying-from-a-rag-model)
- [Initialising a RAG chat interaction](#initalising-a-rag-chat-interaction)
- [Evaluating RAG](#evaluating-RAG)
- [Generating synthetic queries](#generating-synthetic-queries)

Note that with using `uv`, it is useful to run scripts with `uv run`, e.g. `uv run t0-001 rag-chat ...`.

### Serving and querying from the query vector store

**Commands**:
- Serving: `t0-001 serve-vector-store`
- Querying: `t0-001 query-vector-store`

#### Serving the vector store

For serving the vector store, you can use the `t0-001 serve-vector-store` command. This will start a FastAPI server that serves the vector store. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

There are several options for the `t0-001 serve-vector-store` command:
- `--conditions-file`: The folder containing the data. Default is `"./data/nhs-conditions/conditions.jsonl"`.
- `--main-only`: If set, only the main element of the HTML file is extracted.
- `--embedding-model-name`: The name of the embedding model to use.
- `--chunk-overlap`: The character overlap between chunks.
- `--db-choice`: The choice of database to use (either `chroma` or `faiss`).

It is possible to save and load a vector store by using the `--persist-directory` option. By default, we try to load the vector store from the provided path. If it does not exist, we will create a new vector store and save it to the provided path. You can use the `--force-create` option to force the creation of a new vector store, even if it already exists.

Note for loading a `faiss` vector store: you must use the `--trust-source` option to load a `faiss` vector store - without it, you will not be able to load the vector store.

Lastly, you can decide to not serve and just build the vector store by using the `--no-serve` option. This will build the vector store and save it to the provided path, but will not start the FastAPI server.

All of these options have default arguments (see `t0-001 serve-vector-store --help`), so you can just run the command as is. But to save and load the vector store, you need to provide the `--persist-directory` option:
```bash
uv run t0-001 serve-vector-store --persist-directory ./nhs-use-case-db
```

#### Querying the vector store

Once you have served the FastAPI to the vector store, you can query it with the `t0-001 query-vector-store` command. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

There are several options for the `t0-001 query-vector-store` command:
- `--k`: The number of results to return. Default is 4.
- `--with-score`: If True, return the score of the similarity search.

An example command to query the vector store is:
```bash
uv run t0-001 query-vector-store \
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
uv run t0-001 evaluate-vector-store <path-to-input-jsonl> \
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

All of these options have default arguments (see `t0-001 serve-retriever --help`), so you can just run the command as is. But to save and load the vector store, you need to provide the `--persist-directory` and `--local-file-store` options:
```bash
uv run t0-001 serve-retriever \
  --persist-directory ./nhs-use-case-db \
  --local-file-store ./nhs-use-case-fs
```

#### Querying the retriever

Once you have served the FastAPI to the retriever, you can query it with the `t0-001 query-retriever` command. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

An example command to query the RAG model is:
```bash
uv run t0-001 query-retriever \
  "What should I do if I have lost a lot of weight over the last 3 to 6 months?"
```

### Serving and querying from a RAG model

**Commands**:
- Serving: `t0-001 serve-rag`
- Querying: `t0-001 query-rag`

#### Serving the RAG model

For serving the RAG model, you can use the `t0-001 serve-rag` command. This will start a FastAPI server that serves the RAG model. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

Many options are similar to the [vector store](#serving-the-vector-store) and [retriever](#serving-the-retriever) serving commands which are described above. The main difference is that you can specify the LLM to use with the `--llm-provider` and `--llm-model-name` options.
- If `--llm-provider` is set to `huggingface`, the model name should be a Hugging Face model name (e.g., `Qwen/Qwen2.5-1.5B-Instruct`) - this is the default configuration.
- If `--llm-provider` is set to `azure-openai`, the model name should be the name of the Azure OpenAI deployment/model name (e.g., `gpt-4o`).
  - Note that you need to set the `AZURE_OPENAI_API_KEY_{model_name}` and `AZURE_OPENAI_ENDPOINT_{model_name}` environment variables.
  - If these aren't set, you can set them without the model name: `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` - these represent the default key and endpoints.
- If `--llm-provider` is set to `azure`, the model name should be the name of the Azure AI Foundry deployment/model name (e.g., `deepseek-r1`)
  - Note that you need to set the `AZURE_API_KEY_{model_name}` and `AZURE_API_ENDPOINT_{model_name}` environment variables.
  - If these aren't set, you can set them without the model name: `AZURE_API_KEY` and `AZURE_API_ENDPOINT` - these represent the default key and endpoints.

**Note**: for environment variables, you can set them in a `.env` file. By default, the command loads in a `.env` file in the current directory. You can also set this to a different file using the `--env-file` option.

All of these options have default arguments (see `t0-001 serve-rag --help`), so you can just run the command as is. But to save and load the vector store, you need to provide the `--persist-directory` and `--local-file-store` options:
```bash
uv run t0-001 serve-rag \
  --persist-directory ./nhs-use-case-db \
  --local-file-store ./nhs-use-case-fs
```

For using an Azure OpenAI endpoint, you can run something like:
```bash
uv run t0-001 serve-rag \
  --persist-directory ./nhs-use-case-db \
  --local-file-store ./nhs-use-case-fs \
  --llm-provider azure-openai \
  --llm-model-name gpt-4o
```
and set the environment variables in a `.env` file:
```bash
AZURE_OPENAI_API_KEY_gpt-4o=<your-key>
AZURE_OPENAI_ENDPOINT_gpt-4o=<your-endpoint>
```

For using an Azure AI Foundry endpoint, you can run something like:
```bash
uv run t0-001 serve-rag \
  --persist-directory ./nhs-use-case-db \
  --local-file-store ./nhs-use-case-fs \
  --llm-provider azure \
  --llm-model-name deepseek-r1
```
and set the environment variables in a `.env` file:
```bash
AZURE_API_KEY_deepseek-r1=<your-key>
AZURE_API_ENDPOINT_deepseek-r1=<your-endpoint>
```

#### Querying the RAG model

Once you have served the FastAPI to the RAG model, you can query it with the `t0-001 query-rag` command. There are options to specify the host and port, by default it will run on `0.0.0.0:8000`.

An example command to query the RAG model is:
```bash
uv run t0-001 query-rag \
  "What should I do if I have lost a lot of weight over the last 3 to 6 months?"
```

### Initialising a RAG chat interaction

For spinning up a local RAG chat interaction, you can use the `t0-001 rag-chat` command. Most of the options are similar to those discussed above in the `t0-001 serve-vector-store` and `t0-001 serve-rag` commands - use `t0-001 rag-chat --help` to see all the options.

See [Serving the RAG model](#serving-the-rag-model) for the options to specify the LLM to use with the `--llm-provider` and `--llm-model-name` options and using environment variables.

You should be able to just spin it up with default options (below we are using the `--persist-directory` option to load the vector store if it exists, or create it if it doesn't):
```bash
uv run t0-001 rag-chat \
  --persist-directory ./nhs-use-case-db
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

### Evaluating RAG

For evaluating RAG, you can use the `t0-001 evaluate-rag` command. This takes as input a JSONL file where each row has has a query and a target document (i.e. the name of the document or source of the chunk). In the evaluation, we query the vector database by performing a similarity search to obtain the top `k` relevant documents (note that we retrieve full documents rather than chunks) and ask the model to predict the condition and severity of the query.

You can run this evaluation with the `t0-001 evaluate-rag` command:
```bash
uv run t0-001 evaluate-rag data/synthetic_queries/gpt-4o_100_synthetic_queries.jsonl \
  --k 10 \
  --llm-provider azure_openai \
  --llm-model-name gpt-4o \
  --prompt-template-path templates/rag_evaluation_prompt.txt \
  --system-prompt-path templates/rag_evaluation_system_prompt.txt
```

We use tool use to force the model as a form of structured output to get the model to predict the condition and severity.

Note for serving Deepseek-R1 on Azure AI Foundry, tool use is not currently supported, so we slightly adjust the system and prompt template so that it produces an output that we can easily parse. To evaluate Deepseek-R1, you need to use the `--deepseek-r1` option:
```bash
uv run t0-001 evaluate-rag data/synthetic_queries/gpt-4o_100_synthetic_queries.jsonl \
  --k 10 \
  --llm-provider azure \
  --llm-model-name deepseek-r1 \
  --prompt-template-path templates/rag_evaluation_prompt_deepseek_r1.txt \
  --system-prompt-path templates/rag_evaluation_system_prompt_deepseek_r1.txt \
  --deepseek-r1
```

### Generating synthetic queries

For generating synthetic queries from NHS 111 patients, you can use the `t0-001 generate-synth-queries` command. This will generate synthetic queries based on the conditions in the `nhs-use-case` folder and save them to a JSONL file.

The main options for the `t0-001 generate-synth-queries` command are:
- `--n-queries`: The number of queries to generate. Default is 10.
- `--model`: The model to use for generating the queries. This should be the name of the model to use (e.g., `gpt-4o`, `gemma3:1b`, etc.). For Azure OpenAI models, Azure endpoints are used and you will need to set the environment variables for ``AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` (or `AZURE_OPENAI_ENDPOINT_{model}` where `model` is your model name.). Otherwise the model will be called via Ollama.
- `--overwrite`: Flag for overwriting existing output files. This is useful if you want to regenerate the queries.
- `--env-file`: Path to the environment file. This is used to load the environment variables for the Azure endpoints. By default it loads a `.env` file in the current directory.

Use `t0-001 generate-synth-queries --help` to see all the options.

To set the environment variables for using the Azure endpoints, create an `.env` file as described above.

Endpoints can be of the form:
- `https://<your-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>`, where your-resource-name is your globally unique AOAI resource name, and your-deployment-name is your AI Model deployment name.
- OR `https://<your-resource-name>.openai.azure.com/`, where your-resource-name is your globally unique AOAI resource name. In this case, `openai/deployments/<model>` will be appended afterwards using the model name you provide.


### Azure AI Foundry Endpoints

The endpoints and the corresponding API keys can be viewed on the Models + endpoints page of the Azure AI Foundry portal:

Go to `https://ai.azure.com/`, select the `ai_foundry_t0 project`, then in the left pane under `My Assets`, select `Models + endpoints`. You should see a list of endpoints for different models. The endpoints and keys can be viewed by clicking on a model (e.g., `o3-mini`). The key is in the protected section under Endpoint grouping, and the actual endpoint is the Target URI, but only up to the part including ai.azure.com (e.g., https://ai-aifoundrygpt4o065309524447.openai.azure.com).

<img src="img/Azure_Endpoint.png" alt="AI Foundry Endpoint" width="600"/>

To test the endpoints, you can run the `scripts/test_Azure_models.py` script, but don't forget to set the environment variables as listed in the `.env.example` file.

#### Pricing of the models

| Model         | Price per 1M Tokens (USD) |
|---------------|---------------------------|
| gpt-4o        | 4.38                      |
| o3-mini       | 1.93                      |
| DeepSeek-V3   | 2.00                      |
| DeepSeek-R1   | 2.36                      |
| o1            | 26.25                     |
