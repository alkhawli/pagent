# Terraform backend configuration for remote state
# This storage account should be created FIRST before migrating state
# Run the bootstrap commands in the README before enabling this backend

terraform {
  backend "azurerm" {
    resource_group_name  = "pagent-tfstate-rg"
    storage_account_name = "pagenttfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}
