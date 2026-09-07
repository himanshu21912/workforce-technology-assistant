import asyncio
import json
from typing import Any

from app.tools.github import (
    get_github_repository_details,
    search_github_repositories,
)


def print_result(
    title: str,
    result: dict[str, Any],
) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


async def test_repository_search() -> None:
    result = await search_github_repositories(
        query="FastAPI",
        language="Python",
        limit=3,
        sort="stars",
        order="desc",
    )

    print_result(
        title="SEARCH GITHUB REPOSITORIES",
        result=result,
    )


async def test_repository_details() -> None:
    result = await get_github_repository_details(
        owner="fastapi",
        repository="fastapi",
    )

    print_result(
        title="GET GITHUB REPOSITORY DETAILS",
        result=result,
    )


async def test_missing_repository() -> None:
    result = await get_github_repository_details(
        owner="repository-owner-that-does-not-exist-12345",
        repository="repository-that-does-not-exist-12345",
    )

    print_result(
        title="MISSING GITHUB REPOSITORY",
        result=result,
    )


async def main() -> None:
    await test_repository_search()
    await test_repository_details()
    await test_missing_repository()


if __name__ == "__main__":
    asyncio.run(main())