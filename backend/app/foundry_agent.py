from __future__ import annotations

import json
from typing import Any

from openai import AsyncAzureOpenAI

from app.config import Settings
from app.mcp_client import McpClient, McpTool

MAX_TOOL_ITERATIONS = 6

SYSTEM_PROMPT = (
    "You are a helpful assistant for parents using the WebUntis school platform. "
    "Use the available tools to answer questions about timetable, homework, exams, "
    "absences, messages, and school info. Reply in the same language the user wrote in. "
    "Keep answers concise and treat tool results as the source of truth."
)


def build_azure_client(settings: Settings) -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_foundry_api_key,
        api_version=settings.azure_foundry_api_version,
    )


def _tool_definitions(tools: list[McpTool]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema or {"type": "object", "properties": {}},
            },
        }
        for tool in tools
    ]


def _extract_text(result: dict[str, Any]) -> str | None:
    content = result.get("content")
    if not isinstance(content, list):
        return None

    parts = [
        item["text"]
        for item in content
        if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str)
    ]
    return "\n\n".join(parts) if parts else None


async def answer_with_mcp(
    message: str,
    client: McpClient,
    settings: Settings,
    azure_client: AsyncAzureOpenAI | None = None,
) -> dict[str, Any]:
    if not settings.azure_foundry_endpoint or not settings.azure_foundry_api_key:
        raise RuntimeError(
            "Azure AI Foundry is not configured. Set AZURE_FOUNDRY_ENDPOINT and AZURE_FOUNDRY_API_KEY in .env."
        )

    tools = await client.list_tools()
    tool_definitions = _tool_definitions(tools)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    tool_calls_made: list[dict[str, Any]] = []

    owns_client = azure_client is None
    azure_client = azure_client or build_azure_client(settings)

    try:
        for _ in range(MAX_TOOL_ITERATIONS):
            response = await azure_client.chat.completions.create(
                model=settings.azure_foundry_model_deployment,
                messages=messages,
                tools=tool_definitions or None,
            )
            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                return {"answer": assistant_message.content or "", "tool_calls": tool_calls_made}

            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in assistant_message.tool_calls
                    ],
                }
            )

            for tool_call in assistant_message.tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}

                try:
                    result = await client.call_tool(tool_call.function.name, arguments)
                    tool_text = _extract_text(result) or json.dumps(result)
                except Exception as exc:  # noqa: BLE001 - surface MCP failures to the model instead of crashing
                    result = {"error": str(exc)}
                    tool_text = f"Error calling tool: {exc}"

                tool_calls_made.append({"tool": tool_call.function.name, "arguments": arguments, "result": result})
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_text})

        return {
            "answer": "The agent used too many tool calls without producing a final answer.",
            "tool_calls": tool_calls_made,
        }
    finally:
        if owns_client:
            await azure_client.close()
