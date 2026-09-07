import asyncio
from dataclasses import dataclass

from sqlalchemy import select

from app.db.models import (
    Department,
    Employee,
    EmployeeSkill,
    ProficiencyLevel,
    Skill,
)
from app.db.session import AsyncSessionFactory, close_database_engine


@dataclass(frozen=True)
class SkillAssignment:
    name: str
    proficiency: ProficiencyLevel
    years: int


@dataclass(frozen=True)
class EmployeeSeed:
    name: str
    email: str
    role: str
    department: str
    years_of_experience: int
    skills: tuple[SkillAssignment, ...]


DEPARTMENTS = (
    {
        "name": "Engineering",
        "location": "Bangalore",
        "description": "Software engineering and platform development.",
    },
    {
        "name": "Data Science",
        "location": "Bangalore",
        "description": "Artificial intelligence, analytics, and data science.",
    },
    {
        "name": "Quality Assurance",
        "location": "Bangalore",
        "description": "Software quality engineering and test automation.",
    },
    {
        "name": "Human Resources",
        "location": "Bangalore",
        "description": "Employee operations and organizational development.",
    },
)


SKILLS = (
    {
        "name": "Python",
        "category": "Programming Language",
    },
    {
        "name": "TypeScript",
        "category": "Programming Language",
    },
    {
        "name": "FastAPI",
        "category": "Backend Framework",
    },
    {
        "name": "Next.js",
        "category": "Frontend Framework",
    },
    {
        "name": "PostgreSQL",
        "category": "Database",
    },
    {
        "name": "Redis",
        "category": "Database",
    },
    {
        "name": "Docker",
        "category": "DevOps",
    },
    {
        "name": "Playwright",
        "category": "Testing",
    },
    {
        "name": "LangChain",
        "category": "AI Framework",
    },
    {
        "name": "Machine Learning",
        "category": "Artificial Intelligence",
    },
)


EMPLOYEES = (
    EmployeeSeed(
        name="Ravi Kumar",
        email="ravi.kumar@example.com",
        role="Backend Engineer",
        department="Engineering",
        years_of_experience=5,
        skills=(
            SkillAssignment(
                "Python",
                ProficiencyLevel.ADVANCED,
                5,
            ),
            SkillAssignment(
                "FastAPI",
                ProficiencyLevel.ADVANCED,
                3,
            ),
            SkillAssignment(
                "PostgreSQL",
                ProficiencyLevel.ADVANCED,
                4,
            ),
            SkillAssignment(
                "Docker",
                ProficiencyLevel.INTERMEDIATE,
                3,
            ),
        ),
    ),
    EmployeeSeed(
        name="Ananya Sharma",
        email="ananya.sharma@example.com",
        role="AI Engineer",
        department="Data Science",
        years_of_experience=4,
        skills=(
            SkillAssignment(
                "Python",
                ProficiencyLevel.ADVANCED,
                4,
            ),
            SkillAssignment(
                "LangChain",
                ProficiencyLevel.ADVANCED,
                2,
            ),
            SkillAssignment(
                "Machine Learning",
                ProficiencyLevel.ADVANCED,
                4,
            ),
            SkillAssignment(
                "FastAPI",
                ProficiencyLevel.INTERMEDIATE,
                2,
            ),
        ),
    ),
    EmployeeSeed(
        name="Vikram Singh",
        email="vikram.singh@example.com",
        role="Software Engineer",
        department="Engineering",
        years_of_experience=3,
        skills=(
            SkillAssignment(
                "Python",
                ProficiencyLevel.INTERMEDIATE,
                3,
            ),
            SkillAssignment(
                "FastAPI",
                ProficiencyLevel.INTERMEDIATE,
                2,
            ),
            SkillAssignment(
                "Next.js",
                ProficiencyLevel.INTERMEDIATE,
                2,
            ),
            SkillAssignment(
                "Docker",
                ProficiencyLevel.INTERMEDIATE,
                2,
            ),
        ),
    ),
    EmployeeSeed(
        name="Meera Nair",
        email="meera.nair@example.com",
        role="QA Automation Engineer",
        department="Quality Assurance",
        years_of_experience=4,
        skills=(
            SkillAssignment(
                "TypeScript",
                ProficiencyLevel.ADVANCED,
                3,
            ),
            SkillAssignment(
                "Playwright",
                ProficiencyLevel.ADVANCED,
                3,
            ),
            SkillAssignment(
                "Python",
                ProficiencyLevel.INTERMEDIATE,
                2,
            ),
        ),
    ),
    EmployeeSeed(
        name="Arjun Rao",
        email="arjun.rao@example.com",
        role="Frontend Engineer",
        department="Engineering",
        years_of_experience=4,
        skills=(
            SkillAssignment(
                "TypeScript",
                ProficiencyLevel.ADVANCED,
                4,
            ),
            SkillAssignment(
                "Next.js",
                ProficiencyLevel.ADVANCED,
                3,
            ),
            SkillAssignment(
                "Playwright",
                ProficiencyLevel.INTERMEDIATE,
                2,
            ),
        ),
    ),
)


async def seed_departments(session) -> dict[str, Department]:
    existing_result = await session.execute(
        select(Department),
    )

    existing = {
        department.name: department
        for department in existing_result.scalars().all()
    }

    for department_data in DEPARTMENTS:
        name = department_data["name"]

        if name not in existing:
            department = Department(**department_data)
            session.add(department)
            existing[name] = department

    await session.flush()

    return existing


async def seed_skills(session) -> dict[str, Skill]:
    existing_result = await session.execute(
        select(Skill),
    )

    existing = {
        skill.name: skill
        for skill in existing_result.scalars().all()
    }

    for skill_data in SKILLS:
        name = skill_data["name"]

        if name not in existing:
            skill = Skill(**skill_data)
            session.add(skill)
            existing[name] = skill

    await session.flush()

    return existing


async def seed_employees(
    session,
    departments: dict[str, Department],
    skills: dict[str, Skill],
) -> None:
    existing_result = await session.execute(
        select(Employee.email),
    )

    existing_emails = set(existing_result.scalars().all())

    for employee_data in EMPLOYEES:
        if employee_data.email in existing_emails:
            continue

        employee = Employee(
            name=employee_data.name,
            email=employee_data.email,
            role=employee_data.role,
            department_id=departments[
                employee_data.department
            ].id,
            years_of_experience=(
                employee_data.years_of_experience
            ),
        )

        session.add(employee)
        await session.flush()

        for assignment in employee_data.skills:
            employee_skill = EmployeeSkill(
                employee_id=employee.id,
                skill_id=skills[assignment.name].id,
                proficiency_level=assignment.proficiency,
                years_of_experience=assignment.years,
            )

            session.add(employee_skill)


async def seed_database() -> None:
    async with AsyncSessionFactory() as session:
        try:
            async with session.begin():
                departments = await seed_departments(session)
                skills = await seed_skills(session)

                await seed_employees(
                    session,
                    departments,
                    skills,
                )

            print("Database seed completed successfully.")
        except Exception:
            await session.rollback()
            raise


async def main() -> None:
    try:
        await seed_database()
    finally:
        await close_database_engine()


if __name__ == "__main__":
    asyncio.run(main())