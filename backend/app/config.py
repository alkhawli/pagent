import os
from functools import lru_cache
from shlex import split
from urllib.parse import urlsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PAGENT Untis Chatbot"
    app_host: str = "127.0.0.1"
    app_port: int = 8020
    mcp_command: str = "uvx"
    mcp_args: str = "--from git+https://github.com/kohlsalem/untis-mcp --with mcp<2 untis-mcp"
    mcp_startup_timeout_seconds: float = Field(default=30, gt=0)
    webuntis_server: str | None = None
    webuntis_school: str | None = None
    webuntis_user: str | None = None
    webuntis_password: str | None = None
    azure_foundry_endpoint: str = ""
    azure_foundry_api_key: str = ""
    azure_foundry_model_deployment: str = "gpt-4o-mini"
    azure_foundry_api_version: str = "2024-10-21"
    dashboard_data_dir: str = "data"
    dashboard_refresh_times: str = "07:00,13:00,19:00"

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