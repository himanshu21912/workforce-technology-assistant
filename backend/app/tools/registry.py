from langchain_core.tools import BaseTool

from app.tools.workforce import create_workforce_tools


def create_internal_tools() -> list[BaseTool]:
    tools = create_workforce_tools()

    tool_names = [tool.name for tool in tools]

    if len(tool_names) != len(set(tool_names)):
        raise RuntimeError(
            "Duplicate internal tool names were detected."
        )

    return tools