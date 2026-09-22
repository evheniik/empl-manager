from uuid import UUID

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def get_employee(db: Session, employee_id: UUID) -> Employee | None:
    return db.get(Employee, employee_id)


def get_employees(
    db: Session,
    company_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Employee]:
    query = db.query(Employee)
    if company_id is not None:
        query = query.filter(Employee.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def create_employee(db: Session, employee_in: EmployeeCreate) -> Employee:
    employee = Employee(**employee_in.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(
    db: Session, employee: Employee, employee_in: EmployeeUpdate
) -> Employee:
    for field, value in employee_in.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()