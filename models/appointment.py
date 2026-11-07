"""Időpontfoglalás és a kórházi struktúra (részleg, szoba) táblái."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


# --------------------------------------------------------------- kórházi struktúra
class Reszleg(Base):
    __tablename__ = "Reszleg"

    reszlegId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    megnevezes: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Reszleg 1 --- 1..* SzakteruletReszleg ("ezek a szakterületek vannak besorolva hozzá")
    szakterulet_reszlegek: Mapped[List["SzakteruletReszleg"]] = relationship(back_populates="reszleg")
    # Reszleg 1 --- 1..* Szobak ("ezek a szobák tartoznak hozzá")
    szobak: Mapped[List["Szobak"]] = relationship(back_populates="reszleg")


class SzakteruletReszleg(Base):
    """Kapcsolótábla: Szakterulet <-> Reszleg (N:M)."""
    __tablename__ = "SzakteruletReszleg"
    __table_args__ = (UniqueConstraint("szakteruletId", "reszlegId"),)

    szakteruletReszlegId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    szakteruletId: Mapped[int] = mapped_column(ForeignKey("Szakterulet.szakteruletId"), nullable=False)
    reszlegId: Mapped[int] = mapped_column(ForeignKey("Reszleg.reszlegId"), nullable=False)

    szakterulet: Mapped["Szakterulet"] = relationship(back_populates="szakterulet_reszlegek")
    reszleg: Mapped["Reszleg"] = relationship(back_populates="szakterulet_reszlegek")


class Szobak(Base):
    __tablename__ = "Szobak"

    szobaId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    szobaszam: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    leiras: Mapped[Optional[str]] = mapped_column(String)
    reszlegId: Mapped[int] = mapped_column(ForeignKey("Reszleg.reszlegId"), nullable=False)

    reszleg: Mapped["Reszleg"] = relationship(back_populates="szobak")
    rendelesidok: Mapped[List["Rendelesido"]] = relationship(back_populates="szoba")


# --------------------------------------------------------------- időpontfoglalás
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
    # Rendelesido 1 --- 1..* Idopont ("tartalmazza")
    idopontok: Mapped[List["Idopont"]] = relationship(back_populates="rendelesido")


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


class Betegellatas(Base):
    __tablename__ = "Betegellatas"

    betegellatasId: Mapped[str] = mapped_column(String, primary_key=True)
    panasz: Mapped[str] = mapped_column(String)
    diagnozis: Mapped[str] = mapped_column(String)
    eredmeny: Mapped[str] = mapped_column(String)
    # unique=True -> egy időponthoz legfeljebb egy ellátás tartozhat (0..1)
    idopontId: Mapped[int] = mapped_column(
        ForeignKey("Idopont.idopontId"), nullable=False, unique=True
    )

    idopont: Mapped["Idopont"] = relationship(back_populates="betegellatas")
