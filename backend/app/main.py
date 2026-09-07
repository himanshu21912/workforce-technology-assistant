from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.lifespan import application_lifespan


settings = get_settings()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Backend API for the AI-Powered Workforce and "
            "Technology Recommendation Assistant."
        ),
        debug=settings.debug,
        lifespan=application_lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    @application.get(
        "/",
        tags=["Root"],
        summary="Get API information",
    )
    async def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "documentation": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    return application


app = create_application()