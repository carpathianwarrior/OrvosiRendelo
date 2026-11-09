
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
class Rendelesido(Base):
    __tablename__ = "Rendelesido"
    __table_args__ = (
        CheckConstraint("vege > kezdete", name="ck_rendelesido_idotartam"),
        CheckConstraint("maxPaciens > 0", name="ck_rendelesido_maxpaciens"),
    )

    rendelesIdoId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kezdete: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    vege: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    maxPaciens: Mapped[int] = mapped_column(Integer, nullable=False)
    orvosId: Mapped[int] = mapped_column(ForeignKey("Orvos.orvosId"), nullable=False)
    szobaId: Mapped[int] = mapped_column(ForeignKey("Szobak.szobaId"), nullable=False)

    orvos: Mapped["Doctor"] = relationship(back_populates="rendelesidok")
    szoba: Mapped["Szobak"] = relationship(back_populates="rendelesidok")

    idopontok: Mapped[List["Idopont"]] = relationship(back_populates="rendelesido") 