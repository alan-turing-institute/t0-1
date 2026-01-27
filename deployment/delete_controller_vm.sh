# Define Resource Group name
RESOURCE_GROUP="t0-dev-deploy-rg"

# az vm delete --verbose -g $RESOURCE_GROUP -n $ANSIBLE_CONTROLLER_VM_NAME
az group delete --name  $RESOURCE_GROUP
