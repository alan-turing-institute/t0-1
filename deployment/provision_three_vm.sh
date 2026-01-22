#!/bin/bash
#
# This script deploys the `t0-1` across three Azure VMs, with a private network between them.
# It is predominantly a wrapper around the Azure CLI commands.
#

# The following resources will be not be created, but their presence will be checked:
# - The Azure subscription to deploy to "5ae9b3e6-8784-437f-8725-9c05f55ba9b5"
# - A resource group named `s1-reproducing`
# - A reverse proxy
# - The web frontend

# Assume these exist:
RESOURCE_GROUP="s1-reproducing"
LOCATION="uk-south"
REVERSE_PROXY_NAME="t0-reverse-proxy"
SUBSCRIPTION_ID="5ae9b3e6-8784-437f-8725-9c05f55ba9b5"

# The following resources will be created if they do not already exist:
# - A VM for the RAG Conversational service
# - A VM for the t0-1 service
# - A VM for the Qwen with Tools service
# - A private Virtual Network to connect the VMs

# Define VM names
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
    echo "⛔️ Resource Group $RESOURCE_GROUP does not exist."
    exit $MISSING_RESOURCE_GROUP
fi
echo "Resource Group $RESOURCE_GROUP exists."

# Assert Reverse Proxy exists
echo "Checking Reverse Proxy..."
if ! az network vnet list --resource-group "$RESOURCE_GROUP" | jq ".[].name | contains('$REVERSE_PROXY_NAME')" | grep -q true;
then
  echo "⛔️ Reverse Proxy '$REVERSE_PROXY_NAME' does not exist."
  exit $MISSING_REVERSE_PROXY
fi
echo "Reverse Proxy '$REVERSE_PROXY_NAME' exists."

# Assert that the web frontend exists
# TODO - How to do this given it resides on GitHub Pages?


##### 
# Now we can provision the VMs etc
#####

# Check the existence of the RAG Conversational VM
echo "Checking whether RAG Conversational VM exists..."
if ! az vm show --resource-group "$RESOURCE_GROUP" --name "$RAG_CONVERSATION_VM_NAME" &> /dev/null; then
    echo "RAG Conversational VM '$RAG_CONVERSATION_VM_NAME' does not exist. Creating it..."
    
    echo "⛔️ VM creation is currently disabled to avoid unintended resource creation."
    exit 0  # TEMPORARY EXIT TO AVOID UNINTENDED VM CREATION
    
    # TODO - Review all of the parameters here
    # Create the VM
    az vm create \
      --resource-group "$RESOURCE_GROUP" \
      --name "$RAG_CONVERSATION_VM_NAME" \
      --image TBD \
      --admin-username TBD \
      --generate-ssh-keys \
      --location "$LOCATION" \
      --vnet-name "$VNET_NAME" \
      --subnet "default" \
      --no-wait

    echo "RAG Conversational VM '$RAG_CONVERSATION_VM_NAME' creation initiated."
else
    echo "RAG Conversational VM '$RAG_CONVERSATION_VM_NAME' already exists. Skipping creation."
    echo "🚨 No checks have been made on '$RAG_CONVERSATION_VM_NAME' sizing, configuration etc. 🚨"
fi
