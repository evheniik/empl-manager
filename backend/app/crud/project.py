from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_project(db: Session, project_id: UUID) -> Project | None:
    return db.get(Project, project_id)


def get_projects(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    company_id: UUID | None = None,
) -> list[Project]:
    query = db.query(Project)
    if company_id is not None:
        query = query.filter(Project.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    project = Project(**project_in.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    project: Project,
    project_in: ProjectUpdate,
) -> Project:
    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()