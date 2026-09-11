# Azure Deployment Guide

Deploy PAGENT to Azure App Service with automated infrastructure provisioning.

## Prerequisites

- Azure CLI installed and authenticated: `az login`
- Docker installed (for building images)
- Terraform installed
- `just` command runner

## Quick Deploy

```bash
# 1. Initialize and create infrastructure
just tf-init
just tf-apply

# 2. Set secrets in Key Vault
just kv-set-secret WEBUNTIS-USER "your-username"
just kv-set-secret WEBUNTIS-PASSWORD "your-password"
just kv-set-secret AZURE-FOUNDRY-API-KEY "your-api-key"
just kv-set-secret API-KEY "EvncjKw_nyFiVM6rmYt-fud9v-XXHMheWsLU1EhqJug"

# 3. Build and deploy
just deploy

# 4. Check status
just status-azure
```

## Configuration

### terraform.tfvars

Edit `terraform/terraform.tfvars`:

```hcl
# Must be globally unique
acr_name = "pagentacr12345"
keyvault_name = "pagent-kv-12345"

# Adjust as needed
app_service_sku = "B1"  # Basic tier
location = "westeurope"
```

### Required Secrets

Store in Azure Key Vault:

```bash
# WebUntis
WEBUNTIS-SERVER
WEBUNTIS-SCHOOL
WEBUNTIS-USER
WEBUNTIS-PASSWORD

# Azure AI
AZURE-FOUNDRY-ENDPOINT
AZURE-FOUNDRY-API-KEY
AZURE-FOUNDRY-MODEL-DEPLOYMENT
AZURE-FOUNDRY-API-VERSION

# Authentication
API-KEY

# App Settings
APP-NAME
APP-HOST
APP-PORT
MCP-COMMAND
MCP-ARGS
MCP-STARTUP-TIMEOUT-SECONDS
```

## Architecture

- **Azure Container Registry** - Docker image storage with managed identity auth
- **Azure App Service (Linux)** - Backend and frontend hosting
- **Azure Key Vault** - Secret management
- **Managed Identity** - ACR authentication (no passwords needed)
- **Terraform** - Infrastructure as code

### Key Configuration Details

- **Docker Images**: Built for `linux/amd64` platform (Azure requirement)
- **ACR Authentication**: Uses managed identity (no username/password)
- **Image Tag**: Always use `latest` for deployments
- **Backend Port**: 8000 (internal), mapped via WEBSITES_PORT
- **Frontend Port**: 80 (nginx serves on port 80)

## Common Commands

```bash
# Deploy
just deploy              # Build, push, restart

# Monitor
just status-azure        # Check app status
just logs-backend        # View backend logs
just logs-frontend       # View frontend logs
just health-azure        # Health check

# Manage
just restart-all         # Restart both apps
just restart-backend     # Restart backend only
just restart-frontend    # Restart frontend only

# Info
just azure-info          # Show deployment info
just acr-repos           # List ACR repositories
just acr-tags-backend    # List backend tags
```

## Troubleshooting

### Deployment fails with "ImagePullFailure"

Ensure images are built for AMD64:
```bash
docker buildx build --platform linux/amd64 ...
```

### Container won't start

Check logs:
```bash
just logs-backend
az webapp log tail --name pagent-backend --resource-group pagent-rg
```

### 503 Service Unavailable

- Verify Key Vault access policy
- Check environment variables are loading
- Increase startup timeout if needed

### MCP connection errors

If you see "No module named untis_mcp.__main__" or MCP connection failures:

```bash
# Fix MCP configuration in Azure Key Vault
just fix-mcp-azure
```

This updates the MCP command to use the correct entry point (`untis_mcp.server`) and restarts the backend.

Other checks:
- Verify WebUntis credentials in Key Vault
- Check MCP_STARTUP_TIMEOUT_SECONDS (default: 60)
- Review container logs for MCP errors

## Costs

Estimated monthly cost (B1 tier):
- 2x App Service B1: ~$27/month
- Azure Container Registry Basic: ~$5/month
- Key Vault: <$1/month
- **Total: ~$33/month**

Scale up to P1V2 ($78/month per instance) for production.

## URLs

After deployment:
- Frontend: `https://pagent-frontend.azurewebsites.net`
- Backend: `https://pagent-backend.azurewebsites.net`
- Swagger: `https://pagent-backend.azurewebsites.net/docs`

## Important Notes

### Docker Platform
All images MUST be built for `linux/amd64` platform. The build scripts handle this automatically with `docker buildx build --platform linux/amd64`.

### ACR Authentication  
Uses managed identity - no manual password configuration needed. Terraform sets up:
- System-assigned managed identity on both web apps
- `AcrPull` role assignment for each app
- `acr_use_managed_identity_credentials = true` in app config

### Image Tags
Always use `latest` tag. The deployment scripts push both `latest` and timestamped tags.

### Nginx Configuration (Frontend)
The frontend Dockerfile creates nginx config directly in `/etc/nginx/conf.d/default.conf` (not using templates).

## Cleanup

To destroy all Azure resources:
```bash
just tf-destroy
```

**Warning:** This will delete everything, including Key Vault data.
