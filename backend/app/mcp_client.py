from __future__ import annotations

import asyncio
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel

from app.config import Settings


class McpTool(BaseModel):
    name: str
    description: str | None = None
    input_schema: dict[str, Any] | None = None


class McpClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_tools(self) -> list[McpTool]:
        async with self._session() as session:
            response = await session.list_tools()
            return [
                McpTool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema,
                )
                for tool in response.tools
            ]

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        async with self._session() as session:
            response = await session.call_tool(name, arguments or {})
            return response.model_dump(mode="json")

    def _session(self):
        server = StdioServerParameters(
            command=self._settings.mcp_command,
            args=self._settings.mcp_arg_list,
            env=self._settings.mcp_env,
        )
        return _InitializedSession(server, self._settings.mcp_startup_timeout_seconds)


class _InitializedSession:
    def __init__(self, server: StdioServerParameters, timeout: float) -> None:
        self._server = server
        self._timeout = timeout
        self._stdio_context: Any = None
        self._session_context: Any = None
        self._session: ClientSession | None = None

    async def __aenter__(self) -> ClientSession:
        self._stdio_context = stdio_client(self._server)
        read_stream, write_stream = await self._stdio_context.__aenter__()
        self._session_context = ClientSession(read_stream, write_stream)
        self._session = await self._session_context.__aenter__()
        await asyncio.wait_for(self._session.initialize(), timeout=self._timeout)
        return self._session

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self._session_context is not None:
            await self._session_context.__aexit__(exc_type, exc, traceback)
        if self._stdio_context is not None:
            await self._stdio_context.__aexit__(exc_type, exc, traceback)