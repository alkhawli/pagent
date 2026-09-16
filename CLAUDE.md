# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

PAGENT is a parent assistant web app for WebUntis (a school information system). FastAPI backend +
React/TypeScript frontend. It has three main features, each with its own data flow:

1. **Dashboard** — daily snapshot of homework, exams, timetable, and messages, pulled from WebUntis via
   an MCP server and cached in Azure Blob Storage.
2. **AI chat** — natural-language Q&A over the same WebUntis data, using an LLM with tool-calling (function
   calling) against MCP tools.
3. **Meal planning** — LLM-generated weekly family meal plan with a shopping list, incorporating
   user-submitted "food wishes", also cached in Blob Storage.

## Commands

All commands are run via [`just`](https://github.com/casey/just) (`Justfile` at repo root). Windows recipes
have a `-win` suffix; macOS/Linux use the base name.

```bash
# Setup
just install-win / just install        # uv sync (backend) + npm install (frontend)

# Run locally without Docker
just up-win / just up                  # starts backend (uvicorn, port 8020) + frontend (vite, port 5173) in background
just down-win / just down              # stops both
just status-win / just status          # health-check both

# Run locally with Docker (recommended)
just docker-up                         # build + start both containers
just docker-down
just docker-logs

# Tests
just test-win / just test              # cd backend && uv run pytest
```

Direct backend commands (from `backend/`):
```bash
uv sync                                                  # install deps
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
uv run pytest                                            # all tests
uv run pytest tests/test_foundry_agent.py::test_extract_text_from_mcp_result   # single test
```

Direct frontend commands (from `frontend/`):
```bash
npm run dev        # vite dev server
npm run build       # tsc -b && vite build
npm run lint        # oxlint
```

There is no frontend test suite currently. Backend tests live in `backend/tests/` (pytest, configured in
`backend/pyproject.toml` with `pythonpath = ["."]`).

Azure deployment/infra commands (`just tf-*`, `just deploy`, `just restart-backend`, `just logs-backend`,
etc.) operate on live Azure resources via Terraform (`terraform/`) and `az` CLI — treat these as
production-affecting and confirm with the user before running them.

## Architecture

### Backend (`backend/app/`)

Single FastAPI app defined in `main.py` (`create_app()`), with all routes declared inline in that function.
Auth is a single static API key checked via the `X-API-Key` header (`verify_api_key`, no per-user auth).
Settings are a `pydantic-settings` `Settings` object (`config.py`), loaded from `backend/.env` and cached
with `lru_cache`.

Key modules:
- `mcp_client.py` — `McpClient` opens a **fresh stdio subprocess connection** to the WebUntis MCP server
  (`untis-mcp`) per call (`_get_session` is a context manager, not a persistent session). This is what
  `/tools`, `/tools/{name}`, and `/chat` depend on.
- `foundry_agent.py` — `answer_with_mcp()` implements the chat agent: fetches MCP tool definitions, converts
  them to OpenAI-style function schemas, and runs a tool-calling loop (max `MAX_TOOL_ITERATIONS = 6`) against
  Azure AI Foundry's OpenAI-compatible Chat Completions API.
- `dashboard.py` — `build_dashboard()` fans out multiple MCP calls concurrently (`asyncio.gather`) to fetch
  students, homework, messages, subjects, rooms, and timetable, then derives `_build_recommendations()`
  (priority-sorted homework/message/schedule alerts). Message text is translated via `translation.py`
  (LLM-backed, cached per-message in blob storage so repeated refreshes don't re-translate unchanged text).
- `meal_planner.py` — `generate_meal_plan()` prompts Azure OpenAI (Arabic system prompt) for 2-3 recipes
  each covering multiple weekdays, then maps the LLM's freeform `days` field back onto the concrete week's
  weekdays (`_get_next_weekdays`). This day-to-recipe matching is normalized (whitespace-insensitive) and
  falls back to round-robin recipe assignment for any day the LLM didn't explicitly cover — LLM JSON output
  is not schema-validated beyond `response_format={"type": "json_object"}`, so don't assume the model's
  `days` list is complete or well-formed.
- `blob_storage.py` — `BlobJsonStore` wraps Azure Blob Storage as a JSON key-value store. Local dev uses
  `AZURE_STORAGE_CONNECTION_STRING`; deployed environments use `AZURE_STORAGE_ACCOUNT_NAME` with
  `DefaultAzureCredential` (the Web App's managed identity) — there is no local fallback without one of these
  configured.
- `scheduler.py` — `APScheduler` (`AsyncIOScheduler`) cron jobs: daily dashboard refresh
  (`DASHBOARD_REFRESH_TIMES`, comma-separated `HH:MM` list) and weekly meal-plan refresh
  (`MEAL_PLAN_REFRESH_DAY`/`MEAL_PLAN_REFRESH_TIME`). Registered in `main.py`'s `lifespan`, which also kicks
  off an initial dashboard build as a background task on startup so blob storage isn't empty on first boot.

Data flow pattern shared by dashboard and meal-plan: an endpoint (or scheduler job) computes fresh data and
writes it to a blob; `GET /dashboard` and `GET /meal-plan` only ever read the last-written blob snapshot and
503 if nothing has been generated yet. Regeneration (`POST /meal-plan/generate`, `POST /dashboard/refresh`)
and the scheduled cron refresh use the **same** generation function — there is no separate "regenerate" code
path, so bugs in generation affect both equally.

### Frontend (`frontend/src/`)

React + TypeScript + Vite, Tailwind CSS v4, React Router v7, no state management library beyond React
Context. `App.tsx` defines routes; everything except `/login` is wrapped in `ProtectedRoute` (checks for an
API key in `sessionStorage`) and `DashboardProvider` (`context/DashboardContext.tsx`), which loads and holds
the dashboard snapshot for the whole app.

- `api.ts` — thin fetch wrapper (`request<T>`) that attaches `X-API-Key` from `sessionStorage` to every call
  and throws on non-2xx responses. All backend calls go through here; there's no retry/caching layer.
- `pages/` — one component per route (`OverviewPage`, `MessagesPage`, `ChatPage`, `MealPlanPage`,
  `LoginPage`). Page components own their own local loading/error state for anything not in
  `DashboardContext` (e.g. `MealPlanPage` fetches/generates the meal plan itself).
- `components/` — presentational components consumed by pages (e.g. `WeeklyMealCalendar`, `ShoppingList`,
  `CalendarView`, `ChatPanel`, `PriorityBadge`). These generally render props verbatim with no merge/transform
  logic — if a field is empty in the API response, it renders empty.
- `types.ts` — shared TypeScript types mirroring the backend's JSON response shapes (`DashboardSnapshot`,
  `MealPlan`, `DayMeal`, `ChatResponse`, etc.). Keep these in sync manually when backend response shapes
  change; there's no codegen.

### Local dev vs Docker vs Azure

- Local (no Docker): backend on `127.0.0.1:8020`, frontend dev server on `127.0.0.1:5173`, run via `just up`/`just up-win` (PID files in `.run/`).
- Docker Compose: backend container exposes `8020→8000`, frontend container serves a built bundle via nginx
  on `5173→80`, with `VITE_API_BASE_URL` baked in at build time as a Docker build arg.
- Azure: Container Apps/Web Apps behind Terraform (`terraform/`), backend authenticates to Blob Storage via
  managed identity (no connection string), secrets live in Key Vault. `AZURE_FOUNDRY_ENDPOINT` is a Foundry
  **project** endpoint; `Settings.azure_openai_endpoint` derives the resource-level endpoint from it for the
  Azure OpenAI-compatible API calls.

## Language note

User-facing meal-plan content (system prompt, recipe names, weekday names) is generated in **Lebanese Arabic**
by design — this is intentional product behavior, not untranslated text left by mistake.
