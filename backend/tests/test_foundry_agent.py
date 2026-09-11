from app.foundry_agent import _extract_text, _tool_definitions
from app.mcp_client import McpTool


def test_tool_definitions_converts_mcp_tools_to_openai_function_schema() -> None:
    tools = [
        McpTool(name="untis_get_homework", description="Fetch homework", input_schema={"type": "object", "properties": {}}),
    ]

    definitions = _tool_definitions(tools)

    assert definitions == [
        {
            "type": "function",
            "function": {
                "name": "untis_get_homework",
                "description": "Fetch homework",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]


def test_extract_text_from_mcp_result() -> None:
    result = {"content": [{"type": "text", "text": "Hello"}, {"type": "text", "text": "Untis"}]}

    assert _extract_text(result) == "Hello\n\nUntis"
