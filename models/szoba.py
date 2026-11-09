
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
class Szoba(Base):
    __tablename__ = "Szobak"

    szobaId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    szobaszam: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    leiras: Mapped[Optional[str]] = mapped_column(String)
    reszlegId: Mapped[int] = mapped_column(ForeignKey("Reszleg.reszlegId"), nullable=False)

    reszleg: Mapped["Reszleg"] = relationship(back_populates="szobak")
    rendelesidok: Mapped[List["Rendelesido"]] = relationship(back_populates="szoba")