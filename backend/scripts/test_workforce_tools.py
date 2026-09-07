import asyncio
import json
from typing import Any

from app.db.session import close_database_engine
from app.tools import create_internal_tools


def print_result(
    tool_name: str,
    result: dict[str, Any],
) -> None:
    print()
    print("=" * 80)
    print(f"TOOL: {tool_name}")
    print("=" * 80)
    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


async def run_tool_tests() -> None:
    tools = {
        tool.name: tool
        for tool in create_internal_tools()
    }

    search_result = await tools[
        "search_employees"
    ].ainvoke(
        {
            "query": "Python",
            "limit": 10,
        }
    )

    print_result(
        "search_employees",
        search_result,
    )

    employee_details_result = await tools[
        "get_employee_details"
    ].ainvoke(
        {
            "email": "ravi.kumar@example.com",
        }
    )

    print_result(
        "get_employee_details",
        employee_details_result,
    )

    statistics_result = await tools[
        "get_employee_statistics"
    ].ainvoke(
        {
            "department": "Engineering",
        }
    )

    print_result(
        "get_employee_statistics",
        statistics_result,
    )

    skills_result = await tools[
        "analyze_workforce_skills"
    ].ainvoke(
        {
            "department": "Engineering",
            "limit": 10,
        }
    )

    print_result(
        "analyze_workforce_skills",
        skills_result,
    )


async def main() -> None:
    try:
        await run_tool_tests()
    finally:
        await close_database_engine()


if __name__ == "__main__":
    asyncio.run(main())