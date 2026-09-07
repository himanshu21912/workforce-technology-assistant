from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.db.models.department import Department
    from app.db.models.employee_skill import EmployeeSkill


class Employee(TimestampMixin, Base):
    __tablename__ = "employees"

    __table_args__ = (
        CheckConstraint(
            "years_of_experience >= 0",
            name="years_of_experience_non_negative",
        ),
        Index(
            "ix_employees_department_role",
            "department_id",
            "role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    years_of_experience: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey(
            "departments.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    department: Mapped["Department"] = relationship(
        back_populates="employees",
    )

    skill_associations: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"Employee(id={self.id!r}, "
            f"name={self.name!r}, "
            f"email={self.email!r})"
        )