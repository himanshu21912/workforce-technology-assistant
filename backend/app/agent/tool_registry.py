from langchain_core.tools import BaseTool

from app.mcp import load_external_mcp_tools
from app.schemas.agent import AgentSource
from app.tools import create_internal_tools


INTERNAL_TOOL_NAMES = {
    "search_employees",
    "get_employee_details",
    "get_employee_statistics",
    "analyze_workforce_skills",
}

EXTERNAL_TOOL_NAMES = {
    "search_github_repositories",
    "get_github_repository_details",
}


async def create_agent_tools() -> list[BaseTool]:
    """
    Load and combine the application's internal LangChain tools
    with the external GitHub tools discovered through MCP.
    """

    internal_tools = create_internal_tools()

    discovered_mcp_tools = await load_external_mcp_tools()

    external_tools = [
        tool
        for tool in discovered_mcp_tools
        if tool.name in EXTERNAL_TOOL_NAMES
    ]

    all_tools = [
        *internal_tools,
        *external_tools,
    ]

    tool_names = [
        tool.name
        for tool in all_tools
    ]

    if len(tool_names) != len(set(tool_names)):
        raise RuntimeError(
            "Duplicate agent tool names were detected."
        )

    available_tool_names = set(tool_names)

    missing_internal_tools = (
        INTERNAL_TOOL_NAMES - available_tool_names
    )

    if missing_internal_tools:
        missing_names = ", ".join(
            sorted(missing_internal_tools)
        )

        raise RuntimeError(
            "Required internal tools are unavailable: "
            f"{missing_names}"
        )

    missing_external_tools = (
        EXTERNAL_TOOL_NAMES - available_tool_names
    )

    if missing_external_tools:
        missing_names = ", ".join(
            sorted(missing_external_tools)
        )

        raise RuntimeError(
            "Required external tools are unavailable: "
            f"{missing_names}"
        )

    return all_tools


def determine_agent_source(
    tools_used: list[str],
) -> AgentSource:
    """
    Classify where an answer came from, based on which tools
    the agent actually used.
    """

    used_internal = any(
        tool_name in INTERNAL_TOOL_NAMES
        for tool_name in tools_used
    )

    used_external = any(
        tool_name in EXTERNAL_TOOL_NAMES
        for tool_name in tools_used
    )

    if used_internal and used_external:
        return "multi_source"

    if used_internal:
        return "postgresql"

    if used_external:
        return "github_mcp"

    return "llm"
