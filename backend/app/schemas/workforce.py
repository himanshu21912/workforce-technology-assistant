from pydantic import BaseModel, Field, field_validator


class EmployeeStatisticsInput(BaseModel):
    department: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "Optional department name used to restrict "
            "the statistics."
        ),
    )

    @field_validator("department")
    @classmethod
    def normalize_department(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            return None

        return cleaned_value


class WorkforceSkillAnalysisInput(BaseModel):
    department: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "Optional department name used to restrict "
            "the skill analysis."
        ),
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=25,
        description="Maximum number of skills to return.",
    )

    @field_validator("department")
    @classmethod
    def normalize_department(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            return None

        return cleaned_value