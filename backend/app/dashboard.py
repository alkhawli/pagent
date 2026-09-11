from __future__ import annotations

import asyncio
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from app.config import Settings
from app.mcp_client import McpClient
from app.translation import translate_to_english


def _parse_untis_date(value: Any) -> date | None:
    text = str(value)
    if len(text) == 8 and text.isdigit():
        return date(int(text[:4]), int(text[4:6]), int(text[6:8]))
    return None


def _iso(value: Any) -> str | None:
    parsed = _parse_untis_date(value)
    return parsed.isoformat() if parsed else None


def _format_time(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).zfill(4)
    return f"{text[:2]}:{text[2:]}"


async def _call_tool_json(client: McpClient, name: str, arguments: dict[str, Any] | None = None) -> tuple[Any, str | None]:
    """Call an MCP tool and return (parsed_json_or_None, error_message_or_None)."""
    try:
        result = await client.call_tool(name, arguments or {})
    except Exception as exc:  # noqa: BLE001 - surface MCP/transport failures as data, not crashes
        return None, str(exc)

    content = result.get("content")
    text = content[0].get("text") if isinstance(content, list) and content and isinstance(content[0], dict) else None
    if text is None:
        return None, "No content returned by the tool"
    if text.startswith("Error"):
        return None, text
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        return None, text


async def _lookup_id_name_map(client: McpClient, method: str) -> dict[int, str]:
    data, error = await _call_tool_json(client, "untis_raw_call", {"method": method, "parameters": "{}"})
    if error or not isinstance(data, list):
        return {}
    return {item["id"]: item.get("name", "?") for item in data if isinstance(item, dict) and "id" in item}


async def _get_students(client: McpClient) -> list[dict[str, Any]]:
    data, error = await _call_tool_json(client, "untis_get_students")
    if error or not isinstance(data, list):
        return []
    return data


async def _get_homework(client: McpClient) -> dict[str, Any]:
    data, error = await _call_tool_json(client, "untis_get_homework", {"params": {}})
    if error:
        return {"items": [], "error": error}

    payload = data.get("data", data) if isinstance(data, dict) else {}
    homeworks = payload.get("homeworks", [])
    lessons = {lesson["id"]: lesson.get("subject", "?") for lesson in payload.get("lessons", [])}
    teachers = {teacher["id"]: teacher.get("name", "?") for teacher in payload.get("teachers", [])}
    teacher_by_hw = {rec["homeworkId"]: rec.get("teacherId") for rec in payload.get("records", [])}

    items = [
        {
            "id": hw.get("id"),
            "subject": lessons.get(hw.get("lessonId"), "?"),
            "teacher": teachers.get(teacher_by_hw.get(hw.get("id")), None),
            "text": hw.get("text", ""),
            "assigned_date": _iso(hw.get("date")),
            "due_date": _iso(hw.get("dueDate")),
            "completed": bool(hw.get("completed", False)),
        }
        for hw in homeworks
    ]
    items.sort(key=lambda item: item["due_date"] or "9999-99-99")
    return {"items": items, "error": None}


def _translation_cache_path(settings: Settings) -> Path:
    return Path(settings.dashboard_data_dir) / "message_translations.json"


def load_translation_cache(settings: Settings) -> dict[str, dict[str, Any]]:
    path = _translation_cache_path(settings)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_translation_cache(settings: Settings, cache: dict[str, dict[str, Any]]) -> None:
    path = _translation_cache_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


