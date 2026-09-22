from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyDetail, CompanyRead, CompanyUpdate
from app.services import company as company_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[CompanyRead]:
    return company_service.list_companies(db, skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyDetail)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
) -> CompanyDetail:
    return company_service.get_company(db, company_id)


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyRead:
    return company_service.create_company(db, data)


@router.put("/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyRead:
    return company_service.update_company(db, company_id, data)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    company_service.delete_company(db, company_id)