#!/bin/bash
set -e

# Script to build and push Docker images to Azure Container Registry
# Usage: ./scripts/build-and-push.sh [backend|frontend|all] [tag]

COMPONENT=${1:-all}
TAG=${2:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if ACR login server is set
if [ -z "$ACR_LOGIN_SERVER" ]; then
    log_error "ACR_LOGIN_SERVER environment variable is not set"
    log_info "Get it from Terraform output: terraform -chdir=terraform output -raw acr_login_server"
    log_info "Then export it: export ACR_LOGIN_SERVER=<value>"
    exit 1
fi

# Login to ACR
log_info "Logging in to Azure Container Registry..."
az acr login --name ${ACR_LOGIN_SERVER%%.*}

build_and_push_backend() {
    log_info "Building backend Docker image for linux/amd64..."
    docker buildx build --platform linux/amd64 \
        -t ${ACR_LOGIN_SERVER}/pagent-backend:${TAG} \
        -t ${ACR_LOGIN_SERVER}/pagent-backend:latest \
        -f backend/Dockerfile \
        --push \
        backend/

    log_info "Backend image built and pushed successfully!"
}

build_and_push_frontend() {
    log_info "Building frontend Docker image for linux/amd64..."

    # Get backend URL from environment or use default
    BACKEND_URL=${BACKEND_URL:-"https://pagent-backend.azurewebsites.net"}

    docker buildx build --platform linux/amd64 \
        -t ${ACR_LOGIN_SERVER}/pagent-frontend:${TAG} \
        -t ${ACR_LOGIN_SERVER}/pagent-frontend:latest \
        --build-arg VITE_API_BASE_URL=${BACKEND_URL} \
        -f frontend/Dockerfile \
        --push \
        frontend/

    log_info "Frontend image built and pushed successfully!"
}

case $COMPONENT in
    backend)
        build_and_push_backend
        ;;
    frontend)
        build_and_push_frontend
        ;;
    all)
        build_and_push_backend
        build_and_push_frontend
        ;;
    *)
        log_error "Invalid component: $COMPONENT"
        log_info "Usage: $0 [backend|frontend|all] [tag]"
        exit 1
        ;;
esac

log_info "All operations completed successfully!"
log_info "You can now restart the Web Apps to pull the new images:"
log_info "  az webapp restart --name pagent-backend --resource-group pagent-rg"
log_info "  az webapp restart --name pagent-frontend --resource-group pagent-rg"
