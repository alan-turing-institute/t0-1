FROM nvcr.io/nvidia/vllm:25.12.post1-py3
WORKDIR /

# clone t0
RUN git clone https://github.com/alan-turing-institute/t0-1.git
WORKDIR /t0-1

# expose ports
EXPOSE 8010
EXPOSE 8020

CMD ["/bin/bash"]
