# GitHub Actions Setup Guide

## Required Secrets

Add these secrets in your GitHub repository:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### AZURE_CREDENTIALS

Create a service principal with the Azure CLI:

```bash
az ad sp create-for-rbac \
  --name "github-actions-pagent" \
  --role contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/pagent-rg \
  --sdk-auth
```

Copy the entire JSON output and paste it as the `AZURE_CREDENTIALS` secret.

The output should look like:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  "activeDirectoryEndpointUrl": "...",
  "resourceManagerEndpointUrl": "...",
  "activeDirectoryGraphResourceId": "...",
  "sqlManagementEndpointUrl": "...",
  "galleryEndpointUrl": "...",
  "managementEndpointUrl": "..."
}
```

## Workflow Triggers

The CI/CD pipeline runs on:
- **Push to master**: Full deployment (quality checks → build → deploy)
- **Pull requests**: Quality checks only (no deployment)
- **Manual**: `workflow_dispatch` (Actions tab → Run workflow)

## Pipeline Stages

### 1. Backend Quality Checks
- Python 3.13 with uv
- Run pytest
- Ruff linting

### 2. Frontend Quality Checks  
- Node.js 22
- npm ci (install dependencies)
- Lint with oxlint
- Build check

### 3. Build & Push (master only)
- Build Docker images for linux/amd64
- Push to Azure Container Registry
- Tag with `latest` and commit SHA
- Uses GitHub Actions cache for faster builds

### 4. Deploy (master only)
- Restart Azure Web Apps
- Wait 60s for startup
- Health check backend and frontend
- Post deployment summary

## Monitoring

- **GitHub Actions**: Check the Actions tab for pipeline status
- **Azure Logs**: `just logs-backend` or `just logs-frontend`
- **Health Status**: Pipeline includes automated health checks

## Troubleshooting

### Service Principal Permissions

If deployment fails with permission errors, ensure the service principal has:
```bash
# Contributor on resource group
az role assignment create \
  --assignee <SERVICE_PRINCIPAL_CLIENT_ID> \
  --role "Contributor" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/pagent-rg

# AcrPush on container registry
az role assignment create \
  --assignee <SERVICE_PRINCIPAL_CLIENT_ID> \
  --role "AcrPush" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/pagent-rg/providers/Microsoft.ContainerRegistry/registries/pagentacr46073
```

### Failed Health Checks

If health checks fail after deployment:
1. Check Azure Web App logs: `just logs-backend`
2. Verify app is running: `az webapp show --name pagent-backend --resource-group pagent-rg`
3. Restart manually: `just restart-backend`

### Build Cache Issues

Clear GitHub Actions cache:
1. Go to Actions tab
2. Click "Caches" in sidebar
3. Delete old caches
