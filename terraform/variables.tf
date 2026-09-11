variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "pagent"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "pagent-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "acr_name" {
  description = "Name of the Azure Container Registry (must be globally unique, alphanumeric only)"
  type        = string
  default     = "pagentacr"
}

variable "keyvault_name" {
  description = "Name of the Key Vault (must be globally unique, 3-24 chars)"
  type        = string
  default     = "pagent-kv"
}

variable "app_service_sku" {
  description = "SKU for the App Service Plan"
  type        = string
  default     = "B1" # Basic tier, can be changed to P1V2 for production
}

variable "backend_image_name" {
  description = "Docker image name for backend"
  type        = string
  default     = "pagent-backend"
}

variable "backend_image_tag" {
  description = "Docker image tag for backend"
  type        = string
  default     = "latest"
}

variable "frontend_image_name" {
  description = "Docker image name for frontend"
  type        = string
  default     = "pagent-frontend"
}

variable "frontend_image_tag" {
  description = "Docker image tag for frontend"
  type        = string
  default     = "latest"
}

variable "backend_env_vars" {
  description = "Environment variables for backend app"
  type        = map(string)
  default = {
    "ENVIRONMENT" = "production"
    "PORT"        = "8000"
  }
  sensitive = true
}

variable "frontend_env_vars" {
  description = "Environment variables for frontend app"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    "Environment" = "Production"
    "ManagedBy"   = "Terraform"
    "Project"     = "PAGENT"
  }
}
