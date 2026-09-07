from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
)


RepositorySort = Literal[
    "best_match",
    "stars",
    "forks",
    "help_wanted_issues",
    "updated",
]

SortOrder = Literal[
    "asc",
    "desc",
]


class GitHubRepositorySearchInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=256,
        description=(
            "Repository search terms, such as FastAPI, "
            "LangChain, testing automation, or AI agents."
        ),
    )

    language: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "Optional programming language filter, "
            "such as Python or TypeScript."
        ),
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description=(
            "Maximum number of repositories to return."
        ),
    )

    sort: RepositorySort = Field(
        default="best_match",
        description="How GitHub should sort the results.",
    )

    order: SortOrder = Field(
        default="desc",
        description="Ascending or descending sort order.",
    )

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())

        if not normalized:
            raise ValueError(
                "Repository search query cannot be empty."
            )

        return normalized

    @field_validator("language")
    @classmethod
    def normalize_language(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = " ".join(value.strip().split())

        return normalized or None


class GitHubRepositoryDetailsInput(BaseModel):
    owner: str = Field(
        min_length=1,
        max_length=100,
        description="GitHub repository owner or organization.",
    )

    repository: str = Field(
        min_length=1,
        max_length=100,
        description="GitHub repository name.",
    )

    @field_validator("owner", "repository")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Repository owner and name cannot be empty."
            )

        if "/" in normalized:
            raise ValueError(
                "Provide owner and repository separately."
            )

        return normalized


class GitHubRepositorySummary(BaseModel):
    id: int
    full_name: str
    owner: str
    name: str
    description: str | None
    html_url: HttpUrl
    language: str | None

    stars: int
    forks: int
    open_issues: int

    default_branch: str
    archived: bool
    private: bool
    fork: bool

    topics: list[str] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None


class GitHubRepositoryDetails(
    GitHubRepositorySummary
):
    homepage: HttpUrl | None = None
    size_kb: int
    watchers: int
    subscribers: int | None = None
    license_name: str | None = None
    visibility: str | None = None