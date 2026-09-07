from typing import Any

from app.core.exceptions import GitHubRequestError
from app.integrations.github import (
    GitHubClient,
    map_repository_details,
    map_repository_summary,
)
from app.schemas.github import GitHubRepositoryDetails


class GitHubService:
    def __init__(self, client: GitHubClient) -> None:
        self._client = client

    async def search_repositories(
        self,
        *,
        query: str,
        language: str | None,
        limit: int,
        sort: str,
        order: str,
    ) -> dict[str, Any]:
        response_data = await self._client.search_repositories(
            query=query,
            language=language,
            limit=limit,
            sort=sort,
            order=order,
        )

        raw_items = response_data.get("items", [])

        if not isinstance(raw_items, list):
            raise GitHubRequestError(
                "GitHub search results are invalid."
            )

        repositories = []

        for item in raw_items:
            if not isinstance(item, dict):
                continue

            mapped_repository = map_repository_summary(item)

            repositories.append(
                mapped_repository.model_dump(mode="json")
            )

        total_count = response_data.get(
            "total_count",
            len(repositories),
        )

        if not isinstance(total_count, int):
            total_count = len(repositories)

        incomplete_results = response_data.get(
            "incomplete_results",
            False,
        )

        if not isinstance(incomplete_results, bool):
            incomplete_results = False

        return {
            "query": query,
            "language_filter": language,
            "sort": sort,
            "order": order,
            "total_matching_repositories": total_count,
            "returned_count": len(repositories),
            "incomplete_results": incomplete_results,
            "repositories": repositories,
        }

    async def get_repository_details(
        self,
        *,
        owner: str,
        repository: str,
    ) -> GitHubRepositoryDetails:
        response_data = await self._client.get_repository(
            owner=owner,
            repository=repository,
        )

        return map_repository_details(response_data)