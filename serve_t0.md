# Serving t0

Note this is a longer version of the [Serving the rag model section of the README](https://github.com/alan-turing-institute/t0-1/tree/main?tab=readme-ov-file#serving-the-rag-model).

To serve the t0 RAG model, you should turn on the
[`t0-2`](https://portal.azure.com/#@turing.ac.uk/resource/subscriptions/5ae9b3e6-8784-437f-8725-9c05f55ba9b5/resourceGroups/s1-reproducing/providers/Microsoft.Compute/virtualMachines/t0-2/overview)[^1]
virtual machine on Azure by clicking "Start". 

In a minute, you will need to run three scripts (but don't do this yet):
- [scripts/serve_rag_conversational.sh](https://github.com/alan-turing-institute/t0-1/tree/main/scripts/serve_rag_conversational.sh): This sets up an endpoint for the RAG model and serves it using FastAPI
- [scripts/serve_t0_1.sh](https://github.com/alan-turing-institute/t0-1/tree/main/scripts/serve_t0_1.sh): This sets up a vLLM endpoint for [**t0-1.1-k5-32B**](https://huggingface.co/TomasLaz/t0-1.1-k5-32B)
- [scripts/serve_qwen_with_tools.sh](https://github.com/alan-turing-institute/t0-1/tree/main/scripts/serve_qwen_with_tools.sh): This sets up a vLLM endpoint for [**Qwen2.5-32B-Instruct**](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct) with tool calling

[^1]: For now, you need to use the `t0-2` machine because we have configured our front end to interact with an endpoint served from `t0-2`.

## Pre-requisites

Before running, you will need to set your public ssh key on the
server, set up your environment, and also set some environment
variables.

### 1. Add your SSH key to the server


1. ssh key. In the menu on the left, go to "Help" then "Reset
   password." Choose a new username, choose to add your existing
   public key, do that. 


**Via the Azure WebUI**

1. Navigate to the `t0` Azure subscription
2. Navigate to the `t0-2` VM (In the left-hand menu, select "Resources", then select the `t-02` Virtual Machine from the main panel)
3. Start the VM if necessary
4. In the left-hand menu for the `t0-2` Virtual Machine screen, selection "Help" and then "Reset password".
5. In the Reset password page: 
    * For the "Mode" option, select "Add SSH public key"
    * In "Username" add your preferred username
    * Select "SSH public key source" and related options to suit your needs
    * Press "Update"
6. Stop the VM if necessary


**Via the Azure CLI**

1. Login
```
az login
```


2. Ensure that your default subscription is `t0` (id `5ae9b3e6-8784-437f-8725-9c05f55ba9b5`). Either manually inspect the output of this command
```
az account show
```
Or more comprehensively:
```
az account show | jq -r '.id' | xargs test "5ae9b3e6-8784-437f-8725-9c05f55ba9b5" = && echo "default subscription is 't0' 🎉" || echo "⛔️ incorrect default subscription"
```

3. Now add your SSH public key to the `t0-2` VM:

<your-user-name> = your preferred username

`t0-2` is the resource name
`s1-reproducing` is the resource group

```
az vm user update -u <your-user-name> --ssh-key-value "$(< ~/.ssh/your_prefered_key_pair.pub)" -n t0-2 -g s1-reproducing
```

### 2. 
   
2. Log in: Go back to overview, find the machine's public ip, and log
   in to the server. 

1. Set up environment
    - Make sure you have [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed[^2]
    - Clone the repository and move to directory
        ```bash
        git clone git@github.com:alan-turing-institute/t0-1.git
        cd t0-1
        ```
	  (You will need to create a new GitHub access token and use it
        instead of a password to `git clone`. It's under your profile,
        Settings, Developer Settings.)

> [!NOTE]
> Does this just mean use `ssh` auth rather than `https` auth?
> Or if is really means a an access token, does it mean:
> * Fine-grained personal access tokens
 https://github.com/settings/personal-access-tokens
 > * Personal access tokens (classic)
 https://github.com/settings/tokens
> 
> Or is this another way to achieve the same thing as SSH Agent Forwarding:
> https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding


(Some repetition of instructions here)
- Create a virtual environment, activate it and install required dependencies (in editable mode) using [uv](https://github.com/astral-sh/uv):
        ```bash
        uv venv --python=3.12
        source .venv/bin/activate
        uv pip install -e ".[rag,dev]"
        ```
    - Once created, you should just be able to enter the environment by running `source .venv/bin/activate` from your local `t0-1` directory

1. Download the NHS conditions data - see the [Data section of the README](https://github.com/alan-turing-institute/t0-1/tree/main?tab=readme-ov-file#data). If you're a member of the Turing, you can download the data from the t0 sharepoint[^3]. Once downloaded, save it in `t0-1/data/nhs-conditions/v4/qwen_summarised_conditions.jsonl`

2. Set up `.env` file
    - You will need to create a `.env` file in your local `t0-1` directory. Create one and add the following lines to the file[^4]:
        ```
        OPENAI_API_KEY="-"
        OPENAI_BASE_URL_TomasLaz/t0-1.1-k5-32B="http://localhost:8010/v1/"
        OPENAI_BASE_URL_Qwen/Qwen2.5-32B-Instruct="http://localhost:8020/v1/"
        ```

3. Run all three scripts linked above. It is easiest to run these in different `screen` or `tmux` sessions[^5]:
    - For each script (`scripts/serve_t0_1.sh`, `scripts/serve_qwen_with_tools.sh`, `scripts/serve_rag_conversational.sh`)
        - `screen` to start a new terminal session
        - Make sure you're in your local `t0-1` directory
        - Activate your environment with `source .venv/bin/activate`
        - Run the script with `source <script_name>`

4. Once all scripts are running (note that the `serve_t0_1.sh` and `serve_qwen_with_tools.sh` may take a while, especially if it's your first time running them as they will be downloaded first), you should be able to interact with the model on the frontend.
    - If you have the different terminal screen sessions up, you will see logs of the incoming requests

[^2]: I recommend going with either the standalone installer (from the
    uv homepage) or using other package managers like `brew` over doing a pip install.
[^3]: Ask a t0 team member to direct you to the file. At time of writing, the file is in the `t0` Documents folder and the file is in `Documents/nhs-use-case/v4/qwen_summarised_conditions.jsonl`.
[^4]: You might think these environment variables don't look like valid environment variables, and you'd be correct. But for reading `.env` files in Python with `dotenv`, these essentially just get read as key-values in a dictionary, and they're fine for that. The ports here (8010 and 8020) are set in the `serve_t0.sh` and `serve_qwen_with_tools.sh` files respectively. We are using `vllm` to serve the models which is an OpenAI-compatible server. The API key set here could be anything, it just needs to be set to _something_.
[^5]: Alternatively, you could just open three terminals and ssh into `t0-2` three times, but it's not as nice and the scripts would end if you lost connection for whatever reason. In practice, I actually do this, but run `screen` for each script. That way, I can see all terminals at the same time and monitor the requests as they come in.
