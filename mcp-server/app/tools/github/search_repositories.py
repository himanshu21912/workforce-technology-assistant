from typing import Any

from pydantic import ValidationError

from app.core.exceptions import (
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubRequestError,
    GitHubResponseValidationError,
)
from app.integrations.github import GitHubClient
from app.schemas.github import GitHubRepositorySearchInput
from app.services import GitHubService
from app.tools.helpers import (
    failed_tool_response,
    successful_tool_response,
)


async def search_github_repositories(
    query: str,
    language: str | None = None,
    limit: int = 5,
    sort: str = "best_match",
    order: str = "desc",
) -> dict[str, Any]:
    """
    Search current public GitHub repositories.

    Use this tool when current public repository information is
    required, including repository discovery, popularity, stars,
    forks, programming languages, topics, recent activity, or
    open-source project recommendations.

    Args:
        query: Repository search terms.
        language: Optional programming language filter.
        limit: Maximum number of repositories to return.
        sort: Sorting method. Supported values are best_match,
            stars, forks, help_wanted_issues, and updated.
        order: Sort order. Supported values are asc and desc.

    Returns:
        A structured response containing matching repositories.
    """

    tool_name = "search_github_repositories"

    try:
        request = GitHubRepositorySearchInput(
            query=query,
            language=language,
            limit=limit,
            sort=sort,
            order=order,
        )

        async with GitHubClient() as client:
            service = GitHubService(client)

            result = await service.search_repositories(
                query=request.query,
                language=request.language,
                limit=request.limit,
                sort=request.sort,
                order=request.order,
            )

        return successful_tool_response(
            data=result,
            tool_name=tool_name,
        )

    except ValidationError as exception:
        return failed_tool_response(
            code="invalid_search_request",
            message="The repository search request is invalid.",
            tool_name=tool_name,
            details={
                "validation_errors": exception.errors(
                    include_url=False
                ),
            },
        )

    except GitHubAuthenticationError:
        return failed_tool_response(
            code="github_authentication_failed",
            message=(
                "GitHub authentication failed. Check the "
                "configured GitHub token."
            ),
            tool_name=tool_name,
        )

    except GitHubRateLimitError as exception:
        return failed_tool_response(
            code="github_rate_limit_exceeded",
            message=(
                "The GitHub API rate limit has been exceeded."
            ),
            tool_name=tool_name,
            details={
                "remaining": exception.remaining,
                "reset_at": exception.reset_at,
            },
        )

    except GitHubResponseValidationError:
        return failed_tool_response(
            code="github_response_invalid",
            message=(
                "GitHub returned repository data in an "
                "unexpected format."
            ),
            tool_name=tool_name,
        )

    except GitHubRequestError as exception:
        return failed_tool_response(
            code="github_request_failed",
            message=str(exception),
            tool_name=tool_name,
        )

    except Exception:
        return failed_tool_response(
            code="github_search_failed",
            message=(
                "The GitHub repository search could not be "
                "completed."
            ),
            tool_name=tool_name,
        )