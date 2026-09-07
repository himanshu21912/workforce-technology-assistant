from langchain_core.tools import BaseTool

from app.tools.workforce.analyze_workforce_skills import (
    create_analyze_workforce_skills_tool,
)
from app.tools.workforce.get_employee_details import (
    create_get_employee_details_tool,
)
from app.tools.workforce.get_employee_statistics import (
    create_get_employee_statistics_tool,
)
from app.tools.workforce.search_employees import (
    create_search_employees_tool,
)


def create_workforce_tools() -> list[BaseTool]:
    return [
        create_search_employees_tool(),
        create_get_employee_details_tool(),
        create_get_employee_statistics_tool(),
        create_analyze_workforce_skills_tool(),
    ]


__all__ = [
    "create_analyze_workforce_skills_tool",
    "create_get_employee_details_tool",
    "create_get_employee_statistics_tool",
    "create_search_employees_tool",
    "create_workforce_tools",
]