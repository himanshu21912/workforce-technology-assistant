from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AgentExecutionError,
    ApplicationError,
    OllamaEmbeddingError,
    OllamaUnavailableError,
    SessionNotFoundError,
)


def create_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": {},
            }
        },
    )


async def session_not_found_handler(
    request: Request,
    exception: SessionNotFoundError,
) -> JSONResponse:
    del request

    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code="session_not_found",
        message=str(exception),
    )


async def agent_execution_error_handler(
    request: Request,
    exception: AgentExecutionError,
) -> JSONResponse:
    del request

    return create_error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        code="agent_execution_failed",
        message=str(exception),
    )


async def ollama_unavailable_handler(
    request: Request,
    exception: OllamaUnavailableError,
) -> JSONResponse:
    del request

    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="ollama_unavailable",
        message=str(exception),
    )


async def ollama_embedding_error_handler(
    request: Request,
    exception: OllamaEmbeddingError,
) -> JSONResponse:
    del request

    return create_error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        code="embedding_generation_failed",
        message=str(exception),
    )


async def application_error_handler(
    request: Request,
    exception: ApplicationError,
) -> JSONResponse:
    del request

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="application_error",
        message=str(exception),
    )


def register_exception_handlers(
    application: FastAPI,
) -> None:
    application.add_exception_handler(
        SessionNotFoundError,
        session_not_found_handler,
    )

    application.add_exception_handler(
        AgentExecutionError,
        agent_execution_error_handler,
    )

    application.add_exception_handler(
        OllamaUnavailableError,
        ollama_unavailable_handler,
    )

    application.add_exception_handler(
        OllamaEmbeddingError,
        ollama_embedding_error_handler,
    )

    application.add_exception_handler(
        ApplicationError,
        application_error_handler,
    )