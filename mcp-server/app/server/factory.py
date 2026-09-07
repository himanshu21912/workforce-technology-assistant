from fastmcp import FastMCP

from app.core.config import get_settings
from app.tools import get_registered_tool_functions


def create_mcp_server() -> FastMCP:
    settings = get_settings()

    server = FastMCP(
        name=settings.service_name,
    )

    for tool_function in get_registered_tool_functions():
        server.tool(tool_function)

    return server