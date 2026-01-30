# Serving t0

Note this is a longer version of the [Serving the rag model section of the README](https://github.com/alan-turing-institute/t0-1/tree/main?tab=readme-ov-file#serving-the-rag-model).


> [!WARNING]
> The instructions below will start an expensive VM running on Azure. You will continue to be billed for the VM until you deallocate the VM (just shutting down is not sufficient). To shutdown and deallocate the VM, use the following commands:
> ```
> az vm stop --resource-group s1-reproducing --name t0-2
> az vm deallocate --resource-group s1-reproducing --name t0-2
> ```

> [!NOTE]
> These instructions describe how to setup and run the `t0` models on a specific existing VM. (Hostname `t0-2` within the `t0` Azure subscription). The web front-end is preconfigured to work with this VM. The instructions do not cover how to provision a VM from scratch or how to update the web front-end to work with a new VM. 

## Pre-requisites

Before running, you will need to set your public ssh key on the server, set up your environment, and also set some environment variables.

### Add your SSH key to the server

1. ssh key. In the menu on the left, go to "Help" then "Reset password." Choose a new username, choose to add your existing public key, do that. 

**Via the Azure WebUI**

1. Navigate to the `t0` Azure subscription
2. Navigate to the `t0-2 `VM ([link](https://portal.azure.com/#@turing.ac.uk/resource/subscriptions/5ae9b3e6-8784-437f-8725-9c05f55ba9b5/resourceGroups/s1-reproducing/providers/Microsoft.Compute/virtualMachines/t0-2/overview)). (In the left-hand menu, select "Resources", then select the `t-02` Virtual Machine from the main panel)
3. Start the VM if necessary
4. In the left-hand menu for the `t0-2` Virtual Machine screen, selection "Help" and then "Reset password".
5. In the Reset password page: 
    * For the "Mode" option, select "Add SSH public key"
    * In "Username" add your preferred username
    * Select "SSH public key source" and related options to suit your needs
    * Press "Update"
6. Stop the VM if necessary

**Via the Azure CLI**

1. Login to Azure from the command line tool:
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

3. Ensure that the VM is started:

```
az vm start --resource-group s1-reproducing --name t0-2
```
   
5. Now add your SSH public key to the `t0-2` VM:

Use the command below to upload your SSH public, substituting values for `your-user-name` and `your_preferee_key_pair`:
* `<your-user-name>` = your preferred username
* `<~/.ssh/your_prefered_key_pair.pub>` = the path to public key you which to upload. This should be a key you can use to access GitHub.
* `t0-2` is the resource name
* `s1-reproducing` is the resource group

EITHER:
A. Confirm that you can access GitHub using your preferred key pair (See GitHub docs for debugging):

```
# Note: specify the key-pair WITHOUT the `.pub` suffix here
username@your-laptop:~$ ssh -T git@github.com -i ~/.ssh/your_prefered_key_pair -o IdentitiesOnly=yes
```

B. Then upload that key to the server.

```
# Note: specify the key-pair WITH the `.pub` siffix here
az vm user update -u <your-user-name> --ssh-key-value "$(< ~/.ssh/your_prefered_key_pair.pub)" -n t0-2 -g s1-reproducing
```

OR:

Directly load your public directly from GitHub:

* `<your-user-name>` = your preferred username on the server
* `<your-github-username>` = the path to public key you which to upload. This should be a key you can use to access GitHub.


https://github.com/andrewphilipsmith.keys

echo your keys are "$(curl --silent https://github.com/andrewphilipsmith.keys)"

```
az vm user update -u <your-user-name> --ssh-key-value "$(curl --silent https://github.com/<your-github-username>.keys)" -n t0-2 -g s1-reproducing
```



### 2. Confirm the server's IP address

The VM's public IP address should be 20.117.204.190. Confirm this, as the subsequent instructions assume it to be correct.

**Via the Azure CLI**

3.  Log in: Go back to overview, find the machine's public ip, and log
   in to the server. 

1. Get the public IP address of the machine:
```
az network public-ip list --resource-group s1-reproducing | jq --raw-output '.[] | select (.name == "t0-2-ip").ipAddress'
```


### Configure the server environment

These steps are only possible via the command line.

1. SSH into the machine:
   
* `<your-user-name>` = your preferred username
* `<ipaddress>` = the public IP address from the command above

```
ssh <your-user-name>@<ipaddress>
```

2. Setup SSH Agent Forwarding

Follow the instructions in GitHub's [Using SSH agent forwarding](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding) page. Confirm this is working correctly by connecting to the server via SSH and running this command:

```
a.smith@t0-2:~$ ssh -T git@github.com
```

3. Make sure you have [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed:
   
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> [!NOTE]
> This is the default method of installing `uv`. For a full explanation, including alternative installation methods see [the UV documentation](https://docs.astral.sh/uv/getting-started/installation/).
  
4. Clone the repository and move to directory
```bash
git clone git@github.com:alan-turing-institute/t0-1.git
cd t0-1
```

5. Install the t0-1 package in a local virtual environment:
   These commands create a local virtual environment, activate it and then install required dependencies (in editable mode) using [uv](https://github.com/astral-sh/uv):
```bash
uv venv --python=3.12
source .venv/bin/activate
uv sync --all-extras
```

> [!NOTE]
> Using `uv sync --all-extras` will install the exact versions of dependencies that were used when `t0` was last deployed.
> For developers, it may be more appropriate to install the dependencies by resolving the latest compatible versions using `uv pip install -e ".[rag,dev]"`.

6. Obtain the NHS conditions data - see the [Data section of the README](https://github.com/alan-turing-institute/t0-1/tree/main?tab=readme-ov-file#data) for details. There are three options for this:
   
* Run the `make download all` command directly on the server (fewest steps)
* Run the `make download all` command locally on your laptop and then upload the resulting file to the server (minimising time required on the expensive VM).
* If you're a member of the Turing, you can ask a t0 team member to direct you to the file. At time of writing, the file is on SharePoint, in the `t0` Documents folder, at this path `Documents/nhs-use-case/v4/qwen_summarised_conditions.jsonl`.

7. Copy the datafile to the correct location on the server. It should be in `~/t0-1/data/nhs-conditions/v4/qwen_summarised_conditions.jsonl`

To copy a local copy of the datafile to the server, use the following command (substituting suitable values for `<username>` and `<local/path/to/conditions.jsonl>`):
```
ssh <username>@20.117.204.190 'mkdir -p ~/t0-1/data/nhs-conditions/v4' && \
scp <local/path/to/conditions.jsonl> <username>@20.117.204.190:~/t0-1/data/nhs-conditions/v4/qwen_summarised_conditions.jsonl
```

8. Set up an `.env` file

The easiest way to create this is to copy the default file

```
cp .env.default .env
```

 Alternatively, you can manually create the file using `touch .env` and then open the file in an editor and add the following lines to the file[^4]:

```
OPENAI_API_KEY="-"
OPENAI_BASE_URL_TomasLaz/t0-1.1-k5-32B="http://localhost:8010/v1/"
OPENAI_BASE_URL_Qwen/Qwen2.5-32B-Instruct="http://localhost:8020/v1/"
```

> [!NOTE]
> These are not valid shell environment variables. However, they are permitted when reading a `.env` file in Python with `dotenv`. The `dotenv` standard treats these as just as a key-value pair in a dictionary, and the keys are accepted in this context. <br>
> The ports here (8010 and 8020) are set in the `serve_t0.sh` and `serve_qwen_with_tools.sh` files respectively. We are using `vllm` to serve the models, which is an OpenAI-compatible server. The API key value can be any non-empty, non-null string. It is not used to authenticate against OpenAI's API.


## Serving the models

### Default options

The simplest way to serve the models is to use the `launch-all-in-tmux.sh` script:

```
./scripts/launch-all-in-tmux.sh
```

This will create a new `tmux` session, with each of the three core scripts running in a separate pane.

### Details

There are three core long-running scripts, all of which must be running simultaneously:

- [scripts/serve_rag_conversational.sh](https://github.com/alan-turing-institute/t0-1/tree/main/scripts/serve_rag_conversational.sh): This sets up an endpoint for the RAG model and serves it using FastAPI
- [scripts/serve_t0_1.sh](https://github.com/alan-turing-institute/t0-1/tree/main/scripts/serve_t0_1.sh): This sets up a vLLM endpoint for [**t0-1.1-k5-32B**](https://huggingface.co/TomasLaz/t0-1.1-k5-32B)
- [scripts/serve_qwen_with_tools.sh](https://github.com/alan-turing-institute/t0-1/tree/main/scripts/serve_qwen_with_tools.sh): This sets up a vLLM endpoint for [**Qwen2.5-32B-Instruct**](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct) with tool calling

Run all three scripts must be running simultaneously. It is helpful for monitoring and debugging purposes to be able to see the logging output from each. The `launch-all-in-tmux.sh` achieves this using `tmux`; however, there are other ways to achieve the same goal.

For each script:
- Ensure you're in the repo's local `t0-1` directory
- Activate your environment with `source .venv/bin/activate`
- Run the script with `source ./scripts/<script_name>`

# Viewing the Web Interface

The web interface is available at:
https://alan-turing-institute.github.io/t0-1/

If you see the error message below, then the VM has not been set up correctly:
```
Failed to connect to backend at `https://t0-reverse-proxy.azurewebsites.net`. Please check if the backend is running. If you want to change the backend URL, please edit `web/src/App.svelte` and change the `HOST` constant.
```
