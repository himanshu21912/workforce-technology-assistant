from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_name: str = "Workforce Technology Assistant API"
    app_version: str = "0.3.0"
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
    redis_socket_timeout: float = Field(
        default=5.0,
        gt=0,
        le=60,
    )
    redis_max_connections: int = Field(
        default=20,
        ge=1,
        le=500,
    )

    conversation_key_prefix: str = "chat"
    conversation_ttl_seconds: int = Field(
        default=86400,
        ge=60,
    )
    conversation_max_messages: int = Field(
        default=40,
        ge=2,
        le=500,
    )
    session_default_title: str = "New conversation"
    session_list_limit: int = Field(
        default=50,
        ge=1,
        le=500,
    )

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