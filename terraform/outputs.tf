output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID of the created resource group"
  value       = azurerm_resource_group.main.id
}

output "function_app_name" {
  description = "Name of the Function App"
  value       = azurerm_linux_function_app.main.name
}

output "function_app_id" {
  description = "ID of the Function App"
  value       = azurerm_linux_function_app.main.id
}

output "function_app_default_hostname" {
  description = "Default hostname of the Function App"
  value       = azurerm_linux_function_app.main.default_hostname
}

output "function_app_interactions_endpoint" {
  description = "Discord interactions endpoint URL"
  value       = "https://${azurerm_linux_function_app.main.default_hostname}/api/interactions"
}

output "function_app_health_check_endpoint" {
  description = "Health check endpoint URL"
  value       = "https://${azurerm_linux_function_app.main.default_hostname}/api/health"
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_connection_string" {
  description = "Primary connection string of the storage account"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "application_insights_name" {
  description = "Name of Application Insights instance"
  value       = azurerm_application_insights.main.name
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "app_service_plan_name" {
  description = "Name of the App Service Plan"
  value       = azurerm_service_plan.main.name
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.main.name
}

output "key_vault_id" {
  description = "ID of the Key Vault"
  value       = azurerm_key_vault.main.id
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics Workspace"
  value       = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_name" {
  description = "Name of the Log Analytics Workspace"
  value       = azurerm_log_analytics_workspace.main.name
}

# ============================================================================
# COSMOS DB OUTPUTS
# ============================================================================

output "cosmos_db_account_name" {
  description = "Cosmos DB account name"
  value       = azurerm_cosmosdb_account.main.name
}

output "cosmos_db_endpoint" {
  description = "Cosmos DB endpoint URL"
  value       = azurerm_cosmosdb_account.main.endpoint
  sensitive   = true
}

output "cosmos_db_primary_key" {
  description = "Cosmos DB primary key"
  value       = azurerm_cosmosdb_account.main.primary_key
  sensitive   = true
}

# ============================================================================
# DEPLOYMENT INFO
# ============================================================================

output "deployment_summary" {
  description = "Summary of the deployment"
  value = {
    environment           = var.environment
    location              = azurerm_resource_group.main.location
    resource_group        = azurerm_resource_group.main.name
    function_app_endpoint = "https://${azurerm_linux_function_app.main.default_hostname}/api/interactions"
    database_type         = "cosmos"
    application_insights  = azurerm_application_insights.main.name
    key_vault             = azurerm_key_vault.main.name
  }
}

output "next_steps" {
  description = "Next steps after infrastructure creation"
  value       = <<-EOT
    1. Update Discord Developer Portal:
       - Set INTERACTIONS ENDPOINT URL to: https://${azurerm_linux_function_app.main.default_hostname}/api/interactions
       - Verify the endpoint in Discord Developer Portal

    2. Deploy Function App code:
       - Run: func azure functionapp publish ${azurerm_linux_function_app.main.name}

    3. Monitor logs:
       - Open Application Insights: ${azurerm_application_insights.main.name}
       - Or check: Log Analytics Workspace: ${azurerm_log_analytics_workspace.main.name}

    4. Test the bot:
       - Run /help in your Discord server
       - Check logs for errors
  EOT
}
