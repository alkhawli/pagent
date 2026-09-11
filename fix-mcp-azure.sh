#!/usr/bin/env bash
# Fix MCP configuration in Azure Key Vault
set -euo pipefail

echo "Updating MCP configuration in Azure Key Vault..."

# Get Key Vault name from Terraform output
KV_NAME=$(cd terraform && terraform output -raw key_vault_name)

echo "Key Vault: $KV_NAME"

# Update MCP secrets with correct values for Docker container
echo "Setting MCP_COMMAND..."
az keyvault secret set --vault-name "$KV_NAME" \
    --name "MCP-COMMAND" \
    --value "/app/.venv/bin/python" \
    --output none

echo "Setting MCP_ARGS..."
az keyvault secret set --vault-name "$KV_NAME" \
    --name "MCP-ARGS" \
    --value "-m untis_mcp.server" \
    --output none

echo "Setting MCP_STARTUP_TIMEOUT_SECONDS..."
az keyvault secret set --vault-name "$KV_NAME" \
    --name "MCP-STARTUP-TIMEOUT-SECONDS" \
    --value "60" \
    --output none

echo ""
echo "✅ MCP configuration updated successfully!"
echo ""
echo "Next steps:"
echo "1. Restart the backend app:"
echo "   just restart-backend"
echo ""
echo "2. Check the logs:"
echo "   just logs-backend"
