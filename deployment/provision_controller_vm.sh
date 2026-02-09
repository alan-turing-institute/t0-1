#!/bin/bash
#
# This script creates a Ansible Control Node VM on Azure.
# It is predominantly a wrapper around the Azure CLI commands, and party
# exists becuase of problems installing Ansible Gallaxy Azure Collection
# on macOS.

# Assume these exist:
LOCATION="uksouth" # Check this exists in output to `az account list-locations`
SUBSCRIPTION_ID="5ae9b3e6-8784-437f-8725-9c05f55ba9b5"

# The following resources will be created if they do not already exist:
# - A Resource Group
# - A VM to use as an Ansible Control Node

# Define Resource Group name
RESOURCE_GROUP="t0-dev-deploy-rg"

# Define VM names
ANSIBLE_CONTROLLER_VM_NAME="quickstartansible"
RAG_CONVERSATION_VM_NAME="rag-conversational-vm"
T0_1_VM_NAME="t0-1-vm"
QWEN_WITH_TOOLS_VM_NAME="qwen-with-tools-vm"

# Private Virtual Network
VNET_NAME="t0-1-private-vnet"


# ERROR CODES
MISSING_AZURE_CLI=1
MISSING_JQ=2

AZURE_CLI_NOT_LOGGED_IN=10
INCORRECT_AZURE_SUBSCRIPTION=11

MISSING_RESOURCE_GROUP=20
MISSING_REVERSE_PROXY=21

# Check tool dependencies
echo "Checking preconditions..."
# Check Azure CLI
if ! command -v az &> /dev/null
then
    echo "⛔️ Azure CLI is not installed."
    exit $MISSING_AZURE_CLI
fi
echo "Azure CLI is installed"

# Check jq
if ! command -v jq &> /dev/null
then
    echo "⛔️ jq is not installed."
    exit $MISSING_JQ
fi
echo "jq is installed"

# Check login to Azure
# TODO - TO BE TESTED!!!
echo "Checking Azure CLI login..."
if ! az account show &> /dev/null
then
    echo "⛔️ Azure CLI is not logged in."
    exit $AZURE_CLI_NOT_LOGGED_IN
fi
echo "Azure CLI is logged in"

# Assert Azure subscription
echo "Checking Azure subscription..."
CURRENT_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
if [ "$CURRENT_SUBSCRIPTION_ID" != "$SUBSCRIPTION_ID" ]; then
  echo "⛔️ Incorrect default subscription (got: $CURRENT_SUBSCRIPTION_ID)"
  exit $INCORRECT_AZURE_SUBSCRIPTION
fi
echo "Default subscription is correct"

# Assert Resource Group
echo "Checking Resource Group..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null
then
    echo "⚠️ Resource Group $RESOURCE_GROUP does not exist."
    echo "Attempting to create Resource Group $RESOURCE_GROUP"
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi
echo "Resource Group $RESOURCE_GROUP exists."

##### 
# Now we can provision the VM etc
#####

# Get list of available sizes using:
# az vm list-sizes --location uksouth
# or:
# az vm list-sizes --location uksouth | jq "[.[] | select(.numberOfCores == 1)]"
default_size=Standard_D2s_v5 # default value of '--size' will be changed to 'Standard_D2s_v5' from 'Standard_DS1_v2' in a future release.

# Check the existence of the RAG Conversational VM
echo "Checking whether Controller VM exists..."
if ! az vm show --resource-group "$RESOURCE_GROUP" --name "$ANSIBLE_CONTROLLER_VM_NAME" &> /dev/null; then
    echo "Controller VM '$ANSIBLE_CONTROLLER_VM_NAME' does not exist. Creating it..."
    
    # echo "⛔️ VM creation is currently disabled to avoid unintended resource creation."
    # exit 0  # TEMPORARY EXIT TO AVOID UNINTENDED VM CREATION
    
    # TODO - Review all of the parameters here
    # Create the VM
    az vm create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$ANSIBLE_CONTROLLER_VM_NAME" \
      --image Ubuntu2204 \
      --custom-data controller_cloud_init.yaml \
      --size $default_size \
      --verbose

    echo "Controller VM '$ANSIBLE_CONTROLLER_VM_NAME' creation initiated."
else
    echo "Controller VM '$ANSIBLE_CONTROLLER_VM_NAME' already exists. Skipping creation."
    echo "🚨 No checks have been made on '$ANSIBLE_CONTROLLER_VM_NAME' sizing, configuration etc. 🚨"
fi
