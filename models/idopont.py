"""Időpontfoglalás és a kórházi struktúra (részleg, szoba) táblái."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

class Idopont(Base):
    __tablename__ = "Idopont"
    __table_args__ = (
        CheckConstraint("vege > kezdete", name="ck_idopont_idotartam"),
        # DB-szintű védelem a dupla foglalás ellen (egyszerre két folyamat esetén is)
        UniqueConstraint("rendelesIdoId", "kezdete", name="uq_idopont_rendelesido_kezdete"),
    )

    idopontId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kezdete: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    vege: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    betegId: Mapped[int] = mapped_column(ForeignKey("Beteg.betegId"), nullable=False)
    rendelesIdoId: Mapped[int] = mapped_column(ForeignKey("Rendelesido.rendelesIdoId"), nullable=False)

    beteg: Mapped["Patient"] = relationship(back_populates="idopontok")
    rendelesido: Mapped["Rendelesido"] = relationship(back_populates="idopontok")
    # Idopont 1 --- 0..1 Betegellatas ("megtörténik benne")
    betegellatas: Mapped[Optional["Betegellatas"]] = relationship(
        back_populates="idopont", uselist=False
    )