from langchain_core.tools import BaseTool

from app.mcp.client import create_mcp_client


async def load_external_mcp_tools() -> list[BaseTool]:
    client = create_mcp_client()

    tools = await client.get_tools()

    return list(tools)