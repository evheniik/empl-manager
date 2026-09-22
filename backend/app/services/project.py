from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import company as company_crud
from app.crud import project as project_crud
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def _get_project_or_404(db: Session, project_id: UUID) -> Project:
    project = project_crud.get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


def _ensure_company_exists(db: Session, company_id: UUID) -> None:
    if company_crud.get_company(db, company_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )


def list_projects(
    db: Session,
    company_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Project]:
    return project_crud.get_projects(
        db, company_id=company_id, skip=skip, limit=limit
    )


def get_project(db: Session, project_id: UUID) -> Project:
    return _get_project_or_404(db, project_id)


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    _ensure_company_exists(db, project_in.company_id)
    return project_crud.create_project(db, project_in)


def update_project(
    db: Session, project_id: UUID, project_in: ProjectUpdate
) -> Project:
    project = _get_project_or_404(db, project_id)
    new_company_id = project_in.model_dump(exclude_unset=True).get("company_id")
    if new_company_id is not None and new_company_id != project.company_id:
        _ensure_company_exists(db, new_company_id)
    return project_crud.update_project(db, project, project_in)


def delete_project(db: Session, project_id: UUID) -> None:
    project = _get_project_or_404(db, project_id)
    project_crud.delete_project(db, project)