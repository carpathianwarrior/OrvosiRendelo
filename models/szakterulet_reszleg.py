from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
class SzakteruletReszleg(Base):

    __tablename__ = "SzakteruletReszleg"
    __table_args__ = (UniqueConstraint("szakteruletId", "reszlegId"),)

    szakteruletReszlegId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    szakteruletId: Mapped[int] = mapped_column(ForeignKey("Szakterulet.szakteruletId"), nullable=False)
    reszlegId: Mapped[int] = mapped_column(ForeignKey("Reszleg.reszlegId"), nullable=False)

    szakterulet: Mapped["Szakterulet"] = relationship(back_populates="szakterulet_reszlegek")
    reszleg: Mapped["Reszleg"] = relationship(back_populates="szakterulet_reszlegek")