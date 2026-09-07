from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "GitHub MCP Server"
    service_version: str = "0.2.0"
    environment: str = "development"

    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8001

    github_api_base_url: str = "https://api.github.com"
    github_token: str | None = None

    github_request_timeout: float = Field(
        default=10.0,
        gt=0,
        le=60,
    )

    github_user_agent: str = (
        "workforce-technology-assistant/0.2.0"
    )

    github_api_version: str = "2022-11-28"

    github_default_result_limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    github_max_result_limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()