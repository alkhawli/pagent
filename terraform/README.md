# PAGENT Azure Deployment with Terraform

This directory contains Terraform configurations to deploy the PAGENT application (backend and frontend) to Azure Web App services with automated Docker build and push.

## Architecture

- **Azure Container Registry (ACR)**: Stores Docker images for backend and frontend
- **Azure Key Vault**: Securely stores secrets (ACR credentials, API keys, etc.)
- **Azure App Service Plan**: Linux-based hosting plan for both web apps
- **Backend Web App**: FastAPI application running in a Docker container
- **Frontend Web App**: React + Nginx application running in a Docker container
- **Managed Identities**: Both web apps have system-assigned identities with Key Vault access

## Prerequisites

1. **Azure CLI** installed and authenticated:
   ```bash
   az login
   ```

2. **Terraform** installed (>= 1.0):
   ```bash
   brew install terraform  # macOS
   ```

3. **Docker** installed and running

## Initial Setup

### 1. Configure Terraform Variables

Copy the example variables file:
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and customize:
- `acr_name`: Must be globally unique, alphanumeric only (e.g., `pagentacr12345`)
- `keyvault_name`: Must be globally unique, 3-24 chars (e.g., `pagent-kv-12345`)
- `location`: Your preferred Azure region
- `app_service_sku`: `B1` for dev/test, `P1V2` for production

### 2. Add Secrets to Environment Variables

You can configure secrets in two ways:

#### Option A: App Service Configuration (Simpler)

Add secrets directly in `terraform.tfvars`:
```hcl
backend_env_vars = {
  "ENVIRONMENT"    = "production"
  "PORT"           = "8000"
  "API_KEY"        = "your-secret-api-key"
  "DATABASE_URL"   = "your-database-connection-string"
}
```

#### Option B: Key Vault References (More Secure)

First, add secrets to Key Vault after deployment:
```bash
# After terraform apply
az keyvault secret set --vault-name pagent-kv-12345 --name "api-key" --value "your-secret-value"
```

Then reference them in `terraform.tfvars`:
```hcl
backend_env_vars = {
  "ENVIRONMENT" = "production"
  "PORT"        = "8000"
  "API_KEY"     = "@Microsoft.KeyVault(SecretUri=https://pagent-kv-12345.vault.azure.net/secrets/api-key/)"
}
```

### 3. Initialize and Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply configuration
terraform apply
```

This will create:
- Resource Group
- Container Registry
- Key Vault (with ACR credentials stored)
- App Service Plan
- Backend Web App
- Frontend Web App
- Managed identities and access policies

## Building and Deploying Docker Images

### Quick Deploy (Recommended)

Use the automated deployment script:

```bash
# From project root
./scripts/deploy.sh

# Or with a specific tag
./scripts/deploy.sh v1.0.0
```

This script will:
1. Get ACR details from Terraform outputs
2. Build and push both Docker images
3. Update Web App configurations
4. Restart both web apps
5. Display deployment URLs

### Manual Build and Push

If you prefer to build and push manually:

```bash
# Export ACR login server
export ACR_LOGIN_SERVER=$(cd terraform && terraform output -raw acr_login_server)

# Export backend URL for frontend build
export BACKEND_URL=$(cd terraform && terraform output -raw backend_url)

# Build and push both images
./scripts/build-and-push.sh all

# Or build individually
./scripts/build-and-push.sh backend
./scripts/build-and-push.sh frontend

# Restart web apps to pull new images
az webapp restart --name pagent-backend --resource-group pagent-rg
az webapp restart --name pagent-frontend --resource-group pagent-rg
```

## Updating Configuration

### Update Environment Variables

1. Edit `terraform.tfvars` and modify `backend_env_vars` or `frontend_env_vars`
2. Apply changes:
   ```bash
   cd terraform
   terraform apply
   ```

### Update Docker Images

After code changes:
```bash
./scripts/deploy.sh v1.0.1
```

### Add Key Vault Secrets

```bash
# Get Key Vault name
KV_NAME=$(cd terraform && terraform output -raw key_vault_name)

# Add a secret
az keyvault secret set --vault-name $KV_NAME --name "my-secret" --value "secret-value"

# Reference it in terraform.tfvars
backend_env_vars = {
  "MY_SECRET" = "@Microsoft.KeyVault(SecretUri=https://${KV_NAME}.vault.azure.net/secrets/my-secret/)"
}

# Apply the change
cd terraform && terraform apply
```

## Monitoring and Troubleshooting

### View Application URLs

```bash
cd terraform
terraform output backend_url
terraform output frontend_url
```

### View Logs

```bash
# Backend logs
az webapp log tail --name pagent-backend --resource-group pagent-rg

# Frontend logs
az webapp log tail --name pagent-frontend --resource-group pagent-rg
```

### Check Deployment Status

```bash
# Backend status
az webapp show --name pagent-backend --resource-group pagent-rg --query state

# Frontend status
az webapp show --name pagent-frontend --resource-group pagent-rg --query state
```

### Access Key Vault Secrets

```bash
KV_NAME=$(cd terraform && terraform output -raw key_vault_name)
az keyvault secret list --vault-name $KV_NAME
az keyvault secret show --vault-name $KV_NAME --name "api-key"
```

### View Container Registry Images

```bash
ACR_NAME=$(cd terraform && terraform output -raw acr_login_server | cut -d. -f1)
az acr repository list --name $ACR_NAME
az acr repository show-tags --name $ACR_NAME --repository pagent-backend
az acr repository show-tags --name $ACR_NAME --repository pagent-frontend
```

## Cost Optimization

Current configuration uses:
- **ACR Basic**: ~$5/month
- **App Service Plan B1**: ~$13/month
- **Key Vault**: ~$0.03/10k operations

For production, consider:
- Upgrade to **P1V2** ($73/month) for better performance
- Use **ACR Standard** for geo-replication
- Enable **auto-scaling** for the App Service Plan

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy
        run: |
          cd terraform
          terraform init
          terraform apply -auto-approve
          cd ..
          ./scripts/deploy.sh ${{ github.sha }}
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

## Security Best Practices

1. **Never commit** `terraform.tfvars` to git (it's in `.gitignore`)
2. **Use Key Vault** for sensitive secrets instead of app settings
3. **Enable HTTPS only** (already configured)
4. **Use Managed Identities** for Azure service authentication (already configured)
5. **Regularly rotate** ACR credentials
6. **Enable diagnostic logs** for production environments

## Troubleshooting Common Issues

### "ACR name already exists"
The ACR name must be globally unique. Change `acr_name` in `terraform.tfvars`.

### "Key Vault name already exists"
The Key Vault name must be globally unique. Change `keyvault_name` in `terraform.tfvars`.

### "Web App not starting"
Check logs with `az webapp log tail` and verify:
- Docker image exists in ACR
- Environment variables are correct
- Health check endpoint (`/health`) is responding

### "Cannot connect to backend from frontend"
Ensure `API_BASE_URL` is set correctly. It's automatically configured but can be overridden in `frontend_env_vars`.

## Support

For issues specific to:
- **Terraform**: Check [Terraform Azure Provider docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- **Azure Web Apps**: Check [Azure App Service docs](https://docs.microsoft.com/en-us/azure/app-service/)
- **Docker**: Verify images build locally first
