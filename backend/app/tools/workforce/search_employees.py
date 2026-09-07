from typing import Any

from langchain_core.tools import BaseTool, tool

from app.db.repositories import EmployeeRepository
from app.db.session import AsyncSessionFactory
from app.schemas.employee import EmployeeSearchInput
from app.services import EmployeeService
from app.tools.workforce.helpers import (
    failed_tool_response,
    successful_tool_response,
)


def create_search_employees_tool() -> BaseTool:
    @tool(
        "search_employees",
        args_schema=EmployeeSearchInput,
    )
    async def search_employees(
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Search the organization's internal employee database.

        Use this tool for questions about employees, names,
        email addresses, job roles, departments, technologies,
        skills, or skill categories. The search is
        case-insensitive and returns structured employee data.
        Do not use this tool for public GitHub information.
        """

        try:
            async with AsyncSessionFactory() as session:
                repository = EmployeeRepository(session)
                service = EmployeeService(repository)

                employees = await service.search_employees(
                    query=query,
                    limit=limit,
                )

            employee_data = [
                employee.model_dump(mode="json")
                for employee in employees
            ]

            return successful_tool_response(
                data={
                    "query": query,
                    "count": len(employee_data),
                    "employees": employee_data,
                },
                metadata={
                    "source": "postgresql",
                    "tool": "search_employees",
                },
            )

        except Exception:
            return failed_tool_response(
                code="employee_search_failed",
                message=(
                    "The employee search could not be "
                    "completed."
                ),
            )

    return search_employees