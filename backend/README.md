# PAGENT Untis Chatbot (backend)

FastAPI chatbot that:

- Talks to the [kohlsalem/untis-mcp](https://github.com/kohlsalem/untis-mcp) WebUntis MCP server over stdio.
- Uses an Azure AI Foundry-hosted chat model (via the Azure OpenAI-compatible API) as the agent that decides which
  MCP tool to call, executes it, and turns the result into a natural-language answer.

## Setup

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` with your WebUntis values:

```env
WEBUNTIS_SERVER=couven.webuntis.com
WEBUNTIS_SCHOOL=couven
WEBUNTIS_USER=your-username
WEBUNTIS_PASSWORD=your-password
```

The default MCP command is:

```env
MCP_COMMAND=uvx
MCP_ARGS="--from git+https://github.com/kohlsalem/untis-mcp --with mcp<2 untis-mcp"
```

If you clone the MCP server yourself, change those values to your local command. On Windows, for example:

```env
MCP_COMMAND=C:\Projects\untis-mcp\.venv\Scripts\python.exe
MCP_ARGS="-m untis_mcp.server"
```

### Azure AI Foundry

Set these values in `.env` (get them from your Foundry project's overview page):

```env
AZURE_FOUNDRY_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_FOUNDRY_API_KEY=your-api-key
AZURE_FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini
AZURE_FOUNDRY_API_VERSION=2024-10-21
```

`AZURE_FOUNDRY_API_KEY` is a secret — never commit it. The app derives the Azure OpenAI-compatible resource
endpoint from `AZURE_FOUNDRY_ENDPOINT` and calls Chat Completions with function/tool calling, where each MCP tool
is exposed to the model as a callable function.

### Web search (news / trends pages)

The `/news` and `/trends` endpoints use a separate, pre-built Azure AI Foundry agent that has its own web search
tool configured in the Foundry portal (e.g. Bing grounding). Set these values in `.env`:

```env
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDRY_AGENT_NAME=personal-web
FOUNDRY_AGENT_VERSION=3
```

This uses `DefaultAzureCredential` (no API key), so you need to be logged in via `az login` locally; in Azure it
uses the Web App's managed identity, which must have access to the Foundry project.

## Run

```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

Open <http://127.0.0.1:8020> or call the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8020/health
Invoke-RestMethod http://127.0.0.1:8020/tools
Invoke-RestMethod http://127.0.0.1:8020/chat -Method Post -ContentType "application/json" -Body '{"message":"Welche Hausaufgaben gibt es?"}'
```

## Test

```powershell
uv run pytest
```
