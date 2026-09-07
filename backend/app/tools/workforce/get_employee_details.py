from typing import Any

from langchain_core.tools import BaseTool, tool

from app.core.exceptions import EmployeeNotFoundError
from app.db.repositories import EmployeeRepository
from app.db.session import AsyncSessionFactory
from app.schemas.employee import EmployeeDetailsInput
from app.services import EmployeeService
from app.tools.workforce.helpers import (
    failed_tool_response,
    successful_tool_response,
)


def create_get_employee_details_tool() -> BaseTool:
    @tool(
        "get_employee_details",
        args_schema=EmployeeDetailsInput,
    )
    async def get_employee_details(
        employee_id: int | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve complete information for one internal employee.

        Use this tool when an employee ID or employee email is
        known and detailed information is required. Provide
        exactly one identifier: employee_id or email. The result
        includes role, department, overall experience, and skills.
        """

        try:
            request = EmployeeDetailsInput(
                employee_id=employee_id,
                email=email,
            )

            request.validate_identifier()

            async with AsyncSessionFactory() as session:
                repository = EmployeeRepository(session)
                service = EmployeeService(repository)

                employee = await service.get_employee_details(
                    employee_id=request.employee_id,
                    email=request.email,
                )

            return successful_tool_response(
                data={
                    "employee": employee.model_dump(
                        mode="json"
                    ),
                },
                metadata={
                    "source": "postgresql",
                    "tool": "get_employee_details",
                },
            )

        except EmployeeNotFoundError as exception:
            return failed_tool_response(
                code="employee_not_found",
                message=str(exception),
            )

        except ValueError as exception:
            return failed_tool_response(
                code="invalid_employee_identifier",
                message=str(exception),
            )

        except Exception:
            return failed_tool_response(
                code="employee_details_failed",
                message=(
                    "Employee details could not be retrieved."
                ),
            )

    return get_employee_details