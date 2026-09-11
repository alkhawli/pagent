from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.dashboard import build_dashboard, load_latest_snapshot, save_snapshot
from app.foundry_agent import answer_with_mcp
from app.mcp_client import McpClient
from app.scheduler import create_scheduler, refresh_dashboard_snapshot


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ToolCallRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    scheduler = create_scheduler(settings)
    scheduler.start()
    if load_latest_snapshot(settings) is None:
        asyncio.create_task(refresh_dashboard_snapshot(settings))
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def create_app() -> FastAPI:
    app = FastAPI(title=get_settings().app_name, lifespan=lifespan)

    # CORS configuration - allow frontend to access backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://pagent-frontend.azurewebsites.net",
            "https://pagent-backend.azurewebsites.net",  # For testing via backend
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/dashboard", dependencies=[Depends(verify_api_key)])
    async def dashboard(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
        snapshot = load_latest_snapshot(settings)
        if snapshot is None:
            raise HTTPException(status_code=503, detail="Dashboard data is not ready yet. Try again shortly.")
        return snapshot

    @app.post("/dashboard/refresh", dependencies=[Depends(verify_api_key)])
    async def refresh_dashboard(
        client: McpClient = Depends(get_mcp_client),
        settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        try:
            data = await build_dashboard(client, settings)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Dashboard refresh failed: {exc}") from exc
        save_snapshot(settings, data)
        return data

    @app.get("/tools", dependencies=[Depends(verify_api_key)])
    async def list_tools(client: McpClient = Depends(get_mcp_client)) -> dict[str, Any]:
        try:
            return {"tools": [tool.model_dump(mode="json") for tool in await client.list_tools()]}
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"MCP connection failed: {exc}") from exc

    @app.post("/tools/{tool_name}", dependencies=[Depends(verify_api_key)])
    async def call_tool(
        tool_name: str,
        request: ToolCallRequest,
        client: McpClient = Depends(get_mcp_client),
    ) -> dict[str, Any]:
        try:
            return {"tool": tool_name, "result": await client.call_tool(tool_name, request.arguments)}
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"MCP tool call failed: {exc}") from exc

    @app.post("/chat", dependencies=[Depends(verify_api_key)])
    async def chat(
        request: ChatRequest,
        client: McpClient = Depends(get_mcp_client),
        settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        try:
            return await answer_with_mcp(request.message, client, settings)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Foundry agent chat failed: {exc}") from exc

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return INDEX_HTML

    return app


def get_mcp_client(settings: Settings = Depends(get_settings)) -> McpClient:
    return McpClient(settings)


def verify_api_key(
    api_key: str = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if not settings.api_key or api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


app = create_app()


INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PAGENT Untis Chatbot</title>
  <style>
    :root { color-scheme: light; font-family: Georgia, 'Times New Roman', serif; }
    body { margin: 0; min-height: 100vh; background: #f7f1e4; color: #1f2a24; }
    main { max-width: 860px; margin: 0 auto; padding: 48px 20px; }
    h1 { font-size: clamp(2rem, 7vw, 4.8rem); line-height: .95; margin: 0 0 24px; letter-spacing: 0; }
    form { display: grid; gap: 12px; }
    textarea { min-height: 112px; resize: vertical; border: 2px solid #1f2a24; border-radius: 8px; padding: 14px; font: 1rem/1.5 ui-monospace, SFMono-Regular, Consolas, monospace; background: #fffaf0; }
    button { width: fit-content; border: 0; border-radius: 8px; padding: 12px 18px; background: #0f5132; color: #fffaf0; font-weight: 700; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #fffaf0; border: 2px solid #1f2a24; border-radius: 8px; padding: 16px; min-height: 160px; }
  </style>
</head>
<body>
  <main>
    <h1>Untis Chatbot</h1>
    <form id="chat-form">
      <textarea id="message" name="message" placeholder="Welche Hausaufgaben gibt es?" required></textarea>
      <button type="submit">Ask Untis</button>
    </form>
    <pre id="output">Ready.</pre>
  </main>
  <script>
    const form = document.querySelector('#chat-form');
    const output = document.querySelector('#output');
    const button = document.querySelector('button');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      button.disabled = true;
      output.textContent = 'Connecting to MCP...';
      const message = document.querySelector('#message').value;
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      output.textContent = response.ok ? (data.answer || JSON.stringify(data, null, 2)) : JSON.stringify(data, null, 2);
      button.disabled = false;
    });
  </script>
</body>
</html>
"""