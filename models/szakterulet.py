from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

class Szakterulet(Base):
    __tablename__ = "Szakterulet"

    szakteruletId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    megnevezes: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Szakterulet 1 --- 1..* OrvosSzakterulet ("nekik ez a szakterületük")
    orvos_szakteruletek: Mapped[List["OrvosSzakterulet"]] = relationship(back_populates="szakterulet")
    # Szakterulet 1 --- 1..* SzakteruletReszleg ("ezeken a részlegeken van")
    szakterulet_reszlegek: Mapped[List["SzakteruletReszleg"]] = relationship(back_populates="szakterulet")