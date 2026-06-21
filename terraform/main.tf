# Bloom Discord Bot serverless infrastructure

# Current Azure context
data "azurerm_client_config" "current" {}

# Resource group

resource "azurerm_resource_group" "main" {
  name     = "${var.resource_group_name}-${var.environment}"
  location = var.location
  tags     = var.tags
}

# Storage account

resource "azurerm_storage_account" "main" {
  name                     = "${replace(var.storage_account_name, "-", "")}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  tags = var.tags
}

# Application Insights

resource "azurerm_application_insights" "main" {
  name                = "${var.function_app_name}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  retention_in_days   = var.log_retention_days

  tags = var.tags
}

# App Service plan

resource "azurerm_service_plan" "main" {
  name                = "${var.app_service_plan_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.function_app_sku

  tags = var.tags
}

# Function App

resource "azurerm_linux_function_app" "main" {
  name                = "${var.function_app_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  storage_account_name       = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key

  site_config {
    application_stack {
      python_version = var.python_version
    }

    # Performance and monitoring
    application_insights_key               = azurerm_application_insights.main.instrumentation_key
    application_insights_connection_string = azurerm_application_insights.main.connection_string
  }

  app_settings = {
    DISCORD_PUBLIC_KEY = var.discord_public_key
    DB_TYPE            = "cosmos"

    # Cosmos DB settings
    COSMOS_ENDPOINT = azurerm_cosmosdb_account.main.endpoint
    COSMOS_KEY      = azurerm_cosmosdb_account.main.primary_key

    # Functions runtime
    FUNCTIONS_WORKER_RUNTIME = "python"
    AzureWebJobsStorage      = azurerm_storage_account.main.primary_blob_connection_string
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Cosmos DB resources

resource "azurerm_cosmosdb_account" "main" {
  name                = "${var.cosmos_db_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }

  tags = var.tags
}

# Cosmos DB database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "bloom"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

# Cosmos DB contributors container
resource "azurerm_cosmosdb_sql_container" "contributors" {
  name                = "contributors"
  database_name       = azurerm_cosmosdb_sql_database.main.name
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  partition_key_paths = ["/guild_id"]

  indexing_policy {
    indexing_mode = "consistent"
  }
}

# Key Vault

resource "azurerm_key_vault" "main" {
  name                = "bloom-kv-${var.environment}-${random_string.keyvault_suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions    = ["Get", "List", "Create", "Delete", "Update"]
    secret_permissions = ["Get", "List", "Set", "Delete"]
  }

  # Allow Function App to read secrets.
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_linux_function_app.main.identity[0].principal_id

    secret_permissions = ["Get", "List"]
  }

  tags = var.tags
}

# Store Discord public key in Key Vault
resource "azurerm_key_vault_secret" "discord_public_key" {
  name         = "discord-public-key"
  value        = var.discord_public_key
  key_vault_id = azurerm_key_vault.main.id
}

# Random suffix for globally unique Key Vault name

resource "random_string" "keyvault_suffix" {
  length  = 6
  special = false
  upper   = false
}

# Log Analytics workspace

resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.function_app_name}-logs-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days

  tags = var.tags
}
