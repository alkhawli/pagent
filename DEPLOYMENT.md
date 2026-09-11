# PAGENT Azure Deployment Guide

Complete automation for deploying PAGENT backend and frontend to Azure Web Apps with Docker.

## Quick Start

### 1. Prerequisites

```bash
# Ensure you're logged in
az login

# Verify authentication
az account show
```

### 2. Configure Deployment

```bash
# Copy and edit Terraform variables
cd terraform
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars - REQUIRED CHANGES:
# - acr_name: Must be globally unique, alphanumeric only (e.g., "pagentacr12345")
# - keyvault_name: Must be globally unique, 3-24 chars (e.g., "pagent-kv-12345")
```

### 3. Deploy Infrastructure and Application

```bash
# One-command setup (creates all Azure resources)
just azure-setup

# After infrastructure is ready, deploy the application
just deploy

# Or do it all in one step
just azure-deploy
```

### 4. Access Your Application

```bash
# Show deployment info
just azure-info

# Open in browser
just open-frontend-azure
just open-backend-azure
```

## Available Commands

### Infrastructure Management

```bash
just tf-init              # Initialize Terraform
just tf-plan              # Preview infrastructure changes
just tf-apply             # Create/update infrastructure
just tf-destroy           # Delete all Azure resources
just tf-output            # Show all Terraform outputs
```

### Docker Image Management

```bash
just build-backend        # Build and push backend image
just build-frontend       # Build and push frontend image
just build-all           # Build and push both images
just build-all v1.0.0    # Build with specific tag

just acr-repos           # List all ACR repositories
just acr-tags-backend    # List backend image tags
just acr-tags-frontend   # List frontend image tags
```

### Application Deployment

```bash
just deploy              # Full deployment (build + push + restart)
just deploy v1.0.0       # Deploy with specific tag
just azure-deploy        # Full deployment including infrastructure update

just restart-backend     # Restart backend web app
just restart-frontend    # Restart frontend web app
just restart-all         # Restart both web apps
```

### Monitoring and Troubleshooting

```bash
just status-azure        # Check both web apps status
just health-azure        # Health check both apps
just azure-info          # Show deployment details

just logs-backend        # Tail backend logs (Ctrl+C to exit)
just logs-frontend       # Tail frontend logs (Ctrl+C to exit)

just backend-url         # Print backend URL
just frontend-url        # Print frontend URL
```

### Key Vault Secrets Management

```bash
just kv-set-secret api-key "your-secret-value"
just kv-get-secret api-key
just kv-list
```

To use Key Vault secrets in your app, reference them in `terraform.tfvars`:

```hcl
backend_env_vars = {
  "API_KEY" = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-12345.vault.azure.net/secrets/api-key/)"
}
```

Then apply: `just tf-apply`

## Configuration

### Environment Variables

Edit `terraform/terraform.tfvars` to configure:

**Backend environment variables:**
```hcl
backend_env_vars = {
  "ENVIRONMENT"    = "production"
  "PORT"           = "8000"
  "DATABASE_URL"   = "your-database-url"
  "API_KEY"        = "your-api-key"  # Or use Key Vault reference
}
```

**Frontend environment variables:**
```hcl
frontend_env_vars = {
  "CUSTOM_VAR" = "value"
  # API_BASE_URL is automatically set to backend URL
}
```

After changing variables:
```bash
just tf-apply
just restart-all
```

### Scaling

**Change App Service SKU:**

Edit `terraform/terraform.tfvars`:
```hcl
app_service_sku = "P1V2"  # or B1, B2, P2V2, etc.
```

Then apply:
```bash
just tf-apply
```

## Common Workflows

### Initial Deployment

```bash
# 1. Configure variables
cd terraform && cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 2. Setup infrastructure and deploy
just azure-setup
just deploy

# 3. Verify
just azure-info
just health-azure
```

### Update Application Code

```bash
# After making code changes
just deploy

# Or with a specific version tag
just deploy v1.0.1
```

