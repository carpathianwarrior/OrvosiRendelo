from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

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