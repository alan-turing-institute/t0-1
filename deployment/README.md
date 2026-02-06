# Readme - Programmatic deployment

## Overview

The main components of t0 can be programmatically deployed to Azure using Ansible. These include:
* An Ansible "Control Node" (where we run the Ansible command and playbooks)
* One Ansible "Managed Node". This is a GPU-enabled VM which is created and managed by Ansible, and hosts `t0`.

## Prerequisites
To run the programmatic deployment of t0 you will need the following on your control node:
* Azure CLI (Install instructions) https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest
* Ansible (Control node install) https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html
* Ansible Azure Collection https://galaxy.ansible.com/ui/repo/published/azure/azcollection/
* `make` and `pandoc` on the. control node (to run the data download script)


I was not able to get the "Ansible Azure Collection" to run correctly on my Mac. Instead, I created a small Azure VM to serve as my control node. The control node can be recreated using the script `deployment/provision_controller_vm.sh`.

## Authentication
A complete solution would allow for authentication using an Azure Service Principal (https://learn.microsoft.com/en-us/azure/developer/ansible/create-ansible-service-principal?tabs=azure-cli). I do not have permission to create a Service Principal.

This process has been tested by manually authenticating the Azure CLI (using `az login`) on the control node before running the Ansible Playbooks.

## Connecting to the Ansible Control Node



## Deploying t0 (software, but not data)

The process of deploying t0 requires two playbooks. Run these, on the control node, from the root of the repository, in order:
```
$ ansible-playbook deployment/playbook_create_gpu_host.yaml
$ ansible-playbook deployment/playbook_deploy_t0.yaml
```

## Launching the app:

Login to the GPU VM using SSH, and follow the instructions in file 'serve_t0.md' under the headings "Serving the models / Default options". 

* First, ssh to the control node (see above for details).
* Then from the control node, ssh to the GPU VM using the command:
```
$ ssh ssh ansible@40.120.36.97 -i ~/ssh_keys/id_ed25519_t0_ansible
```
* Then switch to user `t0` to launch the app:
```
$ sudo -i -u t0
$ cd ~./t0-1
$ ./scripts/lanch-all-in-tmux.sh
```

* Wait for all three panes to show "Application startup complete". You should then be able to access the app at: https://alan-turing-institute.github.io/t0-1/


## Destroying the deployed resources

The expensive GPU VM can be destroyed using the script:
```
$ ./deployment/delete_gpu_resource_group.sh
```
The other resources are cheap to leave running, but can be deleted in the Azure Web Portal if desired.

## Explaination

How this works and why certain choices were made.... to be added.
