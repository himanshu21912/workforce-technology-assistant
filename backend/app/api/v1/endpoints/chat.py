from fastapi import APIRouter, status

from app.api.dependencies import (
    ChatServiceDependency,
)
from app.schemas.chat import AskRequest, AskResponse
from app.schemas.error import ErrorResponse


router = APIRouter(
    prefix="/ask",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the AI assistant a question",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Session not found.",
        },
        502: {
            "model": ErrorResponse,
            "description": (
                "The AI agent or external dependency failed."
            ),
        },
    },
)
async def ask_question(
    request: AskRequest,
    chat_service: ChatServiceDependency,
) -> AskResponse:
    return await chat_service.ask(
        session_id=request.session_id,
        question=request.question,
        context=request.context,
    )