from collections.abc import Mapping
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import (
    GitHubAuthenticationError,
    GitHubNotFoundError,
    GitHubRateLimitError,
    GitHubRequestError,
)


class GitHubClient:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()

        self._owns_client = client is None

        self._client = client or httpx.AsyncClient(
            base_url=settings.github_api_base_url,
            timeout=httpx.Timeout(
                settings.github_request_timeout
            ),
            headers=self._build_headers(),
            follow_redirects=True,
        )

    @staticmethod
    def _build_headers() -> dict[str, str]:
        settings = get_settings()

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": (
                settings.github_api_version
            ),
            "User-Agent": settings.github_user_agent,
        }

        if settings.github_token:
            headers["Authorization"] = (
                f"Bearer {settings.github_token}"
            )

        return headers

    @staticmethod
    def _parse_optional_integer(
        value: str | None,
    ) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None

    @classmethod
    def _raise_for_error(
        cls,
        response: httpx.Response,
    ) -> None:
        if response.status_code < 400:
            return

        message = "GitHub request failed."

        try:
            response_data = response.json()

            if isinstance(response_data, dict):
                github_message = response_data.get("message")

                if isinstance(github_message, str):
                    message = github_message
        except ValueError:
            pass

        remaining = cls._parse_optional_integer(
            response.headers.get("X-RateLimit-Remaining")
        )

        reset_at = cls._parse_optional_integer(
            response.headers.get("X-RateLimit-Reset")
        )

        if response.status_code == 401:
            raise GitHubAuthenticationError(
                "GitHub authentication failed."
            )

        if response.status_code == 404:
            raise GitHubNotFoundError(
                "The requested GitHub resource was not found."
            )

        if response.status_code == 429 or (
            response.status_code == 403
            and remaining == 0
        ):
            raise GitHubRateLimitError(
                message,
                remaining=remaining,
                reset_at=reset_at,
            )

        raise GitHubRequestError(
            f"GitHub returned HTTP "
            f"{response.status_code}: {message}"
        )

    async def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
    ) -> httpx.Response:
        try:
            response = await self._client.get(
                path,
                params=params,
            )
        except httpx.TimeoutException as exception:
            raise GitHubRequestError(
                "The GitHub request timed out."
            ) from exception
        except httpx.RequestError as exception:
            raise GitHubRequestError(
                "The GitHub API could not be reached."
            ) from exception

        self._raise_for_error(response)

        return response

    async def search_repositories(
        self,
        *,
        query: str,
        language: str | None,
        limit: int,
        sort: str,
        order: str,
    ) -> dict[str, Any]:
        qualified_query = query

        if language:
            qualified_query = (
                f"{qualified_query} language:{language}"
            )

        parameters: dict[str, str | int] = {
            "q": qualified_query,
            "per_page": limit,
            "page": 1,
            "order": order,
        }

        if sort != "best_match":
            parameters["sort"] = sort

        response = await self._get(
            "/search/repositories",
            params=parameters,
        )

        response_data = response.json()

        if not isinstance(response_data, dict):
            raise GitHubRequestError(
                "GitHub returned an unsupported search response."
            )

        return response_data

    async def get_repository(
        self,
        *,
        owner: str,
        repository: str,
    ) -> dict[str, Any]:
        response = await self._get(
            f"/repos/{owner}/{repository}",
        )

        response_data = response.json()

        if not isinstance(response_data, dict):
            raise GitHubRequestError(
                "GitHub returned unsupported repository data."
            )

        return response_data

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "GitHubClient":
        return self

    async def __aexit__(
        self,
        exception_type,
        exception,
        traceback,
    ) -> None:
        await self.close()