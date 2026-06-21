variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name (dev, stg, prd)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "stg", "prd"], var.environment)
    error_message = "Environment must be dev, stg, or prd."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-bloom-discord-bot-eus-01"
}

variable "function_app_name" {
  description = "Name of the Function App"
  type        = string
  default     = "fa-bloom-discord-bot-eus-01"
}

variable "storage_account_name" {
  description = "Name of the storage account (must be globally unique, lowercase)"
  type        = string
  default     = "stbloomdiscordboteus01"
  validation {
    condition     = length(var.storage_account_name) >= 3 && length(var.storage_account_name) <= 24
    error_message = "Storage account name must be 3-24 characters."
  }
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = "asp-bloom-discord-bot-eus-01"
}

variable "discord_public_key" {
  description = "Discord bot public key from Developer Portal"
  type        = string
  sensitive   = true
}

variable "discord_bot_token" {
  description = "Discord bot token (for reference, not used in Function App)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "cosmos_db_name" {
  description = "Name of Cosmos DB account"
  type        = string
  default     = "cosmos-bloom-discord-bot-eus-01"
}

variable "python_version" {
  description = "Python version for Function App"
  type        = string
  default     = "3.11"
}

variable "function_app_sku" {
  description = "SKU for Function App (Y1 = consumption, B1 = basic, P1V2 = premium)"
  type        = string
  default     = "Y1"
  validation {
    condition     = contains(["Y1", "B1", "B2", "B3", "P1V2", "P2V2", "P3V2"], var.function_app_sku)
    error_message = "Invalid SKU for Function App."
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Discord-Bot"
    Environment = "prd"
    ManagedBy   = "Terraform"
  }
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}
