from typing import Any

from app.schemas.tool import ToolError, ToolResponse


def successful_tool_response(
    data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = ToolResponse(
        success=True,
        data=data,
        error=None,
        metadata=metadata or {},
    )

    return response.model_dump(mode="json")


def failed_tool_response(
    code: str,
    message: str,
) -> dict[str, Any]:
    response = ToolResponse(
        success=False,
        data=None,
        error=ToolError(
            code=code,
            message=message,
        ),
        metadata={},
    )

    return response.model_dump(mode="json")