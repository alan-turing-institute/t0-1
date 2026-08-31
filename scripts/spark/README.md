# Running t0 on the spark

All t0-1 code, models and data are in the `/t0` directory. Its set so you should be able to read, write and execute all files in that directory. 
If things break, you can run `sudo chmod +wrx -R /t0` to fix permissions.

## Logging in and set up

1. `cd /t0/t0_1/t0-1/`

2. Check your bashrc, you should have the following env variables set:

```bash
export HF_HOME=/t0/models/.cache/huggingface
export HF_TOKEN=your_huggingface_token
```

3. Check you are on the `spark` branch with `git branch`

## Running the models with vllm

To run vllm on the spark you need to use the nvidia vllm docker image. 
It should be built for you already but if not I've put the command to rebuild it at the bottom of these instructions

Now, in window 1:

4. `cd /t0/t0_1/t0-1/`

5. `sudo docker run --volume /t0/models:/models --volume /t0/t0_1/t0-1:/t0-1_local --gpus all --entrypoint "/bin/bash" -it --env HF_TOKEN=$HF_TOKEN -p 8010:8010 -p 8020:8020 t0-im`

6. Run `./scripts/spark/run_gemma2.5_gpt-oss_router.sh`. This will start up the vllm servers and you will see `Waiting for vLLM to start...` in the terminal until everything is set up. Once its working, you'll get your command prompt back.

## Running RAG (t0-1 code)

Now, in window 2:

7. `cd /t0/t0_1/t0-1/`

8. `source .venv/bin/activate`

9. Run `./scripts/serve_rag_conversational.sh` to actually start up the t0-1 rag server.

## Running the frontend

Now, in window 3:

10. `cd /t0/t0_1/t0-1/`

11. `cd web`

12. You may need to install node and pnpm first (google this). Then you can run `pnpm install` to install the dependencies for the frontend. 

13. Run `pnpm dev` to start the frontend.

## DGX dashboard

The nvidia DGX dashboard is available at `http://localhost:11000/`. 
This shows the memory usage and GPU utilisation.

## Rebuilding the container image

To rebuild the docker image (e.g. if you make any changes to the code):
`sudo docker build ./docker -t t0-im --no-cache`



