backend_port := "8020"
frontend_port := "5173"

# ============================================================================
# Docker Commands (Cross-platform: macOS, Linux, Windows)
# ============================================================================

# Default recipe - show available commands
default:
    @just --list

# Quick setup: Build and start Docker containers
setup: docker-up

# Build Docker images
docker-build:
    docker compose build

# Start containers in background (build if needed, install deps first)
docker-up: docker-build
    docker compose up -d
    @echo "✓ Containers started!"
    @echo "Backend:  http://localhost:{{backend_port}}"
    @echo "Frontend: http://localhost:{{frontend_port}}"

# Stop containers
docker-down:
    docker compose down

# Stop and remove containers with volumes
docker-clean:
    docker compose down -v

# View container logs
docker-logs:
    docker compose logs -f

# Restart containers
docker-restart:
    docker compose restart

# Check container status
docker-status:
    docker compose ps

# ============================================================================
# Local Development (Without Docker)
# ============================================================================

# Install backend (uv) and frontend (npm) dependencies (macOS/Linux)
install:
    #!/usr/bin/env bash
    echo "Installing backend dependencies (uv sync)..."
    cd backend && uv sync && cd ..
    echo "Installing frontend dependencies (npm install)..."
    cd frontend && npm install

# Install dependencies (Windows)
install-win:
    #!powershell.exe -NoProfile
    Write-Host "Installing backend dependencies (uv sync)..."
    Push-Location backend
    uv sync
    Pop-Location
    Write-Host "Installing frontend dependencies (npm install)..."
    Push-Location frontend
    npm install
    Pop-Location

# Start backend (FastAPI) and frontend (Vite) in the background (macOS/Linux)
up:
    #!/usr/bin/env bash
    mkdir -p .run

    if [ -f .run/backend.pid ]; then
        echo "Backend already running (or stale .run/backend.pid). Run 'just down' first."
    else
        cd backend
        nohup uv run uvicorn app.main:app --host 127.0.0.1 --port {{backend_port}} > ../.run/backend.log 2>&1 &
        echo $! > ../.run/backend.pid
        cd ..
        echo "Backend started (PID $(cat .run/backend.pid)) at http://127.0.0.1:{{backend_port}}"
    fi

    if [ -f .run/frontend.pid ]; then
        echo "Frontend already running (or stale .run/frontend.pid). Run 'just down' first."
    else
        cd frontend
        nohup npm run dev > ../.run/frontend.log 2>&1 &
        echo $! > ../.run/frontend.pid
        cd ..
        echo "Frontend started (PID $(cat .run/frontend.pid)) at http://127.0.0.1:{{frontend_port}}"
    fi

# Start backend and frontend (Windows)
up-win:
    #!powershell.exe -NoProfile
    New-Item -ItemType Directory -Force -Path .run | Out-Null

    if (Test-Path .run/backend.pid) {
        Write-Host "Backend already running (or stale .run/backend.pid). Run 'just down-win' first."
    } else {
        $backend = Start-Process -FilePath "uv" -ArgumentList "run","uvicorn","app.main:app","--host","127.0.0.1","--port","{{backend_port}}" -WorkingDirectory "backend" -PassThru -WindowStyle Hidden
        Set-Content -Path .run/backend.pid -Value $backend.Id
        Write-Host "Backend started (PID $($backend.Id)) at http://127.0.0.1:{{backend_port}}"
    }

    if (Test-Path .run/frontend.pid) {
        Write-Host "Frontend already running (or stale .run/frontend.pid). Run 'just down-win' first."
    } else {
        $frontend = Start-Process -FilePath "cmd.exe" -ArgumentList "/c","npm","run","dev" -WorkingDirectory "frontend" -PassThru -WindowStyle Hidden
        Set-Content -Path .run/frontend.pid -Value $frontend.Id
        Write-Host "Frontend started (PID $($frontend.Id)) at http://127.0.0.1:{{frontend_port}}"
    }

# Stop backend and frontend (macOS/Linux)
down:
    #!/usr/bin/env bash
    for name in backend frontend; do
        pidfile=".run/$name.pid"
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" && echo "Stopped $name (PID $pid)"
            else
                echo "$name process $pid not running"
            fi
            rm "$pidfile"
        else
            echo "$name is not running (no $pidfile)"
        fi
    done

# Stop backend and frontend (Windows)
down-win:
    #!powershell.exe -NoProfile
    foreach ($name in "backend","frontend") {
        $pidFile = ".run/$name.pid"
        if (Test-Path $pidFile) {
            $procId = Get-Content $pidFile
            try {
                taskkill /PID $procId /T /F | Out-Null
                Write-Host "Stopped $name (PID $procId)"
            } catch {
                Write-Host "Could not stop $name (PID $procId): $_"
            }
            Remove-Item $pidFile -Force
        } else {
            Write-Host "$name is not running (no $pidFile)"
        }
    }

# Run backend tests (macOS/Linux)
test:
    #!/usr/bin/env bash
    cd backend && uv run pytest

# Run backend tests (Windows)
test-win:
    #!powershell.exe -NoProfile
    Push-Location backend
    uv run pytest
    Pop-Location

