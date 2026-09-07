from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
)

from app.core.config import get_settings


def create_mcp_client() -> MultiServerMCPClient:
    settings = get_settings()

    return MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": settings.mcp_server_url,
            }
        }
    )