FROM nvcr.io/nvidia/vllm:25.10-py3
WORKDIR /

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"

# clone t0
RUN git clone https://github.com/alan-turing-institute/t0-1.git
WORKDIR /t0-1

# checkout spark branch
RUN git checkout spark

# create uv .venv
RUN uv venv --python=3.11
RUN uv sync --extra rag

# expose ports
EXPOSE 8010
EXPOSE 8020

ENV HF_HOME=/models/.cache/huggingface
ENV VLLM_ALLOW_LONG_MAX_MODEL_LEN=1

CMD ["/bin/bash"]