# Check whether backend/frontend are reachable (macOS/Linux)
status:
    #!/usr/bin/env bash
    echo "Checking backend..."
    curl -f -s http://127.0.0.1:{{backend_port}}/health && echo "Backend: healthy (http://127.0.0.1:{{backend_port}})" || echo "Backend: not reachable"
    echo "Checking frontend..."
    curl -f -s -o /dev/null http://127.0.0.1:{{frontend_port}} && echo "Frontend: reachable (http://127.0.0.1:{{frontend_port}})" || echo "Frontend: not reachable"

# Check status (Windows)
status-win:
    #!powershell.exe -NoProfile
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:{{backend_port}}/health" -TimeoutSec 3
        Write-Host "Backend: $($health.status) (http://127.0.0.1:{{backend_port}})"
    } catch {
        Write-Host "Backend: not reachable (http://127.0.0.1:{{backend_port}})"
    }
    try {
        Invoke-WebRequest "http://127.0.0.1:{{frontend_port}}" -TimeoutSec 3 -UseBasicParsing | Out-Null
        Write-Host "Frontend: reachable (http://127.0.0.1:{{frontend_port}})"
    } catch {
        Write-Host "Frontend: not reachable (http://127.0.0.1:{{frontend_port}})"
    }

# ============================================================================
# Azure Deployment Recipes
# ============================================================================

# Initialize Terraform
tf-init:
    cd terraform && terraform init

# Plan Terraform changes
tf-plan:
    cd terraform && terraform plan

# Apply Terraform configuration
tf-apply:
    cd terraform && terraform apply

# Destroy all Azure resources
tf-destroy:
    cd terraform && terraform destroy

# Show Terraform outputs
tf-output:
    cd terraform && terraform output

# Get ACR login server
acr-login:
    @cd terraform && terraform output -raw acr_login_server

# Get backend URL
backend-url:
    @cd terraform && terraform output -raw backend_url

# Get frontend URL
frontend-url:
    @cd terraform && terraform output -raw frontend_url

# Build and push backend image
build-backend TAG="latest":
    #!/usr/bin/env bash
    set -e
    export ACR_LOGIN_SERVER=$(cd terraform && terraform output -raw acr_login_server)
    ./scripts/build-and-push.sh backend {{TAG}}

# Build and push frontend image
build-frontend TAG="latest":
    #!/usr/bin/env bash
    set -e
    export ACR_LOGIN_SERVER=$(cd terraform && terraform output -raw acr_login_server)
    export BACKEND_URL=$(cd terraform && terraform output -raw backend_url)
    ./scripts/build-and-push.sh frontend {{TAG}}

# Build and push both images
build-all TAG="latest":
    #!/usr/bin/env bash
    set -e
    export ACR_LOGIN_SERVER=$(cd terraform && terraform output -raw acr_login_server)
    export BACKEND_URL=$(cd terraform && terraform output -raw backend_url)
    ./scripts/build-and-push.sh all {{TAG}}

# Deploy everything (build, push, restart)
deploy TAG="latest":
    ./scripts/deploy.sh {{TAG}}

# Restart backend web app
restart-backend:
    #!/usr/bin/env bash
    set -e
    WEBAPP_NAME=$(cd terraform && terraform output -raw backend_webapp_name)
    RG=$(cd terraform && terraform output -raw resource_group_name)
    az webapp restart --name $WEBAPP_NAME --resource-group $RG

# Restart frontend web app
restart-frontend:
    #!/usr/bin/env bash
    set -e
    WEBAPP_NAME=$(cd terraform && terraform output -raw frontend_webapp_name)
    RG=$(cd terraform && terraform output -raw resource_group_name)
    az webapp restart --name $WEBAPP_NAME --resource-group $RG

# Restart both web apps
restart-all: restart-backend restart-frontend

# View backend logs
logs-backend:
    #!/usr/bin/env bash
    set -e
    WEBAPP_NAME=$(cd terraform && terraform output -raw backend_webapp_name)
    RG=$(cd terraform && terraform output -raw resource_group_name)
    az webapp log tail --name $WEBAPP_NAME --resource-group $RG

# View frontend logs
logs-frontend:
    #!/usr/bin/env bash
    set -e
    WEBAPP_NAME=$(cd terraform && terraform output -raw frontend_webapp_name)
    RG=$(cd terraform && terraform output -raw resource_group_name)
    az webapp log tail --name $WEBAPP_NAME --resource-group $RG

# Check backend status on Azure
status-backend-azure:
    #!/usr/bin/env bash
    set -e
    WEBAPP_NAME=$(cd terraform && terraform output -raw backend_webapp_name)
    RG=$(cd terraform && terraform output -raw resource_group_name)
    az webapp show --name $WEBAPP_NAME --resource-group $RG --query "{name:name, state:state, url:defaultHostName}"

# Check frontend status on Azure
status-frontend-azure:
    #!/usr/bin/env bash
    set -e
    WEBAPP_NAME=$(cd terraform && terraform output -raw frontend_webapp_name)
    RG=$(cd terraform && terraform output -raw resource_group_name)
    az webapp show --name $WEBAPP_NAME --resource-group $RG --query "{name:name, state:state, url:defaultHostName}"