async def _get_messages(client: McpClient, settings: Settings) -> dict[str, Any]:
    data, error = await _call_tool_json(client, "untis_get_messages")
    if error:
        return {"items": [], "unread_count": 0, "error": error}

    raw_messages = data.get("incomingMessages", []) if isinstance(data, dict) else []
    raw_messages.sort(key=lambda item: item.get("sentDateTime") or "", reverse=True)
    unread_count = sum(1 for item in raw_messages if not item.get("isMessageRead", False))

    # Only translate the messages we actually display, so a large unread backlog does not
    # trigger dozens of translation calls on every refresh.
    top_messages = raw_messages[:10]

    cache = load_translation_cache(settings)
    entries: list[dict[str, Any] | None] = [None] * len(top_messages)
    pending: list[tuple[int, str, str]] = []

    for index, message in enumerate(top_messages):
        subject_de = message.get("subject", "")
        text_de = (message.get("contentPreview") or "").strip()
        cached = cache.get(str(message.get("id")))
        if cached and cached.get("text_de") == text_de:
            entries[index] = {
                "subject_en": cached["subject_en"],
                "text_en": cached["text_en"],
                "translated_at": cached["translated_at"],
            }
        elif not subject_de.strip() and not text_de:
            # Nothing to translate - avoid an LLM call for an empty message.
            entries[index] = {"subject_en": subject_de, "text_en": text_de, "translated_at": None}
        else:
            pending.append((index, subject_de, text_de))

    if pending:
        results = await asyncio.gather(
            *(translate_to_english(settings, subject_de, text_de) for _, subject_de, text_de in pending)
        )
        translated_at = datetime.now().isoformat(timespec="seconds")
        for (index, subject_de, text_de), (subject_en, text_en) in zip(pending, results):
            entries[index] = {"subject_en": subject_en, "text_en": text_en, "translated_at": translated_at}
            cache[str(top_messages[index].get("id"))] = {
                "subject_de": subject_de,
                "text_de": text_de,
                "subject_en": subject_en,
                "text_en": text_en,
                "translated_at": translated_at,
            }
        save_translation_cache(settings, cache)

    items = [
        {
            "id": message.get("id"),
            "subject_de": message.get("subject", ""),
            "subject_en": entry["subject_en"],
            "sender": (message.get("sender") or {}).get("displayName", "unknown"),
            "sent_at": message.get("sentDateTime"),
            "read": bool(message.get("isMessageRead", False)),
            "has_attachments": bool(message.get("hasAttachments", False)),
            "text_de": (message.get("contentPreview") or "").strip(),
            "text_en": entry["text_en"],
            "translated_at": entry["translated_at"],
        }
        for message, entry in zip(top_messages, entries)
        if entry is not None
    ]
    return {"items": items, "unread_count": unread_count, "error": None}


def _first_day_of_month_offset(base: date, months_offset: int) -> date:
    total = base.year * 12 + (base.month - 1) + months_offset
    year, month = divmod(total, 12)
    return date(year, month + 1, 1)


def current_schedule_range() -> tuple[date, date]:
    """The 2-month window (current month + next month) used for schedule and personal calendar data."""
    today = date.today()
    range_start = _first_day_of_month_offset(today, 0)
    range_end = _first_day_of_month_offset(today, 2) - timedelta(days=1)
    return range_start, range_end


async def _get_timetable_for_range(
    client: McpClient,
    student: dict[str, Any] | None,
    start: date,
    end: date,
    subject_map: dict[int, str],
    room_map: dict[int, str],
) -> dict[str, Any]:
    if student is None:
        return {"by_date": {}, "error": "No student found on this account"}

    params = {
        "id": student.get("personId"),
        "type": student.get("personType"),
        "startDate": int(start.strftime("%Y%m%d")),
        "endDate": int(end.strftime("%Y%m%d")),
    }
    data, error = await _call_tool_json(client, "untis_raw_call", {"method": "getTimetable", "parameters": json.dumps(params)})
    if error:
        return {"by_date": {}, "error": error}

    periods = data if isinstance(data, list) else []
    by_date: dict[str, list[dict[str, Any]]] = {}
    for period in periods:
        iso = _iso(period.get("date"))
        if iso is None:
            continue
        subjects = period.get("su", [])
        rooms = period.get("ro", [])
        subject_id = subjects[0].get("id") if subjects else None
        room_id = rooms[0].get("id") if rooms else None
        by_date.setdefault(iso, []).append(
            {
                "start_time": _format_time(period.get("startTime")),
                "end_time": _format_time(period.get("endTime")),
                "subject": subject_map.get(subject_id, "?"),
                "room": room_map.get(room_id, ""),
                "cancelled": period.get("code") == "cancelled",
            }
        )

    for items in by_date.values():
        items.sort(key=lambda item: item["start_time"] or "99:99")

    return {"by_date": by_date, "error": None}


