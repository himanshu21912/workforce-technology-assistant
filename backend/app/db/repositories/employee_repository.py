from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Department,
    Employee,
    EmployeeSkill,
    Skill,
)


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _with_employee_relationships(
        statement: Select,
    ) -> Select:
        return statement.options(
            selectinload(Employee.department),
            selectinload(
                Employee.skill_associations
            ).selectinload(EmployeeSkill.skill),
        )

    async def search(
        self,
        query: str,
        limit: int,
    ) -> list[Employee]:
        search_pattern = f"%{query.strip()}%"

        matching_employee_ids = (
            select(Employee.id)
            .join(
                Department,
                Employee.department_id == Department.id,
            )
            .outerjoin(
                EmployeeSkill,
                EmployeeSkill.employee_id == Employee.id,
            )
            .outerjoin(
                Skill,
                Skill.id == EmployeeSkill.skill_id,
            )
            .where(
                or_(
                    Employee.name.ilike(search_pattern),
                    Employee.email.ilike(search_pattern),
                    Employee.role.ilike(search_pattern),
                    Department.name.ilike(search_pattern),
                    Skill.name.ilike(search_pattern),
                    Skill.category.ilike(search_pattern),
                )
            )
            # GROUP BY on the primary key deduplicates the rows the
            # skill outer joins produce. DISTINCT cannot be used here:
            # PostgreSQL requires every ORDER BY expression to appear in
            # the select list, and this subquery must return exactly one
            # column to be usable with IN. Grouping by the primary key
            # makes employees.name functionally dependent, so ordering
            # by it stays valid.
            .group_by(Employee.id)
            .order_by(Employee.name.asc())
            .limit(limit)
        )

        statement = (
            select(Employee)
            .where(Employee.id.in_(matching_employee_ids))
            .order_by(Employee.name.asc())
        )

        statement = self._with_employee_relationships(
            statement,
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_by_id(
        self,
        employee_id: int,
    ) -> Employee | None:
        statement = select(Employee).where(
            Employee.id == employee_id,
        )

        statement = self._with_employee_relationships(
            statement,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> Employee | None:
        statement = select(Employee).where(
            func.lower(Employee.email) == email.strip().lower(),
        )

        statement = self._with_employee_relationships(
            statement,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()