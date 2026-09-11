from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

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
        self._session_lock = asyncio.Lock()
        self._current_session: ClientSession | None = None
        self._stdio_exit_stack: list[Any] = []

    async def list_tools(self) -> list[McpTool]:
        async with self._get_session() as session:
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
        async with self._get_session() as session:
            response = await session.call_tool(name, arguments or {})
            return response.model_dump(mode="json")

    @asynccontextmanager
    async def _get_session(self) -> AsyncGenerator[ClientSession, None]:
        """Get or create a session for this operation. Creates a fresh session each time."""
        server = StdioServerParameters(
            command=self._settings.mcp_command,
            args=self._settings.mcp_arg_list,
            env=self._settings.mcp_env,
        )

        stdio_context = stdio_client(server)
        session_context = None
        session = None

        try:
            read_stream, write_stream = await stdio_context.__aenter__()
            session_context = ClientSession(read_stream, write_stream)
            session = await session_context.__aenter__()
            await asyncio.wait_for(session.initialize(), timeout=self._settings.mcp_startup_timeout_seconds)
            yield session
        finally:
            # Clean up in reverse order, suppressing cancel scope errors
            if session_context is not None:
                try:
                    await session_context.__aexit__(None, None, None)
                except (RuntimeError, Exception):
                    pass

            if stdio_context is not None:
                try:
                    await stdio_context.__aexit__(None, None, None)
                except (RuntimeError, Exception):
                    pass