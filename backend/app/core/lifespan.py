from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import close_database_engine
from app.integrations.redis import close_redis_client


@asynccontextmanager
async def application_lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    del application

    yield

    await close_redis_client()
    await close_database_engine()