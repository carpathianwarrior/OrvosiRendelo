"""Beteg."""
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Patient(Base):
    __tablename__ = "Beteg"

    betegId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    felhasznaloId: Mapped[int] = mapped_column(
        ForeignKey("Felhasznalo.felhasznaloId"), nullable=False, unique=True
    )
    telefonszam: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="patient")
    # Beteg 1 --- 0..* Idopont ("lefoglal")
    idopontok: Mapped[List["Idopont"]] = relationship(back_populates="beteg")
