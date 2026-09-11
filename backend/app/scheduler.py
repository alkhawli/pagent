from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import Settings
from app.dashboard import build_dashboard, save_snapshot
from app.mcp_client import McpClient

logger = logging.getLogger(__name__)


async def refresh_dashboard_snapshot(settings: Settings) -> None:
    client = McpClient(settings)
    try:
        data = await build_dashboard(client, settings)
    except Exception:
        logger.exception("Dashboard snapshot refresh failed")
        return
    save_snapshot(settings, data)


def create_scheduler(settings: Settings) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    for time_str in settings.dashboard_refresh_time_list:
        hour, _, minute = time_str.partition(":")
        scheduler.add_job(
            refresh_dashboard_snapshot,
            CronTrigger(hour=int(hour), minute=int(minute or 0)),
            args=[settings],
            id=f"dashboard-refresh-{time_str}",
            replace_existing=True,
        )
    return scheduler
