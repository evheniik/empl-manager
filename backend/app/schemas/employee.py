from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    position: str
    company_id: UUID


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    company_id: Optional[UUID] = None


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: str
    position: str
    company_id: UUID
    created_at: datetime
