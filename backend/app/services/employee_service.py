from app.core.exceptions import EmployeeNotFoundError
from app.db.models import Employee
from app.db.repositories import EmployeeRepository
from app.schemas.employee import (
    EmployeeResponse,
    EmployeeSkillResponse,
)


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository,
    ) -> None:
        self._repository = repository

    @staticmethod
    def _to_response(
        employee: Employee,
    ) -> EmployeeResponse:
        sorted_associations = sorted(
            employee.skill_associations,
            key=lambda association: association.skill.name,
        )

        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            email=employee.email,
            role=employee.role,
            department=employee.department.name,
            department_location=(
                employee.department.location
            ),
            years_of_experience=(
                employee.years_of_experience
            ),
            skills=[
                EmployeeSkillResponse(
                    id=association.skill.id,
                    name=association.skill.name,
                    category=association.skill.category,
                    proficiency_level=(
                        association.proficiency_level
                    ),
                    years_of_experience=(
                        association.years_of_experience
                    ),
                )
                for association in sorted_associations
            ],
        )

    async def search_employees(
        self,
        query: str,
        limit: int,
    ) -> list[EmployeeResponse]:
        employees = await self._repository.search(
            query=query,
            limit=limit,
        )

        return [
            self._to_response(employee)
            for employee in employees
        ]

    async def get_employee_details(
        self,
        employee_id: int | None,
        email: str | None,
    ) -> EmployeeResponse:
        provided_identifier_count = sum(
            value is not None
            for value in (
                employee_id,
                email,
            )
        )

        if provided_identifier_count != 1:
            raise ValueError(
                "Provide exactly one of employee_id or email."
            )

        if employee_id is not None:
            employee = await self._repository.get_by_id(
                employee_id
            )
        else:
            employee = await self._repository.get_by_email(
                email or ""
            )

        if employee is None:
            raise EmployeeNotFoundError(
                "No employee was found for the provided identifier."
            )

        return self._to_response(employee)