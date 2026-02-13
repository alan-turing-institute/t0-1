# Set up on Framework Desktop

The Framework is running Fedora and KDE. Packages are up to date;
updates are done with `sudo dnf update`. Note that the ROCm packages
are from a different version of Fedora, so you end up with
warnings. However, llama.cpp comes with its own ROCm binaries, so in
fact the system ones should have no effect (and at some point I will
sync them with upstream Fedora.

## llama.cpp

As of 10 February 2026, vllm is not working on the
Framework. (Specifically, after `uv install`, when running `vllm
serve`, there is a error about a missing libmpi_cxx.so.40. Someone else
posted an open issue on the vllm repo a couple of days ago and I
assume there will be a fix soon.

> https://github.com/vllm-project/vllm/issues/34090

However, the pre-built llama.cpp downloaded from lemonade.ai does
work. 

> https://github.com/lemonade-sdk/llamacpp-rocm

These instructions assume that `llama.cpp` is in your path. (I
unzipped the pre-built files into `~/Apps/llama-cpp` (though you can
put them anywhere) then symlinked the binaries to `~/.local/bin` which
happens to be in my path. You might have to `chmod +x llama-server`
(and any other binary you'd like to run.)

I have also set the environment variable `LLAMA_CACHE` to
`/data/t0-rcp/llama.cpp` so that downloads from HuggingFace will go to
the right place.

## Models

These are in `/data/t0-rcp/llama.cpp`. There is a unix group "t0-rcp"
to which you should belong and which should have read/write access.

## Setup of t0-1

I used `uv pip install -e ".[rag,dev]"` rather than `uv sync`. 

NOTE: I've locked all the langchain-related module versions in
pyproject.toml. 

## Changes to the launch scripts

The launch script is in `t0-1/scripts/framework`

## Running

- Run the scripts from the project root. 
- In a new install you might need to create t0-1/v4-summarised-db and
  t0-1/v4-summarised-lfs
- Don't forget to make the .env file in project root. Its content is:

  ```
  OPENAI_API_KEY="-"
  OPENAI_BASE_URL_/data/t0-rcp/llama.cpp/t0-2.5-gemma-3-4B-it-F16.gguf="http://localhost:8080/v1/"
  OPENAI_BASE_URL_/data/t0-rcp/llama.cpp/unsloth_gpt-oss-20b-GGUF_gpt-oss-20b-Q8_0.gguf="http://localhost:8090/v1/"
  ```

## Running

In project root:
```sh
source .venv/bin/activate
llama-server -ngl 99 --jinja --port 8090 -m /data/t0-rcp/llama.cpp/unsloth_gpt-oss-20b-GGUF_gpt-oss-20b-Q8_0.gguf 
llama-server -ngl 99 -m /data/t0-rcp/llama.cpp/t0-2.5-gemma-3-4B-it-F16.gguf 
./scripts/framework/serve_rag_conversational.sh
```

In `web/`:
```
pnpm dev
```

