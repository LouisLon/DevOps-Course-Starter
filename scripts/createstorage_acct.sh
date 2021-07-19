#!/bin/bash
read -p 'Azure resource group: ' RESOURCE_GROUP_NAME
echo
STORAGE_ACCOUNT_NAME=tfstate$RANDOM
CONTAINER_NAME=tfstate


echo $STORAGE_ACCOUNT_NAME
# Create storage account
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --sku Standard_LRS --encryption-services blob
# Create blob container
az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME

ACCOUNT_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP_NAME --account-name $STORAGE_ACCOUNT_NAME --query '[0].value' -o tsv)
echo $ACCOUNT_KEY
export ARM_ACCESS_KEY=$ACCOUNT_KEY
echo "Storage account $STORAGE_ACCOUNT_NAME created"