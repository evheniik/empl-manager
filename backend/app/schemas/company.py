from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime


class _EmployeeBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: str
    position: str


class _ProjectBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None


class CompanyDetail(CompanyRead):
    employees: list[_EmployeeBrief] = []
    projects: list[_ProjectBrief] = []