# Check status of both Azure apps
status-azure: status-backend-azure status-frontend-azure

# List ACR repositories
acr-repos:
    #!/usr/bin/env bash
    set -e
    ACR_NAME=$(cd terraform && terraform output -raw acr_login_server | cut -d. -f1)
    az acr repository list --name $ACR_NAME -o table

# List backend image tags
acr-tags-backend:
    #!/usr/bin/env bash
    set -e
    ACR_NAME=$(cd terraform && terraform output -raw acr_login_server | cut -d. -f1)
    az acr repository show-tags --name $ACR_NAME --repository pagent-backend -o table

# List frontend image tags
acr-tags-frontend:
    #!/usr/bin/env bash
    set -e
    ACR_NAME=$(cd terraform && terraform output -raw acr_login_server | cut -d. -f1)
    az acr repository show-tags --name $ACR_NAME --repository pagent-frontend -o table

# Add a secret to Key Vault
kv-set-secret NAME VALUE:
    #!/usr/bin/env bash
    set -e
    KV_NAME=$(cd terraform && terraform output -raw key_vault_name)
    az keyvault secret set --vault-name $KV_NAME --name "{{NAME}}" --value "{{VALUE}}"

# Fix MCP configuration in Azure Key Vault (for deployed app)
fix-mcp-azure:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Updating MCP configuration in Azure Key Vault..."
    KV_NAME=$(cd terraform && terraform output -raw key_vault_name)
    echo "Key Vault: $KV_NAME"
    echo "Setting MCP_COMMAND..."
    az keyvault secret set --vault-name "$KV_NAME" --name "MCP-COMMAND" --value "/app/.venv/bin/python" --output none
    echo "Setting MCP_ARGS..."
    az keyvault secret set --vault-name "$KV_NAME" --name "MCP-ARGS" --value "-m untis_mcp.server" --output none
    echo "Setting MCP_STARTUP_TIMEOUT_SECONDS..."
    az keyvault secret set --vault-name "$KV_NAME" --name "MCP-STARTUP-TIMEOUT-SECONDS" --value "60" --output none
    echo ""
    echo "✅ MCP configuration updated!"
    echo "Restarting backend to apply changes..."
    just restart-backend
    echo ""
    echo "Check logs with: just logs-backend"

# Get a secret from Key Vault
kv-get-secret NAME:
    #!/usr/bin/env bash
    set -e
    KV_NAME=$(cd terraform && terraform output -raw key_vault_name)
    az keyvault secret show --vault-name $KV_NAME --name "{{NAME}}" --query value -o tsv

# List all Key Vault secrets
kv-list:
    #!/usr/bin/env bash
    set -e
    KV_NAME=$(cd terraform && terraform output -raw key_vault_name)
    az keyvault secret list --vault-name $KV_NAME -o table

# Open backend URL in browser
open-backend-azure:
    #!/usr/bin/env bash
    BACKEND_URL=$(cd terraform && terraform output -raw backend_url)
    open $BACKEND_URL

# Open frontend URL in browser
open-frontend-azure:
    #!/usr/bin/env bash
    FRONTEND_URL=$(cd terraform && terraform output -raw frontend_url)
    open $FRONTEND_URL

# Setup: Initialize and apply Terraform
azure-setup:
    @echo "Setting up Azure infrastructure..."
    just tf-init
    just tf-apply
    @echo ""
    @echo "✓ Infrastructure created!"
    @echo "Next steps:"
    @echo "  1. Run: just deploy"
    @echo "  2. Check status: just status-azure"
    @echo "  3. Open frontend: just open-frontend-azure"

# Full deployment workflow
azure-deploy TAG="latest":
    @echo "Starting full deployment..."
    just tf-apply
    just build-all {{TAG}}
    just restart-all
    @echo ""
    @echo "✓ Deployment complete!"
    just status-azure

# Health check Azure apps
health-azure:
    #!/usr/bin/env bash
    set -e
    BACKEND_URL=$(cd terraform && terraform output -raw backend_url)
    echo "Checking backend health..."
    curl -f -s ${BACKEND_URL}/health || echo "Backend health check failed"
    echo ""
    echo "Checking frontend..."
    FRONTEND_URL=$(cd terraform && terraform output -raw frontend_url)
    curl -f -s -o /dev/null ${FRONTEND_URL} && echo "Frontend is responding" || echo "Frontend check failed"

# Show deployment info
azure-info:
    #!/usr/bin/env bash
    set -e
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  PAGENT Azure Deployment Information"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Resource Group: $(cd terraform && terraform output -raw resource_group_name)"
    echo "ACR Server:     $(cd terraform && terraform output -raw acr_login_server)"
    echo "Key Vault:      $(cd terraform && terraform output -raw key_vault_name)"
    echo ""
    echo "Backend:        $(cd terraform && terraform output -raw backend_url)"
    echo "Frontend:       $(cd terraform && terraform output -raw frontend_url)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
