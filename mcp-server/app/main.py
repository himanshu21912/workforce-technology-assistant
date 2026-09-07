from app.core.config import get_settings
from app.server.factory import create_mcp_server


settings = get_settings()
mcp = create_mcp_server()


def main() -> None:
    mcp.run(
        transport="http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()