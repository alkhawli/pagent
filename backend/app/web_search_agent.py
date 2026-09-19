from __future__ import annotations

import asyncio
import logging

from app.config import Settings

logger = logging.getLogger(__name__)


def _run_agent_query_sync(settings: Settings, prompt: str) -> str:
    """Runs a single-shot query against a pre-built Azure AI Foundry agent (with its own web
    search tool already configured in the Foundry portal) via the agent_reference responses API.

    Uses the synchronous azure-ai-projects SDK (no mature async surface yet), so this is meant
    to be called via asyncio.to_thread from async code.
    """
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    if not settings.azure_ai_project_endpoint or not settings.foundry_agent_name:
        raise RuntimeError(
            "Foundry web-search agent is not configured. Set AZURE_AI_PROJECT_ENDPOINT and "
            "FOUNDRY_AGENT_NAME in .env."
        )

    credential = DefaultAzureCredential()
    try:
        project_client = AIProjectClient(endpoint=settings.azure_ai_project_endpoint, credential=credential)
        with project_client:
            openai_client = project_client.get_openai_client()
            response = openai_client.responses.create(
                input=[{"role": "user", "content": prompt}],
                extra_body={
                    "agent_reference": {
                        "name": settings.foundry_agent_name,
                        "version": settings.foundry_agent_version,
                        "type": "agent_reference",
                    }
                },
            )
            return response.output_text
    finally:
        credential.close()


async def run_agent_query(settings: Settings, prompt: str) -> str:
    """Runs a query against the Foundry web-search agent and returns the answer text."""
    return await asyncio.to_thread(_run_agent_query_sync, settings, prompt)
