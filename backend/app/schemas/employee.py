from pydantic import BaseModel, Field, field_validator

from app.db.models.employee_skill import ProficiencyLevel


class EmployeeSkillResponse(BaseModel):
    id: int
    name: str
    category: str
    proficiency_level: ProficiencyLevel
    years_of_experience: int


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department: str
    department_location: str | None
    years_of_experience: int
    skills: list[EmployeeSkillResponse]


class EmployeeSearchInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=100,
        description=(
            "Employee name, email, role, department, skill, "
            "or other workforce keyword to search for."
        ),
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of employees to return.",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Search query cannot be empty.")

        return cleaned_value


class EmployeeDetailsInput(BaseModel):
    employee_id: int | None = Field(
        default=None,
        ge=1,
        description="Unique numeric employee identifier.",
    )

    email: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
        description="Employee email address.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip().lower()

        if not cleaned_value:
            return None

        return cleaned_value

    def validate_identifier(self) -> None:
        provided_identifiers = sum(
            value is not None
            for value in (
                self.employee_id,
                self.email,
            )
        )

        if provided_identifiers != 1:
            raise ValueError(
                "Provide exactly one of employee_id or email."
            )