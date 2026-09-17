from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.blob_storage import BlobJsonStore
from app.config import Settings
from app.dashboard import build_dashboard
from app.mcp_client import McpClient
from app.meal_planner import generate_meal_plan

logger = logging.getLogger(__name__)


async def _record_refresh_status(settings: Settings, store: BlobJsonStore, *, success: bool, error: str | None) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    status = await store.read_json(settings.dashboard_blob_container, settings.dashboard_status_blob_name) or {}
    status["last_attempt_at"] = now
    if success:
        status["last_success_at"] = now
        status["last_error"] = None
    else:
        status["last_error"] = error
    await store.write_json(settings.dashboard_blob_container, settings.dashboard_status_blob_name, status)


async def refresh_dashboard_snapshot(settings: Settings, store: BlobJsonStore) -> None:
    client = McpClient(settings)
    try:
        data = await build_dashboard(client, settings, store)
    except Exception as exc:
        logger.exception("Dashboard snapshot refresh failed")
        await _record_refresh_status(settings, store, success=False, error=str(exc))
        return
    await store.write_json(settings.dashboard_blob_container, settings.dashboard_blob_name, data)
    await _record_refresh_status(settings, store, success=True, error=None)


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
