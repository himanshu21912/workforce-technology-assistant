from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.employee import Employee
    from app.db.models.skill import Skill


class ProficiencyLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EmployeeSkill(TimestampMixin, Base):
    __tablename__ = "employee_skills"

    __table_args__ = (
        CheckConstraint(
            "years_of_experience >= 0",
            name="skill_experience_non_negative",
        ),
        Index(
            "ix_employee_skills_skill_proficiency",
            "skill_id",
            "proficiency_level",
        ),
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    skill_id: Mapped[int] = mapped_column(
        ForeignKey(
            "skills.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    proficiency_level: Mapped[ProficiencyLevel] = mapped_column(
        Enum(
            ProficiencyLevel,
            name="proficiency_level",
            native_enum=False,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        nullable=False,
    )

    years_of_experience: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="skill_associations",
    )

    skill: Mapped["Skill"] = relationship(
        back_populates="employee_associations",
    )

    def __repr__(self) -> str:
        return (
            f"EmployeeSkill(employee_id={self.employee_id!r}, "
            f"skill_id={self.skill_id!r}, "
            f"proficiency={self.proficiency_level!r})"
        )