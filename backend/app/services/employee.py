from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import company as company_crud
from app.crud import employee as employee_crud
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def _get_employee_or_404(db: Session, employee_id: UUID) -> Employee:
    employee = employee_crud.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee


def _ensure_company_exists(db: Session, company_id: UUID) -> None:
    if company_crud.get_company(db, company_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )


def _check_email_unique(
    db: Session, email: str, exclude_employee_id: UUID | None = None
) -> None:
    query = db.query(Employee).filter(Employee.email == email)
    if exclude_employee_id is not None:
        query = query.filter(Employee.id != exclude_employee_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with this email already exists",
        )


def list_employees(
    db: Session,
    company_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Employee]:
    return employee_crud.get_employees(
        db, company_id=company_id, skip=skip, limit=limit
    )


def get_employee(db: Session, employee_id: UUID) -> Employee:
    return _get_employee_or_404(db, employee_id)


def create_employee(db: Session, employee_in: EmployeeCreate) -> Employee:
    _ensure_company_exists(db, employee_in.company_id)
    _check_email_unique(db, employee_in.email)
    return employee_crud.create_employee(db, employee_in)


def update_employee(
    db: Session, employee_id: UUID, employee_in: EmployeeUpdate
) -> Employee:
    employee = _get_employee_or_404(db, employee_id)
    update_data = employee_in.model_dump(exclude_unset=True)
    if "company_id" in update_data:
        _ensure_company_exists(db, update_data["company_id"])
    if "email" in update_data:
        _check_email_unique(db, update_data["email"], exclude_employee_id=employee.id)
    return employee_crud.update_employee(db, employee, employee_in)


def delete_employee(db: Session, employee_id: UUID) -> None:
    employee = _get_employee_or_404(db, employee_id)
    employee_crud.delete_employee(db, employee)