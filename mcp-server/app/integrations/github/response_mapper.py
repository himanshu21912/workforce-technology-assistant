from typing import Any

from pydantic import ValidationError

from app.core.exceptions import (
    GitHubResponseValidationError,
)
from app.schemas.github import (
    GitHubRepositoryDetails,
    GitHubRepositorySummary,
)


def _get_owner_login(
    repository_data: dict[str, Any],
) -> str:
    owner_data = repository_data.get("owner")

    if not isinstance(owner_data, dict):
        raise GitHubResponseValidationError(
            "GitHub repository owner data is missing."
        )

    owner_login = owner_data.get("login")

    if not isinstance(owner_login, str):
        raise GitHubResponseValidationError(
            "GitHub repository owner login is missing."
        )

    return owner_login


def map_repository_summary(
    repository_data: dict[str, Any],
) -> GitHubRepositorySummary:
    try:
        return GitHubRepositorySummary(
            id=repository_data["id"],
            full_name=repository_data["full_name"],
            owner=_get_owner_login(repository_data),
            name=repository_data["name"],
            description=repository_data.get("description"),
            html_url=repository_data["html_url"],
            language=repository_data.get("language"),
            stars=repository_data.get(
                "stargazers_count",
                0,
            ),
            forks=repository_data.get(
                "forks_count",
                0,
            ),
            open_issues=repository_data.get(
                "open_issues_count",
                0,
            ),
            default_branch=repository_data.get(
                "default_branch",
                "main",
            ),
            archived=repository_data.get(
                "archived",
                False,
            ),
            private=repository_data.get(
                "private",
                False,
            ),
            fork=repository_data.get(
                "fork",
                False,
            ),
            topics=repository_data.get(
                "topics",
                [],
            )
            or [],
            created_at=repository_data["created_at"],
            updated_at=repository_data["updated_at"],
            pushed_at=repository_data.get("pushed_at"),
        )

    except (KeyError, TypeError, ValidationError) as exception:
        raise GitHubResponseValidationError(
            "GitHub returned an invalid repository response."
        ) from exception


def map_repository_details(
    repository_data: dict[str, Any],
) -> GitHubRepositoryDetails:
    summary = map_repository_summary(repository_data)

    license_data = repository_data.get("license")

    license_name = None

    if isinstance(license_data, dict):
        raw_license_name = license_data.get("name")

        if isinstance(raw_license_name, str):
            license_name = raw_license_name

    try:
        return GitHubRepositoryDetails(
            **summary.model_dump(),
            homepage=repository_data.get("homepage") or None,
            size_kb=repository_data.get("size", 0),
            watchers=repository_data.get(
                "watchers_count",
                0,
            ),
            subscribers=repository_data.get(
                "subscribers_count"
            ),
            license_name=license_name,
            visibility=repository_data.get("visibility"),
        )

    except (TypeError, ValidationError) as exception:
        raise GitHubResponseValidationError(
            "GitHub returned invalid repository details."
        ) from exception