"""Orvos és az orvosok szakterületeivel kapcsolatos táblák."""
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Doctor(Base):
    __tablename__ = "Orvos"

    orvosId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    felhasznaloId: Mapped[int] = mapped_column(
        ForeignKey("Felhasznalo.felhasznaloId"), nullable=False, unique=True
    )
    szakterulet: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="doctor")
    # Orvos 1 --- 1..* OrvosSzakterulet ("ezek a szakterületei")
    orvos_szakteruletek: Mapped[List["OrvosSzakterulet"]] = relationship(back_populates="orvos")
    # Orvos 1 --- 0..* Rendelesido ("rendel ekkor")
    rendelesidok: Mapped[List["Rendelesido"]] = relationship(back_populates="orvos")






