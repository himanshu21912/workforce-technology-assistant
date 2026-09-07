class GitHubIntegrationError(Exception):
    """Base exception for GitHub integration failures."""


class GitHubAuthenticationError(GitHubIntegrationError):
    """Raised when GitHub rejects authentication."""


class GitHubRateLimitError(GitHubIntegrationError):
    def __init__(
        self,
        message: str,
        *,
        remaining: int | None = None,
        reset_at: int | None = None,
    ) -> None:
        super().__init__(message)

        self.remaining = remaining
        self.reset_at = reset_at


class GitHubNotFoundError(GitHubIntegrationError):
    """Raised when a requested GitHub resource is absent."""


class GitHubRequestError(GitHubIntegrationError):
    """Raised for GitHub request or response failures."""


class GitHubResponseValidationError(
    GitHubIntegrationError
):
    """Raised for unsupported GitHub response structures."""