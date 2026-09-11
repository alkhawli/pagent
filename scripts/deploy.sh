#!/bin/bash
set -e

# Complete deployment script: build, push, and deploy
# Usage: ./scripts/deploy.sh [tag]

TAG=${1:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Get Terraform outputs
log_step "Getting Terraform outputs..."
cd terraform

if [ ! -f "terraform.tfstate" ]; then
    log_error "Terraform state not found. Please run 'terraform apply' first."
    exit 1
fi

export ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)
BACKEND_WEBAPP_NAME=$(terraform output -raw backend_webapp_name)
FRONTEND_WEBAPP_NAME=$(terraform output -raw frontend_webapp_name)
RESOURCE_GROUP=$(terraform output -raw resource_group_name)
BACKEND_URL=$(terraform output -raw backend_url)

cd ..

log_info "ACR Login Server: $ACR_LOGIN_SERVER"
log_info "Backend Web App: $BACKEND_WEBAPP_NAME"
log_info "Frontend Web App: $FRONTEND_WEBAPP_NAME"
log_info "Resource Group: $RESOURCE_GROUP"

# Build and push images
log_step "Building and pushing Docker images..."
export BACKEND_URL=$BACKEND_URL
./scripts/build-and-push.sh all $TAG

# Wait a moment for images to be available
log_info "Waiting for images to be available in ACR..."
sleep 5

# Update Web App configurations to use the new tag
log_step "Updating Web App configurations..."

log_info "Updating backend Web App..."
az webapp config container set \
    --name $BACKEND_WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name ${ACR_LOGIN_SERVER}/pagent-backend:${TAG}

log_info "Updating frontend Web App..."
az webapp config container set \
    --name $FRONTEND_WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name ${ACR_LOGIN_SERVER}/pagent-frontend:${TAG}

# Restart Web Apps
log_step "Restarting Web Apps..."

log_info "Restarting backend..."
az webapp restart \
    --name $BACKEND_WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP

log_info "Restarting frontend..."
az webapp restart \
    --name $FRONTEND_WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP

# Show deployment info
log_step "Deployment completed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Frontend URL: $BACKEND_URL"
echo "  Backend URL:  $(cd terraform && terraform output -raw frontend_url)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_info "Monitor deployment logs with:"
echo "  az webapp log tail --name $BACKEND_WEBAPP_NAME --resource-group $RESOURCE_GROUP"
echo "  az webapp log tail --name $FRONTEND_WEBAPP_NAME --resource-group $RESOURCE_GROUP"
