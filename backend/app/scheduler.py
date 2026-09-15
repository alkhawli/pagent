from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.blob_storage import BlobJsonStore
from app.config import Settings
from app.dashboard import build_dashboard
from app.mcp_client import McpClient
from app.meal_planner import generate_meal_plan

logger = logging.getLogger(__name__)


async def refresh_dashboard_snapshot(settings: Settings, store: BlobJsonStore) -> None:
    client = McpClient(settings)
    try:
        data = await build_dashboard(client, settings, store)
    except Exception:
        logger.exception("Dashboard snapshot refresh failed")
        return
    await store.write_json(settings.dashboard_blob_container, settings.dashboard_blob_name, data)


async def refresh_meal_plan_snapshot(settings: Settings, store: BlobJsonStore) -> None:
    try:
        # Load food wishes
        wishes_data = await store.read_json(settings.meal_plan_blob_container, settings.food_wishes_blob_name)
        food_wishes = wishes_data.get("wishes", []) if wishes_data else []

        data = await generate_meal_plan(settings, food_wishes=food_wishes)
    except Exception:
        logger.exception("Meal plan snapshot refresh failed")
        return
    await store.write_json(settings.meal_plan_blob_container, settings.meal_plan_blob_name, data)


def create_scheduler(settings: Settings, store: BlobJsonStore) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    for time_str in settings.dashboard_refresh_time_list:
        hour, _, minute = time_str.partition(":")
        scheduler.add_job(
            refresh_dashboard_snapshot,
            CronTrigger(hour=int(hour), minute=int(minute or 0)),
            args=[settings, store],
            id=f"dashboard-refresh-{time_str}",
            replace_existing=True,
        )

    meal_hour, _, meal_minute = settings.meal_plan_refresh_time.partition(":")
    scheduler.add_job(
        refresh_meal_plan_snapshot,
        CronTrigger(day_of_week=settings.meal_plan_refresh_day, hour=int(meal_hour), minute=int(meal_minute or 0)),
        args=[settings, store],
        id="meal-plan-refresh",
        replace_existing=True,
    )

    return scheduler
