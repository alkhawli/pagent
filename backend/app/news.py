from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from app.config import Settings
from app.web_search_agent import run_agent_query

logger = logging.getLogger(__name__)

NEWS_PROMPT = (
    "Search the web for the latest headlines and give me today's top world news, top technology "
    "news, and top football (soccer) news, each with 5-8 items. Respond with ONLY a single JSON "
    "object, no markdown fences and no extra commentary, matching this exact shape: "
    '{"world": [{"title": str, "summary": str, "source": str, "url": str}], '
    '"tech": [...], "football": [...]}. Keep each summary to 1-2 sentences and include the '
    "source name and article URL for every item."
)


def _parse_news_json(raw_text: str) -> dict[str, list[dict[str, Any]]]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("News agent did not return valid JSON; falling back to raw text section")
        return {
            "world": [{"title": "News summary", "summary": raw_text, "source": "", "url": ""}],
            "tech": [],
            "football": [],
        }

    return {
        "world": data.get("world", []) or [],
        "tech": data.get("tech", []) or [],
        "football": data.get("football", []) or [],
    }


async def generate_news(settings: Settings) -> dict[str, Any]:
    """Generates a daily news snapshot (world, tech, football) using the Foundry web-search agent."""
    raw_text = await run_agent_query(settings, NEWS_PROMPT)
    sections = _parse_news_json(raw_text)
    return {
        "generated_at": datetime.now().isoformat(),
        **sections,
    }
