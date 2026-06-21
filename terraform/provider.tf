terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Uncomment to use remote state (Azure Storage Account)
  # backend "azurerm" {
  #   resource_group_name  = "bloom-terraform-state"
  #   storage_account_name = "bloomtfstate"
  #   container_name       = "tfstate"
  #   key                  = "discord-bot.tfstate"
  # }

  # For now, using local state file (terraform.tfstate)
}

provider "azurerm" {
  features {}

  subscription_id = var.azure_subscription_id
}
