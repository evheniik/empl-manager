from uuid import UUID

from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
    return db.query(Company).offset(skip).limit(limit).all()


def get_company(db: Session, company_id: UUID) -> Company | None:
    return db.get(Company, company_id)


def create_company(db: Session, data: CompanyCreate) -> Company:
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def update_company(db: Session, company: Company, data: CompanyUpdate) -> Company:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company: Company) -> None:
    db.delete(company)
    db.commit()