from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import company as company_crud
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def _get_company_or_404(db: Session, company_id: UUID) -> Company:
    company = company_crud.get_company(db, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return company


def list_companies(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
    return company_crud.get_companies(db, skip=skip, limit=limit)


def get_company(db: Session, company_id: UUID) -> Company:
    return _get_company_or_404(db, company_id)


def create_company(db: Session, data: CompanyCreate) -> Company:
    return company_crud.create_company(db, data)


def update_company(db: Session, company_id: UUID, data: CompanyUpdate) -> Company:
    company = _get_company_or_404(db, company_id)
    return company_crud.update_company(db, company, data)


def delete_company(db: Session, company_id: UUID) -> None:
    company = _get_company_or_404(db, company_id)
    company_crud.delete_company(db, company)