### Update Configuration Only

```bash
# Edit terraform/terraform.tfvars
just tf-apply
just restart-all
```

### Add/Update Secrets

```bash
# Add secret to Key Vault
just kv-set-secret "db-password" "super-secret-password"

# Reference in terraform.tfvars
backend_env_vars = {
  "DATABASE_PASSWORD" = "@Microsoft.KeyVault(SecretUri=https://your-kv.vault.azure.net/secrets/db-password/)"
}

# Apply changes
just tf-apply
```

### View Application Logs

```bash
# Real-time backend logs
just logs-backend

# Real-time frontend logs
just logs-frontend
```

### Rollback to Previous Image

```bash
# List available tags
just acr-tags-backend
just acr-tags-frontend

# Deploy specific version
just deploy v1.0.0
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Resource Group                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐         ┌──────────────────────┐  │
│  │  Container Registry │         │     Key Vault        │  │
│  │  (ACR)              │         │  - ACR credentials   │  │
│  │  - backend:latest   │         │  - App secrets       │  │
│  │  - frontend:latest  │         │                      │  │
│  └─────────────────────┘         └──────────────────────┘  │
│           │                                  ▲               │
│           │ Pull images                      │ Read secrets │
│           ▼                                  │               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          App Service Plan (Linux)                   │   │
│  ├─────────────────────┬───────────────────────────────┤   │
│  │  Backend Web App    │    Frontend Web App           │   │
│  │  - FastAPI          │    - React + Nginx            │   │
│  │  - Port 8000        │    - Port 80                  │   │
│  │  - /health endpoint │    - Serves static files      │   │
│  │  - Managed Identity ├───▶ API_BASE_URL configured   │   │
│  └─────────────────────┴───────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Costs (Approximate)

- **Container Registry (Basic)**: ~$5/month
- **App Service Plan B1**: ~$13/month
- **Key Vault**: ~$0.03/10k operations

**Total: ~$18/month for Basic tier**

For production:
- **App Service Plan P1V2**: ~$73/month (includes auto-scaling, better performance)
- **Total: ~$78/month**

## Troubleshooting

### "ACR name already exists"
The ACR name must be globally unique across all Azure. Try adding random numbers:
```hcl
acr_name = "pagentacr47829"
```

### "Key Vault name already exists"
Similar issue - add a unique suffix:
```hcl
keyvault_name = "pagent-kv-47829"
```

### Web App not starting
```bash
# Check logs
just logs-backend
just logs-frontend

# Verify images exist
just acr-repos

# Check web app status
just status-azure
```

### Health check failing
```bash
# Test backend health endpoint
curl $(just backend-url)/health

# Check backend logs
just logs-backend
```

### Cannot connect to backend from frontend
The frontend automatically gets `API_BASE_URL` set to the backend URL. Verify:
```bash
just azure-info
```

## Security Best Practices

1. **Never commit** `terraform.tfvars` (it's in `.gitignore`)
2. **Use Key Vault** for all sensitive secrets
3. **Rotate credentials** regularly:
   ```bash
   az acr credential renew --name <acr-name> --password-name password
   ```
4. **Enable diagnostic logs** (for production):
   ```bash
   just logs-backend > backend-$(date +%Y%m%d).log &
   ```
5. **Use Managed Identities** (already configured) instead of connection strings where possible

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  TAG: ${{ github.sha }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Install just
        run: curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
      
      - name: Deploy
        run: |
          just tf-apply -auto-approve
          just deploy ${{ env.TAG }}
```

### Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: AzureCLI@2
  inputs:
    azureSubscription: 'your-service-connection'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
      just tf-apply -auto-approve
      just deploy $(Build.SourceVersion)
```

## Support

- **Terraform Issues**: [terraform/README.md](terraform/README.md)
- **Azure CLI**: Run `az --help` or check [Azure CLI docs](https://docs.microsoft.com/en-us/cli/azure/)
- **Just commands**: Run `just --list` to see all available commands
