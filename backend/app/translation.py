from __future__ import annotations

import json

from app.config import Settings
from app.foundry_agent import build_azure_client

TRANSLATION_SYSTEM_PROMPT = (
    "Translate messages from German to English. "
    'Respond with strict JSON only: {"subject": "...", "text": "..."}. '
    "Keep names, dates, and numbers unchanged. If the input is already in English, return it as-is."
)


async def translate_to_english(settings: Settings, subject: str, text: str) -> tuple[str, str]:
    """Translate a message subject+body to English via the Foundry model. Falls back to the original on failure."""
    if not settings.azure_foundry_endpoint or not settings.azure_foundry_api_key:
        return subject, text

    client = build_azure_client(settings)
    try:
        response = await client.chat.completions.create(
            model=settings.azure_foundry_model_deployment,
            messages=[
                {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps({"subject": subject, "text": text})},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        return parsed.get("subject", subject), parsed.get("text", text)
    except Exception:
        return subject, text
    finally:
        await client.close()
