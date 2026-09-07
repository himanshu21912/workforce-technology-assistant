from collections.abc import Callable
from typing import Any

from app.tools.github import (
    get_github_repository_details,
    search_github_repositories,
)
from app.tools.system import get_server_information


MCPToolFunction = Callable[..., Any]


def get_registered_tool_functions() -> list[MCPToolFunction]:
    tool_functions: list[MCPToolFunction] = [
        get_server_information,
        search_github_repositories,
        get_github_repository_details,
    ]

    tool_names = [
        tool_function.__name__
        for tool_function in tool_functions
    ]

    if len(tool_names) != len(set(tool_names)):
        raise RuntimeError(
            "Duplicate MCP tool function names were detected."
        )

    return tool_functions