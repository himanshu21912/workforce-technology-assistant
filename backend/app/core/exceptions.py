class ApplicationError(Exception):
    """Base exception for controlled application failures."""


class EmployeeNotFoundError(ApplicationError):
    """Raised when an employee cannot be found."""


class DepartmentNotFoundError(ApplicationError):
    """Raised when a department cannot be found."""