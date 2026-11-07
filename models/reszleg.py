"""Időpontfoglalás és a kórházi struktúra (részleg, szoba) táblái."""
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

    # Reszleg 1 --- 1..* SzakteruletReszleg ("ezek a szakterületek vannak besorolva hozzá")
    szakterulet_reszlegek: Mapped[List["SzakteruletReszleg"]] = relationship(back_populates="reszleg")
    # Reszleg 1 --- 1..* Szobak ("ezek a szobák tartoznak hozzá")
    szobak: Mapped[List["Szobak"]] = relationship(back_populates="reszleg")