from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: UUID


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[UUID] = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    company_id: UUID
    created_at: datetime
