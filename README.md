# PAGENT - WebUntis Parent Dashboard

A parent assistant chatbot for WebUntis, featuring AI-powered Q&A and automated dashboard generation.

**Tech Stack:** FastAPI (Python) backend with Azure AI Foundry, React (TypeScript) frontend, MCP integration for WebUntis data.

## Features

- 📊 **Automated Dashboard** - Daily snapshots of homework, exams, and timetable
- 💬 **AI Chat Assistant** - Ask questions about your student's schedule using natural language
- 🔄 **WebUntis Integration** - Live data via MCP (Model Context Protocol)
- 🔐 **Secure** - API key authentication for all endpoints

## Quick Start

### Local Development

1. **Configure credentials:**
   ```bash
   # Edit backend/.env with your WebUntis and Azure credentials
   cp backend/.env.example backend/.env
   ```

2. **Start services:**
   ```bash
   # Using Docker (recommended)
   just docker-up

   # Or without Docker (macOS/Linux)
   just install && just up

   # Or without Docker (Windows)
   just install-win && just up-win
   ```

3. **Access the app:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8020
   - Swagger UI: http://localhost:8020/docs

4. **Login:**
   - Username: `toufik.malak`
   - Password: `ryantibanoah123$`

### Deploy to Azure

```bash
# Initialize infrastructure
just tf-init
just tf-apply

# Set secrets in Key Vault (first time only)
just kv-set-secret WEBUNTIS-USER "your-username"
just kv-set-secret WEBUNTIS-PASSWORD "your-password"
just kv-set-secret AZURE-FOUNDRY-API-KEY "your-api-key"
just kv-set-secret API-KEY "your-api-key"

# Deploy application
just deploy

# Check status
just status-azure
```

**Live URLs:**
- Frontend: https://pagent-frontend.azurewebsites.net
- Backend: https://pagent-backend.azurewebsites.net

**Azure Configuration:**
- Images built for `linux/amd64` platform
- ACR authentication via managed identity (automatic)
- Always uses `latest` tag

## Configuration

### Backend Environment Variables

Required in `backend/.env`:

```bash
# WebUntis Credentials
WEBUNTIS_SERVER=couven.webuntis.com
WEBUNTIS_SCHOOL=your-school
WEBUNTIS_USER=your-username
WEBUNTIS_PASSWORD=your-password

# Azure AI Foundry
AZURE_FOUNDRY_ENDPOINT=https://...
AZURE_FOUNDRY_API_KEY=...
AZURE_FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini

# API Authentication
API_KEY=your-api-key-here
```

### Frontend Environment Variables

Required in `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8020
```

For Azure deployment, this is automatically set to the backend URL during Docker build.

## Available Commands

```bash
# Docker
just docker-up        # Start containers
just docker-down      # Stop containers
just docker-logs      # View logs

# Local Development (macOS/Linux)
just install          # Install dependencies
just up              # Start services
just down            # Stop services
just status          # Check status
just test            # Run tests

# Local Development (Windows)
just install-win     # Install dependencies
just up-win          # Start services
just down-win        # Stop services

# Azure Deployment
just deploy          # Build, push, and restart
just status-azure    # Check Azure status
just logs-backend    # View backend logs
just restart-all     # Restart all services

# Terraform
just tf-init         # Initialize Terraform
just tf-plan         # Plan changes
just tf-apply        # Apply infrastructure
just tf-destroy      # Destroy resources
```

## Project Structure

```
pagent/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # API routes and app configuration
│   │   ├── config.py    # Settings and environment variables
│   │   ├── dashboard.py # Dashboard data aggregation
│   │   ├── mcp_client.py# WebUntis MCP client
│   │   └── foundry_agent.py # Azure AI chat integration
│   ├── Dockerfile       # Backend container (AMD64)
│   └── .env            # Backend configuration
├── frontend/            # React + Vite application
│   ├── src/
│   │   ├── pages/      # Login and Dashboard pages
│   │   ├── components/ # UI components
│   │   └── api.ts      # Backend API client
│   ├── Dockerfile      # Frontend container (AMD64)
│   └── .env           # Frontend configuration
├── terraform/          # Azure infrastructure as code
│   ├── main.tf        # Resource definitions
│   ├── variables.tf   # Input variables
│   └── outputs.tf     # Output values
├── scripts/           # Deployment automation
│   ├── build-and-push.sh
│   └── deploy.sh
├── Justfile           # Task automation
└── docker-compose.yml # Local container orchestration
```

## Architecture

**Backend:**
- FastAPI with async support
- MCP client for WebUntis integration
- Azure AI Foundry (OpenAI-compatible API) for chat
- Scheduled dashboard refresh (APScheduler)
- API key authentication

**Frontend:**
- React 18 with TypeScript
- Vite for fast builds
- Tailwind CSS for styling
- Protected routes with session-based auth

**Infrastructure:**
- Azure Container Registry (ACR) for images
- Azure App Service (Linux) for hosting
- Azure Key Vault for secrets
- Terraform for infrastructure as code

## Authentication

### Frontend Login
- Hardcoded credentials in `frontend/src/pages/LoginPage.tsx`
- Stores API key in sessionStorage after successful login
- Protected routes redirect to login if not authenticated

### API Authentication
- All endpoints (except `/health`) require `X-API-Key` header
- Swagger UI has global "Authorize" button for testing
- API key stored in Azure Key Vault for production

## Development Notes

### Building for Azure (ARM64 Mac Users)

Docker images must be built for AMD64 (Azure's architecture):

```bash
docker buildx build --platform linux/amd64 -t <image-name> .
```

The `just deploy` command handles this automatically.

### MCP Integration

The backend uses the [untis-mcp](https://github.com/kohlsalem/untis-mcp) server to fetch WebUntis data:
- Installed in Docker image during build
- Runs as subprocess via stdio
- Provides tools: `get_timetable`, `get_homeworks`, `get_exams`

### Scheduled Dashboard Refresh

Dashboard data is automatically refreshed at configured times (default: 07:00, 13:00, 19:00).

Manually trigger refresh:
```bash
curl -X POST -H "X-API-Key: <key>" http://localhost:8020/dashboard/refresh
```

## Troubleshooting

### Port conflicts
```bash
# macOS/Linux
lsof -ti:8020 | xargs kill
lsof -ti:5173 | xargs kill
```

### Container logs
```bash
# Local
just docker-logs

# Azure
just logs-backend
just logs-frontend
```

### Azure deployment issues
```bash
# Check container status
az webapp show --name pagent-backend --resource-group pagent-rg

# View live logs
az webapp log tail --name pagent-backend --resource-group pagent-rg
```

### MCP connection errors
- Verify WebUntis credentials in `.env`
- Check `MCP_STARTUP_TIMEOUT_SECONDS` (increase if needed)
- Ensure `untis-mcp` is installed in Docker image

## License

MIT

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [untis-mcp](https://github.com/kohlsalem/untis-mcp)
- [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry/)
