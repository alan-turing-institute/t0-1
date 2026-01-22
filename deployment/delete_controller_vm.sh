# Define Resource Group name
RESOURCE_GROUP="t0-dev-deploy-rg"

# Define VM names
ANSIBLE_CONTROLLER_VM_NAME="quickstartansible"

az vm delete --verbose -g $RESOURCE_GROUP -n $ANSIBLE_CONTROLLER_VM_NAME