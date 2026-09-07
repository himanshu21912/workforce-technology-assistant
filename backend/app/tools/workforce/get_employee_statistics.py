from typing import Any

from langchain_core.tools import BaseTool, tool

from app.core.exceptions import DepartmentNotFoundError
from app.db.repositories import (
    WorkforceAnalyticsRepository,
)
from app.db.session import AsyncSessionFactory
from app.schemas.workforce import EmployeeStatisticsInput
from app.services import WorkforceAnalyticsService
from app.tools.workforce.helpers import (
    failed_tool_response,
    successful_tool_response,
)


def create_get_employee_statistics_tool() -> BaseTool:
    @tool(
        "get_employee_statistics",
        args_schema=EmployeeStatisticsInput,
    )
    async def get_employee_statistics(
        department: str | None = None,
    ) -> dict[str, Any]:
        """
        Return internal workforce statistics from PostgreSQL.

        Use this tool for employee counts, department counts,
        role distributions, and average employee experience.
        Optionally restrict the statistics to one department.
        Do not use this tool for information about one specific
        employee.
        """

        try:
            async with AsyncSessionFactory() as session:
                repository = WorkforceAnalyticsRepository(
                    session
                )

                service = WorkforceAnalyticsService(
                    repository
                )

                statistics = (
                    await service.get_employee_statistics(
                        department=department,
                    )
                )

            return successful_tool_response(
                data=statistics,
                metadata={
                    "source": "postgresql",
                    "tool": "get_employee_statistics",
                },
            )

        except DepartmentNotFoundError as exception:
            return failed_tool_response(
                code="department_not_found",
                message=str(exception),
            )

        except Exception:
            return failed_tool_response(
                code="employee_statistics_failed",
                message=(
                    "Workforce statistics could not be "
                    "calculated."
                ),
            )

    return get_employee_statistics