from typing import Literal

from pydantic import BaseModel


class ServiceInformation(BaseModel):
    name: str
    version: str
    environment: str


class DependencyHealth(BaseModel):
    status: Literal["connected", "unavailable"]
    message: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: ServiceInformation
    dependencies: dict[str, DependencyHealth]