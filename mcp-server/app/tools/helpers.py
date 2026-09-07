from typing import Any

from app.schemas.tool import ToolError, ToolResponse


def successful_tool_response(
    *,
    data: dict[str, Any],
    tool_name: str,
) -> dict[str, Any]:
    response = ToolResponse(
        success=True,
        data=data,
        error=None,
        metadata={
            "source": "github_rest_api",
            "tool": tool_name,
        },
    )

    return response.model_dump(mode="json")


def failed_tool_response(
    *,
    code: str,
    message: str,
    tool_name: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = ToolResponse(
        success=False,
        data=None,
        error=ToolError(
            code=code,
            message=message,
            details=details or {},
        ),
        metadata={
            "source": "github_rest_api",
            "tool": tool_name,
        },
    )

    return response.model_dump(mode="json")