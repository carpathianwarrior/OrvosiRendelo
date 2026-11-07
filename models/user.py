"""Közös felhasználó tábla: ide kerül a belépéshez szükséges összes adat."""
from typing import Optional

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import ROLE_DOCTOR, ROLE_PATIENT
from database.base import Base


class User(Base):
    __tablename__ = "Felhasznalo"
    __table_args__ = (
        CheckConstraint(f"szerep IN ('{ROLE_DOCTOR}', '{ROLE_PATIENT}')",
                        name="ck_felhasznalo_szerep"),
    )

    felhasznaloId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nev: Mapped[str] = mapped_column(String, nullable=False)
    TAJ: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True)
    jelszo_hash: Mapped[str] = mapped_column(String, nullable=False)
    szerep: Mapped[str] = mapped_column(String, nullable=False)

    # User 1 --- 0..1 Doctor / Patient (a szerep dönti el, melyik létezik)
    doctor: Mapped[Optional["Doctor"]] = relationship(back_populates="user", uselist=False)
    patient: Mapped[Optional["Patient"]] = relationship(back_populates="user", uselist=False)
