from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from app.blob_storage import BlobJsonStore
from app.config import Settings, get_settings
from app.dashboard import build_dashboard
from app.foundry_agent import answer_with_mcp
from app.mcp_client import McpClient
from app.meal_planner import generate_meal_plan
from app.scheduler import create_scheduler, refresh_dashboard_snapshot


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ToolCallRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    store = BlobJsonStore(settings)
    app.state.blob_store = store
    scheduler = create_scheduler(settings, store)
    scheduler.start()
    # Trigger initial dashboard build so blob storage is populated on first boot
    asyncio.create_task(refresh_dashboard_snapshot(settings, store))
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await store.close()


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
        snapshot = await app.state.blob_store.read_json(settings.dashboard_blob_container, settings.dashboard_blob_name)
        if snapshot is None:
            raise HTTPException(status_code=503, detail="Dashboard data is not ready yet. Try again shortly.")
        return snapshot

    @app.post("/dashboard/refresh", dependencies=[Depends(verify_api_key)])
    async def refresh_dashboard(
        client: McpClient = Depends(get_mcp_client),
        settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        try:
            data = await build_dashboard(client, settings, app.state.blob_store)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Dashboard refresh failed: {exc}") from exc
        await app.state.blob_store.write_json(settings.dashboard_blob_container, settings.dashboard_blob_name, data)
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

    @app.get("/meal-plan", dependencies=[Depends(verify_api_key)])
    async def meal_plan(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
        snapshot = await app.state.blob_store.read_json(settings.meal_plan_blob_container, settings.meal_plan_blob_name)
        if snapshot is None:
            raise HTTPException(status_code=503, detail="Meal plan is not ready yet. Try again shortly.")
        return snapshot

    @app.post("/meal-plan/generate", dependencies=[Depends(verify_api_key)])
    async def generate_meal_plan_endpoint(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
        try:
            # Load food wishes
            wishes_data = await app.state.blob_store.read_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name)
            food_wishes = wishes_data.get("wishes", []) if wishes_data else []

            data = await generate_meal_plan(settings, food_wishes=food_wishes)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Meal plan generation failed: {exc}") from exc
        await app.state.blob_store.write_json(settings.meal_plan_blob_container, settings.meal_plan_blob_name, data)
        return data

    @app.get("/meal-plan/wishes", dependencies=[Depends(verify_api_key)])
    async def get_food_wishes(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
        wishes_data = await app.state.blob_store.read_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name)
        return wishes_data or {"wishes": []}

    @app.post("/meal-plan/wishes", dependencies=[Depends(verify_api_key)])
    async def add_food_wish(
        wish: dict[str, str],
        settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        if not wish.get("text"):
            raise HTTPException(status_code=400, detail="Wish text is required")

        wishes_data = await app.state.blob_store.read_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name)
        wishes = wishes_data.get("wishes", []) if wishes_data else []
        wishes.append(wish["text"])

        new_data = {"wishes": wishes}
        await app.state.blob_store.write_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name, new_data)
        return new_data

    @app.delete("/meal-plan/wishes/{index}", dependencies=[Depends(verify_api_key)])
    async def delete_food_wish(index: int, settings: Settings = Depends(get_settings)) -> dict[str, Any]:
        wishes_data = await app.state.blob_store.read_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name)
        wishes = wishes_data.get("wishes", []) if wishes_data else []

        if index < 0 or index >= len(wishes):
            raise HTTPException(status_code=404, detail="Wish not found")

        wishes.pop(index)
        new_data = {"wishes": wishes}
        await app.state.blob_store.write_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name, new_data)
        return new_data

    @app.get("/")
    async def index() -> dict[str, str]:
        return {"message": "PAGENT Family Assistant API", "status": "running"}

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