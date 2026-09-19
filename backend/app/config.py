import os
from functools import lru_cache
from shlex import split
from urllib.parse import urlsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PAGENT Family Assistant"
    app_host: str = "127.0.0.1"
    app_port: int = 8020
    api_key: str = ""
    mcp_command: str = "/app/.venv/bin/python"
    mcp_args: str = "-m untis_mcp.server"
    mcp_startup_timeout_seconds: float = Field(default=30, gt=0)
    webuntis_server: str | None = None
    webuntis_school: str | None = None
    webuntis_user: str | None = None
    webuntis_password: str | None = None
    azure_foundry_endpoint: str = ""
    azure_foundry_api_key: str = ""
    azure_foundry_model_deployment: str = "gpt-4o-mini"
    azure_foundry_api_version: str = "2024-10-21"
    # Azure AI Foundry project + pre-built agent used for web-search (news/trends pages).
    # azure_ai_project_endpoint is the "Azure AI Project" endpoint shown in the Foundry portal
    # Overview page (can be the same resource as azure_foundry_endpoint above).
    # foundry_agent_name/foundry_agent_version reference a Foundry agent (already configured with
    # its own web search tool) invoked via the agent_reference responses API.
    azure_ai_project_endpoint: str = ""
    foundry_agent_name: str = "personal-web"
    foundry_agent_version: str = "3"
    dashboard_refresh_times: str = "06:30"
    meal_plan_refresh_day: str = "fri"
    meal_plan_refresh_time: str = "20:00"
    news_refresh_time: str = "07:00"
    trends_refresh_day: str = "mon"
    trends_refresh_time: str = "08:00"
    azure_storage_account_name: str = ""
    azure_storage_connection_string: str = ""
    dashboard_blob_container: str = "dashboard-data"
    dashboard_blob_name: str = "latest.json"
    dashboard_status_blob_name: str = "refresh-status.json"
    translation_cache_blob_name: str = "message-translations.json"
    meal_plan_blob_container: str = "meal-plans"
    meal_plan_blob_name: str = "latest.json"
    food_wishes_blob_name: str = "wishes.json"
    news_blob_container: str = "news-data"
    news_blob_name: str = "latest.json"
    trends_blob_container: str = "trends-data"
    trends_blob_name: str = "latest.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def dashboard_refresh_time_list(self) -> list[str]:
        return [value.strip() for value in self.dashboard_refresh_times.split(",") if value.strip()]

    @property
    def azure_openai_endpoint(self) -> str:
        """Resource-level endpoint derived from the Foundry project endpoint, for the Azure OpenAI-compatible API."""
        parsed = urlsplit(self.azure_foundry_endpoint)
        return f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else ""

    @property
    def mcp_arg_list(self) -> list[str]:
        return split(self.mcp_args)

    @property
    def mcp_env(self) -> dict[str, str]:
        env = os.environ.copy()
        webuntis_values = {
            "WEBUNTIS_SERVER": self.webuntis_server,
            "WEBUNTIS_SCHOOL": self.webuntis_school,
            "WEBUNTIS_USER": self.webuntis_user,
            "WEBUNTIS_PASSWORD": self.webuntis_password,
        }
        env.update({key: value for key, value in webuntis_values.items() if value})
        return env


@lru_cache
def get_settings() -> Settings:
    return Settings()