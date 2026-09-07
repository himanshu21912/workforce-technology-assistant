from typing import Any

from pydantic import ValidationError

from app.core.exceptions import (
    GitHubAuthenticationError,
    GitHubNotFoundError,
    GitHubRateLimitError,
    GitHubRequestError,
    GitHubResponseValidationError,
)
from app.integrations.github import GitHubClient
from app.schemas.github import GitHubRepositoryDetailsInput
from app.services import GitHubService
from app.tools.helpers import (
    failed_tool_response,
    successful_tool_response,
)


async def get_github_repository_details(
    owner: str,
    repository: str,
) -> dict[str, Any]:
    """
    Retrieve current details about one public GitHub repository.

    Use this tool when the GitHub repository owner and repository
    name are already known. The result includes current stars,
    forks, language, topics, issues, license, activity dates,
    homepage, and repository URL.

    Args:
        owner: GitHub user or organization that owns the repository.
        repository: Repository name without the owner prefix.

    Returns:
        A structured response containing repository details.
    """

    tool_name = "get_github_repository_details"

    try:
        request = GitHubRepositoryDetailsInput(
            owner=owner,
            repository=repository,
        )

        async with GitHubClient() as client:
            service = GitHubService(client)

            result = await service.get_repository_details(
                owner=request.owner,
                repository=request.repository,
            )

        return successful_tool_response(
            data={
                "repository": result.model_dump(
                    mode="json"
                ),
            },
            tool_name=tool_name,
        )

    except ValidationError as exception:
        return failed_tool_response(
            code="invalid_repository_request",
            message=(
                "The GitHub repository details request is "
                "invalid."
            ),
            tool_name=tool_name,
            details={
                "validation_errors": exception.errors(
                    include_url=False
                ),
            },
        )

    except GitHubNotFoundError:
        return failed_tool_response(
            code="github_repository_not_found",
            message=(
                f"GitHub repository "
                f"'{owner}/{repository}' was not found."
            ),
            tool_name=tool_name,
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
            code="github_repository_details_failed",
            message=(
                "GitHub repository details could not be "
                "retrieved."
            ),
            tool_name=tool_name,
        )