from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_name: str = "Workforce Technology Assistant API"
    app_version: str = "0.2.0"
    environment: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:3000"

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "workforce_assistant"
    postgres_user: str = "workforce_user"
    postgres_password: str = "workforce_password"

    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30

    redis_url: str = "redis://redis:6379/0"

    mcp_server_url: str = "http://mcp-server:8001/mcp"

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_chat_model: str = "qwen3:8b"
    ollama_embedding_model: str = "embeddinggemma"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()