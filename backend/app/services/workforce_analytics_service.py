from typing import Any

from app.core.exceptions import DepartmentNotFoundError
from app.db.repositories import (
    WorkforceAnalyticsRepository,
)


class WorkforceAnalyticsService:
    def __init__(
        self,
        repository: WorkforceAnalyticsRepository,
    ) -> None:
        self._repository = repository

    async def _validate_department(
        self,
        department: str | None,
    ) -> None:
        if department is None:
            return

        exists = await self._repository.department_exists(
            department
        )

        if not exists:
            raise DepartmentNotFoundError(
                f"Department '{department}' was not found."
            )

    async def get_employee_statistics(
        self,
        department: str | None,
    ) -> dict[str, Any]:
        await self._validate_department(department)

        return await self._repository.get_overall_statistics(
            department=department,
        )

    async def analyze_workforce_skills(
        self,
        department: str | None,
        limit: int,
    ) -> dict[str, Any]:
        await self._validate_department(department)

        skills = await self._repository.get_skill_analysis(
            department=department,
            limit=limit,
        )

        return {
            "department_filter": department,
            "total_skills_returned": len(skills),
            "skills": skills,
        }