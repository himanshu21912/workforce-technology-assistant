from typing import Any

from langchain_core.tools import BaseTool, tool

from app.core.exceptions import DepartmentNotFoundError
from app.db.repositories import (
    WorkforceAnalyticsRepository,
)
from app.db.session import AsyncSessionFactory
from app.schemas.workforce import (
    WorkforceSkillAnalysisInput,
)
from app.services import WorkforceAnalyticsService
from app.tools.workforce.helpers import (
    failed_tool_response,
    successful_tool_response,
)


def create_analyze_workforce_skills_tool() -> BaseTool:
    @tool(
        "analyze_workforce_skills",
        args_schema=WorkforceSkillAnalysisInput,
    )
    async def analyze_workforce_skills(
        department: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Analyze skills available across the internal workforce.

        Use this tool for questions about common technologies,
        skill distribution, capability concentration, or average
        skill-specific experience. Optionally restrict the
        analysis to one department.
        """

        try:
            async with AsyncSessionFactory() as session:
                repository = WorkforceAnalyticsRepository(
                    session
                )

                service = WorkforceAnalyticsService(
                    repository
                )

                analysis = (
                    await service.analyze_workforce_skills(
                        department=department,
                        limit=limit,
                    )
                )

            return successful_tool_response(
                data=analysis,
                metadata={
                    "source": "postgresql",
                    "tool": "analyze_workforce_skills",
                },
            )

        except DepartmentNotFoundError as exception:
            return failed_tool_response(
                code="department_not_found",
                message=str(exception),
            )

        except Exception:
            return failed_tool_response(
                code="workforce_skill_analysis_failed",
                message=(
                    "The workforce skill analysis could not "
                    "be completed."
                ),
            )

    return analyze_workforce_skills