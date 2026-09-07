from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from app.api.dependencies import (
    SemanticCacheServiceDependency,
    SessionServiceDependency,
)
from app.schemas.chat import DeleteSessionResponse
from app.schemas.error import ErrorResponse
from app.schemas.session import (
    ChatSession,
    CreateSessionInput,
    SessionHistory,
    SessionListResponse,
    UpdateSessionInput,
)


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post(
    "",
    response_model=ChatSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create a conversation session",
)
async def create_session(
    request: CreateSessionInput,
    session_service: SessionServiceDependency,
) -> ChatSession:
    return await session_service.create_session(
        title=request.title
    )


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List active conversation sessions",
)
async def list_sessions(
    session_service: SessionServiceDependency,
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
) -> SessionListResponse:
    sessions = await session_service.list_sessions(
        limit=limit
    )

    return SessionListResponse(
        count=len(sessions),
        sessions=sessions,
    )


@router.get(
    "/{session_id}",
    response_model=SessionHistory,
    summary="Get session history",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Session not found.",
        }
    },
)
async def get_session_history(
    session_id: str,
    session_service: SessionServiceDependency,
    message_limit: int | None = Query(
        default=None,
        ge=1,
        le=500,
    ),
) -> SessionHistory:
    try:
        return await session_service.get_session_history(
            session_id=session_id,
            message_limit=message_limit,
        )
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "session_not_found",
                "message": str(exception),
            },
        ) from exception


@router.patch(
    "/{session_id}",
    response_model=ChatSession,
    summary="Update the session title",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Session not found.",
        }
    },
)
async def update_session(
    session_id: str,
    request: UpdateSessionInput,
    session_service: SessionServiceDependency,
) -> ChatSession:
    try:
        return await session_service.update_session_title(
            session_id=session_id,
            title=request.title,
        )
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "session_not_found",
                "message": str(exception),
            },
        ) from exception

@router.delete(
    "/{session_id}",
    response_model=DeleteSessionResponse,
    summary="Delete a session and its semantic cache",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Session not found.",
        }
    },
)
async def delete_session(
    session_id: str,
    session_service: SessionServiceDependency,
    semantic_cache_service: (
        SemanticCacheServiceDependency
    ),
) -> DeleteSessionResponse:
    session = await session_service.get_session(
        session_id
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "session_not_found",
                "message": (
                    "The requested session was not found."
                ),
            },
        )

    semantic_cache_entries_deleted = (
        await semantic_cache_service.clear_session(
            session_id
        )
    )

    session_deleted = (
        await session_service.delete_session(
            session_id
        )
    )

    return DeleteSessionResponse(
        session_id=session_id,
        session_deleted=session_deleted,
        semantic_cache_entries_deleted=(
            semantic_cache_entries_deleted
        ),
    )