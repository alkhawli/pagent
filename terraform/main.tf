terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Container Registry
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}

# Key Vault for secrets
resource "azurerm_key_vault" "kv" {
  name                       = var.keyvault_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  tags = var.tags
}

# Key Vault Access Policy for current user
resource "azurerm_key_vault_access_policy" "user" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Purge", "Recover"
  ]
}

# Store ACR credentials in Key Vault
resource "azurerm_key_vault_secret" "acr_username" {
  name         = "acr-username"
  value        = azurerm_container_registry.acr.admin_username
  key_vault_id = azurerm_key_vault.kv.id

  depends_on = [azurerm_key_vault_access_policy.user]
}

resource "azurerm_key_vault_secret" "acr_password" {
  name         = "acr-password"
  value        = azurerm_container_registry.acr.admin_password
  key_vault_id = azurerm_key_vault.kv.id

  depends_on = [azurerm_key_vault_access_policy.user]
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "${var.project_name}-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.app_service_sku
  tags                = var.tags
}

# Backend Web App
resource "azurerm_linux_web_app" "backend" {
  name                = "${var.project_name}-backend"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true
  tags                = var.tags

  site_config {
    always_on                         = true
    container_registry_use_managed_identity = true

    application_stack {
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
      docker_image_name   = "${var.backend_image_name}:${var.backend_image_tag}"
    }

    health_check_path                 = "/health"
    health_check_eviction_time_in_min = 10
  }

  app_settings = merge(
    var.backend_env_vars,
    {
      "WEBSITES_PORT"                       = "8000"
      "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
      "AZURE_STORAGE_ACCOUNT_NAME"          = azurerm_storage_account.app_storage.name
      "DASHBOARD_BLOB_CONTAINER"            = azurerm_storage_container.dashboard_data.name
      "MEAL_PLAN_BLOB_CONTAINER"            = azurerm_storage_container.meal_plans.name
      "NEWS_BLOB_CONTAINER"                 = azurerm_storage_container.news_data.name
      "TRENDS_BLOB_CONTAINER"               = azurerm_storage_container.trends_data.name
    }
  )

  identity {
    type = "SystemAssigned"
  }
}

# Key Vault Access Policy for Backend Web App
resource "azurerm_key_vault_access_policy" "backend" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = azurerm_linux_web_app.backend.identity[0].tenant_id
  object_id    = azurerm_linux_web_app.backend.identity[0].principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

# ACR Pull Role Assignment for Backend
resource "azurerm_role_assignment" "backend_acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_linux_web_app.backend.identity[0].principal_id
}

# Frontend Web App
resource "azurerm_linux_web_app" "frontend" {
  name                = "${var.project_name}-frontend"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true
  tags                = var.tags

  site_config {
    always_on                         = true
    container_registry_use_managed_identity = true

    application_stack {
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
      docker_image_name   = "${var.frontend_image_name}:${var.frontend_image_tag}"
    }
  }

  app_settings = merge(
    var.frontend_env_vars,
    {
      "WEBSITES_PORT"                       = "80"
      "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
      "API_BASE_URL"                        = "https://${azurerm_linux_web_app.backend.default_hostname}"
    }
  )

  identity {
    type = "SystemAssigned"
  }
}

# Key Vault Access Policy for Frontend Web App
resource "azurerm_key_vault_access_policy" "frontend" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = azurerm_linux_web_app.frontend.identity[0].tenant_id
  object_id    = azurerm_linux_web_app.frontend.identity[0].principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

# ACR Pull Role Assignment for Frontend
resource "azurerm_role_assignment" "frontend_acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_linux_web_app.frontend.identity[0].principal_id
}

# Storage Account for application data
resource "azurerm_storage_account" "app_storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  blob_properties {
    versioning_enabled = true
    delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

# Storage container for meal plans
resource "azurerm_storage_container" "meal_plans" {
  name                  = "meal-plans"
  storage_account_id    = azurerm_storage_account.app_storage.id
  container_access_type = "private"
}

# Storage container for dashboard (schedule/Untis) snapshots
resource "azurerm_storage_container" "dashboard_data" {
  name                  = "dashboard-data"
  storage_account_id    = azurerm_storage_account.app_storage.id
  container_access_type = "private"
}

# Storage container for daily news snapshots
resource "azurerm_storage_container" "news_data" {
  name                  = "news-data"
  storage_account_id    = azurerm_storage_account.app_storage.id
  container_access_type = "private"
}

# Storage container for weekly AI/GitHub trends snapshots
resource "azurerm_storage_container" "trends_data" {
  name                  = "trends-data"
  storage_account_id    = azurerm_storage_account.app_storage.id
  container_access_type = "private"
}

# Key-less blob access for the backend Web App via its managed identity
resource "azurerm_role_assignment" "backend_storage_blob" {
  scope                = azurerm_storage_account.app_storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_web_app.backend.identity[0].principal_id
}
