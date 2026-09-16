from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from openai import AsyncAzureOpenAI

from app.config import Settings
from app.foundry_agent import build_azure_client

MEAL_PLANNER_SYSTEM_PROMPT = """إنت مساعد تخطيط أكل مختص للعيل المشغولة بلبنان. لازم تعمل برنامج أكل صحي لـ5 أيام شغل (الإتنين-الجمعة).

المطلوب:
- عيلة فيها أب وأم و3 ولاد (5 أشخاص)
- أكل صحي ومناسب للولاد (ما فيو حرّ كتير)
- وقت التحضير: 30-45 دقيقة أقصى شي
- بدنا 2-3 وصفات بس، كل وصفة بتكفي ليومين أو أكتر
- الأكل لازم يكون من المطبخ اللبناني أو أكلات منعرفها بالمنطقة
- استعمل مكونات متوفرة بالسوبرماركت عنّا
- ليسته تسوّق منظمة حسب أقسام السوبرماركت

الشكل المطلوب (JSON):
{
  "recipes": [
    {
      "name": "إسم الأكلة",
      "prep_time": "35 دقيقة",
      "serves": "5-6 أشخاص",
      "days": ["الإتنين", "التلات"],
      "ingredients": ["مكوّن 1", "مكوّن 2", ...],
      "instructions": ["خطوة 1", "خطوة 2", ...]
    }
  ],
  "shopping_list": [
    {
      "category": "خضار وفواكه",
      "items": ["بندورة - 1 كيلو", "بصل - 500 غرام", ...]
    },
    {
      "category": "لحمة ودجاج",
      "items": ["صدور دجاج - 1.5 كيلو", ...]
    },
    {
      "category": "ألبان وأجبان",
      "items": ["حليب - 2 ليتر", ...]
    },
    {
      "category": "بهارات وأساسيات",
      "items": ["رز - 2 كيلو", "معكرونة - 500 غرام", ...]
    }
  ]
}

ملاحظات مهمة:
- وزّع الوصفات على 5 أيام بحيث كل وصفة بتكفي ليومين أو تلاتة
- اذكر الكميات بالزبط بليستة التسوّق
- خلّي الأكلات متنوّعة (لحمة، دجاج، سمك إذا بتقدر)
- ركّز على أكل عملي وسريع بالتحضير
- استعمل لهجة لبنانية بالتعليمات
- مهم جداً: اكتب كل النصوص بحروف عربية فقط (أ ب ت ث...)، ما تستعمل ولا حرف عبري (مثل א ב ש) حتى لو كان شكلو شبه حرف عربي
"""


def _get_next_weekdays(count: int = 5) -> list[dict[str, str]]:
    """Generate next N weekdays starting from today."""
    arabic_days = {
        0: "الإتنين",
        1: "التلات",
        2: "الأربعا",
        3: "الخميس",
        4: "الجمعة",
        5: "السبت",
        6: "الأحد",
    }

    today = datetime.now()
    days = []

    current = today
    while len(days) < count:
        weekday = current.weekday()
        # Skip weekends (Friday=4, Saturday=5 in ISO, but we want Monday-Friday work week)
        # Actually in ISO: Monday=0, Sunday=6, so Friday=4, Saturday=5
        # For a work week Mon-Fri, we skip Sat(5) and Sun(6)
        if weekday not in (5, 6):
            days.append({"date": current.strftime("%Y-%m-%d"), "day_name": arabic_days[weekday]})
        current += timedelta(days=1)

    return days


async def generate_meal_plan(
    settings: Settings, azure_client: AsyncAzureOpenAI | None = None, food_wishes: list[str] | None = None
) -> dict[str, Any]:
    """Generate a weekly meal plan using Azure OpenAI."""
    if not settings.azure_foundry_endpoint or not settings.azure_foundry_api_key:
        raise RuntimeError(
            "Azure AI Foundry is not configured. Set AZURE_FOUNDRY_ENDPOINT and AZURE_FOUNDRY_API_KEY in .env."
        )

    owns_client = azure_client is None
    azure_client = azure_client or build_azure_client(settings)

    weekdays = _get_next_weekdays(5)

    wishes_text = ""
    if food_wishes:
        wishes_text = f"\n\nالعيلة طلبت أكلات معيّنة، حاول تحطّها بالبرنامج:\n{chr(10).join(f'- {wish}' for wish in food_wishes)}\n"

    user_prompt = f"""اعمل برنامج أكل لهالأسبوع:

الأيام:
{chr(10).join(f"- {day['day_name']} ({day['date']})" for day in weekdays)}
{wishes_text}
تذكّر: بدنا 2-3 وصفات بس، كل وصفة بتكفي ليومين أو أكتر من الأيام هدول.
"""

    try:
        response = await azure_client.chat.completions.create(
            model=settings.azure_foundry_model_deployment,
            messages=[
                {"role": "system", "content": MEAL_PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from Azure OpenAI")

        plan_data = json.loads(content)

        # Build the response with day-by-day breakdown
        recipes = plan_data.get("recipes", [])

        def normalize(text: str) -> str:
            return "".join(text.split())

        unmatched_indices: list[int] = []
        matched_recipe_for_day: list[dict[str, Any] | None] = []

        for weekday in weekdays:
            # Find which recipe covers this day (tolerate whitespace differences)
            matching_recipe = None
            target = normalize(weekday["day_name"])
            for recipe in recipes:
                recipe_days = [normalize(d) for d in recipe.get("days", [])]
                if target in recipe_days:
                    matching_recipe = recipe
                    break
            matched_recipe_for_day.append(matching_recipe)
            if matching_recipe is None:
                unmatched_indices.append(len(matched_recipe_for_day) - 1)

        # Fallback: if the LLM didn't explicitly assign a recipe to every day,
        # distribute the returned recipes round-robin instead of leaving days empty.
        if unmatched_indices and recipes:
            for position, day_index in enumerate(unmatched_indices):
                matched_recipe_for_day[day_index] = recipes[position % len(recipes)]

        days = []
        for weekday, matching_recipe in zip(weekdays, matched_recipe_for_day):
            if matching_recipe:
                days.append(
                    {
                        "date": weekday["date"],
                        "day_name": weekday["day_name"],
                        "recipe_name": matching_recipe["name"],
                        "prep_time": matching_recipe.get("prep_time", ""),
                        "serves": matching_recipe.get("serves", ""),
                        "ingredients": matching_recipe.get("ingredients", []),
                        "instructions": matching_recipe.get("instructions", []),
                    }
                )
            else:
                # Only reachable if the LLM returned no recipes at all
                days.append(
                    {
                        "date": weekday["date"],
                        "day_name": weekday["day_name"],
                        "recipe_name": "غير محدد",
                        "prep_time": "",
                        "serves": "",
                        "ingredients": [],
                        "instructions": [],
                    }
                )

        return {
            "generated_at": datetime.now().isoformat(),
            "days": days,
            "shopping_list": plan_data.get("shopping_list", []),
        }

    finally:
        if owns_client:
            await azure_client.close()
