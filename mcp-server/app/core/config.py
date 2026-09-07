from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "GitHub MCP Server"
    service_version: str = "0.1.0"
    environment: str = "development"

    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8001

    github_api_base_url: str = "https://api.github.com"
    github_token: str | None = None
    github_request_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()