from fastmcp import FastMCP

from app.core.config import get_settings
from app.tools.system import get_server_information


def create_mcp_server() -> FastMCP:
    settings = get_settings()

    server = FastMCP(
        name=settings.service_name,
    )

    server.tool(
        name="get_server_information",
        description=(
            "Return the name, version, environment, and status "
            "of the GitHub MCP server."
        ),
    )(get_server_information)

    return server