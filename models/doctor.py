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


class Szakterulet(Base):
    __tablename__ = "Szakterulet"

    szakteruletId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    megnevezes: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Szakterulet 1 --- 1..* OrvosSzakterulet ("nekik ez a szakterületük")
    orvos_szakteruletek: Mapped[List["OrvosSzakterulet"]] = relationship(back_populates="szakterulet")
    # Szakterulet 1 --- 1..* SzakteruletReszleg ("ezeken a részlegeken van")
    szakterulet_reszlegek: Mapped[List["SzakteruletReszleg"]] = relationship(back_populates="szakterulet")


class OrvosSzakterulet(Base):
    """Kapcsolótábla: Orvos <-> Szakterulet (N:M)."""
    __tablename__ = "OrvosSzakterulet"
    __table_args__ = (UniqueConstraint("orvosId", "szakteruletId"),)

    orvosSzakteruletId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orvosId: Mapped[int] = mapped_column(ForeignKey("Orvos.orvosId"), nullable=False)
    szakteruletId: Mapped[int] = mapped_column(ForeignKey("Szakterulet.szakteruletId"), nullable=False)

    orvos: Mapped["Doctor"] = relationship(back_populates="orvos_szakteruletek")
    szakterulet: Mapped["Szakterulet"] = relationship(back_populates="orvos_szakteruletek")