def _build_recommendations(
    today: date,
    homework: dict[str, Any],
    messages: dict[str, Any],
    schedule: dict[str, Any],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    tomorrow = today + timedelta(days=1)
    by_date = schedule.get("by_date", {})

    for hw in homework["items"]:
        if hw["completed"] or not hw["due_date"]:
            continue
        due = date.fromisoformat(hw["due_date"])
        days_left = (due - today).days
        if days_left < 0:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "Homework",
                    "title": f"Overdue: {hw['subject']} homework",
                    "detail": hw["text"] or "No description provided.",
                    "date": hw["due_date"],
                }
            )
        elif days_left <= 2:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "Homework",
                    "title": f"Due soon: {hw['subject']} homework (due {hw['due_date']})",
                    "detail": hw["text"] or "No description provided.",
                    "date": hw["due_date"],
                }
            )
        elif days_left <= 7:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "Homework",
                    "title": f"Upcoming: {hw['subject']} homework (due {hw['due_date']})",
                    "detail": hw["text"] or "No description provided.",
                    "date": hw["due_date"],
                }
            )

    if messages["unread_count"] > 0:
        recommendations.append(
            {
                "priority": "medium",
                "category": "Message",
                "title": f"{messages['unread_count']} unread school message(s)",
                "detail": "Check the Messages tab for details.",
                "date": None,
            }
        )

    for label, iso in (("today", today.isoformat()), ("tomorrow", tomorrow.isoformat())):
        cancelled = [item for item in by_date.get(iso, []) if item["cancelled"]]
        if cancelled:
            subjects = ", ".join(sorted({item["subject"] for item in cancelled}))
            recommendations.append(
                {
                    "priority": "low",
                    "category": "Schedule",
                    "title": f"Lesson(s) cancelled {label}: {subjects}",
                    "detail": "Double check the schedule for changes.",
                    "date": None,
                }
            )

    for label, section in (("Homework", homework), ("Messages", messages), ("Schedule", schedule)):
        if section.get("error"):
            recommendations.append(
                {
                    "priority": "info",
                    "category": "System",
                    "title": f"{label} data is temporarily unavailable",
                    "detail": section["error"],
                    "date": None,
                }
            )

    priority_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    recommendations.sort(key=lambda item: (priority_order.get(item["priority"], 9), item["date"] or "9999-99-99"))

    if not any(item["priority"] in ("high", "medium") for item in recommendations):
        recommendations.insert(
            0,
            {
                "priority": "low",
                "category": "Status",
                "title": "No urgent items today",
                "detail": "Nothing due soon. Nice work staying on top of things!",
                "date": None,
            },
        )

    return recommendations


async def build_dashboard(client: McpClient, settings: Settings) -> dict[str, Any]:
    students, homework, messages, subject_map, room_map = await asyncio.gather(
        _get_students(client),
        _get_homework(client),
        _get_messages(client, settings),
        _lookup_id_name_map(client, "getSubjects"),
        _lookup_id_name_map(client, "getRooms"),
    )

    primary_student = students[0] if students else None
    today = date.today()

    range_start, range_end = current_schedule_range()
    schedule = await _get_timetable_for_range(client, primary_student, range_start, range_end, subject_map, room_map)

    recommendations = _build_recommendations(today, homework, messages, schedule)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "student": primary_student,
        "today": today.isoformat(),
        "recommendations": recommendations,
        "homework": homework,
        "messages": messages,
        "schedule": {"range_start": range_start.isoformat(), "range_end": range_end.isoformat(), **schedule},
    }



def _snapshots_root(settings: Settings) -> Path:
    return Path(settings.dashboard_data_dir) / "snapshots"


def latest_snapshot_path(settings: Settings) -> Path:
    return Path(settings.dashboard_data_dir) / "latest.json"


def save_snapshot(settings: Settings, data: dict[str, Any]) -> Path:
    """Persist a dashboard snapshot under data/snapshots/<year>/<month>/<timestamp>.json and update latest.json."""
    now = datetime.now()
    month_dir = _snapshots_root(settings) / f"{now:%Y}" / f"{now:%m}"
    month_dir.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    snapshot_path = month_dir / f"{now:%Y-%m-%dT%H-%M-%S}.json"
    snapshot_path.write_text(payload, encoding="utf-8")

    latest_path = latest_snapshot_path(settings)
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(payload, encoding="utf-8")
    return snapshot_path


def load_latest_snapshot(settings: Settings) -> dict[str, Any] | None:
    path = latest_snapshot_path(settings)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
