from typing import Any

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Department,
    Employee,
    EmployeeSkill,
    Skill,
)


class WorkforceAnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def department_exists(
        self,
        department_name: str,
    ) -> bool:
        statement = select(Department.id).where(
            func.lower(Department.name)
            == department_name.strip().lower(),
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none() is not None

    async def get_overall_statistics(
        self,
        department: str | None = None,
    ) -> dict[str, Any]:
        employee_count_statement = select(
            func.count(distinct(Employee.id))
        )

        average_experience_statement = select(
            func.coalesce(
                func.avg(Employee.years_of_experience),
                0,
            )
        )

        if department:
            employee_count_statement = (
                employee_count_statement
                .join(
                    Department,
                    Department.id == Employee.department_id,
                )
                .where(
                    func.lower(Department.name)
                    == department.strip().lower()
                )
            )

            average_experience_statement = (
                average_experience_statement
                .join(
                    Department,
                    Department.id == Employee.department_id,
                )
                .where(
                    func.lower(Department.name)
                    == department.strip().lower()
                )
            )

        employee_count_result = await self._session.execute(
            employee_count_statement
        )

        average_experience_result = await self._session.execute(
            average_experience_statement
        )

        total_employees = int(
            employee_count_result.scalar_one()
        )

        average_experience = float(
            average_experience_result.scalar_one()
        )

        if department:
            department_rows = [
                {
                    "department": department,
                    "employee_count": total_employees,
                }
            ]
        else:
            department_statement = (
                select(
                    Department.name,
                    func.count(Employee.id).label(
                        "employee_count"
                    ),
                )
                .outerjoin(
                    Employee,
                    Employee.department_id == Department.id,
                )
                .group_by(
                    Department.id,
                    Department.name,
                )
                .order_by(
                    func.count(Employee.id).desc(),
                    Department.name.asc(),
                )
            )

            department_result = await self._session.execute(
                department_statement
            )

            department_rows = [
                {
                    "department": row.name,
                    "employee_count": int(
                        row.employee_count
                    ),
                }
                for row in department_result.all()
            ]

        role_statement = (
            select(
                Employee.role,
                func.count(Employee.id).label(
                    "employee_count"
                ),
            )
            .group_by(Employee.role)
            .order_by(
                func.count(Employee.id).desc(),
                Employee.role.asc(),
            )
        )

        if department:
            role_statement = (
                role_statement
                .join(
                    Department,
                    Department.id == Employee.department_id,
                )
                .where(
                    func.lower(Department.name)
                    == department.strip().lower()
                )
            )

        role_result = await self._session.execute(
            role_statement
        )

        role_rows = [
            {
                "role": row.role,
                "employee_count": int(
                    row.employee_count
                ),
            }
            for row in role_result.all()
        ]

        return {
            "department_filter": department,
            "total_employees": total_employees,
            "average_years_of_experience": round(
                average_experience,
                2,
            ),
            "employees_by_department": department_rows,
            "employees_by_role": role_rows,
        }

    async def get_skill_analysis(
        self,
        department: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        statement = (
            select(
                Skill.id,
                Skill.name,
                Skill.category,
                func.count(
                    distinct(EmployeeSkill.employee_id)
                ).label("employee_count"),
                func.coalesce(
                    func.avg(
                        EmployeeSkill.years_of_experience
                    ),
                    0,
                ).label("average_skill_experience"),
            )
            .join(
                EmployeeSkill,
                EmployeeSkill.skill_id == Skill.id,
            )
            .join(
                Employee,
                Employee.id == EmployeeSkill.employee_id,
            )
            .group_by(
                Skill.id,
                Skill.name,
                Skill.category,
            )
            .order_by(
                func.count(
                    distinct(EmployeeSkill.employee_id)
                ).desc(),
                Skill.name.asc(),
            )
            .limit(limit)
        )

        if department:
            statement = (
                statement
                .join(
                    Department,
                    Department.id == Employee.department_id,
                )
                .where(
                    func.lower(Department.name)
                    == department.strip().lower()
                )
            )

        result = await self._session.execute(statement)

        return [
            {
                "skill_id": row.id,
                "skill": row.name,
                "category": row.category,
                "employee_count": int(row.employee_count),
                "average_years_of_experience": round(
                    float(row.average_skill_experience),
                    2,
                ),
            }
            for row in result.all()
        ]