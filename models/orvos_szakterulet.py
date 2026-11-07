from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

class OrvosSzakterulet(Base):
    """Kapcsolótábla: Orvos <-> Szakterulet (N:M)."""
    __tablename__ = "OrvosSzakterulet"
    __table_args__ = (UniqueConstraint("orvosId", "szakteruletId"),)

    orvosSzakteruletId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orvosId: Mapped[int] = mapped_column(ForeignKey("Orvos.orvosId"), nullable=False)
    szakteruletId: Mapped[int] = mapped_column(ForeignKey("Szakterulet.szakteruletId"), nullable=False)

    orvos: Mapped["Doctor"] = relationship(back_populates="orvos_szakteruletek")
    szakterulet: Mapped["Szakterulet"] = relationship(back_populates="orvos_szakteruletek")