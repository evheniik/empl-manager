from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="company", cascade="all, delete-orphan", lazy="selectin"
    )
    projects: Mapped[list["Project"]] = relationship(
        back_populates="company", cascade="all, delete-orphan", lazy="selectin"
    )
