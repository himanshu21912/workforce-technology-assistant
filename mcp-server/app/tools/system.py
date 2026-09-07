from app.core.config import get_settings


def get_server_information() -> dict[str, str]:
    """
    Return basic information about the GitHub MCP server.

    This diagnostic tool is used to verify that the MCP server
    is running and able to execute tools.
    """

    settings = get_settings()

    return {
        "name": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "status": "ok",
    }