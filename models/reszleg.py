from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
class Reszleg(Base):
    __tablename__ = "Reszleg"

    reszlegId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    megnevezes: Mapped[str] = mapped_column(String, nullable=False, unique=True)


    szakterulet_reszlegek: Mapped[List["SzakteruletReszleg"]] = relationship(back_populates="reszleg")

    szobak: Mapped[List["Szobak"]] = relationship(back_populates="reszleg")