from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from app.config import Settings
from app.web_search_agent import run_agent_query

logger = logging.getLogger(__name__)

TRENDS_PROMPT = (
    "Search the web for the latest AI trends this week and the top trending repositories on "
    "GitHub this week (github.com/trending). Respond with ONLY a single JSON object, no markdown "
    "fences and no extra commentary, matching this exact shape: "
    '{"ai_trends": [{"title": str, "summary": str, "source": str, "url": str}], '
    '"github_repos": [{"name": str, "description": str, "url": str, "language": str, "stars": str}]}. '
    "Include 5-8 items in ai_trends and up to 10 items in github_repos, ordered by relevance/popularity, "
    "with repo names, short descriptions, primary language, and star counts where available."
)


def _parse_trends_json(raw_text: str) -> dict[str, list[dict[str, Any]]]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Trends agent did not return valid JSON; falling back to raw text section")
        return {
            "ai_trends": [{"title": "Trends summary", "summary": raw_text, "source": "", "url": ""}],
            "github_repos": [],
        }

    return {
        "ai_trends": data.get("ai_trends", []) or [],
        "github_repos": data.get("github_repos", []) or [],
    }


async def generate_trends(settings: Settings) -> dict[str, Any]:
    """Generates a weekly snapshot of AI trends and top trending GitHub repos via the Foundry web-search agent."""
    raw_text = await run_agent_query(settings, TRENDS_PROMPT)
    sections = _parse_trends_json(raw_text)
    return {
        "generated_at": datetime.now().isoformat(),
        **sections,
    }
