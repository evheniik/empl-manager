from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services import employee as employee_service

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeRead])
def read_employees(
    company_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list:
    return employee_service.list_employees(
        db, company_id=company_id, skip=skip, limit=limit
    )


@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee(employee_id: UUID, db: Session = Depends(get_db)):
    return employee_service.get_employee(db, employee_id)


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return employee_service.create_employee(db, employee_in)


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: UUID,
    employee_in: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return employee_service.update_employee(db, employee_id, employee_in)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee_service.delete_employee(db, employee_id)