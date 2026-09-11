# PAGENT - WebUntis Parent Dashboard

A parent assistant chatbot for WebUntis with AI-powered Q&A and automated dashboard generation.

**Tech Stack:** FastAPI (Python) + Azure AI Foundry, React (TypeScript), MCP integration

## Features

- 📊 **Automated Dashboard** - Daily snapshots of homework, exams, and timetable
- 💬 **AI Chat Assistant** - Natural language queries about student's schedule
- 🔄 **WebUntis Integration** - Live data via MCP (Model Context Protocol)
- 🔐 **Secure** - API key authentication

## Live URLs

- **Frontend**: https://pagent-frontend.azurewebsites.net
- **Backend API**: https://pagent-backend.azurewebsites.net
- **API Docs**: https://pagent-backend.azurewebsites.net/docs

## Quick Start

### Local Development

```bash
# Using Docker (recommended)
just docker-up

# Without Docker (macOS/Linux)
just install && just up

# Without Docker (Windows)
just install-win && just up-win
```

**Access the app:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8020

### Configuration

Create `backend/.env`:
```env
# WebUntis
WEBUNTIS_SERVER=your-server.webuntis.com
WEBUNTIS_SCHOOL=your-school
WEBUNTIS_USER=your-username
WEBUNTIS_PASSWORD=your-password

# Azure AI Foundry
AZURE_FOUNDRY_ENDPOINT=https://...
AZURE_FOUNDRY_API_KEY=...
AZURE_FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini

# API Key
API_KEY=your-api-key-here
```

## Deployment

**Automated CI/CD via GitHub Actions** 🚀

Every push to `master` triggers:
1. Quality checks (tests, linting)
2. Docker image builds
3. Push to Azure Container Registry
4. Deploy to Azure Web Apps
5. Health checks

See [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) for setup instructions.

## Commands

```bash
# Local Development
just docker-up          # Start with Docker
just docker-down        # Stop containers
just docker-logs        # View logs

# Azure
just status-azure       # Check deployment status
just logs-backend       # View backend logs
just restart-backend    # Restart backend
just tf-init            # Initialize Terraform
just tf-apply           # Apply infrastructure
```

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Azure infrastructure setup
- [GitHub Actions](docs/GITHUB_ACTIONS.md) - CI/CD pipeline configuration
- [DevOps Summary](docs/DEVOPS_SUMMARY.md) - Complete DevOps overview

## Architecture

- **Backend**: FastAPI + MCP (WebUntis data)
- **Frontend**: React + TypeScript + Vite
- **Infrastructure**: Azure Container Apps + Key Vault + ACR
- **CI/CD**: GitHub Actions
- **Authentication**: Managed Identity (ACR) + API Keys

## License

Private project
