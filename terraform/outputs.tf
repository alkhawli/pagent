output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "acr_login_server" {
  description = "ACR login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "ACR admin username"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

output "acr_admin_password" {
  description = "ACR admin password"
  value       = azurerm_container_registry.acr.admin_password
  sensitive   = true
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = azurerm_key_vault.kv.name
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = azurerm_key_vault.kv.vault_uri
}

output "backend_url" {
  description = "Backend Web App URL"
  value       = "https://${azurerm_linux_web_app.backend.default_hostname}"
}

output "backend_webapp_name" {
  description = "Backend Web App name"
  value       = azurerm_linux_web_app.backend.name
}

output "frontend_url" {
  description = "Frontend Web App URL"
  value       = "https://${azurerm_linux_web_app.frontend.default_hostname}"
}

output "frontend_webapp_name" {
  description = "Frontend Web App name"
  value       = azurerm_linux_web_app.frontend.name
}

output "backend_identity_principal_id" {
  description = "Backend Web App managed identity principal ID"
  value       = azurerm_linux_web_app.backend.identity[0].principal_id
}

output "frontend_identity_principal_id" {
  description = "Frontend Web App managed identity principal ID"
  value       = azurerm_linux_web_app.frontend.identity[0].principal_id
}

output "storage_account_name" {
  description = "Name of the application storage account"
  value       = azurerm_storage_account.app_storage.name
}

output "storage_account_primary_key" {
  description = "Primary access key for the storage account"
  value       = azurerm_storage_account.app_storage.primary_access_key
  sensitive   = true
}

output "storage_account_connection_string" {
  description = "Connection string for the storage account"
  value       = azurerm_storage_account.app_storage.primary_connection_string
  sensitive   = true
}
