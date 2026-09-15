# Terraform auto-loaded variables for production
# These values are safe to commit as they don't contain secrets

project_name        = "pagent"
resource_group_name = "pagent-rg"
location            = "westeurope"

# Must be globally unique, alphanumeric only (no hyphens)
acr_name = "pagentacr46073"

# Must be globally unique, 3-24 chars
keyvault_name = "pagent-kv-46073"

# Must be globally unique, 3-24 chars, lowercase/numbers only
storage_account_name = "pagentstorage46073"

# App Service Plan SKU
# B1 = Basic (dev/test), P1V2 = Premium (production)
app_service_sku = "B1"

# Docker image configuration
backend_image_name  = "pagent-backend"
backend_image_tag   = "latest"
frontend_image_name = "pagent-frontend"
frontend_image_tag  = "latest"

# Backend environment variables
# Using Key Vault references for secrets
backend_env_vars = {
  "ENVIRONMENT" = "production"
  "PORT"        = "8000"

  # App Configuration
  "APP_NAME" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/APP-NAME/)"
  "APP_HOST" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/APP-HOST/)"
  "APP_PORT" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/APP-PORT/)"
  "API_KEY"  = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/API-KEY/)"

  # MCP Configuration - using installed package instead of uvx
  "MCP_COMMAND"                 = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/MCP-COMMAND/)"
  "MCP_ARGS"                    = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/MCP-ARGS/)"
  "MCP_STARTUP_TIMEOUT_SECONDS" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/MCP-STARTUP-TIMEOUT-SECONDS/)"

  # WebUntis Credentials
  "WEBUNTIS_SERVER"   = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/WEBUNTIS-SERVER/)"
  "WEBUNTIS_SCHOOL"   = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/WEBUNTIS-SCHOOL/)"
  "WEBUNTIS_USER"     = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/WEBUNTIS-USER/)"
  "WEBUNTIS_PASSWORD" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/WEBUNTIS-PASSWORD/)"

  # Azure AI Foundry
  "AZURE_FOUNDRY_ENDPOINT"         = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/AZURE-FOUNDRY-ENDPOINT/)"
  "AZURE_FOUNDRY_API_KEY"          = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/AZURE-FOUNDRY-API-KEY/)"
  "AZURE_FOUNDRY_MODEL_DEPLOYMENT" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/AZURE-FOUNDRY-MODEL-DEPLOYMENT/)"
  "AZURE_FOUNDRY_API_VERSION"      = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-46073.vault.azure.net/secrets/AZURE-FOUNDRY-API-VERSION/)"
}

# Frontend environment variables
frontend_env_vars = {
  # API_BASE_URL is automatically set to the backend URL
}

tags = {
  "Environment" = "Production"
  "ManagedBy"   = "Terraform"
  "Project"     = "PAGENT"
}
